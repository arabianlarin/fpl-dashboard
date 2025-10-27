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
from datasets import get_dataset, get_player_data

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
    select event, cast(net_points as int) average, 'League Average' flag from avgs
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
        if trace.name == 'League Average':
            trace.textposition = 'bottom center'
        elif trace.name == 'Global Average':
            trace.textposition = 'top center'
    
    fig.update_layout(
        title='Average Points by GW',
        template='plotly_dark',
        yaxis_title=None,
        xaxis_title=None,
        legend=dict(
        title=None,
        orientation='h',
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5)
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
    highest_scores = get_dataset(league_id).highest_scores[['event', 'player_name', 'net_points', 'chip']]
    fig = go.Figure(
        data=[go.Table(
                columnwidth=[10, 80, 20, 50],
                header=dict(
                    values=['GW', 'Name', 'Points', 'Chip Used'],
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

    ht = len(highest_scores)*25 + 53
        
    fig.update_layout(
        title='🔝 Highest Points Each GW',
        template='plotly_dark',
        height=ht,
        margin=dict(r=0, l=0, t=25, b=0)
    )
    
    return fig

def table_lowest_scores(league_id):
    lowest_scores = get_dataset(league_id).lowest_scores[['event', 'player_name', 'net_points', 'chip']]
    fig = go.Figure(
        data=[go.Table(
            columnwidth=[10, 80, 20, 50],
            header=dict(
                values=['GW', 'Name', 'Points', 'Chip Used'],
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

    ht = len(lowest_scores)*25 + 53
    
    fig.update_layout(
        title='👎🏻 Lowest Points Each GW',
        template='plotly_dark',
        height=ht,
        margin=dict(r=0, l=0, t=25, b=0)
    )
    
    return fig

def table_standings(league_id, gw):
    global standings
    standings = get_dataset(league_id).standings
    standings_temp = standings[standings.event==gw][['event', 'player_name', 'net_points', 'total_points', 'league_rank_dyn', 'prev_league_rank', 'overall_rank', 'chip']].sort_values('overall_rank')#.head(11)
    standings_temp['overall_rank'] = standings_temp['overall_rank'].apply(lambda x: f"{x:,}".replace(',', ' '))
    fig = go.Figure(
        data=[go.Table(
            columnwidth=[10, 80, 20, 50, 50, 50, 50, 50],
            header=dict(
                values=['GW', 'Name', 'Points', 'Total Points', 'League Rank', 'Previous League Rank', 'Overall Rank', 'Chip Used'],
                fill_color='lightgray',
                align='center',
                font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[standings_temp[col] for col in standings_temp.columns],
                fill_color='white',
                align='center',
                font=dict(color='black', size=11)
            )
        )]
    )
    
    fig.update_layout(
        title=f'⚽️ League Standings GW{standings_temp.event.max()}',
        template='plotly_dark',
    )
    
    return fig

def table_gw_bench_points(league_id):
    global bench
    bench = get_dataset(league_id).bench
    bench_gw = bench.head(10)
    fig = go.Figure(data=[
        go.Table(columnwidth=[10, 40, 20],
                             header=dict(values=['GW', 'Name', 'Bench Points'],
                             fill_color='lightgray',
                             align='center',
                             font=dict(color='black', size=12)),
                 cells=dict(values=[bench_gw[col] for col in bench_gw.columns],
                            fill_color='white',
                            align='center',
                            font=dict(color='black', size=11)))
    ])

    fig.update_layout(title=f'🪑 Most Bench Points', template='plotly_dark', margin=dict(r=0, l=0, t=25, b=0), height=290)
    return fig

def table_total_bench_points(league_id):
    bench_total = duckdb.query('select player_name, sum(points_on_bench), round(avg(points_on_bench), 2) from bench group by 1 order by 2 desc').to_df().head(10)
    fig = go.Figure(data=[
        go.Table(columnwidth=[30, 25, 25],
                             header=dict(values=['Name', 'Total Bench Points', 'Avg Bench Points per GW'],
                             fill_color='lightgray',
                             align='center',
                             font=dict(color='black', size=12)),
                 cells=dict(values=[bench_total[col] for col in bench_total.columns],
                            fill_color='white',
                            align='center',
                            font=dict(color='black', size=11)))
    ])

    fig.update_layout(title=f'🪑 Most Bench Points Total', template='plotly_dark', margin=dict(r=0, l=0, t=25, b=0), height=290)
    return fig

def table_h2h(league_id, man1, man2):
    if man1 == '' or man2 == '':
        return ''
    if man1 == man2:
        return 'Please choose a non-duplicate manager'
    else:
        global h2h
        h2h = get_dataset(league_id).h2h
        h2h_temp = h2h[(h2h.man1 == man1) & (h2h.man2 == man2)]
        max_gw = gw.event.max()
        h2h_temp = duckdb.query(f'''
        select
        'GWs won' flag,
        count(case when points1 > points2 then man1 end) man1,
        count(case when points2 > points1 then man2 end) man2
        from h2h_temp
        union all
        select
        'Points' flag,
        sum(points1) man1,
        sum(points2) man2
        from h2h_temp
        union all
        select
        'Avg Points' flag,
        avg(points1) man1,
        avg(points2) man2
        from h2h_temp
        union all
        select
        'Overall rank' flag,
        or1 man1, or2 man2
        from h2h_temp
        where gw = {max_gw}
        union all
        select
        'Highest GW' flag,
        max(points1) man1,
        max(points2) man2
        from h2h_temp
        union all
        select
        'Lowest GW' flag,
        min(points1) man1,
        min(points2) man2
        from h2h_temp
        '''
        ).to_df()
    
        h2h_temp['man1'] = h2h_temp['man1'].apply(lambda x: f"{int(x):,}".replace(',', ' '))
        h2h_temp['man2'] = h2h_temp['man2'].apply(lambda x: f"{int(x):,}".replace(',', ' '))
    
        #labels = pd.DataFrame({'Metric': ['GWs won', 'Total points', 'Overall rank']})
    
        #h2h = pd.concat([h2h_gw, total_points, overall_rank], axis=0)
        #h2h[f'man1'] = h2h[f'man1'].apply(lambda x: f"{x:,}".replace(',', ' '))
        #h2h[f'man2'] = h2h[f'man2'].apply(lambda x: f"{x:,}".replace(',', ' '))
    
        #h2h = pd.concat([h2h, labels], axis=1)
        
        fig = go.Figure(data=[
            go.Table(columnwidth=[2, 3, 3],
                                 header=dict(values=['Metric', man1, man2],
                                 fill_color='lightgray',
                                 align='center',
                                 font=dict(color='black', size=12)),
                     cells=dict(values=[h2h_temp[col] for col in h2h_temp.columns],
                                fill_color='white',
                                align='center',
                                font=dict(color='black', size=11)))
        ])
        return h2h_temp.rename(columns={'flag': 'Metric', 'man1': man1, 'man2': man2}).style.set_table_styles([
    {'selector': 'th', 'props': [('text-align', 'center')]},  # headers
    {'selector': 'td', 'props': [('text-align', 'center')]}   # cells
])

def chart_h2h(league_id, man1, man2):
    h2h_temp = standings[standings.player_name.isin([man1, man2])]
    fig = px.line(h2h_temp.sort_values(['event'])[['event', 'player_name', 'net_points']],
              x='event',
              y='net_points',
              color='player_name',
              title='Points by GW',
              category_orders={'player_name': [man1, man2]},
              color_discrete_sequence=pc.qualitative.Light24)
    fig.update_layout(
        xaxis_title='Gameweek',
        yaxis_title='Total Points',
        legend_title='Manager',
        template='plotly_dark'
    )
    return fig

def chart_player_comparison_att(player1, player2):
    global data
    data = get_player_data()
    metrics = ["Sh_per_90_Standard", 'SoT_per_90_Standard', 'G+A_Per', "xG_Expected", "xA_Expected", 'KP', 'creativity', 'threat']
    scaler = MinMaxScaler()
    df_scaled = data.copy()
    df_scaled[metrics] = scaler.fit_transform(data[metrics])
    p1 = df_scaled[df_scaled["Player"] == player1][metrics].values.flatten()
    p2 = df_scaled[df_scaled["Player"] == player2][metrics].values.flatten()

    ph1 = data.loc[data["Player"] == player1.strip(), "photo"].values[0]
    ph2 = data.loc[data["Player"] == player2.strip(), "photo"].values[0]
    
    metrics_closed = metrics + [metrics[0]]
    p1 = list(p1) + [p1[0]]
    p2 = list(p2) + [p2[0]]

    fig = make_subplots(
        rows=1, cols=3,
        column_widths=[0.25, 0.5, 0.25],
        specs=[[{"type": "xy"}, {"type": "polar"}, {"type": "xy"}]],
    )

    fig.add_layout_image(
        dict(
            source=Image.open(f"photos/{ph1}"),
            xref="paper", yref="paper",
            x=0.13, y=0.6,
            sizex=0.72, sizey=0.85,
            xanchor="center", yanchor="middle",
            layer="below"
        )
    )

    fig.add_layout_image(
        dict(
            source=Image.open(f"photos/{ph2}"),
            xref="paper", yref="paper",
            x=0.87, y=0.6,
            sizex=0.72, sizey=0.85,
            xanchor="center", yanchor="middle",
            layer="below"
        )
    )
    
    # --- Plotly radar chart ---
    # fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=p1,
        theta=['Shots/90', 'Shots on Target/90', 'G+A/90', 'xG/90', 'xA/90', 'Key Passes/90', 'Creativity', 'Threat'],
        fill='toself',
        name=player1,
        line=dict(color='#D62E0F', width=4),
        fillcolor='#DB5B42',
        opacity=0.5
    ), row=1, col=2)
    fig.add_trace(go.Scatterpolar(
        r=p2,
        theta=['Shots/90', 'Shots on Target/90', 'G+A/90', 'xG/90', 'xA/90', 'Key Passes/90', 'Creativity', 'Threat'],
        fill='toself',
        name=player2,
        line=dict(color='#120FD6', width=4),
        fillcolor='#4F4ED9',
        opacity=0.5
    ), row=1, col=2)
    
    fig.update_layout(
        polar=dict(radialaxis=dict(
            visible=True,
            range=[0, 1],
            color="black",          # ← makes the tick labels black
            tickfont=dict(color="rgba(0,0,0,0)")  # ← ensures tick text is black
        )),
        showlegend=True,
        legend=dict(
             orientation="h",      # horizontal layout
            x=0.5,                # center horizontally
            y=1.15,               # position above the chart
            xanchor="center",     # anchor at center
            yanchor="bottom",     # anchor at bottom of legend box
            bgcolor="rgba(0,0,0,0)"  # transparent background (optional) 
        ),
        #title=dict(text=f"{player1} vs {player2}", x=0.5, xanchor='center', font=dict(size=24)),
        width=500,  # 👈 increase size
        height=500, # 👈 increase size
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig

def chart_player_comparison_def(player1, player2):
    #global data
    #data = get_player_data()
    metrics = ["TklW_Tackles", 'Blocks_Blocks', 'Int', "Clr", "defensive_contribution_per_90", 'CBIT/90', 'CS_percent', 'Err', 'expected_goals_conceded_per_90']
    scaler = MinMaxScaler()
    df_scaled = data.copy()
    df_scaled[metrics] = scaler.fit_transform(data[metrics])
    p1 = df_scaled[df_scaled["Player"] == player1][metrics].values.flatten()
    p2 = df_scaled[df_scaled["Player"] == player2][metrics].values.flatten()

    ph1 = data.loc[data["Player"] == player1, "photo"].values[0]
    ph2 = data.loc[data["Player"] == player2, "photo"].values[0]
    
    metrics_closed = metrics + [metrics[0]]
    p1 = list(p1) + [p1[0]]
    p2 = list(p2) + [p2[0]]

    fig = make_subplots(
        rows=1, cols=3,
        column_widths=[0.25, 0.5, 0.25],
        specs=[[{"type": "xy"}, {"type": "polar"}, {"type": "xy"}]],
    )

    fig.add_layout_image(
        dict(
            source=Image.open(f"photos/{ph1}"),
            xref="paper", yref="paper",
            x=0.13, y=0.6,
            sizex=0.72, sizey=0.85,
            xanchor="center", yanchor="middle",
            layer="below"
        )
    )

    fig.add_layout_image(
        dict(
            source=Image.open(f"photos/{ph2}"),
            xref="paper", yref="paper",
            x=0.87, y=0.6,
            sizex=0.72, sizey=0.85,
            xanchor="center", yanchor="middle",
            layer="below"
        )
    )
    
    # --- Plotly radar chart ---
    # fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=p1,
        theta=['Tackles Won/90', 'Blocks/90', 'Interceptions/90', 'Clearances/90', 'DefCon/90', 'CBIT/90', 'Clean Sheets %', 'Errors Lead to Shot/90', 'xGC'],
        fill='toself',
        name=player1,
        line=dict(color='#D62E0F', width=4),
        fillcolor='#DB5B42',
        opacity=0.5
    ), row=1, col=2)
    fig.add_trace(go.Scatterpolar(
        r=p2,
        theta=['Tackles won/90', 'Blocks/90', 'Interceptions/90', 'Clearances/90', 'DefCon/90', 'CBIT/90', 'Clean Sheets %', 'Errors lead to goal/90', 'xGC'],
        fill='toself',
        name=player2,
        line=dict(color='#120FD6', width=4),
        fillcolor='#4F4ED9',
        opacity=0.5
    ), row=1, col=2)
    
    fig.update_layout(
        polar=dict(radialaxis=dict(
            visible=True,
            range=[0, 1],
            color="black",          # ← makes the tick labels black
            tickfont=dict(color="rgba(0,0,0,0)")  # ← ensures tick text is black
        )),
        showlegend=True,
        legend=dict(
             orientation="h",      # horizontal layout
            x=0.5,                # center horizontally
            y=1.15,               # position above the chart
            xanchor="center",     # anchor at center
            yanchor="bottom",     # anchor at bottom of legend box
            bgcolor="rgba(0,0,0,0)"  # transparent background (optional) 
        ),
        #title=dict(text=f"{player1} vs {player2}", x=0.5, xanchor='center', font=dict(size=24)),
        width=500,  # 👈 increase size
        height=500, # 👈 increase size
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig

def chart_player_comparison_gk(player1, player2):
    #global data
    #data = get_player_data()
    metrics = ["Save_percent", 'CS_percent', 'Save_percent_Penalty', "Err", 'expected_goals_conceded_per_90']
    scaler = MinMaxScaler()
    df_scaled = data.copy()
    df_scaled[metrics] = scaler.fit_transform(data[metrics])
    p1 = df_scaled[df_scaled["Player"] == player1][metrics].values.flatten()
    p2 = df_scaled[df_scaled["Player"] == player2][metrics].values.flatten()

    ph1 = data.loc[data["Player"] == player1, "photo"].values[0]
    ph2 = data.loc[data["Player"] == player2, "photo"].values[0]
    
    metrics_closed = metrics + [metrics[0]]
    p1 = list(p1) + [p1[0]]
    p2 = list(p2) + [p2[0]]

    fig = make_subplots(
        rows=1, cols=3,
        column_widths=[0.25, 0.5, 0.25],
        specs=[[{"type": "xy"}, {"type": "polar"}, {"type": "xy"}]],
    )

    fig.add_layout_image(
        dict(
            source=Image.open(f"photos/{ph1}"),
            xref="paper", yref="paper",
            x=0.13, y=0.6,
            sizex=0.72, sizey=0.85,
            xanchor="center", yanchor="middle",
            layer="below"
        )
    )

    fig.add_layout_image(
        dict(
            source=Image.open(f"photos/{ph2}"),
            xref="paper", yref="paper",
            x=0.87, y=0.6,
            sizex=0.72, sizey=0.85,
            xanchor="center", yanchor="middle",
            layer="below"
        )
    )
    
    # --- Plotly radar chart ---
    # fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=p1,
        theta=['Saves %/90', 'Clean Sheets %', 'Saved Penalties %', 'Errors Lead to Shot/90', 'xGC'],
        fill='toself',
        name=player1,
        line=dict(color='#D62E0F', width=4),
        fillcolor='#DB5B42',
        opacity=0.5
    ), row=1, col=2)
    fig.add_trace(go.Scatterpolar(
        r=p2,
        theta=['Saves %/90', 'Clean Sheets %', 'Saved Penalties %', 'Errors Lead to Shot/90', 'xGC'],
        fill='toself',
        name=player2,
        line=dict(color='#120FD6', width=4),
        fillcolor='#4F4ED9',
        opacity=0.5
    ), row=1, col=2)
    
    fig.update_layout(
        polar=dict(radialaxis=dict(
            visible=True,
            range=[0, 1],
            color="black",          # ← makes the tick labels black
            tickfont=dict(color="rgba(0,0,0,0)")  # ← ensures tick text is black
        )),
        showlegend=True,
        legend=dict(
             orientation="h",      # horizontal layout
            x=0.5,                # center horizontally
            y=1.15,               # position above the chart
            xanchor="center",     # anchor at center
            yanchor="bottom",     # anchor at bottom of legend box
            bgcolor="rgba(0,0,0,0)"  # transparent background (optional) 
        ),
        #title=dict(text=f"{player1} vs {player2}", x=0.5, xanchor='center', font=dict(size=24)),
        width=500,  # 👈 increase size
        height=500, # 👈 increase size
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig

def table_player_data():
    data_c = get_player_data()[['web_name', 'short_name', 'Next_3_Fixtures', 'position', 'now_cost', 'selected_by_percent', 'total_points',
         'Min_Playing', 'Gls', 'G_minus_PK', 'Ast', 'G+A', 'npxG_Expected', 'xG_Expected', 'diff', 'xA_Expected', 'Sh_per_90_Standard',
         'SoT_per_90_Standard', 'Shots on Target %', 'G_per_Sh_Standard', 'KP_per_90', 'Crs_per_90', 'Final_Third_per_90',
        'defensive_contribution_per_90', 'Tkl_Tackles', 'TklW_Tackles', 'Tackles Won %',
       'Blocks_Blocks', 'Int', 'Clr', 'Err', 'CBIT/90',
                               'SoTA', 'Saves', 'Save_percent', 'CS', 'CS_percent', 'PKatt_Penalty',
       'PKA_Penalty', 'PKsv_Penalty', 'PKm_Penalty', 'Save_percent_Penalty', 'expected_goals_conceded_per_90'
                               ]]
    data_c.columns = ['Player', 'Club', 'Next 3 Opp', 'Position', 'Price', 'Selected by %', 'Total Points',
                   'Minutes', 'Goals', 'nPG', 'Assists', 'G+A', 'npxG', 'xG', 'npxG minus G', 'xA', 'Shots/90', 'Shots on Target/90',
                       'Shots on Target %', 'Goals per Shot', 'Key Passes/90', 'Crosses/90', 'Passes into final 3rd/90',
            'Defensive Contribution/90', 'Tackles Attempted/90', 'Tackles Won/90', 'Tackles Won %', 'Blocks/90', 'Interceptions/90', 'Clearances/90',
                     'Errors Lead to Shot/90', 'CBIT/90',
                     'Shots on Target Attempted', 'Saves', 'Saves %', 'Clean Sheets', 'Clean Sheets %', 'Penalties Attempted', 'Penalties Conceded', 'Penalties Saved', 'Penalties Missed', 'Penalties Saved %', 'xGC'
                     ]
    return data_c

def chart_xg():
    data_xg = get_player_data()[['web_name', 'G_minus_PK', 'npxG_Expected']].sort_values('G_minus_PK', ascending=False).head(10)
    fig = px.scatter(
        data_xg,
        x='npxG_Expected',
        y='G_minus_PK',
        text='web_name',       # shows player names on hover
        size_max=10,
        title='Non-Penalty Goals vs xG (Top 10 scorers)'
    )

    fig.update_traces(textposition='top center')
    fig.update_layout(xaxis_title='Expected Non-Penalty Goals (npxG)',
                      yaxis_title='Non-Penalty Goals Scored (Gls)',
                     yaxis=dict(range=[0, data_xg['G_minus_PK'].max() * 1.2]))

    return fig

def chart_xa():
    data_xa = get_player_data()[['web_name', 'Ast', 'xA_Expected']].sort_values('Ast', ascending=False).head(10)
    fig = px.scatter(
        data_xa,
        x='xA_Expected',
        y='Ast',
        text='web_name',       # shows player names on hover
        size_max=10,
        title='Assists vs xA (Top 10 assistants)'
    )

    # for i, row in data.iterrows():
    #     fig.add_annotation(
    #         x=row['xG_Expected'],
    #         y=row['Gls'],
    #         text=row['web_name'],
    #         showarrow=False,
    #         textangle=45,
    #         yshift=5
    #     )
    
    fig.update_traces(textposition='top right')
    fig.update_layout(xaxis_title='Expected Assists (xA)',
                      yaxis_title='Assists deliveried',
                     yaxis=dict(range=[0, data_xa['Ast'].max() * 1.2]))

    return fig

class xg_data:
    def __init__(self, fig_u, fig_o):
        self.fig_u = fig_u
        self.fig_o = fig_o

def chart_perform_xg():
    data_xg = get_player_data()[['web_name', 'G_minus_PK', 'npxG_Expected']]
    data_xg['diff'] = round(data_xg['G_minus_PK'] - data_xg['npxG_Expected'], 2)
    under = data_xg.sort_values('diff')[['web_name', 'diff']].head(10)
    over = data_xg.sort_values('diff', ascending=False)[['web_name', 'diff']].head(10)

    fig_u = px.bar(
        under,
        x='diff',               # bar length
        y='web_name',           # player names
        orientation='h',        # horizontal
        title='Difference between Goals and xG',
        text='diff'             # show numbers on bars
    )

    fig_u.update_traces(textposition='outside')
    fig_u.update_layout(
        xaxis_title='Difference (Goals - xG)',
        yaxis_title=None,
        yaxis=dict(autorange='reversed')  # so top player appears at top
    )

    fig_o = px.bar(
        over,
        x='diff',               # bar length
        y='web_name',           # player names
        orientation='h',        # horizontal
        title='Difference between Goals and xG',
        text='diff'             # show numbers on bars
    )

    fig_o.update_traces(textposition='outside')
    fig_o.update_layout(
        xaxis_title='Difference (Goals - xG)',
        yaxis_title=None,
        yaxis=dict(autorange='reversed')  # so top player appears at top
    )
    
    return xg_data(fig_u, fig_o)




















    