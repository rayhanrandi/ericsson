from datetime import datetime

from langchain_core.prompts import PromptTemplate

from config.db.clickhouse import ClickhouseClient
from config.logging import Logger
from config.utils import setup_env, get_env_value
from dotenv import load_dotenv

from rag.query import LLMQuery
from rag.response import LLMResponse


logger = Logger().setup_logger("rag")

load_dotenv()

logger.info(f' [*] Starting LLM call...')


template = '''You are a Clickhouse SQL expert. Given an input question, first create a syntactically correct Clickhouse SQL query to run, then look at the results of the query and return the answer to the input question.
You have access to a database containing a variety of historical and recent data entries from an observability monitoring system.
For this task, focus only on date and time constraint provided in the question. That means that you have to query for rows where the time between now (NOW()) and the requested time is valid.
Your analysis should not consider data older than this time window, even if it is accessible. 
Analyze the resulting data to produce relevant insights, trends, or observations. 

Unless the user specifies in the question a specific number of examples to obtain, query for all data in the database. Else query for at most {top_k} results using the LIMIT clause as per PostgreSQL.
Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns or rows that do not exist. Also, pay attention to which column is in which table.
Pay attention to use NOW() function to get the current date and time, as your query must contain rows that are 15 minutes behind current time and date.
The question will contain the sentence "XX minutes"", which means that you have to calculate the time difference between NOW() and  

That being said, answer the question in the following structure if none of the above conditions are violated.

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:
{table_info}

Remember to output the SQL query that is executed!
If there are any errors, ALWAYS output what the error is and the executed query.

Question: {input}'''

template="""You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
You have access to a database containing a variety of historical and recent data entries from an observability monitoring system.
For this task, focus only on the entries from the requested time interval.
Your analysis should not consider data older than this time window, even if it is accessible. 
Analyze the recent data exclusively to produce relevant insights, trends, or observations. 

Data Retrieval Instructions:
1. Retrieve only records from the requested time interval, disregarding all older data.
2. If records from the requested time interval are insufficient or unavailable, return an output indicating no relevant recent data was found.

Summary of Required Analysis:
- Total number of records in the requested time interval
- Average values, high/low points, or spikes observed in the recent data (if applicable) for all columns.
- Any notable patterns or deviations from expected values in the requested time interval.
- Are there any outliers based on the prediction column.

Instructions:
1. Based on the provided data, summarize any observed patterns, trends, or potential anomalies from the requested time interval only.
2. Highlight any irregularities or deviations that may need attention.
3. Identify any immediate insights that could be drawn from the data set gathered from the requested time interval.

DO NOT BY ANY MEANS make up any information. 
IF there is not enough data or an error occured that resulted in no data gathered for the analysis, DO NOT by any means make up any information.
Instead, say that there are currently not enough data or there may be issues with the analysis, and to please try again later.

Unless the user specifies in the question a specific number of examples to obtain, query for all data in the database. Else query for at most {top_k} results using the LIMIT clause as per PostgreSQL.
Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns or rows that do not exist. Also, pay attention to which column is in which table.

If the question is asking for data that does not exist in any of the database tables, do NOT by any means return an SQL Query.
Instead, respond by saying "There is not enough data to analyze.".

That being said, answer the question in the following structure if none of the above conditions are violated.

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:
{table_info}

Question: {input}"""

logger.info(' [*] Setting up LLM query...')
q = LLMQuery(
    db_host=get_env_value("CLICKHOUSE_HOST"),
    db_port=get_env_value("CLICKHOUSE_PORT"),
    db_user=get_env_value("CLICKHOUSE_USERNAME"),
    # db_password=get_env_value("CLICKHOUSE_PASSWORD"),
    db_name=get_env_value("CLICKHOUSE_DATABASE"),
    together_endpoint=get_env_value("TOGETHER_ENDPOINT"),
    together_api_key=get_env_value("TOGETHER_API_KEY"),
    together_llm_model=get_env_value("TOGETHER_LLM_MODEL"),
    input_variables=["question", "top_k", "table_info"],
    template=template
)

prompt = PromptTemplate.from_template("""Given the following user question, corresponding SQL query, and SQL result, answer the user question with the following format:

Question: {question}
SQL Query: {query}
SQL Result: {result}
                                    
Answer: """
)

answer_prompt = PromptTemplate.from_template("""Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}

If the SQL query isn't syntactically valid, or it returns a generic set of rows or columns,
respond by saying "There is not enough data to analyze" and do NOT mention anything regarding SQL/SQL queries or any errors!.

Please remember this one important rule when you don't have enough information about the question:
Do NOT mention anything regarding SQL/SQL queries or any errors!

Answer:""")

logger.info(f' [*] Setting up LLM response...')
llm_response = LLMResponse(
    answer_prompt=answer_prompt,
    llm_query=q
)

question = f'''What is the overall analysis of the data from the last {get_env_value("DATA_INTERVAL")} days? 
Are there any key insights or observabilities?
Are there any outlier data based on the prediction column?
Are there any possible mitigations to perform if there are any issues?'''


# save summary to db for grafana dashboard query
# conform to sql escape characters
logger.info(' [*] Calling LLM...')
summary = llm_response.get_response(question)

logger.info( f' [*] LLM response: \n{summary}')

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

ch_client = ClickhouseClient(
    host=get_env_value("CLICKHOUSE_HOST"),
    port=get_env_value("CLICKHOUSE_PORT"),
    user=get_env_value("CLICKHOUSE_USERNAME"),
    # password=get_env_value("CLICKHOUSE_PASSWORD"),
    database=get_env_value("CLICKHOUSE_DATABASE"),
    table=get_env_value("CLICKHOUSE_SUMMARY_TABLE")
)

values = { 
    "timestamp": timestamp,
    "summary": summary
}

try:
    query_code = ch_client.execute_insert(values)
except Exception as e:
    logger.error(f' [X] Query failed: {e}')

logger.info(f' [*] Query executed with result: {str(type(query_code)) or "unsuccessful 400"}.')
