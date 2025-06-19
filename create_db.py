import pandas as pd
import sqlite3
import pathlib
import sys


def make_tables(conn: sqlite3.Connection):
    print("Creating Tables")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE projects(
            project_id text PRIMARY KEY
        )
        """
    )
    c.execute(
        """
        CREATE TABLE subjects(
            subject_id text PRIMARY KEY,
            condition text,
            age integer,
            sex text,
            treatment text,
            response text
        )   
        """
    )
    c.execute(
        """
        CREATE TABLE project_subject_relation(
            project_id text REFERENCES projects(project_id) ON DELETE CASCADE,
            subject_id text REFERENCES subject(subject_id) ON DELETE CASCADE
        )   
        """
    )
    c.execute(
        """
        CREATE TABLE samples(
            sample_id text PRIMARY KEY,
            sample_type text,
            time_from_treatment_start integer,
            b_cell integer,
            cd8_t_cell integer,
            cd4_t_cell integer,
            nk_cell integer,
            monocyte integer
        )   
        """
    )
    c.execute(
        """
        CREATE TABLE subject_sample_relation(
            subject_id text REFERENCES subject(subject_id) ON DELETE CASCADE,
            sample_id text REFERENCES samples(sample_id) ON DELETE CASCADE
        )   
        """
    )

    c.execute(
        """
        CREATE VIEW project_patient_sample_view AS 
        SELECT 
            p.project_id,
            s.subject_id,
            s.condition,
            s.age,
            s.sex,
            s.treatment,
            s.response,
            sa.sample_id,
            sa.sample_type,
            sa.time_from_treatment_start,
            sa.b_cell,
            sa.cd8_t_cell,
            sa.cd4_t_cell,
            sa.nk_cell,
            sa.monocyte
        FROM 
            projects p 
        INNER JOIN project_subject_relation psr ON p.project_id = psr.project_id
        INNER JOIN subjects s ON s.subject_id = psr.subject_id
        INNER JOIN subject_sample_relation ssr ON ssr.subject_id = s.subject_id
        INNER JOIN samples sa ON ssr.sample_id = sa.sample_id
        """
    )
    conn.commit()


def _execute_and_commit_sql(conn: sqlite3.Connection, sql_str: str, params):
    cursor = conn.cursor()
    cursor.execute(sql_str, params)
    conn.commit()


def _executemany_and_commit_sql(conn: sqlite3.Connection, sql_str: str, list_of_params):
    cursor = conn.cursor()
    cursor.executemany(sql_str, list_of_params)
    conn.commit()


def insert_project(conn: sqlite3.Connection, project_id: str):
    _execute_and_commit_sql(
        conn,
        "INSERT OR IGNORE INTO projects VALUES(:id)",
        {"id": project_id},
    )


def insert_values(conn: sqlite3.Connection, columns_to_filter: list, sql_str: str):
    vals_to_insert = df[columns_to_filter].drop_duplicates()

    data_to_insert = list(vals_to_insert.itertuples(index=False, name=None))
    print(f"Inserting {len(data_to_insert)} rows.")

    _executemany_and_commit_sql(conn, sql_str=sql_str, list_of_params=data_to_insert)


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


if __name__ == "__main__":

    if len(sys.argv) > 1:
        data_path = pathlib.Path(sys.argv[1])
    else:
        data_path = pathlib.Path("cell-count.csv")
    df = pd.read_csv(data_path)

    dest_path = pathlib.Path("cell_count.db")
    if dest_path.exists():
        are_you_sure = input("Database already exists, do you want to delete (Y/N)? ")

        if are_you_sure == "Y":
            dest_path.unlink()
            conn = sqlite3.connect(dest_path)
            make_tables(conn)
        else:
            conn = sqlite3.connect(dest_path)
            print(f"Attempting to update database with {data_path}.")

    else:
        conn = sqlite3.connect(dest_path)
        make_tables(conn)

    print("Inserting Projects")
    for proj in df["project"].unique():
        insert_project(conn, proj)

    print("Inserting Subjects")
    insert_values(
        conn,
        ["subject", "condition", "age", "sex", "treatment", "response"],
        """INSERT OR IGNORE INTO subjects 
            (subject_id,condition,age,sex,treatment,response)
        VALUES (?,?,?,?,?,?)
        """,
    )

    print("Inserting Project-Subject Relations")
    insert_values(
        conn,
        ["project", "subject"],
        "INSERT OR IGNORE INTO project_subject_relation (project_id, subject_id) VALUES (?, ?);",
    )

    print("Inserting Samples")
    insert_values(
        conn,
        [
            "sample",
            "sample_type",
            "time_from_treatment_start",
            "b_cell",
            "cd8_t_cell",
            "cd4_t_cell",
            "nk_cell",
            "monocyte",
        ],
        """
            INSERT OR IGNORE INTO samples (sample_id,sample_type,time_from_treatment_start,b_cell,
                cd8_t_cell,cd4_t_cell,nk_cell,monocyte
            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
    )

    print("Inserting Subject-Sample Relations")
    insert_values(
        conn,
        ["sample", "subject"],
        "INSERT OR IGNORE INTO subject_sample_relation (sample_id, subject_id) VALUES (?, ?);",
    )
