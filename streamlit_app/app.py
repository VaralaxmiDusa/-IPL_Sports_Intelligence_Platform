import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from groq import Groq
import os
import pathlib
from dotenv import load_dotenv
os.environ.setdefault("GROQ_API_KEY", "")
# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="IPL Sports Intelligence Platform",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F6E56;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #888;
        text-align: center;
        font-style: italic;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #0F6E56;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────
CURRENT_TEAMS = [
    'Mumbai Indians',
    'Chennai Super Kings',
    'Royal Challengers Bangalore',
    'Kolkata Knight Riders',
    'Delhi Capitals',
    'Punjab Kings',
    'Rajasthan Royals',
    'Sunrisers Hyderabad',
    'Gujarat Titans',
    'Lucknow Super Giants'
]

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    base    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'processed') + '/'
    batter  = pd.read_csv(base + 'fact_batter_stats.csv')
    bowler  = pd.read_csv(base + 'fact_bowler_stats.csv')
    player  = pd.read_csv(base + 'dim_player.csv')
    matches = pd.read_csv(base + 'dim_match.csv')
    phase   = pd.read_csv(base + 'fact_team_phase_stats.csv')
    return batter, bowler, player, matches, phase

batter, bowler, player, matches, phase = load_data()
ALL_SEASONS = sorted(batter['season'].unique())

# ── SIDEBAR ───────────────────────────────────────────────
st.sidebar.markdown("## 🏏 IPL Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home",
     "⚔️ Player Comparison",
     "📊 Phase Intelligence",
     "🏆 Career Rankings",
     "🤖 AI Match Preview",
     "🔍 Ask The Data"]
)

st.sidebar.markdown("---")

# GLOBAL SEASON FILTER — applies everywhere
st.sidebar.markdown("### 📅 Season Filter")
season_mode = st.sidebar.radio(
    "Select era",
    ["All time (2007–2024)",
     "Recent (2020–2024)",
     "Custom range"]
)

if season_mode == "All time (2007–2024)":
    selected_seasons = ALL_SEASONS
elif season_mode == "Recent (2020–2024)":
    selected_seasons = [s for s in ALL_SEASONS
                        if s >= '2020']
else:
    min_s, max_s = st.sidebar.select_slider(
        "Pick season range",
        options=ALL_SEASONS,
        value=(ALL_SEASONS[0], ALL_SEASONS[-1])
    )
    selected_seasons = [s for s in ALL_SEASONS
                        if min_s <= s <= max_s]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Seasons selected:** {len(selected_seasons)}")
st.sidebar.markdown(f"**Teams:** 10 current IPL teams")
st.sidebar.markdown(f"**Data:** Historical IPL records")

# Filter data by selected seasons globally
bat = batter[batter['season'].isin(selected_seasons)]
bowl = bowler[bowler['season'].isin(selected_seasons)]
ph = phase[phase['season'].isin(selected_seasons)]
mat = matches[matches['season'].isin(selected_seasons)]

