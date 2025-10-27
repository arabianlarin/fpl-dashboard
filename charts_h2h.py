import pandas as pd
import duckdb
import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import ipywidgets as widgets
from PIL import Image
from IPython.display import display, clear_output
from ipywidgets import interact, Dropdown, Output, VBox, HBox
from sklearn.preprocessing import MinMaxScaler
import fpl_api as fa
import h2h

def standings(league_id):
    dt = h2h.get_h2h_league_info(league_id)
    fig = go.Figure(
        data=[go.Table(
            #columnwidth=[80, 80, 20, 50],
            header=dict(
                values=['Manager', 'League Rank', 'Played', 'Won', 'Draw', 'Lost', 'Points'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[dt[col] for col in dt.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )

    fig.update_layout(
        title='H2H League Standings',
        template='plotly_dark'
    )
    
    return fig

def max_win_streak(league_id):
    global df_h2h
    df_h2h = h2h.get_complete_table(league_id)
    ccc = duckdb.query('''
    select manager, gw_points, opponent, opponent_points, gw, case when gw_points > opponent_points then 'win' when gw_points = opponent_points then 'draw' else 'loss' end result
    from df_h2h
    order by 1, 2
    ''').to_df()

    ccc = ccc.sort_values(by=['manager', 'gw'])

    def find_streaks(group):
        group = group.copy()
        group['streak_id'] = (group['result'] != group['result'].shift()).cumsum()
        group['rn'] = range(len(group))
        return group
    
    ccc = ccc.groupby('manager', group_keys=False).apply(find_streaks)
    
    streaks = ccc.groupby(['manager', 'result', 'streak_id']).agg(
        streak_length=('gw', 'count'),
        start_gw=('gw', 'min'),
        end_gw=('gw', 'max')
    ).reset_index()
    
    # Победы
    max_win = streaks[streaks['result'] == 'win'].sort_values(['manager', 'streak_length'], ascending=[True, False]) \
        .drop_duplicates('manager')
    
    # Поражения
    max_loss = streaks[streaks['result'] == 'loss'].sort_values(['manager', 'streak_length'], ascending=[True, False]) \
        .drop_duplicates('manager')

    global final
    final = pd.merge(
        max_win[['manager', 'streak_length', 'start_gw', 'end_gw']].rename(
            columns={
                'streak_length': 'max_win_streak',
                'start_gw': 'win_start_gw',
                'end_gw': 'win_end_gw'
            }),
        max_loss[['manager', 'streak_length', 'start_gw', 'end_gw']].rename(
            columns={
                'streak_length': 'max_loss_streak',
                'start_gw': 'loss_start_gw',
                'end_gw': 'loss_end_gw'
            }),
        on='manager',
        how='outer'
    )

    final = final[final.manager != 'AVERAGE']
    
    final_win = final.sort_values('max_win_streak', ascending=False)[['manager', 'max_win_streak', 'win_start_gw', 'win_end_gw']].head(10)

    fig = go.Figure(
        data=[go.Table(
            #columnwidth=[80, 80, 20, 50],
            header=dict(
                values=['Manager', 'Win Streak Length', 'Streak Start GW', 'Streak End GW'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[final_win[col] for col in final_win.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )

    fig.update_layout(
        title='Longest Win Streaks (Top 10)',
        template='plotly_dark'
    )
    
    return fig

def antiotsk(league_id):
    antiotsk = duckdb.query('''
    with ccc as (
    select *, gw_points - opponent_points points_diff
    from df_h2h
    where points_diff between 1 and 3
    order by points_diff
    )
    select opponent, count(*) from ccc
    where opponent != 'AVERAGE'
    group by 1
    order by 2 desc
    ''').to_df().head(10)

    fig = go.Figure(
        data=[go.Table(
            #columnwidth=[80, 80, 20, 50],
            header=dict(
                values=['Manager', 'Otskok Losses'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[antiotsk[col] for col in antiotsk.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )

    fig.update_layout(
        title='Antiotksokers (lost by 3 points or less) (Top 10)',
        template='plotly_dark'
    )

    return fig

def otskokers(league_id):
    #otskokers
    otsk = duckdb.query('''
    with ccc as (
    select *, gw_points - opponent_points points_diff
    from df_h2h
    where points_diff between 1 and 3
    order by points_diff
    )
    select manager, count(*) cnt from ccc
    group by 1
    order by 2 desc
    ''').to_df().head(10)
    
    fig = go.Figure(
        data=[go.Table(
            #columnwidth=[80, 80, 20, 50],
            header=dict(
                values=['Manager', 'Otskok Wins'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[otsk[col] for col in otsk.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )

    fig.update_layout(
        title='Otksokers (won by 3 points or less) (Top 10)',
        template='plotly_dark'
    )
    return fig

def max_loss_streak(league_id):
    final_loss = final.sort_values('max_loss_streak', ascending=False)[['manager', 'max_loss_streak', 'loss_start_gw', 'loss_end_gw']].head(10)

    fig = go.Figure(
        data=[go.Table(
            #columnwidth=[80, 80, 20, 50],
            header=dict(
                values=['Manager', 'Loss Streak Length', 'Streak Start GW', 'Streak End GW'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[final_loss[col] for col in final_loss.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )

    fig.update_layout(
        title='Longest Loss Streaks (Top 10)',
        template='plotly_dark'
    )
    
    return fig