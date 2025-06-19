import pandas as pd
import sqlite3
import pathlib
import sys

from db_manager.db_initiation import make_tables
from db_manager.db_insertion import insert_project, insert_values

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
        df,
        ["subject", "condition", "age", "sex", "treatment", "response"],
        """INSERT OR IGNORE INTO subjects 
            (subject_id,condition,age,sex,treatment,response)
        VALUES (?,?,?,?,?,?)
        """,
    )

    print("Inserting Project-Subject Relations")
    insert_values(
        conn,
        df,
        ["project", "subject"],
        "INSERT OR IGNORE INTO project_subject_relation (project_id, subject_id) VALUES (?, ?);",
    )

    print("Inserting Samples")
    insert_values(
        conn,
        df,
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
        df,
        ["sample", "subject"],
        "INSERT OR IGNORE INTO subject_sample_relation (sample_id, subject_id) VALUES (?, ?);",
    )
