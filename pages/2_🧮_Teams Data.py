import streamlit as st
import pandas as pd
import charts as ch
import datasets as da
import fpl_api as fa
from st_aggrid import AgGrid, GridOptionsBuilder
import base64

st.set_page_config(page_title='FPL Teams Data', layout='wide',
    initial_sidebar_state='expanded')

st.title('Teams Data')

df = ch.table_team_data()

tab4, tab5 = st.tabs(['Team Stats', 'Stats vs Team'])

with tab4:

    tab1, tab2, tab3 = st.tabs(['Attacking', 'Defending', 'Goalkeeping'])

    with tab1:
        filtered_df = df[df.Team_or_Opponent=='team']
        
        filtered_df = filtered_df[['Club', 'Next 3 Opp',
                    'Minutes', 'Goals', 'Pens', 'G+A', 'npxG', 'G minus npxG', 'xG', 'xA', 'npxG/90', 'xA/90', 'Shots/90', 'Shots on Target/90',
                      'Shots on Target %', 'Goals per Shot', 'Key Passes/90', 'Crosses/90', 'Passes into final 3rd/90']].reset_index(drop=True)

        # gb = GridOptionsBuilder.from_dataframe(filtered_df)
        # cell_style = {
        #     "border": "1px solid black",  # adds a black border
        #     "padding": "4px"
        # }
        # gb.configure_default_column(cellStyle=cell_style)
        # gb.configure_default_column(minwidth=50)
        # gb.configure_column("Player", pinned="left")# freeze first column
        # #gb.configure_column("Passes into final 3rd/90", width=200)
        # tooltips = {
        # 'Next 3 Opp': 'Capital letters = home, small letters = away'
        # }
        # for col, tip in tooltips.items():
        #     gb.configure_column(col, headerTooltip=tip)
        # grid_options = gb.build()
        
        # AgGrid(filtered_df, gridOptions=grid_options, height=400, enable_enterprise_modules=False)
        st.dataframe(filtered_df, hide_index=True, height=735)

    with tab2:
        filtered_df2 = df[df.Team_or_Opponent=='team']
        
        filtered_df2 = filtered_df2[['Club', 'Next 3 Opp',
                    'Minutes', 'Goals', 'Assists', 'G+A', 'Tackles Attempted/90', 'Tackles Won/90', 'Blocks/90', 'Interceptions/90', 'Clearances/90',
                        'Errors Lead to Shot/90'
                                    ]].reset_index(drop=True)

        # gb2 = GridOptionsBuilder.from_dataframe(filtered_df2)
        # cell_style = {
        #     "border": "1px solid black",  # adds a black border
        #     "padding": "4px"
        # }
        # gb2.configure_default_column(cellStyle=cell_style)
        # gb2.configure_default_column(minwidth=50)
        # gb2.configure_column("Player", pinned="left")# freeze first column
        # tooltips = {
        # 'Next 3 Opp': 'Capital letters = home, small letters = away',
        #     'CBIT/90': 'Clearances, Blocks, Interceptions, Tackles per 90'
        # }
        # for col, tip in tooltips.items():
        #     gb2.configure_column(col, headerTooltip=tip)
        # grid_options = gb2.build()
        
        # AgGrid(filtered_df2, gridOptions=grid_options, height=400, enable_enterprise_modules=False)
        st.dataframe(filtered_df2, hide_index=True, height=735)

    with tab3:
        filtered_df3 = df[df.Team_or_Opponent=='team']
        
        #st.subheader("Filtered Players")
        filtered_df3 = filtered_df3[['Club', 'Next 3 Opp',
                    'Minutes', 'Saves', 'Saves %', 'Clean Sheets', 'Clean Sheets %', 'Penalties Attempted', 'Penalties Conceded', 'Penalties Saved', 'Penalties Missed', 'Penalties Saved %'
                                    ]].reset_index(drop=True)

        # gb3 = GridOptionsBuilder.from_dataframe(filtered_df3)
        # cell_style = {
        #     "border": "1px solid black",  # adds a black border
        #     "padding": "4px"
        # }
        # gb3.configure_default_column(cellStyle=cell_style)
        # gb3.configure_default_column(minwidth=50)
        # gb3.configure_column("Player", pinned="left")# freeze first column
        # tooltips = {
        # 'Next 3 Opp': 'Capital letters = home, small letters = away',
        # }
        # for col, tip in tooltips.items():
        #     gb3.configure_column(col, headerTooltip=tip)
        # grid_options = gb3.build()
        st.dataframe(filtered_df3, hide_index=True, height=735)
        #AgGrid(filtered_df3, gridOptions=grid_options, height=400, enable_enterprise_modules=False)

