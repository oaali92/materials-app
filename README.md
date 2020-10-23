# Materials Company Loader

This is an application that has been developed to load datafiles into a postgresql data model and add a visualization layer to that data model. This is an all encompasing solution that sits on top of Postgres with a python CLI loader and a streamlit dataviewer. 

## Installation
---------------
To install the packages necessary in order to run the loader and viewer, please set up a virtual environment through `pip` or `conda`, depending on your preference.

You may install the necessary packages using the [pip requirements](/requirements.txt) file or the [conda requirements](requirements.yml) file. 

### Option 1 (pip) 
[Code reference](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
```
pip install -r requirements.txt
```

### Option 2 (conda)
[Code reference](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) 
```
conda env create -f requirements.yml
```

## Part 1: Loader
---------------
The loader is used to parse lab generated text files and load them into the SQL database based on your config file. A [config file template](/lab_loader/config_template.json) sits inside of the lab_loader folder.
The template carries the following parameters and definitions:

```  
{
    "source": {
        "folderPath": "<path_to_directory_with_files>"
    }, 
    "destination": {
        "folderPath": "<path_for_where_files_should_be_archived>"
    },
    "serverCredentials": {
        "host": "<server_ip>",
        "port": "<server_port>",
        "database": "<sql_database_name>",
        "user": "<postgres_user_name>",
        "password": "<postgres_password>"
    }
}
```

Once this is all configured properly, the next step would be to run the loader. 

You can run the loader from the command line using the following command:
```
python <path_to_app.py> -c <path_to_config.json>
```
An example command running from same directory as the app would look like this:

`python app.py -c config.json`

## Step 2: Viewer
---------------
The viewer is configured using `streamlit`, which was used just to setup an easy scripting methodology for dashboarding. The viewer utilizes both `streamlit` and `bokeh` plots. To run the streamlit CLI tool, the command is simple:
```
streamlit run <path_to_viewer.py> -- -c <path_to_config.json>
```
The `config.json` file is the same one used for the loader, as the server configuration is exactly the same.

The `--`  separates streamlit arguments from CLI arguments and is necessary in order to pass in the `-c config.json`.

An example command run from the same directory as the viewer would look like this:
`streamlit run viewer.py -- -c config.json`