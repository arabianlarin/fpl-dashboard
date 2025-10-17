import requests
import pandas as pd
from datetime import datetime
import os
from time import sleep

league_id = 1209664
num_gameweeks = 38

class teamsData:
    def __init__(self, teams, team_lookup):
        self.teams = teams
        self.team_lookup = team_lookup

class bootstrapData:
    def __init__(self, players, averages):
        self.players = players
        self.averages = averages

def get_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_league_standings(league_id):
    url = f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/'
    data = get_json(url)
    standings = data['standings']['results']
    return pd.DataFrame(standings)

def get_manager_history(team_id):
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/history/'
    data = get_json(url)
    df_current = pd.DataFrame(data['current'])
    df_current['team_id'] = team_id
    return df_current

def get_manager_info(team_id):
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/'
    data = get_json(url)
    info = {
        'team_id': team_id,
        'team_name': data['name'],
        'player_first_name': data['player_first_name'],
        'player_last_name': data['player_last_name'],
        'overall_points': data['summary_overall_points'],
        'overall_rank': data['summary_overall_rank'],
        'team_value': data['last_deadline_value'] / 10,
        'bank': data['last_deadline_bank'] / 10,
        'last_deadline_total_transfers': data.get('last_deadline_total_transfers', None)
    }
    return pd.DataFrame([info])

def get_gw_picks(team_id, gw):
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/'
    data = get_json(url)
    df = pd.DataFrame(data['picks'])
    df['gameweek'] = gw
    df['team_id'] = team_id
    return df

def get_full_picks_history(team_id, num_gws=38):
    all_gws = []
    for gw in range(1, num_gws + 1):
        try:
            picks = get_gw_picks(team_id, gw)
            all_gws.append(picks)
        except requests.HTTPError:
            break
    return pd.concat(all_gws, ignore_index=True) if all_gws else pd.DataFrame()

def get_chip_usage(team_id, num_gws=38):
    chips_used = []
    for gw in range(1, num_gws + 1):
        url = f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/'
        try:
            data = get_json(url)
            chip = data.get('active_chip')
            if chip:
                chips_used.append({'team_id': team_id, 'gameweek': gw, 'chip': chip})
        except requests.HTTPError:
            break
    return pd.DataFrame(chips_used)

def get_positions():
    return pd.DataFrame({
            'element_type': [1, 2, 3, 4],
            'position': ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
            })

def get_bootstrap():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()
    events = data['events']
    players = pd.DataFrame(data['elements'])
    players = players[['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type', 'now_cost', 'selected_by_percent', 'total_points']]
    averages = pd.DataFrame([{
        'gameweek': e['id'],
        'name': 'Average',
        'average_points': e['average_entry_score']
    } for e in events if e['finished']])
    return bootstrapData(players, averages)
    
# def get_player_history():
#     url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
#     response = requests.get(url)
#     data = response.json()
#     players = pd.DataFrame(data['elements'])
#     return players[['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type', 'now_cost', 'selected_by_percent', 'total_points']]

def get_teams():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()
    teams = pd.DataFrame(data['teams'])
    teams = teams[['id', 'name', 'short_name']]
    team_lookup = teams.set_index('id')['name'].to_dict()
    return teamsData(teams, team_lookup)

def get_player_history_detailed():
    all_histories = []

    for idx, row in get_bootstrap().players.iterrows():
        player_id = row.get('id')
        first = (row.get('first_name') or '').strip()
        second = (row.get('second_name') or '').strip()
        if first or second:
            full_name = f'{first} {second}'.strip()
        else:
            full_name = row.get('web_name') or ''
    
        team_id = row.get('team')
        team_name = None
        if team_id is not None:
            team_name = get_teams().team_lookup.get(team_id)
        if not team_name:
            team_name = row.get('name') or row.get('name_team') or row.get('team_name') or ''
    
        url = f'https://fantasy.premierleague.com/api/element-summary/{player_id}/'
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            history = data.get('history', [])
            if history:
                df = pd.DataFrame(history)
                df = df.rename(columns={'round': 'gameweek'})
                df['player_id'] = player_id
                df['player_name'] = full_name
                df['team_name'] = team_name
                keep_cols = ['player_id', 'player_name', 'team_name', 'gameweek',
                             'total_points', 'minutes', 'goals_scored',
                             'assists', 'clean_sheets', 'yellow_cards', 'red_cards',
                             'influence', 'creativity', 'threat', 'ict_index',
                             'clearances_blocks_interceptions', 'recoveries', 'tackles',
                             'defensive_contribution', 'starts', 'expected_goals',
                             'expected_assists', 'expected_goal_involvements',
                             'expected_goals_conceded']
                present = [c for c in keep_cols if c in df.columns]
                df = df[present]
                all_histories.append(df)
        except Exception as e:
            print(f'Failed to fetch player {player_id} ({full_name}): {e}')
        sleep(0.18)
    
    if all_histories:
        player_history = pd.concat(all_histories, ignore_index=True)
        if 'gameweek' in player_history.columns:
            player_history['gameweek'] = player_history['gameweek'].astype(int)
    else:
        player_history = pd.DataFrame()

    return player_history

def get_history(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_history = []
    for team_id in manager_ids:
        hist = get_manager_history(team_id)
        all_history.append(hist)
    return pd.concat(all_history, ignore_index=True)

def get_info(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_info = []
    for team_id in manager_ids:
        info = get_manager_info(team_id)
        all_info.append(info)
    return pd.concat(all_info, ignore_index=True)

def get_picks(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_picks = []
    for team_id in manager_ids:
        picks = get_full_picks_history(team_id)
        if not picks.empty:
            all_picks.append(picks)
    return pd.concat(all_picks, ignore_index=True) if all_picks else pd.DataFrame()

def get_chips(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_chips = []
    for team_id in manager_ids:
        chips = get_chip_usage(team_id)
        if not chips.empty:
            all_chips.append(chips)
    return pd.concat(all_chips, ignore_index=True) if all_chips else pd.DataFrame()