if (!require("worldfootballR")) {
  install.packages("worldfootballR", repos = "https://cloud.r-project.org/")
}
library(worldfootballR)
library(dplyr)

fetch_fbref_data <- function(stat_type) {
  fb_big5_advanced_season_stats(
    season_end_year = 2026,
    stat_type = stat_type,
    team_or_player = "player",
    time_pause = 7
  )
}

#Load datasets ---
df_st  <- fetch_fbref_data("standard")
df_sh  <- fetch_fbref_data("shooting")
df_p   <- fetch_fbref_data("passing")
df_def <- fetch_fbref_data("defense")
df_misc <- fetch_fbref_data("misc")
df_k   <- fetch_fbref_data("keepers")

#Filter Premier League only ---
filter_pl <- function(df) df %>% filter(Comp == "Premier League")

df_st  <- filter_pl(df_st)
df_sh  <- filter_pl(df_sh)
df_p   <- filter_pl(df_p)
df_def <- filter_pl(df_def)
df_misc <- filter_pl(df_misc)
df_k   <- filter_pl(df_k)

#Select relevant columns ---
df_st <- df_st %>%
  select(any_of(c(
    'Squad', 'Player', 'Starts_Playing', 'Min_Playing', 'Gls', 'Ast', 'G+A', 'G_minus_PK',
    'PK', 'PKatt', 'xG_Expected', 'npxG_Expected', 'xAG_Expected', 'npxG+xAG_Expected',
    'PrgC_Progression', 'PrgP_Progression', 'PrgR_Progression', 'Gls_Per', 'Ast_Per',
    'G+A_Per', 'G_minus_PK_Per', 'G+A_minus_PK_Per', 'xG_Per', 'xAG_Per', 'xG+xAG_Per',
    'npxG_Per'
  )))

df_sh <- df_sh %>%
  select(any_of(c(
    'Squad', 'Player', 'Gls_Standard', 'Sh_Standard', 'SoT_Standard',
    'SoT_percent_Standard', 'Sh_per_90_Standard', 'SoT_per_90_Standard',
    'G_per_Sh_Standard', 'G_per_SoT_Standard', 'Dist_Standard'
  )))

df_p <- df_p %>%
  select(any_of(c(
    'Squad', 'Player', 'Cmp_Total', 'Att_Total', 'Cmp_percent_Total',
    'xAG', 'xA_Expected', 'A_minus_xAG_Expected', 'KP',
    'Final_Third', 'PPA', 'CrsPA', 'PrgP'
  )))

df_def <- df_def %>%
  select(any_of(c(
    'Squad', 'Player', 'Tkl_Tackles', 'TklW_Tackles',
    'Blocks_Blocks', 'Int', 'Tkl+Int', 'Clr', 'Err'
  )))

df_misc <- df_misc %>%
  select(any_of(c(
    'Squad', 'Player', 'Fls', 'Fld', 'Off', 'Crs',
    'Won_Aerial', 'Lost_Aerial', 'Won_percent_Aerial'
  )))

df_k <- df_k %>%
  select(any_of(c(
    'Squad', 'Player', 'GA', 'GA90', 'SoTA', 'Saves', 'Save_percent',
    'CS', 'CS_percent', 'PKatt_Penalty', 'PKA_Penalty', 'PKsv_Penalty',
    'PKm_Penalty', 'Save_percent_Penalty'
  )))

# --- 4. Merge all datasets on Player & Squad ---
merged_df <- df_st %>%
  full_join(df_sh,  by = c("Squad", "Player")) %>%
  full_join(df_p,   by = c("Squad", "Player")) %>%
  full_join(df_def, by = c("Squad", "Player")) %>%
  full_join(df_misc,by = c("Squad", "Player")) %>%
  full_join(df_k,   by = c("Squad", "Player"))

# --- 5. Save outputs ---
dir.create("data", showWarnings = FALSE)

# Individual tables (optional)
write.csv(df_st,  "data/df_st.csv",  row.names = FALSE)
write.csv(df_sh,  "data/df_sh.csv",  row.names = FALSE)
write.csv(df_p,   "data/df_p.csv",   row.names = FALSE)
write.csv(df_def, "data/df_def.csv", row.names = FALSE)
write.csv(df_misc,"data/df_misc.csv",row.names = FALSE)
write.csv(df_k,   "data/df_k.csv",   row.names = FALSE)

# Unified dataset
write.csv(merged_df, "data/fbref_data.csv", row.names = FALSE)

cat("✅ Merged Premier League FBref data saved to data/fbref_premier_league_2026.csv\n")
