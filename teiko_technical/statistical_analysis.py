from typing import Tuple

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import pathlib
from scipy import stats
from streamlit.connections import SQLConnection


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


def get_box_plot_and_df(
    conn: SQLConnection, data_overview_df: pd.DataFrame
) -> Tuple[go.Figure, pd.DataFrame]:

    patient_sample_df = conn.query(
        """
        SELECT 
            sample_id as sample,
            sample_type,
            response,
            treatment,
            sex,
            project_id as project,
            time_from_treatment_start,
            subject_id as subject
        FROM project_patient_sample_view
        """
    )

    miraclib_pbmc_df = patient_sample_df.query(
        "sample_type == 'PBMC' and treatment == 'miraclib'"
    )

    comparison_df = data_overview_df.merge(miraclib_pbmc_df, how="inner", on="sample")

    fig = make_comparison_figure(comparison_df)
    fig.update_layout(
        title="Relative Population of Responders vs Non-Responders by Cell Type"
    )

    return fig, comparison_df


def get_subset_box_plot_and_additional_info_dfs(
    comparison_df, t=0
) -> Tuple[go.Figure, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    samples_df = comparison_df.query(f"time_from_treatment_start == {t}")

    fig = make_comparison_figure(samples_df)
    fig.update_layout(
        title=f"Relative Population of Responders vs Non-Responders by Cell Type at t={t}"
    )

    samples_from_each_project_df = samples_df.groupby("project", as_index=False)[
        "sample"
    ].size()
    num_responders_non_responders_df = samples_df.groupby("response", as_index=False)[
        "subject"
    ].size()
    num_subjects_by_sex_df = samples_df.groupby("sex", as_index=False)["subject"].size()

    return (
        fig,
        samples_from_each_project_df,
        num_responders_non_responders_df,
        num_subjects_by_sex_df,
    )
