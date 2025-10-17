import streamlit as st
import pandas as pd
import charts as ch

league_id = 1209664

st.title('FPL Dashboard')

fig1 = ch.chart_points_by_gw(league_id)

fig2 = ch.chart_average_by_gw(league_id)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)