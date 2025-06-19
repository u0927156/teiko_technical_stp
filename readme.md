# Teiko Technical

Author: Spencer Peterson

## Installation / Running

### Environment
I've used poetry to manage packages for this project. See the [documentation](https://python-poetry.org/docs/) for details on how to setup poetry on your machine. 

Once poetry is installed, you can run `poetry install` to build an environment. 

### DB Setup
Once your enviroment is setup, you can run `poetry run python create_db.py` to set up a local sqlite 
database. If a database is already set up, the program will ask if you want to delete the existing database completely or append to it. 

If you want to add additional csv files of the same format to the database, you can run `poetry run python create_db.py your_file_here.csv`. This will add additional information to the existing database.

### Streamlit App
To run the program and visualize the results, use the command `poetry run python -m streamlit app.py`. This will create a local version of the web app this program makes that includes the data overview and statistical analysis. 

## Database Schema

The database is organized into three main tables, projects, subjects, and samples. There are two tables that contain the relations between projects and subjects and subjects and samples respectively. 

The idea behind this design is to follow table normalization rules to ensure as little information is repeated as possible. All subject level information is stored in the subjects table and all sample level information is stored in the samples table. This minimizes space requirements and scales well with this type of relational database.

Some additional improvements may include decoupling the cell counts from the sample. This would involve adding a single table the first could be cell_counts and would contain a foreign key referencing the sample its associated with, the cell_name column, and the count. This would allow greater flexibility if some samples include or exclude certain cell types. If felt the complexity this added to the analytics wasn't worth it for this example project, but there are situations where I'd advocate for this design to ensure future flexibility. After all, there's no thing more permanent than a temporary solution. 

## Code Structure

I've organized my code into two internal packages. The first is the `db_manager` package. This contains the code for creating the database and inserting and deleting data. The other package, `teiko_technical`, is where I've included the code that does the actual analysis requested by Bob Loblaw. 

Additionally, `app.py` is responsible for creating the streamlit app. 

This structure seperates code that doesn't interact with each other and allows me to simply import things into `app.py` to maximize its legibility. 

I've also included a folder of the files I used to explore the problem. They are in python files that function as notebooks using the `% ##` notation. I've included them to show a halfway done state and in case I need to revisit the analysis at a later date in a more freeform format. 

