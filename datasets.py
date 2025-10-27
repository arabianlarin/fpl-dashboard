import duckdb
import fpl_api as fa
import streamlit as st
import fbref as fbr
import pandas as pd

class datasetData:
    def __init__(self, gw, highest_scores, lowest_scores, standings, bench, h2h):
        self.gw = gw
        self.highest_scores = highest_scores
        self.lowest_scores = lowest_scores
        self.standings = standings
        self.bench = bench
        self.h2h = h2h

@st.cache_resource
def get_dataset(league_id):

    df_history = fa.get_history(league_id)
    df_chips = fa.get_chips(league_id)
    averages = fa.get_bootstrap().averages
    #df_picks = fa.get_picks(league_id)
    df_info = fa.get_info(league_id)
    #df_positions = fa.get_positions()
    #player_history = fa.get_player_history_detailed()
    #teams = fa.get_teams().teams

    gw = duckdb.query('''
    select
    event,
    concat(mi.player_first_name, ' ', mi.player_last_name) player_name,
    mi.team_name,
    gh.points,
    gh.points - gh.event_transfers_cost net_points,
    gh.total_points,
    row_number() over (partition by gh.event order by gh.total_points desc) league_rank,
    gh.overall_rank,
    gh.percentile_rank,
    gh.event_transfers,
    gh.event_transfers_cost,
    gh.points_on_bench,
    cu.chip
    from df_history gh
    left join df_info mi on gh.team_id = mi.team_id
    left join df_chips cu on gh.team_id = cu.team_id and gh.event = cu.gameweek
    union all
    select
    gameweek,
    name,
    name,
    average_points,
    average_points,
    null,
    null,
    null,
    null,
    0,
    0,
    0,
    null
    from averages
    ''').to_df()
    
    # gw_detailed = duckdb.query('''
    # select
    # p.gameweek,
    # mi.team_name,
    # dpo.position,
    # ph.player_name,
    # dt.short_name club,
    # ph.total_points,
    # p.is_captain,
    # p.is_vice_captain,
    # p.multiplier,
    # ph.minutes,
    # ph.goals_scored,
    # ph.assists,
    # ph.clean_sheets,
    # ph.yellow_cards,
    # ph.red_cards
    # from df_picks p
    # left join df_info mi on p.team_id = mi.team_id
    # left join df_positions dpo on p.element_type = dpo.element_type
    # left join player_history ph on p.element = ph.player_id and p.gameweek = ph.gameweek
    # left join teams dt on ph.team_name = dt.name
    # ''').to_df()

    
    highest_scores = duckdb.query('''
    select event, player_name, team_name, net_points,
    coalesce(
      case when chip = 'wildcard' then 'Wildcard'
           when chip = 'freehit' then 'Free Hit'
           when chip = '3xc' then 'Triple Captain'
           when chip = 'bboost' then 'Bench Boost'
           else chip end,
      'None') chip
    from (
    select
    *, row_number() over (partition by event order by net_points desc) gw_rank, max(net_points) over (partition by event order by net_points desc, overall_rank asc) max_gw_rank
    from gw
    where player_name != 'Average') a
    where net_points = max_gw_rank
    order by 1
    ''').to_df()

    lowest_scores = duckdb.query('''
    select event, player_name, team_name, net_points,
    coalesce(
      case when chip = 'wildcard' then 'Wildcard'
           when chip = 'freehit' then 'Free Hit'
           when chip = '3xc' then 'Triple Captain'
           when chip = 'bboost' then 'Bench Boost'
           else chip end,
      'None') chip
    from (
    select
    *, row_number() over (partition by event order by net_points desc) gw_rank, min(net_points) over (partition by event order by net_points, overall_rank desc) min_gw_rank
    from gw
    where player_name != 'Average') a
    where net_points = min_gw_rank
    order by 1
    ''').to_df()

    standings = duckdb.query('''
    select
    event,
    player_name,
    team_name,
    net_points,
    total_points,
    case
      when league_rank < prev_league_rank then concat('⬆️ ', cast(league_rank as varchar))
      when league_rank > prev_league_rank then concat('⬇️ ', cast(league_rank as varchar))
      else concat('↔️ ', cast(league_rank as varchar))
    end league_rank_dyn,
    league_rank,
    prev_league_rank - league_rank rank_gain,
    coalesce(cast(prev_league_rank as varchar), 'N/A') prev_league_rank,
    overall_rank,
    coalesce(
      case when chip = 'wildcard' then 'Wildcard'
           when chip = 'freehit' then 'Free Hit'
           when chip = '3xc' then 'Triple Captain'
           when chip = 'bboost' then 'Bench Boost'
           else chip end,
      'None') chip
    from (
    select
    event, player_name, team_name, net_points, total_points, league_rank, lag(league_rank) over (partition by player_name order by event asc) prev_league_rank, overall_rank,
    chip
    from gw
    where 1=1
    --and event = (select max(event) from gw)
    and player_name != 'Average'
    order by league_rank)
    --where event = (select max(event) from gw)
    order by event, league_rank
    '''
    ).to_df()

    bench = duckdb.query('''
    select
    event,
    player_name,
    points_on_bench
    from gw
    where player_name != 'Average'
    order by 3 desc
    '''
    ).to_df()

    h2h = duckdb.query('''
    select gw1.event gw, gw1.player_name man1, gw1.net_points points1, gw1.overall_rank or1, gw2.player_name man2, gw2.net_points points2,
    gw2.overall_rank or2
    from gw gw1
    left join gw gw2 on gw1.event = gw2.event
    ''').to_df()
    
    return datasetData(gw, highest_scores, lowest_scores, standings, bench, h2h)

