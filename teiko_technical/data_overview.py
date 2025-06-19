import pandas as pd
import sqlite3
from streamlit.connections import SQLConnection


def fetch_data_overview(conn: SQLConnection):

    df = conn.query(
        """
            SELECT sample_id as sample, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
            FROM project_patient_sample_view
        """
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
