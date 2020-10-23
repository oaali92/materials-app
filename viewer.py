"""
CLI app that views materials procurement, processing, and lab data
"""

__author__ = "Omar"
import streamlit as st
import json
import argparse
import os.path as osp
import logging
from lab_loader.client import Client
from data_viewer.charts import create_crossplot, numerical_columns, create_histogram, create_histogram_chart, data_load, get_material_composition, create_pi_chart, create_impurity_bars, create_impurity_data

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
    
    (process_df, material_df, material_makeup, output_material, icp_data, hall_data) = data_load(client)
    
    ## Streamlit
    st.title('Materials Viewer')

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

    material_selector = st.sidebar.selectbox(
        'Select Material by Composition', output_material['name']
    )

    hist_data, edges = create_histogram(output_material, histogram_selector)
    histogram = create_histogram_chart(hist_data, edges)
    st.write(histogram)
    st.title('Material Make-Up')
    material = get_material_composition(material_selector, material_makeup)
    pi = create_pi_chart(material)
    st.subheader('Material Composition')
    st.write(pi)
    
    new_df  = create_impurity_data(material_selector, output_material)
    st.subheader('Material Impurities')
    fig = create_impurity_bars(new_df)
    st.write(fig)
    if st.checkbox('Show raw data'):
        st.subheader('Processing Data')
        st.write(process_df)
        st.subheader('Lab Data')
        st.write(output_material)
        st.subheader('Material Makeup')
        st.write(material_makeup)
        st.subheader('Procurement Data')
        st.write(material_df)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--config", help="Required configuration file for viewer"
    )

    args = parser.parse_args()
    main(args)