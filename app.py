import streamlit as st
import pandas as pd
import charts as ch

league_id = 1209664
st.set_page_config(
    page_title='Ziga-Zaga FPL Dashboard',
    page_icon='🏳‍🌈',  # You can use an emoji OR a local image file (e.g. "logo.png")
    layout='wide'
)

st.title('FPL Dashboard')

fig1 = ch.chart_points_by_gw(league_id)
fig2 = ch.chart_average_by_gw(league_id)

tab1 = ch.table_standings(league_id)
tab2 = ch.table_highest_scores(league_id)
tab3 = ch.table_lowest_scores(league_id)

st.plotly_chart(tab1, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(tab2, use_container_width=True)

with col2:
    st.plotly_chart(tab3, use_container_width=True)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)