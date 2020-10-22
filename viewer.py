"""
CLI app that views materials procurement, processing, and lab data
"""

__author__ = "Omar"
import streamlit as st
import json
import pandas as pd
import numpy as np
import argparse
import os.path as osp
import logging
from lab_loader.client import Client



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
    
    
    hall_df = client.get_data('hall_measurement')
    
    st.title('Materials App')


    def load_data():
        hall_df = client.get_data('hall_measurement')
        return hall_df

    data_load_state = st.text('Loading data...')
    data = load_data()

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)

    st.subheader('Probe Resistance Histogram')
    st.bar_chart(data.proberesistance)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--config", help="Required configuration file for viewer"
    )

    args = parser.parse_args()
    main(args)