from typing import Tuple

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import pathlib
from scipy import stats
from streamlit.connections import SQLConnection


def make_comparison_figure(df, color="response") -> go.Figure:
    """Make a comparison box plot of cell type percentage.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the data used to build the figure.
    color : str, optional
        What to divide up by color, by default "response"

    Returns
    -------
    go.Figure
        A box plot figure. Significant differences as measured by a Bonferroni-corrected KS test
        are included in the plot.
    """
    fig = go.Figure()
    fig = px.box(df, x="population", y="percentage", color=color)

    # Report significant differences in the plot
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
    """Get the miraclib treatment box plot.

    Parameters
    ----------
    conn : SQLConnection
        A connection to the database.
    data_overview_df : pd.DataFrame
        The data overview.

    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        The figure and the data results.
    """

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
        title="Relative Population of Responders vs Non-Responders by Cell Type for PBMC Miraclib Samples"
    )

    return fig, comparison_df


def get_subset_box_plot_and_additional_info_dfs(
    comparison_df: pd.DataFrame, t=0
) -> Tuple[go.Figure, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get a box plot figure for the subset of dataframes at t=0 and
    additional information about the project, sex, and responder status for the subset.

    Parameters
    ----------
    comparison_df : pd.DataFrame
        The comparison dataframe.
    t : int, optional
        The time to examine, by default 0

    Returns
    -------
    Tuple[go.Figure, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        The figure, samples from each project, the responders, and the subject sex count
        data frames.
    """
    samples_df = comparison_df.query(f"time_from_treatment_start == {t}")

    fig = make_comparison_figure(samples_df)
    fig.update_layout(
        title=f"Relative Population of Responders vs Non-Responders by Cell Type for PBMC Miraclib Samples at t={t}"
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