with tab5:

    tab1, tab2, tab3 = st.tabs(['Attacking', 'Defending', 'Goalkeeping'])

    with tab1:
        filtered_df = df[df.Team_or_Opponent=='opponent']
        
        filtered_df = filtered_df[['Club', 'Next 3 Opp',
                    'Minutes', 'Goals', 'Pens', 'G+A', 'npxG', 'G minus npxG', 'xG', 'xA', 'npxG/90', 'xA/90', 'Shots/90', 'Shots on Target/90',
                      'Shots on Target %', 'Goals per Shot', 'Key Passes/90', 'Crosses/90', 'Passes into final 3rd/90']].reset_index(drop=True)

        # gb = GridOptionsBuilder.from_dataframe(filtered_df)
        # cell_style = {
        #     "border": "1px solid black",  # adds a black border
        #     "padding": "4px"
        # }
        # gb.configure_default_column(cellStyle=cell_style)
        # gb.configure_default_column(minwidth=50)
        # gb.configure_column("Player", pinned="left")# freeze first column
        # #gb.configure_column("Passes into final 3rd/90", width=200)
        # tooltips = {
        # 'Next 3 Opp': 'Capital letters = home, small letters = away'
        # }
        # for col, tip in tooltips.items():
        #     gb.configure_column(col, headerTooltip=tip)
        # grid_options = gb.build()
        
        # AgGrid(filtered_df, gridOptions=grid_options, height=400, enable_enterprise_modules=False)
        st.dataframe(filtered_df, hide_index=True)

    with tab2:
        filtered_df2 = df[df.Team_or_Opponent=='opponent']
        
        filtered_df2 = filtered_df2[['Club', 'Next 3 Opp',
                    'Minutes', 'Goals', 'Assists', 'G+A', 'Tackles Attempted/90', 'Tackles Won/90', 'Blocks/90', 'Interceptions/90', 'Clearances/90',
                        'Errors Lead to Shot/90'
                                    ]].reset_index(drop=True)

        # gb2 = GridOptionsBuilder.from_dataframe(filtered_df2)
        # cell_style = {
        #     "border": "1px solid black",  # adds a black border
        #     "padding": "4px"
        # }
        # gb2.configure_default_column(cellStyle=cell_style)
        # gb2.configure_default_column(minwidth=50)
        # gb2.configure_column("Player", pinned="left")# freeze first column
        # tooltips = {
        # 'Next 3 Opp': 'Capital letters = home, small letters = away',
        #     'CBIT/90': 'Clearances, Blocks, Interceptions, Tackles per 90'
        # }
        # for col, tip in tooltips.items():
        #     gb2.configure_column(col, headerTooltip=tip)
        # grid_options = gb2.build()
        
        # AgGrid(filtered_df2, gridOptions=grid_options, height=400, enable_enterprise_modules=False)
        st.dataframe(filtered_df2, hide_index=True, height=735)

    with tab3:
        filtered_df3 = df[df.Team_or_Opponent=='opponent']
        
        #st.subheader("Filtered Players")
        filtered_df3 = filtered_df3[['Club', 'Next 3 Opp',
                    'Minutes', 'Saves', 'Saves %', 'Clean Sheets', 'Clean Sheets %', 'Penalties Attempted', 'Penalties Conceded', 'Penalties Saved', 'Penalties Missed', 'Penalties Saved %'
                                    ]].reset_index(drop=True)

        # gb3 = GridOptionsBuilder.from_dataframe(filtered_df3)
        # cell_style = {
        #     "border": "1px solid black",  # adds a black border
        #     "padding": "4px"
        # }
        # gb3.configure_default_column(cellStyle=cell_style)
        # gb3.configure_default_column(minwidth=50)
        # gb3.configure_column("Player", pinned="left")# freeze first column
        # tooltips = {
        # 'Next 3 Opp': 'Capital letters = home, small letters = away',
        # }
        # for col, tip in tooltips.items():
        #     gb3.configure_column(col, headerTooltip=tip)
        # grid_options = gb3.build()
        st.dataframe(filtered_df3, hide_index=True, height=735)
        #AgGrid(filtered_df3, gridOptions=grid_options, height=400, enable_enterprise_modules=False)

st.plotly_chart(ch.chart_xg_diff_teams())

st.plotly_chart(ch.chart_xg_diff_teams_opp())
