from mindsdb_sdk import connect
from dotenv import load_dotenv
from .queries import (
    CREATE_AGENT_QUERY,
    CREATE_KNOWLEDGE_BASE_QUERY,
    INSERT_KNOWLEDGE_BASE_QUERY,
    SELECT_ANSWER_QUERY,
)
from json import dumps

load_dotenv()
server = connect()
files_db = server.get_database("files")

PROJECT_NAME = "herbal_rem"
KB_NAME = f"{PROJECT_NAME}.remedy_kb"


def setup():
    server.create_project("herbal")

    run_query(CREATE_KNOWLEDGE_BASE_QUERY)
    run_query(INSERT_KNOWLEDGE_BASE_QUERY)
    run_query(CREATE_AGENT_QUERY)


def run_query(query: str):
    return server.query(query).fetch()


def run_agent(question: str) -> str:
    query = SELECT_ANSWER_QUERY.format(question=question)
    result = run_query(query)
    if (
        result is not None
        and hasattr(result, "empty")
        and not result.empty
        and "answer" in result
    ):
        return result["answer"][0]
    else:
        return "No answer found."


def create_kb_query(embedding_model):
    return f"""
CREATE KNOWLEDGE BASE IF NOT EXISTS {KB_NAME}
...
""".format(embedding_model=dumps(embedding_model))


def insert_kb_query(embedding_model):
    return f"""
INSERT INTO {KB_NAME} (
    SELECT ...
    FROM files.herbal_data
);
"""
