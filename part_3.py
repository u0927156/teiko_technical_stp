# %%
# imports
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import pathlib
from scipy import stats

from part_2 import fetch_data_overview


# %%
# Fetch data
db_path = pathlib.Path("cell_count.db")
conn = sqlite3.connect(db_path)

df = fetch_data_overview(conn)

c = conn.cursor()
c.execute(
    "SELECT sample_id, sample_type, response, treatment FROM project_patient_sample_view"
)
patient_sample_data = c.fetchall()

patient_sample_df = pd.DataFrame(
    data=patient_sample_data, columns=["sample", "sample_type", "response", "treatment"]
)

miraclib_pbmc_df = patient_sample_df.query(
    "sample_type == 'PBMC' and treatment == 'miraclib'"
)

comparison_df = df.merge(miraclib_pbmc_df, how="inner", on="sample")

fig = go.Figure()
fig = px.box(comparison_df, x="population", y="percentage", color="response")

for pop in comparison_df["population"].unique():
    pop_df = comparison_df.query(f"population == '{pop}'")
    stats_results = stats.mannwhitneyu(
        pop_df.query("response == 'yes'")["percentage"],
        pop_df.query("response == 'no'")["percentage"],
    )

    # Bonferroni corrected p-value corrects for multiple comparisons
    bonferroni_p_value = stats_results.pvalue * comparison_df["population"].nunique()

    if bonferroni_p_value < 0.05:
        fig.add_annotation(
            x=pop,
            text=f"p={bonferroni_p_value:.3e}",
            showarrow=False,
            y=pop_df["percentage"].max() * 1.05,
        )


fig.update_layout(
    # yaxis=dict(
    #     title=dict(
    #         text='normalized moisture')
    # ),
    title="Relative Population of Responders vs Non-Responders by Cell Type"
)
fig.show()
# %%
