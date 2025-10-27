import requests
import pandas as pd
import duckdb
import h2h
import charts_h2h as ch2
import streamlit as st

#league_id = 1209828
st.set_page_config(
    page_title='Ziga-Zaga FPL Dashboard',
    page_icon='⚔️',  # You can use an emoji OR a local image file (e.g. "logo.png")
    layout='wide'
)

league_id = st.text_input('Enter your H2H League ID', placeholder='e.g. 1000')

if league_id:
    try:
        league_name = h2h.get_league_name(league_id)
        
        tab1 = ch2.standings(league_id)
        st.plotly_chart(tab1)
        
        tab2 = ch2.max_win_streak(league_id)
        tab3 = ch2.max_loss_streak(league_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(tab2)
        
        with col2:
            st.plotly_chart(tab3)
    
        tab4 = ch2.otskokers(league_id)
        tab5 = ch2.antiotsk(league_id)
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(tab4)
        with col4:
            st.plotly_chart(tab5)
    except:
        st.error('Please enter a valid league ID')

else:
    st.info("Enter your league ID above to see data.")