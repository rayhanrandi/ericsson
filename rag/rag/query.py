from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

from langchain.chains import create_sql_query_chain

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class LLMQuery:
    """
    Initializes connection to DB for LLM to create queries according to user questions.
    """
    
    def __init__(
        self,
        db_user: str, db_host: str, db_port: str, db_name: str,
        together_endpoint: str, together_api_key: str, together_llm_model: str,
        input_variables: list[str],
        template: str,
        db_password: str = None
    ):
        self.db_uri = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        self.db = SQLDatabase.from_uri(self.db_uri)
        self.llm = ChatOpenAI(
            base_url=together_endpoint,
            api_key=together_api_key,
            model=together_llm_model,
            temperature=0,
            verbose=True
        )
        self.input_variables = input_variables
        self.template = template

    def write_query(self):
        return create_sql_query_chain(
            llm=self.llm, 
            db=self.db, 
            prompt= PromptTemplate(
                input_variables=self.input_variables,
                template=self.template
            )
        )

    def execute_query(self):
        return QuerySQLDataBaseTool(db=self.db)
    