import sqlite3


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
