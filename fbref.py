from datetime import datetime
import duckdb
import fpl_api as fa
import unidecode
import re
from rapidfuzz import process, fuzz
import pandas as pd
import streamlit as st

@st.cache_data(ttl=86400)
def get_fbref_data():
    #subprocess.run(['Rscript', 'fetch_fbref_data.R'], check=True)
    fbref_data = pd.read_csv('data/fbref_data.csv')
    fbref_data = duckdb.query('''
    select
    dst.Player,
    sum(Starts_Playing) Starts_Playing,
    sum(Min_Playing) Min_Playing,
    SUM(Gls_Standard) AS Gls_Standard,
        SUM(Sh_Standard) AS Sh_Standard,
        SUM(SoT_Standard) AS SoT_Standard,
        round(SUM(Sh_Standard)/sum(Min_Playing) * 90, 2) AS Sh_per_90_Standard,
        round(SUM(SoT_Standard)/sum(Min_Playing) * 90, 2) AS SoT_per_90_Standard,
        SUM(SoT_percent_Standard) AS SoT_percent_Standard,
        --SUM(Sh_per_90_Standard) AS Sh_per_90_Standard,
        --SUM(SoT_per_90_Standard) AS SoT_per_90_Standard,
        SUM(G_per_Sh_Standard) AS G_per_Sh_Standard,
        SUM(G_per_SoT_Standard) AS G_per_SoT_Standard,
        SUM(Dist_Standard) AS Dist_Standard,
        SUM(Cmp_Total) AS Cmp_Total,
        SUM(Att_Total) AS Att_Total,
        SUM(Cmp_percent_Total) AS Cmp_percent_Total,
        SUM(xAG) AS xAG,
        SUM(xA_Expected) AS xA_Expected,
        SUM(A_minus_xAG_Expected) AS A_minus_xAG_Expected,
        SUM(KP) AS KP,
        round(SUM(KP)/sum(Min_Playing) * 90, 2) AS KP_per_90,
        SUM(Final_Third) AS Final_Third,
        round(SUM(Final_Third)/sum(Min_Playing) * 90, 2) AS Final_Third_per_90,
        SUM(PPA) AS PPA,
        SUM(CrsPA) AS CrsPA,
        SUM(PrgP) AS PrgP,
        round(SUM(Tkl_Tackles)/sum(Min_Playing) * 90, 2) AS Tkl_Tackles,
        round(SUM(TklW_Tackles)/sum(Min_Playing) * 90, 2) AS TklW_Tackles,
        round(SUM(Blocks_Blocks)/sum(Min_Playing) * 90, 2) AS Blocks_Blocks,
        round(SUM(Int)/sum(Min_Playing) * 90, 2) AS Int,
        SUM("Tkl+Int") AS "Tkl+Int",
        round(SUM(Clr)/sum(Min_Playing) * 90, 2) AS Clr,
        round(SUM(Err)/sum(Min_Playing) * 90, 2) AS Err,
        SUM(Fls) AS Fls,
        SUM(Fld) AS Fld,
        SUM(Off) AS Off,
        SUM(Crs) AS Crs,
        round(SUM(Crs)/sum(Min_Playing) * 90, 2) AS Crs_per_90,
        SUM(Won_Aerial) AS Won_Aerial,
        SUM(Lost_Aerial) AS Lost_Aerial,
        SUM(Won_percent_Aerial) AS Won_percent_Aerial,
        SUM(GA) AS GA,
        SUM(GA90) AS GA90,
        SUM(SoTA) AS SoTA,
        SUM(Saves) AS Saves,
        SUM(Save_percent) AS Save_percent,
        SUM(CS) AS CS,
        SUM(CS_percent) AS CS_percent,
        SUM(PKatt_Penalty) AS PKatt_Penalty,
        SUM(PKA_Penalty) AS PKA_Penalty,
        SUM(PKsv_Penalty) AS PKsv_Penalty,
        SUM(PKm_Penalty) AS PKm_Penalty,
        SUM(Save_percent_Penalty) AS Save_percent_Penalty,
        SUM(Min_Playing) AS Min_Playing,
        SUM(Gls) AS Gls,
        SUM(dst.Ast) AS Ast,
        SUM("G+A") AS "G+A",
        SUM(G_minus_PK) AS G_minus_PK,
        SUM(PK) AS PK,
        SUM(PKatt) AS PKatt,
        SUM(xG_Expected) AS xG_Expected,
        SUM(npxG_Expected) AS npxG_Expected,
        SUM(xAG_Expected) AS xAG_Expected,
        SUM("npxG+xAG_Expected") AS "npxG+xAG_Expected",
        SUM(PrgC_Progression) AS PrgC_Progression,
        SUM(PrgP_Progression) AS PrgP_Progression,
        SUM(PrgR_Progression) AS PrgR_Progression,
        SUM(Gls_Per) AS Gls_Per,
        SUM(Ast_Per) AS Ast_Per,
        SUM("G+A_Per") AS "G+A_Per",
        SUM(G_minus_PK_Per) AS G_minus_PK_Per,
        SUM("G+A_minus_PK_Per") AS "G+A_minus_PK_Per",
        SUM(xG_Per) AS xG_Per,
        SUM(xAG_Per) AS xAG_Per,
        SUM("xG+xAG_Per") AS "xG+xAG_Per",
        SUM(npxG_Per) AS npxG_Per
    from fbref_data dst
    /*left join df_sh dsh using (Player, Squad)
    left join df_p p using (Player, Squad)
    left join df_def ddef using (Player, Squad)
    left join df_misc dmisc using (Player, Squad)
    left join df_k dk using (Player, Squad)*/
    group by 1
    '''
    ).to_df()

    fbref_data['name_norm'] = fbref_data['Player'].apply(normalize_name)

    return fbref_data

def fuzzy_match(name, choices, threshold=70):
    match, score, _ = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
    return match if score >= threshold else None

def normalize_name(name):
    name = unidecode.unidecode(name)  # remove accents
    name = re.sub(r"[^a-zA-Z\s]", "", name)  # remove punctuation
    name = re.sub(r"\s+", " ", name).strip().lower()  # normalize spaces + lowercase
    return name

def shorten_name(name):
    if pd.isna(name):
        return name
    parts = name.split()
    return " ".join(parts[:2]) if len(parts) > 2 else name
