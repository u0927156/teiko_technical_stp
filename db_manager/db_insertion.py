import sqlite3

import pandas as pd

from db_manager.db_helpers import _execute_and_commit_sql, _executemany_and_commit_sql


def insert_project(conn: sqlite3.Connection, project_id: str):
    _execute_and_commit_sql(
        conn,
        "INSERT OR IGNORE INTO projects VALUES(:id)",
        {"id": project_id},
    )


def insert_values(
    conn: sqlite3.Connection, df: pd.DataFrame, columns_to_filter: list, sql_str: str
):
    vals_to_insert = df[columns_to_filter].drop_duplicates()

    data_to_insert = list(vals_to_insert.itertuples(index=False, name=None))
    print(f"Inserting {len(data_to_insert)} rows.")

    _executemany_and_commit_sql(conn, sql_str=sql_str, list_of_params=data_to_insert)
