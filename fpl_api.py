import requests
import pandas as pd
from datetime import datetime
import os
from time import sleep
import streamlit as st
import duckdb
import base64

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

@st.cache_data(ttl=86400)
def get_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=86400)
def get_league_standings(league_id):
    url = f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/'
    data = get_json(url)
    standings = data['standings']['results']
    return pd.DataFrame(standings)

@st.cache_data(ttl=86400)
def get_manager_history(team_id):
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/history/'
    data = get_json(url)
    df_current = pd.DataFrame(data['current'])
    df_current['team_id'] = team_id
    return df_current

@st.cache_data(ttl=86400)
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

@st.cache_data(ttl=86400)
def get_gw_picks(team_id, gw):
    url = f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/'
    data = get_json(url)
    df = pd.DataFrame(data['picks'])
    df['gameweek'] = gw
    df['team_id'] = team_id
    return df

@st.cache_data(ttl=86400)
def get_full_picks_history(team_id, num_gws=38):
    all_gws = []
    for gw in range(1, num_gws + 1):
        try:
            picks = get_gw_picks(team_id, gw)
            all_gws.append(picks)
        except requests.HTTPError:
            break
    return pd.concat(all_gws, ignore_index=True) if all_gws else pd.DataFrame()

@st.cache_data(ttl=86400)
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

@st.cache_data(ttl=86400)
def get_positions():
    return pd.DataFrame({
            'element_type': [1, 2, 3, 4],
            'position': ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
            })

@st.cache_data(ttl=86400)
def get_bootstrap():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()
    events = data['events']
    players = pd.DataFrame(data['elements'])
    players = players[['first_name',
                        'second_name',
                        'form',
                        'now_cost',
                        'photo',
                        'selected_by_percent',
                        'id',
                        'team',
                        'total_points',
                        'web_name',
                        'influence',
                        'creativity',
                        'threat',
                        'ict_index',
                        'defensive_contribution',
                       'minutes',
                       'element_type',
                       'expected_goals_conceded_per_90'
                      ]]
    players = duckdb.query('''
    select concat(first_name, ' ', second_name) player_name, * from players
    '''
    ).to_df()
    pos = get_positions()
    players = duckdb.query('''select p.*, position from players p left join pos using(element_type)''').to_df()
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

@st.cache_data(ttl=86400)
def get_teams():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()
    teams = pd.DataFrame(data['teams'])
    teams = teams[['id', 'name', 'short_name']]
    team_lookup = teams.set_index('id')['name'].to_dict()
    return teamsData(teams, team_lookup)

@st.cache_data(ttl=86400)
def get_fixtures():
    url = "https://fantasy.premierleague.com/api/fixtures/"
    response = requests.get(url)
    fixtures = response.json()
    fixtures = pd.DataFrame(fixtures)
    teams = get_teams().teams
    teams_df = pd.DataFrame(teams)[["id", "short_name"]].rename(columns={"id": "team_id"})

    fixtures_df = pd.DataFrame(fixtures)

    upcoming = fixtures_df[fixtures_df["finished"] == False]

    upcoming_home = upcoming[["event", "team_h", "team_a"]].rename(
        columns={"team_h": "team", "team_a": "opponent"}
    )
    upcoming_home["venue"] = "H"

    upcoming_away = upcoming[["event", "team_h", "team_a"]].rename(
        columns={"team_a": "team", "team_h": "opponent"}
    )
    upcoming_away["venue"] = "A"

    fixtures_all = pd.concat([upcoming_home, upcoming_away])

    fixtures_all = fixtures_all.merge(
        teams_df, left_on="team", right_on="team_id", how="left"
    ).merge(
        teams_df.rename(columns={"team_id": "opp_id", "short_name": "opp_short_name"}),
        left_on="opponent", right_on="opp_id", how="left"
    )

    fixtures_all["opp_short_name"] = fixtures_all.apply(
        lambda x: x["opp_short_name"].upper() if x["venue"] == "H" else x["opp_short_name"].lower(),
        axis=1
    )

    fixtures_all = fixtures_all.sort_values(by=["team", "event"])
    next3 = (
        fixtures_all.groupby("team")["opp_short_name"]
        .apply(lambda x: " | ".join(x.head(3)))
        .reset_index()
    )

    next3 = next3.merge(teams_df, left_on="team", right_on="team_id", how="left")[["short_name", "opp_short_name"]]
    next3.columns = ["Team", "Next_3_Fixtures"]

    return next3

