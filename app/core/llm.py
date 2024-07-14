from langchain_community.utilities.sql_database import SQLDatabase
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from core.config import Settings

from fastapi import HTTPException

import inspect

import mysql.connector
from mysql.connector import Error

store = {}


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
    """Extract all table information from MariaDB database
    
    Args:
        None
        
    Returns:
        str: Information about all tables in the database.
    """
    settings = Settings()
    database = settings.DATABASE
    host = settings.DATABASE_HOST
    user = settings.DATABASE_USER
    password = settings.DATABASE_PASSWORD

    try:
        # MariaDB에 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # 테이블 목록 조회
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            table_info = []
            for table in tables:
                table_name = table[f'Tables_in_{database}']
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                table_info.append({
                    'table_name': table_name,
                    'columns': columns
                })

            return table_info
    
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



@tool
def run_sql_query(query: str) -> str:
    """Run a SQL query against the database.
    
    Args:
        query (str): The SQL query to execute.
        
    Returns:
        str: The result of the query.
    """
    # db = SQLDatabase.from_uri("sqlite:///./sql_app.db")
    # result = db.run(query)

    settings = Settings()
    database = settings.DATABASE
    host = settings.DATABASE_HOST
    user = settings.DATABASE_USER
    password = settings.DATABASE_PASSWORD

    try:
        # MariaDB에 연결
        connection = mysql.connector.connect(
            host=host,  # 또는 'localhost' for local connections
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():            
            cursor = connection.cursor()

            # 데이터베이스 버전 확인
            cursor.execute("SELECT VERSION();")
            record = cursor.fetchone()
            print("MariaDB 버전:", record)
            
            # 데이터 조회
            cursor.execute(query)
            rows = cursor.fetchall()
            print("test_table의 데이터:")
            for row in rows:
                print(row)
    
    except Error as e:
        raise HTTPException(status_code=404, detail=e)
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return str(rows)


def callLLM():
    settings = Settings()
    API_KEY = settings.API_KEY
    API_BASE = settings.API_BASE

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=API_KEY,
        openai_api_base=API_BASE,
    )

    tools = [get_table_info, run_sql_query]
    llm_with_tools = llm.bind_tools(tools)
    chain = RunnableWithMessageHistory(llm_with_tools, get_session_history)

    return chain


async def process_message(user_prompt: str, session_id: str) -> str:
    messages = [HumanMessage(user_prompt)]
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
                        # Handle exceptions raised during tool invocation
                        tool_output = str(e)
                        # Log or handle the error appropriately

                    new_messages.append(ToolMessage(content=str(
                        tool_output), tool_call_id=tool_call["id"]))
                else:
                    # Handle case where tool is not found for the given tool_call
                    new_messages.append(ToolMessage(
                        content=f"Tool '{tool_call['name']}' not found", tool_call_id=tool_call["id"]))

            messages = new_messages
        else:
            return ai_msg.content
