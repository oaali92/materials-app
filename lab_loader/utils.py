"""
Utility functions to help parse Hall and ICP text files
"""
import os
from pathlib import Path
import re


def _get_file_list(folder_path):
    """
    Gets a list of all files in a directory

    Parameters
    ---------
        folder_path : str
            folder directory that holds the files. 
            note: this function converts the folder path to a PurePath object
    """    
   
    return os.listdir(Path(folder_path))


def _get_row(file_path):
    """
    Generates a "row" of data from the text file path

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
            key = ''.join(data[:-1])
            row[key] = data[-1]
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
        if row['Measurement'] == 'Hall':
            result['hall_data'].append(row)
        else:
            result['icp_data'].append(row)
    return result