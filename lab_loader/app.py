"""
CLI tool that parses and loads Hall and ICP measurement data
"""

__author__ = "Omar"

import argparse
import logging
import os.path as osp
import json
from client import Client
from utils import * 

def main(args):
    if args.config is None:
        logging.error("Please load a json config file.")
        return 

    if osp.splitext(args.config)[1] != ".json":
        logging.error("Please load a file with a json extension.")
        return
    try: 
        with open(args.config) as fp:
            config_params = json.load(fp)
    except Exception:
        logging.error("Config file path could not be loaded. Please load a proper file path.")
        "return"

    client = Client(
        host=config_params['serverCredentials']["host"],
        port=config_params['serverCredentials']["port"],
        database=config_params['serverCredentials']["database"],
        user=config_params['serverCredentials']["user"],
        password=config_params['serverCredentials']["password"]
    )
    folder_path = config_params['source']["folderPath"]
    file_list = get_file_list(folder_path)
    all_lines = []
    for f in file_list:
        lines = parse_file(folder_path + '\\' + f)
        all_lines.append(lines)
        print(lines)




if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", help="Required configuration file for data load")

    args = parser.parse_args()
    main(args)