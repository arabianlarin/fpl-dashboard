import pandas as pd
import requests
from time import sleep
from fpl_api import get_bootstrap, get_teams  # adjust imports to your actual functions

def get_player_history_detailed():
    all_histories = []

    for idx, row in get_bootstrap().players.iterrows():
        player_id = row.get('id')
        first = (row.get('first_name') or '').strip()
        second = (row.get('second_name') or '').strip()
        full_name = row.get('web_name')
    
        team_id = row.get('team')
        team_name = get_teams().team_lookup.get(team_id, '')

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
                keep_cols = [
                    'player_id', 'player_name', 'web_name', 'team_name', 'gameweek',
                    'total_points', 'minutes', 'goals_scored', 'assists',
                    'clean_sheets', 'yellow_cards', 'red_cards', 'influence',
                    'creativity', 'threat', 'ict_index', 'clearances_blocks_interceptions',
                    'recoveries', 'tackles', 'defensive_contribution', 'starts',
                    'expected_goals', 'expected_assists', 'expected_goal_involvements',
                    'expected_goals_conceded'
                ]
                df = df[[c for c in keep_cols if c in df.columns]]
                all_histories.append(df)
        except Exception as e:
            print(f'Failed to fetch player {player_id} ({full_name}): {e}')
        sleep(0.18)
    
    if all_histories:
        player_history = pd.concat(all_histories, ignore_index=True)
        player_history['gameweek'] = player_history['gameweek'].astype(int)
        player_history.to_csv('df.csv', index=False)
        print("✅ Player history updated and saved to df.csv")
    else:
        print("⚠️ No player histories fetched")

if __name__ == "__main__":
    get_player_history_detailed()
