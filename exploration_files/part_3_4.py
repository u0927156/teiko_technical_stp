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
    "SELECT sample_id, sample_type, response, treatment, sex, project_id, time_from_treatment_start, subject_id FROM project_patient_sample_view"
)
patient_sample_data = c.fetchall()

patient_sample_df = pd.DataFrame(
    data=patient_sample_data,
    columns=[
        "sample",
        "sample_type",
        "response",
        "treatment",
        "sex",
        "project",
        "time_from_treatment_start",
        "subject",
    ],
)

miraclib_pbmc_df = patient_sample_df.query(
    "sample_type == 'PBMC' and treatment == 'miraclib'"
)

comparison_df = df.merge(miraclib_pbmc_df, how="inner", on="sample")


def make_comparison_figure(df, color="response"):
    fig = go.Figure()
    fig = px.box(df, x="population", y="percentage", color=color)

    for pop in df["population"].unique():
        pop_df = df.query(f"population == '{pop}'")
        stats_results = stats.mannwhitneyu(
            pop_df.query("response == 'yes'")["percentage"],
            pop_df.query("response == 'no'")["percentage"],
        )

        # Bonferroni corrected p-value corrects for multiple comparisons
        bonferroni_p_value = stats_results.pvalue * df["population"].nunique()

        if bonferroni_p_value < 0.05:
            fig.add_annotation(
                x=pop,
                text=f"p={bonferroni_p_value:.3e}",
                showarrow=False,
                y=pop_df["percentage"].max() * 1.05,
            )

    return fig


fig = make_comparison_figure(comparison_df)


fig.update_layout(
    # yaxis=dict(
    #     title=dict(
    #         text='normalized moisture')
    # ),
    title="Relative Population of Responders vs Non-Responders by Cell Type"
)
fig.show()
# %%
# Part 4 Look at subsets
baseline_samples_df = comparison_df.query("time_from_treatment_start == 0")

baseline_fig = make_comparison_figure(baseline_samples_df)
baseline_fig.update_layout(
    title="Relative Population of Responders vs Non-Responders by Cell Type at t=0"
)
baseline_fig.show()


# %%
samples_from_each_project_df = baseline_samples_df.groupby("project", as_index=False)[
    "sample"
].size()
num_responders_non_responders_df = baseline_samples_df.groupby(
    "response", as_index=False
)["subject"].size()
num_subjects_by_sex_df = baseline_samples_df.groupby("sex", as_index=False)[
    "subject"
].size()


# %%
