from typing import Optional

import chainlit as cl

from bot import create_extract_agent, create_perimiter_agent, create_sql_agent
from permit_client import pdp
from schema import InvalidInformation, InvalidRequest
from tools import AgentContext
from utils import check_authentication, perform_sql_query

extract_agent = create_extract_agent()
perimiter_agent = create_perimiter_agent()
sql_agent = create_sql_agent()


@cl.on_message
async def get_response(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "parts": [{"text": message.content}]})
    response = extract_agent.run_sync(str(history))
    response = response.output
    elements = None
    if isinstance(response, InvalidRequest):
        msg = response.message
    else:
        deps = AgentContext(
            recentquery=message.content,
            usermetadata=cl.user_session.get("user").metadata,
            action=response.action,
            resource=response.resource,
            permit=pdp,
        )
        permitted_bot_response = perimiter_agent.run_sync(str(history), deps=deps)
        print(permitted_bot_response.output)
        if permitted_bot_response.output.can_proceed:
            sql_response = sql_agent.run_sync(str(history))
            if isinstance(sql_response.output, InvalidInformation):
                msg = sql_response.output.error_message
            else:
                msg = sql_response.output.sql_query
                df = perform_sql_query(msg)
                if not isinstance(df, str):
                    elements = [cl.Dataframe(data=df, display="inline")]
        else:
            msg = permitted_bot_response.output.message

    history.append({"role": "model", "parts": [{"text": msg}]})
    cl.user_session.set("history", history)

    await cl.Message(content=msg, elements=elements).send()


@cl.on_chat_start
async def chat_start():
    cl.user_session.set("history", [])


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    user = check_authentication(username, password)
    print(user)
    if user:
        return cl.User(identifier=user["name"], metadata=user)
    return None
