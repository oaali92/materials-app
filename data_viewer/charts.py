from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, VBar, HoverTool
import streamlit as st
import numpy as np

numerical_columns = [
       'milling_time', 'milling_speed', 'hot_press_temperature',
       'hot_press_pressure', 'hot_press_time', 'total_time',
       'pb_concentration', 'sn_concentration', 'o_concentration', 'total_impurity',
       'gasflowrate_x', 'plasmatemperature', 'detectortemperature',
       'fieldstrength_x', 'radiofrequency', 'sampleposition',
       'magnetreversal', 'proberesistance', 'gasflowrate_y', 'current',
       'fieldstrength_y'
       ]   

def create_crossplot(df, x_axis='total_time', y_axis='total_impurity'):
    cds = ColumnDataSource(df)
    p = figure(
        x_axis_label = x_axis,
        y_axis_label = y_axis
    )
    cat1 = p.circle(
        source = cds,
        x = x_axis,
        y = y_axis,
        size = 7
    )
    hover = HoverTool(
        tooltips = [
            ('Name', '@name'),
            ('Material ID', '@hp_material'),
            (x_axis, f'@{x_axis}'),
            (y_axis, f'@{y_axis}')
        ]
    )
    p.add_tools(hover)
    return p

def create_histogram(df, column):
    
    unique_values = df[column].dropna().unique()
    if len(unique_values) < 3:
        bins = 1
    else: 
        bins = round(len(unique_values) / 2)

    hist_data = np.histogram(df[column].dropna(), bins=bins)[0]
    return hist_data