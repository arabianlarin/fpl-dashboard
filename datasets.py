import duckdb
import fpl_api as fa

class datasetData:
    def __init__(self, gw, highest_scores, lowest_scores, standings):
        self.gw = gw
        self.highest_scores = highest_scores
        self.lowest_scores = lowest_scores
        self.standings = standings

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
           when chip = 'benchboost' then 'Bench Boost'
           else chip end,
      'None')
    from (
    select
    *, row_number() over (partition by event order by net_points desc) gw_rank
    from gw) a
    where gw_rank = 1
    order by 1
    ''').to_df()

    lowest_scores = duckdb.query('''
    select event, player_name, team_name, net_points,
    coalesce(
      case when chip = 'wildcard' then 'Wildcard'
           when chip = 'freehit' then 'Free Hit'
           when chip = '3xc' then 'Triple Captain'
           when chip = 'benchboost' then 'Bench Boost'
           else chip end,
      'None')
    from (
    select
    *, row_number() over (partition by event order by net_points desc) gw_rank
    from gw) a
    where gw_rank = 11
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
    coalesce(cast(prev_league_rank as varchar), 'N/A') prev_league_rank,
    overall_rank,
    coalesce(
      case when chip = 'wildcard' then 'Wildcard'
           when chip = 'freehit' then 'Free Hit'
           when chip = '3xc' then 'Triple Captain'
           when chip = 'benchboost' then 'Bench Boost'
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
    where event = (select max(event) from gw)
    order by event, league_rank
    '''
    ).to_df()

    return datasetData(gw, highest_scores, lowest_scores, standings)