import requests
import pandas as pd
import duckdb
import streamlit as st

@st.cache_data(ttl=3600)
def get_h2h_league_info(league_id):
    url = f"https://fantasy.premierleague.com/api/leagues-h2h/{league_id}/standings/"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    
    # Extract managers info
    teams = data['standings']['results']
    league_table = []
    for team in teams:
        league_table.append({
            'Manager': team['player_name'],
            'Rank': team['rank'],
            'Played': team['matches_played'],
            'Won': team['matches_won'],
            'Draw': team['matches_drawn'],
            'Lost': team['matches_lost'],
            'Points': team['total']
        })
    df_league = pd.DataFrame(league_table)
    return df_league

@st.cache_data(ttl=3600)
def get_h2h_managers(league_id):
    managers = {}
    page = 1
    while True:
        url = f"https://fantasy.premierleague.com/api/leagues-h2h/{league_id}/standings/?page_standings={page}"
        res = requests.get(url).json()
        for entry in res['standings']['results']:
            managers[entry['entry']] = entry['player_name']
        if not res['standings']['has_next']:
            break
        page += 1
    return managers

@st.cache_data(ttl=3600)
def get_h2h_fixtures(league_id):
    fixtures = []
    page = 1
    while True:
        url = f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{league_id}/?page={page}"
        res = requests.get(url).json()
        fixtures.extend(res['results'])
        if not res['has_next']:
            break
        page += 1
    return fixtures

@st.cache_data(ttl=3600)
def get_complete_table(league_id):
    managers = get_h2h_managers(league_id)
    fixtures = get_h2h_fixtures(league_id)
    
    rows = []
    for match in fixtures:
        rows.append({
            'gw': match['event'],
            'manager': managers.get(match['entry_1_entry'], 'Unknown'),
            'gw_points': match['entry_1_points'],
            'opponent': managers.get(match['entry_2_entry'], 'Unknown'),
            'opponent_points': match['entry_2_points']
        })
        rows.append({
            'gw': match['event'],
            'manager': managers.get(match['entry_2_entry'], 'Unknown'),
            'gw_points': match['entry_2_points'],
            'opponent': managers.get(match['entry_1_entry'], 'Unknown'),
            'opponent_points': match['entry_1_points']
        })
    
    df_h2h = pd.DataFrame(rows)
    df_h2h.sort_values(by=['gw', 'manager'], inplace=True)
    df_h2h.reset_index(drop=True, inplace=True)

    return df_h2h

@st.cache_data(ttl=3600)
def get_league_name(league_id):
    url = f'https://fantasy.premierleague.com/api/leagues-h2h/{league_id}/standings/'
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return data['league']['name']