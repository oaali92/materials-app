"""
CLI tool that parses and loads Hall and ICP measurement data
"""

__author__ = "Omar"

import argparse
import logging
import os.path as osp
import json
from lab_loader.client import Client
from lab_loader.utils import parse_files, create_df, move_files


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
        logging.error(
            "Config file path could not be loaded. Please load a proper file path."
        )
        "return"

    client = Client(
        host=config_params["serverCredentials"]["host"],
        port=config_params["serverCredentials"]["port"],
        database=config_params["serverCredentials"]["database"],
        user=config_params["serverCredentials"]["user"],
        password=config_params["serverCredentials"]["password"],
    )
    folder_path = config_params["source"]["folderPath"]
    parsed_data = parse_files(folder_path)
    hall_df = create_df(parsed_data["hall_data"])
    icp_df = create_df(parsed_data["icp_data"])
    try:
        if len(hall_df) > 0:
            err = client.insert_data(hall_df, "hall_measurement", 'material_uid')
            if err is not None:
                logging.error(err)
        if len(icp_df) > 0:
            err = client.insert_data(icp_df, "icp_measurement", 'material_uid')

            if err is not None:
                logging.error(err)
        move_files(
            config_params["source"]["folderPath"],
            config_params["destination"]["folderPath"],
        )
    except Exception:
        logging.error("Error inserting data into SQL database.")


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--config", help="Required configuration file for data load"
    )

    args = parser.parse_args()
    main(args)
