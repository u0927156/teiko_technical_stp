import streamlit as st

from teiko_technical.data_overview import fetch_data_overview
from teiko_technical.statistical_analysis import (
    get_box_plot_and_df,
    get_subset_box_plot_and_additional_info_dfs,
)

conn = st.connection("cell_count_db", type="sql")

overview_df = fetch_data_overview(conn)

box_fig, comparison_df = get_box_plot_and_df(conn, overview_df)
(
    subset_box_fig,
    samples_from_each_project_df,
    num_responders_non_responders_df,
    num_subjects_by_sex_df,
) = get_subset_box_plot_and_additional_info_dfs(comparison_df)


st.markdown(
    """
# Cytometry Data Analysis for Loblaw Bio
The following app shows the analysis of cell-count data from recent Loblaw Bio clinical Trials.            
"""
)

st.markdown(
    """
            ## Overview Table
            The following table contains the proportion of each type of cell in each sample.
            """
)
st.dataframe(overview_df)

st.markdown(
    """
            ## Responder vs Non-repsonders
            The following chart shows the differences in cell population relative frequences of 
            those receiving miraclib by response status for PBMC samples only. Comparisons that are significantly significant 
            (p<0.05) are labeled with their p-value. Statistical significance was determined by using 
            a [KS-test](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test). P-values are 
            [Bonferroni corrected](https://en.wikipedia.org/wiki/Bonferroni_correction). 
            """
)
st.plotly_chart(box_fig)

st.markdown(
    """
            ## Subset Information
            The following chart and tables are a subset analysis of samples taken at 0 t from treatment
            """
)
st.plotly_chart(subset_box_fig)

st.markdown("### Number of Samples from each Project")
st.dataframe(samples_from_each_project_df)

st.markdown("### Number of Samples by Responder Status")
st.dataframe(num_responders_non_responders_df)

st.markdown("### Number of Samples by Subject Sex")
st.dataframe(num_subjects_by_sex_df)
