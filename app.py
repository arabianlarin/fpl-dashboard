import streamlit as st

st.set_page_config(page_title='FPL Dashboard', layout='wide',
                   page_icon='icon.png',
    initial_sidebar_state='expanded')

st.title('FPL Dashboard')

st.markdown("""
Welcome to the **FPL Dashboard**!  
This app lets you explore player and team performance using interactive charts and stats, as well as gain some insights about your mini-leagues.

Use the sidebar to navigate between sections:
- ⚔️ H2H League Data -- current standings, longest win/loss streaks
- 🏆 Classic League Data -- current standings, GW winners, bench points, manager H2H, etc.
- ⚽️ Player Data -- football data and player comparison tool (attack, defense, goalkeeping)

App developed by Rakhat Zhussupkhanov. For feedback and suggestions please text [@zhussupkhanov](t.me/zhussupkhanov)
""")


# league_page = st.Page('pages/league_data.py', title='League', icon=':material/add_circle:')
# player_page = st.Page('pages/player_comparison.py', title='Player', icon=':material/delete:')

# pg = st.navigation([league_page, player_page])
# pg.run()