def get_player_data():
    fb = fbr.get_fbref_data()
    players = fa.get_bootstrap().players
    fb['name_norm'] = fb['Player'].apply(fbr.normalize_name)
    players['name_norm'] = players['player_name'].apply(fbr.normalize_name)
    teams = fa.get_teams().teams

    fbref_names = fb['name_norm'].unique()
    players['fbref_match'] = players['name_norm'].apply(lambda x: fbr.fuzzy_match(x, fbref_names))

    mask = (players['fbref_match'].isna()) & (players['minutes'] != 0)

    players.loc[mask, 'name_norm'] = players.loc[mask, 'name_norm'].apply(fbr.shorten_name)

    #players[(players.player_name=='João Pedro Ferreira da Silva') & (players.team==16)]['fbref_match'] == 'Jota'
    players.loc[(players.player_name=='João Pedro Ferreira da Silva') & (players.team==16), 'fbref_match'] = 'Jota'
    players.loc[(players.player_name=='Amara Nallo'), 'fbref_match'] = 'Amara Nallo'
    
    manual_map = {
    'fabio freitas': 'fabio carvalho',
    'alisson becker': 'alisson',
    'jose malheiro': 'jose sa',
    'carlos henrique': 'casemiro',
    'jair paula': 'jair cunha',
    'joao maria': 'joao palhinha',
    'mateus goncalo': 'mateus fernandes',
    'francisco evanilson': 'evanilson',
    'andre trindade': 'andre',
    'estevao almeida': 'estevao willian',
    'norberto bercique': 'beto',
    'felipe rodrigues': 'morato',
    'kevin santos': 'kevin',
    'savio moreira': 'savio',
    'lucas tolentino': 'lucas paqueta',
    'joao victor': 'joao gomes',
    'rodrigo rodri': 'rodri'
    }

    players['name_norm'] = players['name_norm'].replace(manual_map)
    fixtures = fa.get_fixtures()

    full_data = duckdb.query('''
    select
    *
    from players pha
    left join teams t on pha.team = t.id
    left join fixtures f on t.short_name = f.Team
    left join fb fpd on coalesce(pha.fbref_match, pha.name_norm) = fpd.name_norm-- and t.name = fpd.Squad
    '''
    ).to_df()

    full_data["photo"] = full_data["photo"].str.replace(".jpg", ".png", regex=False)
    full_data['now_cost'] = full_data['now_cost']/10
    full_data['selected_by_percent'] = full_data['selected_by_percent'].astype(float)
    full_data['defensive_contribution_per_90'] = round(full_data['defensive_contribution']/90, 2)
    full_data['CBIT/90'] = round(full_data['TklW_Tackles'] + full_data['Blocks_Blocks'] + full_data['Int'] + full_data['Clr'], 2)
    full_data['Tackles Won %'] = round(full_data['TklW_Tackles']*100/full_data['Tkl_Tackles'], 2)
    full_data['Shots on Target %'] = round(full_data['SoT_per_90_Standard']/full_data['Sh_per_90_Standard'] * 100, 2)
    full_data['diff'] = round(full_data['G_minus_PK'] - full_data['npxG_Expected'], 2)

    return full_data.fillna(0)