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
from data_viewer.charts import create_crossplot, numerical_columns, create_histogram


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
    
    sql = """
        select 
            bm.uid as bm_uid, 
            bm.output_material_uid as bm_material, 
            hot_press.uid as hp_uid, 
            hot_press.output_material_uid as hp_material, 
            * 
        from ball_milling bm 
        left join hot_press on hot_press.uid = bm.hot_press_uid
        """
    process_df = client.get_data(table=None, query=sql)
    icp_data = client.get_data('icp_measurement')
    hall_data = client.get_data('hall_measurement')
    material_df = client.get_data('material_procurement')
    material_df['name'] = material_df['material_name'] + material_df['mass_fraction'].astype(str)
    material_df = material_df.groupby('ball_milling_uid')['name'].apply(lambda x: ''.join(x))
    process_df['total_time'] = process_df['milling_time'] + process_df['hot_press_time']
    process_df = process_df.merge(material_df, left_on = 'bm_uid', right_index=True)
    output_material = pd.merge(process_df, icp_data, how = 'left', left_on='hp_material', right_on='material_uid').merge(hall_data, how='left', left_on='hp_material', right_on='material_uid')
    output_material['total_impurity'] = output_material['sn_concentration'] + output_material['o_concentration'] + output_material['pb_concentration']

    ## Streamlit
    st.title('Material Viewer')
    # all_data
    
    st.subheader('Total Production Time')
    x_axis_option = st.sidebar.selectbox(
        'Select X-Axis', numerical_columns
    )
    y_axis_option = st.sidebar.selectbox(
        'Select Y-Axis', numerical_columns
    )
    
    cross_plot = create_crossplot(output_material, x_axis=x_axis_option, y_axis = y_axis_option)
    st.bokeh_chart(cross_plot)
    
    histogram_selector = st.sidebar.selectbox(
        'Select Histogram Field', numerical_columns
    )

    hist_data = create_histogram(output_material, histogram_selector)
    st.bar_chart(hist_data)
    if st.checkbox('Show raw data'):
        st.subheader('Processing Data')
        st.write(process_df)
        st.subheader('Lab Data')
        st.write(output_material)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--config", help="Required configuration file for viewer"
    )

    args = parser.parse_args()
    main(args)