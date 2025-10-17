import duckdb
import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
import plotly.io as pio
import ipywidgets as widgets
from IPython.display import display, clear_output
from ipywidgets import interact, Dropdown, Output, VBox, HBox
from sklearn.preprocessing import MinMaxScaler
import fpl_api as fa
from datasets import get_dataset

def chart_points_by_gw(league_id):
    global gw
    gw = get_dataset(league_id).gw
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

def chart_standings_by_gw(league_id):
    wo_average = gw[gw.player_name != 'Average']
    fig = px.line(wo_average.sort_values(['player_name', 'event']),
                  x='event',
                  y='league_rank',
                  color='player_name',
                  title='League standings by GW',
          #         category_orders={'player_name': ['Assyl Zhassyl', 'Bekzat Kuanyshbay',
          #  'Bekzat Sansyzbay', 'Dake Bratan', 'Kaisar Yessaly',
          #  'Kazybek Nurmanov', 'Makhsutov Ziedulla', 'Rakhat Beisenbek',
          #  'Rakhat Zhussupkhanov', 'Sanzhar Yendybayev', 'Zhanuzak Zholdybay', 'Average']},
                  color_discrete_sequence=pc.qualitative.Light24)
    fig.update_yaxes(autorange='reversed')
    fig.update_layout(
        xaxis_title='Gameweek',
        yaxis_title='League Rank',
        legend_title='Manager',
        template='plotly_dark'
    )
    return fig

def table_highest_scores(league_id):
    highest_scores = get_dataset(league_id).highest_scores
    fig = go.Figure(
        data=[go.Table(
                columnwidth=[10, 80, 50, 20, 50],
                header=dict(
                    values=['GW', 'Name', 'Team Name', 'Points', 'Chip Used'],
                    fill_color='lightgray',
                    align='center',
                    font=dict(color='black', size=12)
                ),
                cells=dict(
                    values=[highest_scores[col] for col in highest_scores.columns],
                    fill_color='white',
                    align='center',
                    font=dict(color='black', size=11)
                )
            )]
        )
        
    fig.update_layout(
        title='Highest Points Each GW',
        template='plotly_dark',
        width = 800,
        height = 350
    )
    
    return fig

def table_lowest_scores(league_id):
    lowest_scores = get_dataset(league_id).lowest_scores
    fig = go.Figure(
        data=[go.Table(
            columnwidth=[10, 20, 15, 10, 15],
            header=dict(
                values=['GW', 'Name', 'Team Name', 'Points', 'Chip Used'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[lowest_scores[col] for col in lowest_scores.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )
    
    fig.update_layout(
        title='Lowest Points Each GW',
        template='plotly_dark',
        width = 800,
        height = 350
    )
    
    return fig

def table_standings(league_id):
    standings = get_dataset(league_id).standings
    standings = standings[['event', 'player_name', 'team_name', 'net_points', 'total_points', 'league_rank_dyn', 'prev_league_rank', 'overall_rank', 'chip']]
    fig = go.Figure(
        data=[go.Table(
            columnwidth=[10, 80, 50, 20, 50, 50, 50, 50, 50],
            header=dict(
                values=['GW', 'Name', 'Team Name', 'Points', 'Total Points', 'League Rank', 'Previous League Rank', 'Overall Rank', 'Chip Used'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[standings[col] for col in standings.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )
    
    fig.update_layout(
        title=f'League Standings GW{standings.event.max()}',
        template='plotly_dark',
    )
    
    return fig