from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, VBar, HoverTool
from bokeh.palettes import Spectral6
from bokeh.transform import cumsum
import streamlit as st
import pandas as pd
import numpy as np
from math import pi

numerical_columns = [
       'milling_time', 'milling_speed', 'hot_press_temperature',
       'hot_press_pressure', 'hot_press_time', 'total_time',
       'pb_concentration', 'sn_concentration', 'o_concentration', 'total_impurity',
       'gasflowrate_x', 'plasmatemperature', 'detectortemperature',
       'fieldstrength_x', 'radiofrequency', 'sampleposition',
       'magnetreversal', 'proberesistance', 'gasflowrate_y', 'current',
       'fieldstrength_y'
       ]   


def data_load(client):
    """
        Takes in a sql client and loads all data required for the dashboard.
    """
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
    g_material_df = material_df.groupby('ball_milling_uid')['name'].apply(lambda x: ''.join(x))
    material_makeup = material_df.pivot_table(values = 'mass_fraction', index='ball_milling_uid', columns = 'material_name')
    material_makeup = pd.concat([g_material_df, material_makeup], axis=1)
    process_df['total_time'] = process_df['milling_time'] + process_df['hot_press_time']
    process_df = process_df.merge(g_material_df, left_on = 'bm_uid', right_index=True)
    output_material = pd.merge(process_df, icp_data, how = 'left', left_on='hp_material', right_on='material_uid').merge(hall_data, how='left', left_on='hp_material', right_on='material_uid')
    output_material['total_impurity'] = output_material['sn_concentration'] + output_material['o_concentration'] + output_material['pb_concentration']
    return (process_df, material_df, material_makeup, output_material, icp_data, hall_data)

def create_crossplot(df, x_axis='total_time', y_axis='total_impurity'):
    """
        Uses dataframe and two axes and creates a cross plot. 
    """
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
    """
        Takes a selected field and shows a distribution
    """
    
    unique_values = df[column].dropna().unique()
    if len(unique_values) < 3:
        bins = 1
    else: 
        bins = round(len(unique_values) / 1.5)

    hist_data = np.histogram(df[column].dropna(), bins=bins)
    return hist_data

def create_histogram_chart(hist, edge):
    fig = figure()
    fig.quad(top=hist, bottom=0, left=edge[:-1], right=edge[1:], fill_color='navy', line_color='white')
    return fig

def get_material_composition(name, df):
    filt = df.loc[df['name'] == name]
    filt = filt[['Cu', 'Se', 'Zn']]
    filt = filt.T
    filt.columns = ['value']
    filt['angle'] = filt['value']/filt['value'].sum() * 2*pi
    filt['color'] = Spectral6[:len(filt)]
    filt = filt.reset_index()
    return filt

def create_pi_chart(df):
    cds = ColumnDataSource(df)
    p = figure(plot_height=350, toolbar_location=None,
           tools="hover", tooltips="@index: @value{0.00}", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='index', source=cds)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    return p

def create_impurity_data(name, df):
    df = df.loc[df['name'] == name]
    df = df[['pb_concentration', 'sn_concentration', 'o_concentration']]
    df = df.T
    df = df.reset_index()
    df['index'] = df['index'].str.replace('_concentration', '').str.title()
    return df

def create_impurity_bars(df):
    df.columns = ['index', 'impurity']
    df['color'] = Spectral6[len(df):]
    cds = ColumnDataSource(df)
    fig = figure(x_range = df['index'].unique())
    fig.vbar(source=cds, x='index', top='impurity', width = 0.8, line_color='color', fill_color = 'color')
    return fig

def create_material_bars(df, field):
    df = df.sort_values(by=field, ascending=False)
    cds = ColumnDataSource(df)
    fig = figure(x_range = df['name'])
    fig.vbar(source=cds, x='name', top=field, width=0.3)
    hover = HoverTool(
        tooltips = [
            ('Name', '@name'),
            ('Material ID', '@hp_material'),
            (field, f'@{field}'),
        ]
    )
    fig.add_tools(hover)
    return fig