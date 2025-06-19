# %%
# Imports
import pandas as pd
import sqlite3
import pathlib


# %%
# Load up db


# %%

db_path = pathlib.Path("cell_count.db")
conn = sqlite3.connect(db_path)


def fetch_data_overview(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute(
        """
                SELECT sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
                FROM project_patient_sample_view

            """
    )
    data = c.fetchall()

    df = pd.DataFrame(
        data=data,
        columns=["sample", "b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"],
    )

    df["total_count"] = (
        df["b_cell"]
        + df["cd8_t_cell"]
        + df["cd4_t_cell"]
        + df["nk_cell"]
        + df["monocyte"]
    )
    unpivoted_df = pd.melt(
        df,
        id_vars=["sample", "total_count"],
        value_vars=["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"],
    )
    unpivoted_df = unpivoted_df.rename(
        columns={"variable": "population", "value": "count"}
    )
    unpivoted_df["percentage"] = (
        unpivoted_df["count"] / unpivoted_df["total_count"]
    ) * 100

    return unpivoted_df


fetch_data_overview(conn=conn)

# %%
