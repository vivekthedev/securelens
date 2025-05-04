import sqlite3
from typing import Union

import pandas as pd


def check_authentication(username, password):
    conn = sqlite3.connect("company.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, password)
    )
    user = cursor.fetchone()

    conn.close()

    if user:
        return dict(user)
    else:
        return False


def perform_sql_query(sql_query: str) -> Union[pd.DataFrame, str]:
    conn = sqlite3.connect("company.db")

    try:
        result = pd.read_sql_query(sql_query, conn)
    except sqlite3.Error as e:
        result = "THERE WAS AN ERROR"

    conn.close()

    return result
