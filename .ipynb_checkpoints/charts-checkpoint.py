import duckdb
import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
import plotly.io as pio
import ipywidgets as widgets
from IPython.display import display, clear_output
from ipywidgets import interact, Dropdown, Output, VBox, HBox
from sklearn.preprocessing import MinMaxScaler
from dash import Dash, dcc, html, Output, Input
import fpl_api as fa
import datasets as da

def chart_points_by_gw(league_id):
    global gw
    gw = da.get_dataset(league_id)#.gw
    fig = px.line(gw.sort_values(['player_name', 'event']),
              x='event',
              y='net_points',
              color='player_name',
              title='Points by GW',
              category_orders={'player_name': ['Assyl Zhassyl', 'Bekzat Kuanyshbay',
       'Bekzat Sansyzbay', 'Dake Bratan', 'Kaisar Yessaly',
       'Kazybek Nurmanov', 'Makhsutov Ziedulla', 'Rakhat Beisenbek',
       'Rakhat Zhussupkhanov', 'Sanzhar Yendybayev', 'Zhanuzak Zholdybay', 'Average']},
              color_discrete_sequence=pc.qualitative.Light24)
    fig.for_each_trace(
        lambda trace: trace.update(
            line=dict(color='gray', dash='dash', width=3),
            name='Average'
        ) if trace.name == 'Average' else trace
    )
    fig.update_layout(
        xaxis_title='Gameweek',
        yaxis_title='Total Points',
        legend_title='Manager',
        template='plotly_dark'
    )
    return fig

def chart_average_by_gw(league_id):
    averages = fa.get_bootstrap().averages
    wo_average = gw[gw.player_name != 'Average']
    avgs = wo_average.pivot_table(values='net_points', index='event', aggfunc='mean').reset_index()
    avg_fin = duckdb.query('''
    select event, cast(net_points as int) average, 'Our Average' flag from avgs
    union
    select gameweek, average_points, 'Global Average' flag from averages
    ''').to_df()
    
    fig = px.line(avg_fin.sort_values(['event', 'average']),
                  x='event',
                  y='average',
                  color='flag',
                  title='Averages',
                  text = 'average',
                  color_discrete_sequence=pc.qualitative.Light24)
    
    fig.for_each_trace(
        lambda trace: trace.update(
            line=dict(color='gray', dash='dash', width=3),
            name='Global Average'
        ) if trace.name == 'Global Average' else trace
    )
    
    fig.update_traces(texttemplate='%{y}', textposition='top center', textfont=dict(size=12),)
    
    for trace in fig.data:
        if trace.name == 'Our Average':
            trace.textposition = 'bottom center'
        elif trace.name == 'Global Average':
            trace.textposition = 'top center'
    
    fig.update_layout(
        title='Average Points by GW',
        template='plotly_dark'
    )
    
    return fig