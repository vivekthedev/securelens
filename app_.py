import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from permit import Permit

from bot import create_permit_agent, create_query_agent
from schema import AllMessages, InvalidRequest, Permission

permit = Permit(
    pdp="https://cloudpdp.api.permit.io",
    token=os.environ["PERMIT_PDP"],
)


app = FastAPI()


origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

query_agent = create_query_agent()
permit_agent = create_permit_agent()


@app.post("/")
def get_response(context: AllMessages):
    chat_history = str(context.messages)
    query = f"CHAT HISTORY: {chat_history} QUERY IS THE LAST MESSAGE"
    response = permit_agent.run_sync(query).output

    if isinstance(response, InvalidRequest):
        return {"error": True, "error_message": response.message}

    return {"response": response.output}


# @app.post('/')
async def check_permissions(permission: Permission):
    """Check if the user has permission to perform the action on the resource."""

    permitted = await permit.check(
        permission.user_id, permission.action, permission.resource
    )
    if permitted:
        return {
            "result": f"{permission.user_id} is PERMITTED to {permission.action} {permission.resource}!"
        }
    else:
        return {"permitted": "no"}
