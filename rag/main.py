from datetime import datetime

from langchain.prompts import ChatPromptTemplate

from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import (
    Clickhouse, 
    ClickhouseSettings
)
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.logging import Logger
from config.utils import setup_env, get_env_value

from rag.query import LLMQuery
from rag.response import LLMResponse
from sql.postgresql import PostgreSQLClient


logger = Logger().setup_logger("rag")

setup_env()

template = '''You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
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

q = LLMQuery(
    db_host=get_env_value("DB_HOST"),
    db_port=get_env_value("DB_PORT"),
    db_user=get_env_value("DB_USER"),
    db_password=get_env_value("DB_PASSWORD"),
    db_name=get_env_value("DB_NAME"),
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

llm_response = LLMResponse(
    answer_prompt=answer_prompt,
    llm_query=q
)

question = f'''What is the overall analysis of the data from the last {get_env_value("DATA_INTERVAL")} minutes? 
Are there any key insights or observabilities? 
Are there any possible mitigations to perform if there are any issues?'''


# save summary to db for grafana dashboard query
# conform to sql escape characters
summary = llm_response.get_response(question).replace("'", "''")

logger.info( f' [*] LLM response: \n{summary}')

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

sql_client = PostgreSQLClient(
    host=get_env_value("DB_HOST"),
    port=get_env_value("DB_PORT"),
    user=get_env_value("DB_USER"),
    password=get_env_value("DB_PASSWORD"),
    database=get_env_value("DB_NAME")
)
table = get_env_value('DB_TABLE') 

query = f"""INSERT INTO {table} (summary, time) VALUES(E'{summary}', '{timestamp}')"""

try:
    query_code = sql_client.query(query)
except Exception as e:
    logger.error(f' [x] Query failed: {e}')

logger.info(f' [*] Query successful with code {query_code}.')