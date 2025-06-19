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
# No subjects are in multiple projects. But for futures sake I'm going to make seperate tables
