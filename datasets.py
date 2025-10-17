import duckdb
import fpl_api as fa

class datasetData:
    def __init__(self, gw, gw_detailed):
        self.gw = gw
        self.gw_detailed = gw_detailed

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

    return gw#datasetData(gw, gw_detailed)