@st.cache_data(ttl=86400)
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

@st.cache_data(ttl=86400)
def get_history(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_history = []
    for team_id in manager_ids:
        hist = get_manager_history(team_id)
        all_history.append(hist)
    return pd.concat(all_history, ignore_index=True)

@st.cache_data(ttl=86400)
def get_info(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_info = []
    for team_id in manager_ids:
        info = get_manager_info(team_id)
        all_info.append(info)
    return pd.concat(all_info, ignore_index=True)

@st.cache_data(ttl=86400)
def get_picks(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_picks = []
    for team_id in manager_ids:
        picks = get_full_picks_history(team_id)
        if not picks.empty:
            all_picks.append(picks)
    return pd.concat(all_picks, ignore_index=True) if all_picks else pd.DataFrame()

@st.cache_data(ttl=86400)
def get_chips(league_id):
    league_df = get_league_standings(league_id)
    manager_ids = league_df['entry'].tolist()
    all_chips = []
    for team_id in manager_ids:
        chips = get_chip_usage(team_id)
        if not chips.empty:
            all_chips.append(chips)
    return pd.concat(all_chips, ignore_index=True) if all_chips else pd.DataFrame()

@st.cache_data(ttl=86400)
def get_league_managers(league_id: int):
    """Fetch all manager IDs and names in a classic league."""
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    managers = []
    page = 1

    while True:
        response = requests.get(url, params={'page_standings': page}, timeout=15)
        response.raise_for_status()
        data = response.json()

        standings = data.get('standings', {}).get('results', [])
        if not standings:
            break

        for s in standings:
            managers.append({
                "manager_id": s["entry"],
                "manager_name": s["player_name"],
                "team_name": s["entry_name"]
            })

        if not data.get('standings', {}).get('has_next'):
            break
        page += 1
        sleep(1)

    return pd.DataFrame(managers)

@st.cache_data(ttl=86400)
def get_manager_transfers(entry_id: int):
    """Fetch all transfers made by a given manager."""
    url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/transfers/"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    transfers = r.json()

    if not transfers:
        return pd.DataFrame()

    df = pd.DataFrame(transfers)
    df["entry"] = entry_id
    return df

@st.cache_data(ttl=86400)
def get_player_names():
    """Get mapping of player IDs to names."""
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    r.raise_for_status()
    data = r.json()
    elements = pd.DataFrame(data["elements"])
    elements["full_name"] = elements["first_name"] + " " + elements["second_name"]
    return elements[["id", "full_name", "web_name"]]

@st.cache_data(ttl=86400)
def get_league_transfers_raw(league_id: int) -> pd.DataFrame:
    """
    Fetches all transfers made by managers in a given FPL league.
    Returns a raw dataframe (as provided by the FPL API), without joining player names.
    """
    
    # 1. Get all managers in the league
    managers = []
    page = 1

    while True:
        url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
        r = requests.get(url, params={"page_standings": page}, timeout=15)
        r.raise_for_status()
        data = r.json()

        results = data.get("standings", {}).get("results", [])
        if not results:
            break

        for res in results:
            managers.append({
                "entry": res["entry"],
                "player_name": res["player_name"],
                "entry_name": res["entry_name"]
            })

        if not data.get("standings", {}).get("has_next"):
            break

        page += 1
        sleep(1)

    if not managers:
        print("⚠️ No managers found in this league.")
        return pd.DataFrame()

    all_transfers = []

    # 2. For each manager, get transfer data
    for m in managers:
        entry_id = m["entry"]
        transfers_url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/transfers/"
        try:
            tr = requests.get(transfers_url, timeout=15)
            tr.raise_for_status()
            transfers = tr.json()

            if transfers:
                df = pd.DataFrame(transfers)
                df["entry"] = entry_id
                df["manager_name"] = m["player_name"]
                df["team_name"] = m["entry_name"]
                all_transfers.append(df)

        except Exception as e:
            print(f"Failed to fetch transfers for {m['player_name']} ({entry_id}): {e}")

        sleep(0.2)  # be gentle to FPL API

    # 3. Combine everything
    if all_transfers:
        df_all = pd.concat(all_transfers, ignore_index=True)
        return df_all
    else:
        print("⚠️ No transfers found for any manager.")
        return pd.DataFrame()
    
def encode_image(image_file):
    """Convert image file to base64 string for Plotly"""
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return "data:image/png;base64," + encoded