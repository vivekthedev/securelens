import os

from dotenv import load_dotenv
from permit import Permit, UserRead

load_dotenv()
import asyncio
import sqlite3

pdp = Permit(
    pdp="https://cloudpdp.api.permit.io",
    token=os.environ["PERMIT_PDP"],
)


async def checkpermission(user, action, resource):
    permitted = await pdp.check(
        user=user,
        action=action,
        resource=resource,
    )
    print(permitted)


async def sync():
    conn = sqlite3.connect("company.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    for user in users:
        user = dict(user)
        user["key"] = user["id"]
        print(user["key"], user["role"])
        del user["id"]
        synced_user: UserRead = await pdp.api.users.sync(
            {
                "key": user["key"],
                "first_name": user["name"],
                "email": user["email"],
                "attributes": {
                    "role": user["role"],
                    "created_at": user["created_at"],
                    "department": user["department"],
                    "job_title": user["job_title"],
                    "phone_number": user["phone_number"],
                    "region": user["region"],
                    "username": user["username"],
                    "is_active": user["is_active"],
                },
            }
        )
        ra = await pdp.api.users.assign_role(
            {"user": user["key"], "role": user["role"], "tenant": "default"}
        )


if __name__ == "__main__":
    # asyncio.run(sync())
    # asyncio.run(checkpermission("1", "read", "customers"))
    pass
