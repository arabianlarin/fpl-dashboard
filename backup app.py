import streamlit as st
import pandas as pd
import charts as ch
import datasets as da

league_id = 1209664
st.set_page_config(
    page_title='Ziga-Zaga FPL Dashboard',
    page_icon='🏳‍🌈',  # You can use an emoji OR a local image file (e.g. "logo.png")
    layout='wide'
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(n+2) {
        margin-top: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        text-align: center !important;
        justify-content: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('FPL Dashboard')

#st.write('Құрметті f')

tab1, tab2 = st.tabs(['Ziga-Zaga GW1-GW10', 'Kish-Nish H2H'])

with tab1:

    #@st.cache_data(ttl=86400)
    standings = da.get_dataset(league_id).standings
    
    col1, _ = st.columns([1, 3])
    with col1:
        selected_gw = st.selectbox('Select GW', sorted(standings.event.unique(), reverse=True), index=0)
    
    rank_gain = standings.sort_values('rank_gain', ascending=False)[standings.event == selected_gw]
    rank_loss = standings.sort_values('rank_gain', ascending=True)[standings.event == selected_gw]
    
    #st.metric(label='👑 Manager of the week', value=f'{standings.head(1).player_name.iloc[0]} ({standings.head(1).net_points.iloc[0]} pts)')
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-around; text-align: center; margin-top: 20px;">
            <div style="flex: 1; margin: 0 10px; border-radius: 10px; padding: 15px;">
                <h5>👑 Manager of the week</h5>
                <h2>{standings[standings.event==selected_gw].sort_values('net_points', ascending=False).head(1).player_name.iloc[0]} ({standings[standings.event==selected_gw].sort_values('net_points', ascending=False).head(1).net_points.iloc[0]} pts)</h2>
            </div>
            <div style="flex: 1; margin: 0 10px; border-radius: 10px; padding: 15px;">
                <h5>🤡 Unskill of the week</h5>
                <h2>{standings[standings.event==selected_gw].sort_values('net_points').head(1).player_name.iloc[0]} ({standings[standings.event==selected_gw].sort_values('net_points').head(1).net_points.iloc[0]} pts)</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    rise_player = rank_gain.head(1).player_name.iloc[0]
    rise_delta = rank_gain.head(1).rank_gain.iloc[0]
    
    fall_player = rank_loss.head(1).player_name.iloc[0]
    fall_delta = rank_loss.head(1).rank_gain.iloc[0]
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-around; text-align: center; margin-top: 20px;">
            <div style="flex: 1; margin: 0 10px; border-radius: 10px; padding: 15px;">
                <h5>↗️ Rise of the week</h5>
                <h2>{rise_player}</h2>
                <p style="color: green; font-weight: bold;">+{rise_delta}</p>
            </div>
            <div style="flex: 1; margin: 0 10px; border-radius: 10px; padding: 15px;">
                <h5>↘️ Downfall of the week</h5>
                <h2>{fall_player}</h2>
                <p style="color: red; font-weight: bold;">{fall_delta}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    fig1 = ch.chart_points_by_gw(league_id)
    fig2 = ch.chart_average_by_gw(league_id)
    
    tab1 = ch.table_standings(league_id, selected_gw)
    tab2 = ch.table_highest_scores(league_id)
    tab3 = ch.table_lowest_scores(league_id)
    tab4 = ch.table_gw_bench_points(league_id)
    tab5 = ch.table_total_bench_points(league_id)
    
    #standings
    st.plotly_chart(tab1, use_container_width=True, key = 'standings')
    
    #highest and lowest points
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(tab2, use_container_width=True, key = 'highest_scores')
        st.markdown("<div style='margin-top:-60px'></div>", unsafe_allow_html=True)
    
    with col2:
        st.plotly_chart(tab3, use_container_width=True, key = 'lowest_scores')
        st.markdown("<div style='margin-top:-60px'></div>", unsafe_allow_html=True)

    #st.markdown("<div style='margin-top:-60px'></div>", unsafe_allow_html=True)    
    with col1:
        st.plotly_chart(tab4, use_container_width=True, key = 'bench_by_gw')
        st.markdown("<div style='margin-top:-60px'></div>", unsafe_allow_html=True)
    
    with col2:
        st.plotly_chart(tab5, use_container_width=True, key = 'bench_total')
        st.markdown("<div style='margin-top:-60px'></div>", unsafe_allow_html=True)
    
    #st.plotly_chart(fig1, use_container_width=True, key = 'points_by_gw')
    st.plotly_chart(fig2, use_container_width=True, key = 'average_by_gw')

    col1, col2 = st.columns(2)
    with col1:
        man1 = st.selectbox("Select Manager 1", list(standings.player_name.unique()), key='m1')
    with col2:
        man2 = st.selectbox("Select Manager 2", list(standings.player_name.unique()), key='m2')

        
    tab6 = ch.table_h2h(league_id, man1, man2)
    
    fig3 = ch.chart_h2h(league_id, man1, man2)
    with st.container():
        st.write(tab6.style
                  .set_properties(**{'text-align': 'center'})
                  .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]))
        st.plotly_chart(fig3, use_container_width=False, key = 'h2h_line')

    player_names = pd.read_csv('data/fbref_data.csv').Player.unique()

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        player1 = st.selectbox("**Player 1**", sorted(player_names))
    with col_sel2:
        player2 = st.selectbox("**Player 2**", sorted(player_names))

    fig7 = ch.chart_player_comparison(player1, player2)

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