# ══════════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<p class="main-header">🏏 IPL Sports Intelligence Platform</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data-driven cricket analysis · Current 10 IPL Teams</p>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="disclaimer">Showing data for {len(selected_seasons)} season(s): {selected_seasons[0]} to {selected_seasons[-1]} · Historical records only</p>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Matches Analysed", f"{bat['match_id'].nunique():,}")
    with col2:
        st.metric("Players Tracked", f"{bat['batter'].nunique():,}")
    with col3:
        st.metric("Total Runs", f"{int(bat['runs'].sum()):,}")
    with col4:
        st.metric("Total Wickets", f"{int(bowl['wickets'].sum()):,}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Run Scoring Trend by Season")
        season_runs = bat.groupby('season')['runs'].sum().reset_index()
        season_runs = season_runs.sort_values('season')
        fig = px.line(
            season_runs, x='season', y='runs',
            markers=True,
            color_discrete_sequence=['#0F6E56']
        )
        fig.update_layout(
            xaxis_title="Season", yaxis_title="Total Runs",
            plot_bgcolor='white', height=350
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏏 Top 10 Run Scorers")
        top_bat = (bat.groupby('batter')['runs']
                   .sum().nlargest(10).reset_index()
                   .sort_values('runs'))
        fig = px.bar(
            top_bat, x='runs', y='batter',
            orientation='h',
            color='runs',
            color_continuous_scale='Greens',
            text='runs'
        )
        fig.update_traces(texttemplate='%{text:,}',
                          textposition='outside')
        fig.update_layout(
            plot_bgcolor='white', height=350,
            coloraxis_showscale=False,
            xaxis_title="Total Runs", yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Top 10 Wicket Takers")
        top_bowl = (bowl.groupby('bowler')['wickets']
                    .sum().nlargest(10).reset_index()
                    .sort_values('wickets'))
        fig = px.bar(
            top_bowl, x='wickets', y='bowler',
            orientation='h',
            color='wickets',
            color_continuous_scale='Oranges',
            text='wickets'
        )
        fig.update_traces(texttemplate='%{text}',
                          textposition='outside')
        fig.update_layout(
            plot_bgcolor='white', height=350,
            coloraxis_showscale=False,
            xaxis_title="Total Wickets", yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🔥 Phase-wise Run Rates — All Teams")
        pivot = (ph.groupby(['batting_team','phase'])
                 ['run_rate'].mean()
                 .unstack()[['Powerplay','Middle','Death']]
                 .round(2))
        fig = px.imshow(
            pivot,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            text_auto=True,
            title=""
        )
        fig.update_layout(height=350,
                          xaxis_title="Phase",
                          yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — PLAYER COMPARISON
# ══════════════════════════════════════════════════════════
elif page == "⚔️ Player Comparison":
    st.markdown('<p class="main-header">⚔️ Player Comparison Engine</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Compare any two players across 10 dimensions</p>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="disclaimer">Based on {len(selected_seasons)} selected season(s) · Historical data only</p>',
                unsafe_allow_html=True)

    all_batters = sorted(bat['batter'].unique())
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("Select Player 1", all_batters,
                          index=all_batters.index('V Kohli')
                          if 'V Kohli' in all_batters else 0)
    with col2:
        p2 = st.selectbox("Select Player 2", all_batters,
                          index=all_batters.index('RG Sharma')
                          if 'RG Sharma' in all_batters else 1)

    if p1 == p2:
        st.warning("Please select two different players.")
        st.stop()

    def get_player_stats(name):
        df = bat[bat['batter'] == name]
        return {
            'matches'     : df['match_id'].nunique(),
            'total_runs'  : int(df['runs'].sum()),
            'avg_runs'    : round(df['runs'].mean(), 1),
            'strike_rate' : round(df['strike_rate'].mean(), 1),
            'fifties'     : int(df['is_fifty'].sum()),
            'hundreds'    : int(df['is_hundred'].sum()),
            'avg_fantasy' : round(df['fantasy_pts'].mean(), 1),
            'form_score'  : round(df['form_score'].iloc[-1], 1),
            'best_score'  : int(df['runs'].max()),
            'fours'       : int(df['fours'].sum()),
            'sixes'       : int(df['sixes'].sum()),
        }

    s1 = get_player_stats(p1)
    s2 = get_player_stats(p2)

    st.markdown("---")
    metrics = ['matches','total_runs','avg_runs','strike_rate',
               'fifties','hundreds','avg_fantasy','best_score']
    labels  = ['Matches','Total Runs','Avg Runs','Strike Rate',
               'Fifties','Hundreds','Avg Fantasy Pts','Best Score']

    cols = st.columns(4)
    for i, (metric, label) in enumerate(zip(metrics, labels)):
        with cols[i % 4]:
            v1, v2 = s1[metric], s2[metric]
            st.metric(label=label,
                      value=f"{p1[:10]}: {v1}",
                      delta=f"vs {p2[:10]}: {v2}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🕸️ Head to Head Radar")
        categories = ['Avg Runs','Strike Rate','Fifties',
                      'Hundreds','Avg Fantasy','Form Score']
        ranges = {
            'avg_runs'    : (0, 60),
            'strike_rate' : (80, 180),
            'fifties'     : (0, 80),
            'hundreds'    : (0, 20),
            'avg_fantasy' : (0, 60),
            'form_score'  : (0, 80),
        }

        def normalize(val, min_val, max_val):
            if max_val == min_val:
                return 50
            return round((val - min_val)/(max_val - min_val)*100, 1)

        keys = list(ranges.keys())
        v1n = [normalize(s1[k], *ranges[k]) for k in keys]
        v2n = [normalize(s2[k], *ranges[k]) for k in keys]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=v1n + [v1n[0]],
            theta=categories + [categories[0]],
            fill='toself', name=p1,
            line_color='#0F6E56',
            fillcolor='rgba(15,110,86,0.2)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=v2n + [v2n[0]],
            theta=categories + [categories[0]],
            fill='toself', name=p2,
            line_color='#E84393',
            fillcolor='rgba(232,67,147,0.2)'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            showlegend=True, height=400,
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Season-wise Run Comparison")
        p1s = (bat[bat['batter']==p1]
               .groupby('season')['runs'].sum().reset_index())
        p2s = (bat[bat['batter']==p2]
               .groupby('season')['runs'].sum().reset_index())
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=p1s['season'], y=p1s['runs'],
            mode='lines+markers', name=p1,
            line=dict(color='#0F6E56', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=p2s['season'], y=p2s['runs'],
            mode='lines+markers', name=p2,
            line=dict(color='#E84393', width=2)
        ))
        fig.update_layout(
            plot_bgcolor='white', height=400,
            xaxis_title="Season", yaxis_title="Runs",
            legend=dict(orientation="h", y=-0.2)
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Data Insight")
    better_avg    = p1 if s1['avg_runs'] > s2['avg_runs'] else p2
    better_sr     = p1 if s1['strike_rate'] > s2['strike_rate'] else p2
    better_consis = p1 if s1['fifties'] > s2['fifties'] else p2
    better_form   = p1 if s1['form_score'] > s2['form_score'] else p2

    st.success(f"**📊 Auto Analysis: {p1} vs {p2}**")
    st.write(f"• **{better_avg}** has the higher batting average ({s1['avg_runs']} vs {s2['avg_runs']})")
    st.write(f"• **{better_sr}** scores faster (SR: {s1['strike_rate']} vs {s2['strike_rate']})")
    st.write(f"• **{better_consis}** is more consistent ({s1['fifties']} fifties vs {s2['fifties']})")
    st.write(f"• **{better_form}** is in better current form (Form score: {s1['form_score']} vs {s2['form_score']})")

# ══════════════════════════════════════════════════════════
# PAGE 3 — PHASE INTELLIGENCE
# ══════════════════════════════════════════════════════════
elif page == "📊 Phase Intelligence":
    st.markdown('<p class="main-header">📊 Phase Intelligence</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyse team strengths and weaknesses by match phase</p>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="disclaimer">Showing {len(selected_seasons)} season(s) · Current 10 IPL teams only</p>',
                unsafe_allow_html=True)

    selected_team = st.selectbox(
        "Select Opposition Team to Analyse",
        sorted(CURRENT_TEAMS)
    )

    team_data = ph[ph['batting_team'] == selected_team]

    col1, col2, col3 = st.columns(3)
    for col, phase_name, color in zip(
        [col1, col2, col3],
        ['Powerplay','Middle','Death'],
        ['#0F6E56','#185FA5','#E84393']
    ):
        pd_ = team_data[team_data['phase'] == phase_name]
        avg_rr   = round(pd_['run_rate'].mean(), 2) if len(pd_) > 0 else 0
        avg_runs = round(pd_['runs'].mean(), 1) if len(pd_) > 0 else 0
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color:{color}">{phase_name}</h4>
                <h2 style="color:{color}">{avg_rr}</h2>
                <p style="color:#666">Avg Run Rate</p>
                <p style="color:#999">{avg_runs} avg runs/match</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📈 {selected_team} — Run Rate by Phase")
        ps = (team_data.groupby(['season','phase'])
              ['run_rate'].mean().reset_index())
        fig = px.line(
            ps, x='season', y='run_rate',
            color='phase', markers=True,
            color_discrete_map={
                'Powerplay':'#0F6E56',
                'Middle'   :'#185FA5',
                'Death'    :'#E84393'
            }
        )
        fig.update_layout(
            plot_bgcolor='white', height=350,
            xaxis_title="Season", yaxis_title="Run Rate"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🔥 All Teams Phase Heatmap")
        pivot = (ph.groupby(['batting_team','phase'])
                 ['run_rate'].mean()
                 .unstack()[['Powerplay','Middle','Death']]
                 .round(2))
        fig = px.imshow(
            pivot,
            color_continuous_scale='RdYlGn',
            aspect='auto', text_auto=True
        )
        fig.update_layout(height=350,
                          xaxis_title="Phase",
                          yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    if len(team_data) > 0:
        weak_phase   = team_data.groupby('phase')['run_rate'].mean().idxmin()
        strong_phase = team_data.groupby('phase')['run_rate'].mean().idxmax()
        st.markdown("---")
        st.success(f"**💡 Scout Report: {selected_team}**")
        st.write(f"• Their **weakest phase is {weak_phase}** — bowl your best bowlers here")
        st.write(f"• Their **strongest phase is {strong_phase}** — expect aggressive batting")
        st.write(f"• Target their {weak_phase} with your most economical bowler")

# ══════════════════════════════════════════════════════════
# PAGE 4 — CAREER RANKINGS
# ══════════════════════════════════════════════════════════
elif page == "🏆 Career Rankings":
    st.markdown('<p class="main-header">🏆 Career Rankings</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">All-time IPL player rankings · Current teams only</p>',
                unsafe_allow_html=True)
    st.markdown(f'<p class="disclaimer">Based on {len(selected_seasons)} selected season(s)</p>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏏 Batting Rankings", "🎯 Bowling Rankings"])

    with tab1:
        col1, col2 = st.columns([1,3])
        with col1:
            min_matches = st.slider("Min Matches", 5, 50, 10)
            metric = st.selectbox("Rank by",
                ['total_runs','avg_runs','strike_rate',
                 'fifties','hundreds','avg_fantasy'])

        bat_career = bat.groupby('batter').agg(
            total_runs  =('runs','sum'),
            avg_runs    =('runs','mean'),
            strike_rate =('strike_rate','mean'),
            fifties     =('is_fifty','sum'),
            hundreds    =('is_hundred','sum'),
            avg_fantasy =('fantasy_pts','mean'),
            matches     =('match_id','nunique'),
        ).round(2).reset_index()
        bat_career = bat_career[
            bat_career['matches'] >= min_matches
        ].nlargest(20, metric)

        with col2:
            fig = px.bar(
                bat_career.sort_values(metric),
                x=metric, y='batter',
                orientation='h',
                color=metric,
                color_continuous_scale='Greens',
                text=metric,
                hover_data=['matches','total_runs','avg_runs']
            )
            fig.update_traces(texttemplate='%{text:.1f}',
                              textposition='outside')
            fig.update_layout(
                height=550, plot_bgcolor='white',
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title=metric.replace('_',' ').title()
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns([1,3])
        with col1:
            min_matches_b = st.slider("Min Matches ", 5, 50, 10)
            bowl_metric = st.selectbox("Rank by ",
                ['total_wickets','avg_economy',
                 'avg_fantasy','matches'])

        bowl_career = bowl.groupby('bowler').agg(
            total_wickets =('wickets','sum'),
            avg_economy   =('economy','mean'),
            avg_fantasy   =('fantasy_pts','mean'),
            matches       =('match_id','nunique'),
        ).round(2).reset_index()
        bowl_career = bowl_career[
            bowl_career['matches'] >= min_matches_b
        ]
        if bowl_metric == 'avg_economy':
            bowl_career = bowl_career.nsmallest(20, bowl_metric)
        else:
            bowl_career = bowl_career.nlargest(20, bowl_metric)

        with col2:
            fig = px.bar(
                bowl_career.sort_values(
                    bowl_metric,
                    ascending=(bowl_metric=='avg_economy')
                ),
                x=bowl_metric, y='bowler',
                orientation='h',
                color=bowl_metric,
                color_continuous_scale='Oranges',
                text=bowl_metric,
                hover_data=['matches','total_wickets','avg_economy']
            )
            fig.update_traces(texttemplate='%{text:.1f}',
                              textposition='outside')
            fig.update_layout(
                height=550, plot_bgcolor='white',
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title=bowl_metric.replace('_',' ').title()
            )
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 5 — AI MATCH PREVIEW
# ══════════════════════════════════════════════════════════
elif page == "🤖 AI Match Preview":
    from groq import Groq  

    st.markdown('<p class="main-header">🤖 AI Match Preview</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-generated analyst report based on real historical data</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="disclaimer">Powered by Claude AI · Based on historical IPL records · Not a live predictor</p>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team 1", sorted(CURRENT_TEAMS))
    with col2:
        team_b = st.selectbox("Team 2",
                              [t for t in sorted(CURRENT_TEAMS)
                               if t != team_a])

    all_venues = sorted(bat['venue'].unique())
    venue = st.selectbox("Venue", all_venues)

    st.info("💡 This generates a real analyst-style report using 17 years of IPL data fed into Claude AI.")

    if st.button("🔍 Generate AI Match Preview", type="primary"):
        with st.spinner("Analysing historical data and generating report..."):

            def get_team_stats(team):
                b = bat[bat['batting_team'] == team]
                w = bowl[bowl['bowling_team'] == team]
                p = ph[ph['batting_team'] == team]
                phase_rr = p.groupby('phase')['run_rate'].mean().round(2).to_dict()
                top_bat = (b.groupby('batter')['runs']
                           .sum().nlargest(3).reset_index())
                top_bat_str = ', '.join(
                    f"{r['batter']} ({int(r['runs'])} runs)"
                    for _, r in top_bat.iterrows()
                )
                top_bowl = (w.groupby('bowler')['wickets']
                            .sum().nlargest(3).reset_index())
                top_bowl_str = ', '.join(
                    f"{r['bowler']} ({int(r['wickets'])} wkts)"
                    for _, r in top_bowl.iterrows()
                )
                venue_bat  = b[b['venue'] == venue]
                venue_avg  = round(venue_bat['runs'].mean(), 1) if len(venue_bat) > 0 else 'N/A'
                wins  = len(mat[mat['winner'] == team])
                total = len(mat[(mat['team1']==team)|(mat['team2']==team)])
                win_pct = round(wins/total*100,1) if total > 0 else 0
                return {
                    'phase_rr'     : phase_rr,
                    'top_batters'  : top_bat_str,
                    'top_bowlers'  : top_bowl_str,
                    'venue_avg'    : venue_avg,
                    'win_pct'      : win_pct,
                    'total_matches': total
                }

            sa = get_team_stats(team_a)
            sb = get_team_stats(team_b)

            prompt = f"""You are an expert IPL cricket analyst.
Based on the following historical data, write a professional
match preview for {team_a} vs {team_b} at {venue}.

{team_a} Historical Stats:
- Win rate: {sa['win_pct']}% ({sa['total_matches']} matches)
- Powerplay RR: {sa['phase_rr'].get('Powerplay','N/A')}
- Middle overs RR: {sa['phase_rr'].get('Middle','N/A')}
- Death overs RR: {sa['phase_rr'].get('Death','N/A')}
- Top run scorers: {sa['top_batters']}
- Top wicket takers: {sa['top_bowlers']}
- Avg runs at {venue}: {sa['venue_avg']}

{team_b} Historical Stats:
- Win rate: {sb['win_pct']}% ({sb['total_matches']} matches)
- Powerplay RR: {sb['phase_rr'].get('Powerplay','N/A')}
- Middle overs RR: {sb['phase_rr'].get('Middle','N/A')}
- Death overs RR: {sb['phase_rr'].get('Death','N/A')}
- Top run scorers: {sb['top_batters']}
- Top wicket takers: {sb['top_bowlers']}
- Avg runs at {venue}: {sb['venue_avg']}

Write a structured preview with these sections:
1. MATCH OVERVIEW (2-3 sentences)
2. {team_a} — Key Strengths & Watch-out (data-backed bullets)
3. {team_b} — Key Strengths & Watch-out (data-backed bullets)
4. KEY BATTLES (2 specific player matchups)
5. VENUE INSIGHT (what data says about {venue})
6. DATA EDGE (which team has historical advantage and why)

Be specific, cite actual numbers, write like a professional
analyst. Under 400 words. Note this is based on historical
data, not live team selection."""

            try:
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


                msg = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=1024,
                    messages=[{"role":"user","content":prompt}]
)
                report = msg.choices[0].message.content

                st.markdown("---")
                st.markdown(f"## 📋 {team_a} vs {team_b}")
                st.markdown(f"**Venue:** {venue} · **Data:** {len(selected_seasons)} seasons")
                st.markdown("---")
                st.markdown(report)
                st.markdown("---")

                with st.expander("📊 Raw Data Used"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**{team_a}**")
                        for k,v in sa.items():
                            st.write(f"{k}: {v}")
                    with c2:
                        st.markdown(f"**{team_b}**")
                        for k,v in sb.items():
                            st.write(f"{k}: {v}")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Set Groq_API_KEY in terminal: $env:Groq_API_KEY='your-key'")

# ══════════════════════════════════════════════════════════
# PAGE 6 — ASK THE DATA
# ══════════════════════════════════════════════════════════
elif page == "🔍 Ask The Data":

    st.markdown('<p class="main-header">🔍 Ask The Data</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask any cricket question in plain English</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="disclaimer">Powered by Claude AI · Answers based on historical IPL data only</p>',
                unsafe_allow_html=True)

    st.markdown("**Try these:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Who scores best in death overs?"):
            st.session_state.question = "Who scores best in death overs?"
    with col2:
        if st.button("Highest scoring venue?"):
            st.session_state.question = "Which venue has the highest scoring matches?"
    with col3:
        if st.button("Best powerplay bowler?"):
            st.session_state.question = "Who is the best bowler in the powerplay?"

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Most consistent batter?"):
            st.session_state.question = "Who is the most consistent batter in IPL history?"
    with col2:
        if st.button("Best team in powerplay?"):
            st.session_state.question = "Which team scores best in the powerplay?"
    with col3:
        if st.button("Most economical bowler?"):
            st.session_state.question = "Who is the most economical bowler in IPL history?"

    question = st.text_input(
        "Or type your own question",
        value=st.session_state.get('question',''),
        placeholder="e.g. Who performs best in finals?"
    )

    if st.button("🔍 Get Answer", type="primary") and question:
        with st.spinner("Searching 900K+ deliveries..."):

            # Pre-compute key stats for context
            death_scores = (bat.merge(
                ph[ph['phase']=='Death'][['match_id','batting_team']],
                on=['match_id','batting_team'], how='inner'
            ).groupby('batter').agg(
                avg_runs=('runs','mean'),
                total_runs=('runs','sum'),
                matches=('match_id','nunique')
            ).round(2).reset_index())
            death_scores = death_scores[
                death_scores['matches'] >= 10
            ].nlargest(5,'avg_runs')

            venue_stats = (bat.groupby('venue').agg(
                avg_score=('runs','mean'),
                matches=('match_id','nunique')
            ).round(1).reset_index().nlargest(5,'avg_score'))

            pp_bowl = (bowl.groupby('bowler').agg(
                avg_wickets=('wickets','mean'),
                economy=('economy','mean'),
                matches=('match_id','nunique')
            ).round(2).reset_index())
            pp_bowl = pp_bowl[
                pp_bowl['matches']>=10
            ].nlargest(5,'avg_wickets')

            consistency = (bat.groupby('batter').agg(
                avg=('runs','mean'),
                std=('runs','std'),
                matches=('match_id','nunique')
            ).round(2).reset_index())
            consistency = consistency[
                consistency['matches']>=20
            ]
            consistency['cv'] = (
                consistency['std']/consistency['avg']
            ).round(2)
            most_consistent = consistency.nsmallest(5,'cv')

            team_pp = (ph[ph['phase']=='Powerplay']
                       .groupby('batting_team')['run_rate']
                       .mean().round(2).reset_index()
                       .sort_values('run_rate', ascending=False))

            context = f"""You are an IPL data analyst with access to historical data.
Answer this question: {question}

Available data:

Top 5 death over batters (min 10 matches):
{death_scores.to_string(index=False)}

Top 5 highest scoring venues:
{venue_stats.to_string(index=False)}

Top 5 wicket-taking bowlers:
{pp_bowl.to_string(index=False)}

Most consistent batters (lowest coefficient of variation):
{most_consistent[['batter','avg','cv','matches']].to_string(index=False)}

Team powerplay run rates:
{team_pp.to_string(index=False)}

Overall ({len(selected_seasons)} seasons):
- Matches: {bat['match_id'].nunique():,}
- Total runs: {int(bat['runs'].sum()):,}
- Total wickets: {int(bowl['wickets'].sum()):,}

Instructions:
- Answer directly and specifically in first sentence
- Cite exact numbers from the data
- Add 2 interesting related insights
- Under 150 words
- If data doesn't cover the question, say so honestly"""

        try:
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                msg = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=512,
                    messages=[{"role":"user","content":context}]
                )
                answer = msg.choices[0].message.content   

                st.markdown("---")
                st.markdown(f"### ❓ {question}")
                st.markdown("---")
                st.success(answer)

                st.markdown("### 📊 Supporting Data")
                q = question.lower()

                if any(w in q for w in ['death','batting','score','runs','batter','consistent']):
                    fig = px.bar(
                        death_scores.sort_values('avg_runs'),
                        x='avg_runs', y='batter',
                        orientation='h',
                        title="Top Batters in Death Overs",
                        color='avg_runs',
                        color_continuous_scale='Greens',
                        text='avg_runs'
                    )
                    fig.update_layout(plot_bgcolor='white',
                                      coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ['venue','ground','stadium','pitch']):
                    fig = px.bar(
                        venue_stats.sort_values('avg_score'),
                        x='avg_score', y='venue',
                        orientation='h',
                        title="Highest Scoring Venues",
                        color='avg_score',
                        color_continuous_scale='Blues',
                        text='avg_score'
                    )
                    fig.update_layout(plot_bgcolor='white',
                                      coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ['bowl','wicket','economy','powerplay']):
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(
                            pp_bowl.sort_values('avg_wickets'),
                            x='avg_wickets', y='bowler',
                            orientation='h',
                            title="Top Wicket Takers",
                            color='avg_wickets',
                            color_continuous_scale='Oranges',
                            text='avg_wickets'
                        )
                        fig.update_layout(plot_bgcolor='white',
                                          coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        fig = px.bar(
                            team_pp,
                            x='run_rate', y='batting_team',
                            orientation='h',
                            title="Team Powerplay Run Rates",
                            color='run_rate',
                            color_continuous_scale='Blues',
                            text='run_rate'
                        )
                        fig.update_layout(plot_bgcolor='white',
                                          coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Set API key: $env:Groq_API_KEY='your-key'")
