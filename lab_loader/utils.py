#%%
"""
Utility functions to help parse Hall and ICP text files
"""
import os
from pathlib import Path
import re
import pandas as pd


def _get_file_list(folder_path):
    """
    Gets a list of all files in a directory

    Parameters
    ---------
        folder_path : str
            folder directory that holds the files. 
            note: this function converts the folder path to a PurePath object
    """    
    all_files = os.listdir(Path(folder_path))
    filtered_files = [file_name for file_name in all_files if file_name.startswith('ICP') or file_name.startswith('Hall')]
    return filtered_files
    # return os.listdir(Path(folder_path))


def _get_row(file_path):
    """
    Generates a "row" of data from the text file path
    Also 

    Parameters
    ---------
        file_path : PurePath
            file path to the text file being loaded
    """
    row = {}
    with open(file_path) as f:
        lines = f.readlines()
    result = [re.sub(' +', ' ', line.replace('\t', ' ').replace('\n', '')) for line in lines]
    for line in result:
        data = line.split(' ')
        if len(data) > 1:
            key = ''.join(data[:-1]).lower()
            row[key] = data[-1]
    new_keys = []
    new_units = []
    for key in list(row.keys()):
        if '(' in key:
            unit = key[key.find("(")+1:key.find(")")]
            new_key = key[:key.find("(")]
            row[new_key] = row.pop(key)
            new_keys.append(new_key)
            new_units.append(unit)
        if key == 'x-labsdata':
            row.pop(key)
    for k, v in zip(new_keys, new_units):
        row[f'{k}_unit'] = v
    return row


def parse_files(folder_path):
    """
    Parses all files in a folder and generates a dictionary of Hall and ICP measurements

    Parameters
    ---------
        folder_path : str
            folder directory that holds the files. 
            note: this function converts the folder path to a PurePath object
    """
    folder_path = Path(folder_path)
    files = _get_file_list(folder_path)
    result = {
        'hall_data': [],
        'icp_data': []
    }
    for file_name in files:
        file_path = folder_path / file_name
        row = _get_row(file_path)
        if row['measurement'] == 'Hall':
            result['hall_data'].append(row)
        else:
            result['icp_data'].append(row)
    return result

def create_df(data):
    """
    Creates a dataframe from a list of dictionaries

    Parameters
    ---------
        data : list
            placeholder for all icp and hall data
        """
    return pd.DataFrame(data)
   
def move_files(from_path, to_path):
    if not os.path.isdir(to_path):
        os.mkdir(to_path)
    parsed_files = _get_file_list(from_path)
    return [os.rename(Path(from_path) / file_name, Path(to_path) / file_name) for file_name in parsed_files]

        
# %%
# string1 = "C:\\Users\\OmarAli\\Documents\\repos\\materials-app\\data\\x-lab-data"
# res = parse_files(string1)
# create_df(res['hall_data'])
# %%
