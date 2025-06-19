# %%
# Imports
import pandas as pd

# %%
# Load data + take a look
df = pd.read_csv("cell-count.csv")
df.head()

# %%
print(len(df))
print(df.project.nunique())
print(df.subject.nunique())
print(df["sample"].nunique())

# %%
# Check if any subjects are present across projects
num_unique_projects = df.groupby("subject")["project"].nunique()
num_unique_projects[num_unique_projects > 1]
# No subjects are in multiple projects. But for futures sake I'm going to make seperate tables and a relation
# table to join them on.

# %%
# Start db experimentation
import sqlite3

conn = sqlite3.connect(":memory:")

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
          project_id text REFERENCES projects(project_id),
          subject_id text REFERENCES subject(subject_id)
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
          subject_id text REFERENCES subject(subject_id),
          sample_id text REFERENCES samples(sample_id)
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
    JOIN project_subject_relation psr ON p.project_id = psr.project_id
    JOIN subjects s ON s.subject_id = psr.subject_id
    JOIN subject_sample_relation ssr ON s.subject_id = s.subject_id
    JOIN samples sa ON ssr.sample_id = sa.sample_id
    """
)
conn.commit()


def _execute_and_commit_sql(conn: sqlite3.Connection, sql_str: str, params):
    cursor = conn.cursor()
    cursor.execute(sql_str, params)
    conn.commit()


def insert_project(conn: sqlite3.Connection, project_id: str):
    _execute_and_commit_sql(
        conn, "INSERT INTO projects VALUES(:id)", {"id": project_id}
    )


def insert_subject(conn: sqlite3.Connection, subject_info):
    _execute_and_commit_sql(
        conn,
        """INSERT INTO subjects 
        (subject_id,
        condition,
        age,
        sex,
        treatment,
        response
        )
        VALUES (
            :subject_id,
            :condition,
            :age,
            :sex,
            :treatment,
            :response
        )
        """,
        {
            "subject_id": subject_info["subject"],
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "treatment": subject_info["treatment"],
            "response": subject_info["response"],
            "condition": subject_info["condition"],
        },
    )


def insert_subject_project_relation(conn: sqlite3.Connection, relation):
    _execute_and_commit_sql(
        conn,
        "INSERT INTO project_subject_relation (project_id, subject_id) VALUES (:project_id, :subject_id);",
        {"project_id": relation["project"], "subject_id": relation["subject"]},
    )


def insert_sample(conn: sqlite3.Connection, sample_info):
    _execute_and_commit_sql(
        conn,
        """
        INSERT INTO samples (
            sample_id,
            sample_type,
            time_from_treatment_start,
            b_cell,
            cd8_t_cell,
            cd4_t_cell,
            nk_cell,
            monocyte
        )
        VALUES(
            :sample_id,
            :sample_type,
            :time_from_treatment_start,
            :b_cell,
            :cd8_t_cell,
            :cd4_t_cell,
            :nk_cell,
            :monocyte
        )
        """,
        {
            "sample_id": sample_info["sample"],
            "sample_type": sample_info["sample_type"],
            "time_from_treatment_start": sample_info["time_from_treatment_start"],
            "b_cell": sample_info["b_cell"],
            "cd8_t_cell": sample_info["cd8_t_cell"],
            "cd4_t_cell": sample_info["cd4_t_cell"],
            "nk_cell": sample_info["nk_cell"],
            "monocyte": sample_info["monocyte"],
        },
    )


def insert_subject_sample_relation(conn: sqlite3.Connection, relation):
    _execute_and_commit_sql(
        conn,
        "INSERT INTO subject_sample_relation (sample_id, subject_id) VALUES (:sample_id, :subject_id);",
        {"sample_id": relation["sample"], "subject_id": relation["subject"]},
    )


for proj in df["project"].unique():
    insert_project(conn, proj)


def insert_values(
    conn: sqlite3.Connection, insertion_func: callable, columns_to_filter: list
):
    for i, row in df[columns_to_filter].drop_duplicates().iterrows():
        insertion_func(conn, row)


insert_values(
    conn,
    insert_subject,
    ["subject", "condition", "age", "sex", "treatment", "response"],
)
insert_values(
    conn,
    insert_subject_project_relation,
    ["project", "subject"],
)

insert_values(
    conn,
    insert_sample,
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
)
insert_values(
    conn,
    insert_subject_sample_relation,
    ["subject", "sample"],
)

# for i, row in df[["subject", "condition", "age", "sex", "treatment", "response"]].drop_duplicates().iterrows():
#     insert_subject(conn, subject_info=row)

# for i, row in (
#     df[["subject", "condition", "age", "sex", "treatment", "response"]]
#     .drop_duplicates()
#     .iterrows()
# ):
#     insert_subject(conn, subject_info=row)


c.execute("SELECT * FROM project_patient_sample_view")

c.fetchall()
