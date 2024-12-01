from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from config.utils import get_env_value

from rag.query import LLMQuery


class LLMResponse:
    """
    Gets response from LLM based on query results and given answer prompt.
    """

    def __init__(
        self,
        answer_prompt: PromptTemplate,
        llm_query: LLMQuery
    ):
       self.answer_prompt = answer_prompt
       self.llm_query = llm_query

    def get_response(self, question: str):
        chain = (
            RunnablePassthrough.assign(query=self.llm_query.write_query()).assign(
                result=itemgetter("query") | self.llm_query.execute_query()
            )
            | self.answer_prompt
            | self.llm_query.llm
            | StrOutputParser()
        )
        response = chain.invoke({
            "top_k": None,
            "question": question,
            "table_info": get_env_value("DB_TABLE")
        })
        return response
       