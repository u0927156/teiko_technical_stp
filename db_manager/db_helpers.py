import sqlite3


def _execute_and_commit_sql(conn: sqlite3.Connection, sql_str: str, params):
    cursor = conn.cursor()
    cursor.execute(sql_str, params)
    conn.commit()


def _executemany_and_commit_sql(conn: sqlite3.Connection, sql_str: str, list_of_params):
    cursor = conn.cursor()
    cursor.executemany(sql_str, list_of_params)
    conn.commit()
