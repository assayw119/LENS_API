from langchain_community.utilities.sql_database import SQLDatabase
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from app.core.config import settings

from fastapi import HTTPException

import inspect

import mysql.connector
from mysql.connector import Error
from app.core.store import chat_history_store  # store 모듈을 가져옴
from typing import List


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    session_history = chat_history_store.get(session_id)
    if not session_history:
        session_history = InMemoryChatMessageHistory()
        chat_history_store.set(session_id, session_history)
    else:
        memory = ConversationBufferWindowMemory(
            chat_memory=session_history,
            k=10,
            return_messages=True,
        )
        key = memory.memory_variables[0]
        messages = memory.load_memory_variables({})[key]
        session_history = InMemoryChatMessageHistory(messages=messages)
        chat_history_store.set(session_id, session_history)
    return session_history


@tool
def get_table_info() -> str:
    """Extract all table information from database

    Args:
        None

    Returns:
        str: Information about the all tables.
    """
    db = SQLDatabase.from_uri(settings.DATABASE_URL)
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

    database = settings.DATABASE
    host = settings.DATABASE_HOST
    user = settings.DATABASE_USER
    password = settings.DATABASE_PASSWORD

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute(query)
            rows = cursor.fetchall()

    except Error as e:
        raise HTTPException(status_code=404, detail=e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return str(rows)


def callLLM():
    API_KEY = settings.API_KEY
    # API_BASE = settings.API_BASE

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=API_KEY,
    )

    tools = [get_table_info, run_sql_query]
    llm_with_tools = llm.bind_tools(tools)
    chain = RunnableWithMessageHistory(llm_with_tools, get_session_history)

    return chain


async def process_message(user_prompt: str, session_id: str, sql_array: List) -> str:

    constraints = """
    --- start of constraints ---
    - 현재 데이터베이스는 MariaDB를 사용합니다. 쿼리를 생성하면 반드시 MariaDB에서 실행할 수 있는 쿼리로 생성해야 합니다.
    - run_sql_query 툴을 사용하여 쿼리를 실행한 결과를 받으면, 데이터 조회 여부를 통해 실행 가능한 쿼리인지 확인해야 합니다.
    - 답변에는 데이터 행을 반환하지 않고 쿼리에 대한 설명만 포함합니다.
    - 쿼리에 대한 설명에는 쿼리 생성 전략, 실행 효율에 대한 평가 등을 포함해서 최소 3줄 이상으로 작성하고 절대 쿼리를 포함하지 않습니다.
    - 사용자에게 답변할 때 조회한 데이터를 절대 반환하지 않습니다.
    - 그 외는 자유롭게 질문에 대해 답변을 제공합니다.
    --- end of constraints ---

    {user_prompt}
    """

    messages = [HumanMessage(constraints.format(user_prompt=user_prompt))]
    chain = callLLM()

    while True:
        ai_msg = chain.invoke(
            messages,
            config={"configurable": {"session_id": session_id}},
        )

        if ai_msg.tool_calls:
            new_messages = []
            for tool_call in ai_msg.tool_calls:
                selected_tool = {
                    "get_table_info": get_table_info,
                    "run_sql_query": run_sql_query
                }.get(tool_call["name"].lower())

                if selected_tool:
                    try:
                        if inspect.iscoroutinefunction(selected_tool.invoke):
                            tool_output = await selected_tool.invoke(tool_call["args"])
                        else:
                            tool_output = selected_tool.invoke(
                                tool_call["args"])
                    except Exception as e:
                        tool_output = str(e)

                    if tool_call["name"].lower() == "run_sql_query":
                        sql_array.append(tool_call["args"])
                    new_messages.append(ToolMessage(content=str(
                        tool_output), tool_call_id=tool_call["id"]))
                else:
                    new_messages.append(ToolMessage(
                        content=f"Tool '{tool_call['name']}' not found", tool_call_id=tool_call["id"]))

            messages = new_messages
        else:
            ai_message = AIMessage(content=ai_msg.content)
            session_history = chat_history_store.get(session_id)
            if session_history:
                session_history.add_message(ai_message)
            else:
                new_history = InMemoryChatMessageHistory(messages=[ai_message])
                chat_history_store.set(session_id, new_history)
            return ai_msg.content
