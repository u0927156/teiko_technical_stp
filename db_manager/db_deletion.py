import sqlite3

import pandas as pd

from db_manager.db_helpers import _execute_and_commit_sql


def delete_sample(conn: sqlite3.Connection, sample_to_delete: str):
    _execute_and_commit_sql(
        conn=conn,
        sql_str="DELETE FROM samples where sample_id = ?",
        params=(sample_to_delete),
    )


def delete_subject(conn: sqlite3.Connection, subject_to_delete: str):
    _execute_and_commit_sql(
        conn=conn,
        sql_str="DELETE FROM samples where subject_id = ?",
        params=(subject_to_delete),
    )


def delete_project(conn: sqlite3.Connection, project_to_delete: str):
    _execute_and_commit_sql(
        conn=conn,
        sql_str="DELETE FROM samples where project_id = ?",
        params=(project_to_delete),
    )
