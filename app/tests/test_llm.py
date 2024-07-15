from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from typing import List

store = {}

# 세션 히스토리를 가져오기


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # session_id로 조회가 된다면 직전 3개의 message만 가져옴
    memory = ConversationBufferWindowMemory(
        chat_memory=store[session_id],
        k=10,
        return_messages=True,
    )
    assert len(memory.memory_variables) == 1
    key = memory.memory_variables[0]
    messages = memory.load_memory_variables({})[key]
    store[session_id] = InMemoryChatMessageHistory(messages=messages)
    return store[session_id]


@tool
def get_table_info() -> str:
    """Extract all table information from database

    Args:
        None

    Returns:
        str: Information about the all tables.
    """
    db = SQLDatabase.from_uri("sqlite:///./sql_app.db")
    db_info = db.get_table_info()
    return db_info


@tool
def run_sql_query(query: str) -> str:
    """Run a SQL query against the database.

    Args:
        query (str): The SQL query to execute.

    Returns:
        str: The result of the query.
    """
    db = SQLDatabase.from_uri("sqlite:///./sql_app.db")
    result = db.run(query)
    return str(result)


def process_message(user_prompt: str, session_id: str) -> str:
    messages = [HumanMessage(user_prompt)]

    while True:
        ai_msg = chain.invoke(
            messages,
            config={"configurable": {"session_id": session_id}},
        )

        if ai_msg.tool_calls:
            new_messages = []
            for tool_call in ai_msg.tool_calls:
                selected_tool = {"get_table_info": get_table_info, "run_sql_query": run_sql_query}[
                    tool_call["name"].lower()]
                tool_output = selected_tool.invoke(tool_call["args"])
                new_messages.append(ToolMessage(content=str(
                    tool_output), tool_call_id=tool_call["id"]))
            messages = new_messages
        else:
            return ai_msg.content


API_KEY = "152d00e9-bfc6-4097-9f75-91c91d42898a"
API_BASE = "http://43.202.9.204:8080/aihub/v2/sandbox"
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=API_KEY,
    openai_api_base=API_BASE,
)

tools = [get_table_info, run_sql_query]

llm_with_tools = llm.bind_tools(tools)

chain = RunnableWithMessageHistory(llm_with_tools, get_session_history)

while True:
    user_prompt = input("Enter your message: ")
    session_id = "1"  # This can be dynamic based on user session management

    response = process_message(user_prompt, session_id)
