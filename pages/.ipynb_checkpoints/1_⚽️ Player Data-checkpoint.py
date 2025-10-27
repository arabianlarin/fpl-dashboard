import streamlit as st
import pandas as pd
import charts as ch
import datasets as da
import fpl_api as fa
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title='FPL Players Data', layout='wide',
    initial_sidebar_state='expanded')

st.title('Players Data')

df = ch.table_player_data()

positions = ["All"] + list(df["Position"].unique())
clubs = ["All"] + list(df["Club"].unique())
prices = ["All"] + sorted(df["Price"].unique())

col1, col2, col3, col4 = st.columns(4)

with col1:
    position_choice = st.selectbox("Select position", options=positions)
with col2:
    club_choice = st.selectbox("Select club", options=clubs)
with col3:    
    player_choice = st.selectbox("Select player", options=["All"] + list(df["Player"].unique()))
with col4:    
    min_price = df["Price"].min()
    max_price = df["Price"].max()
    price_choice = st.slider(
        "Price",
        min_value=float(min_price),
        max_value=float(max_price),
        value=(float(min_price), float(max_price)),
        step=0.1
    )

# positions = st.multiselect("Select positions", options=df_pos["position"].unique(), default=df_pos["position"].unique())
#clubs = st.multiselect("Select clubs", options=df["Club"].unique(), default=df["Club"].unique())
#player_name = st.text_input("Search player name")

tab1, tab2, tab3 = st.tabs(['Attacking', 'Defending', 'Goalkeeping'])

with tab1:
    filtered_df = df.copy()

    if position_choice != "All":
        filtered_df = filtered_df[filtered_df["Position"] == position_choice]
    
    if club_choice != "All":
        filtered_df = filtered_df[filtered_df["Club"] == club_choice]
    
    if player_choice != "All":
        filtered_df = filtered_df[filtered_df["Player"] == player_choice]
    
    # Filter by price range
    filtered_df = filtered_df[(filtered_df["Price"] >= price_choice[0]) & (filtered_df["Price"] <= price_choice[1])]
    
    #st.subheader("Filtered Players")
    filtered_df = filtered_df[['Player', 'Club', 'Next 3 Opp', 'Position', 'Price', 'Selected by %', 'Total Points',
                   'Minutes', 'Goals', 'Assists', 'G+A', 'npxG', 'xG', 'xA', 'Shots/90', 'Shots on Target/90',
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
    filtered_df2 = df.copy()

    if position_choice != "All":
        filtered_df2 = filtered_df2[filtered_df2["Position"] == position_choice]
    
    if club_choice != "All":
        filtered_df2 = filtered_df2[filtered_df2["Club"] == club_choice]
    
    if player_choice != "All":
        filtered_df2 = filtered_df2[filtered_df2["Player"] == player_choice]
    
    # Filter by price range
    filtered_df2 = filtered_df2[(filtered_df2["Price"] >= price_choice[0]) & (filtered_df2["Price"] <= price_choice[1])]
    
    #st.subheader("Filtered Players")
    filtered_df2 = filtered_df2[['Player', 'Club', 'Next 3 Opp', 'Position', 'Price', 'Selected by %', 'Total Points',
                   'Minutes', 'Goals', 'Assists', 'G+A', 'Defensive Contribution/90', 'Tackles Attempted/90', 'Tackles Won/90', 'Tackles Won %', 'Blocks/90', 'Interceptions/90', 'Clearances/90', 'CBIT/90',
                     'Errors Lead to Shot/90', 'xGC'
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
    st.dataframe(filtered_df2, hide_index=True)

with tab3:
    filtered_df3 = df.copy()
    filtered_df3 = filtered_df3[filtered_df3.Position=='Goalkeeper']

    if club_choice != "All":
        filtered_df3 = filtered_df3[filtered_df3["Club"] == club_choice]
    
    if player_choice != "All":
        filtered_df3 = filtered_df3[filtered_df3["Player"] == player_choice]

    filtered_df3 = filtered_df3[(filtered_df3["Price"] >= price_choice[0]) & (filtered_df3["Price"] <= price_choice[1])]
    
    #st.subheader("Filtered Players")
    filtered_df3 = filtered_df3[['Player', 'Club', 'Next 3 Opp', 'Position', 'Price', 'Selected by %', 'Total Points',
                   'Minutes', 'Saves', 'Saves %', 'Clean Sheets', 'Clean Sheets %', 'Penalties Attempted', 'Penalties Conceded', 'Penalties Saved', 'Penalties Missed', 'Penalties Saved %', 'xGC'
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
    st.dataframe(filtered_df3, hide_index=True)
    #AgGrid(filtered_df3, gridOptions=grid_options, height=400, enable_enterprise_modules=False)

st.divider()

st.plotly_chart(ch.chart_xg())

st.plotly_chart(ch.chart_xa())

st.plotly_chart(ch.chart_perform_xg().fig_u, key = 'xg_under')

st.plotly_chart(ch.chart_perform_xg().fig_o, key = 'xg_over')

st.divider()

st.subheader('Players comparison tool')

player_names = pd.read_csv('data/fbref_data.csv').Player.unique()

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    player1 = st.selectbox("**Player 1**", [''] + sorted(player_names), index=0)
with col_sel2:
    player2 = st.selectbox("**Player 2**", [''] + sorted(player_names), index=0)

tab1, tab2, tab3 = st.tabs(['Attacking', 'Defending', 'Goalkeeping'])

with tab1:
    
    if player1 and player2:
    
        fig7 = ch.chart_player_comparison_att(player1, player2)
        
        st.markdown(
            """
            <style>
            .centered-chart {
                display: flex;
                justify-content: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="centered-chart">', unsafe_allow_html=True)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info('Please choose players')

with tab2:
    
    if player1 and player2:
    
        fig7 = ch.chart_player_comparison_def(player1, player2)
        
        st.markdown(
            """
            <style>
            .centered-chart {
                display: flex;
                justify-content: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="centered-chart">', unsafe_allow_html=True)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info('Please choose players')

with tab3:
    if player1 and player2:
    
        fig7 = ch.chart_player_comparison_gk(player1, player2)
        
        st.markdown(
            """
            <style>
            .centered-chart {
                display: flex;
                justify-content: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="centered-chart">', unsafe_allow_html=True)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info('Please choose players')