import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #0F6E56;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .insight-box {
        background: #E8F5E9;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #1D9E75;
        margin: 1rem 0;
    }
    .warning-box {
        background: #FFF3E0;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #EF9F27;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    base = r'C:\23261A6720\SPORTS_ANALYSER\data\processed' + '\\'
    batter  = pd.read_csv(base + 'fact_batter_stats.csv')
    bowler  = pd.read_csv(base + 'fact_bowler_stats.csv')
    player  = pd.read_csv(base + 'dim_player.csv')
    matches = pd.read_csv(base + 'dim_match.csv')
    team    = pd.read_csv(base + 'dim_team.csv')
    phase   = pd.read_csv(base + 'fact_team_phase_stats.csv')
    return batter, bowler, player, matches, team, phase

batter, bowler, player, matches, team, phase = load_data()

# ── SIDEBAR ───────────────────────────────────────────────
st.sidebar.markdown("## 🏏 IPL Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home",
     "⚔️ Player Comparison",
     "📊 Phase Intelligence",
     "🏆 Career Rankings"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Data:** IPL 2007–2024")
st.sidebar.markdown("**Matches:** 1,090")
st.sidebar.markdown("**Players:** 731")

# ══════════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<p class="main-header">🏏 IPL Sports Intelligence Platform</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data-driven cricket analysis · IPL 2007–2024 · 900K+ deliveries</p>',
                unsafe_allow_html=True)

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", "1,090")
    with col2:
        st.metric("Total Players", "731")
    with col3:
        total_runs = int(batter['runs'].sum())
        st.metric("Total Runs Scored", f"{total_runs:,}")
    with col4:
        total_wkts = int(bowler['wickets'].sum())
        st.metric("Total Wickets", f"{total_wkts:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Run Scoring Trend by Season")
        season_runs = batter.groupby('season')['runs'].sum().reset_index()
        season_runs = season_runs.sort_values('season')
        fig = px.line(
            season_runs, x='season', y='runs',
            markers=True,
            color_discrete_sequence=['#0F6E56']
        )
        fig.update_layout(
            xaxis_title="Season",
            yaxis_title="Total Runs",
            plot_bgcolor='white',
            height=350
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏏 Top 10 Run Scorers — All Time")
        top_batters = (batter.groupby('batter')['runs']
                       .sum()
                       .nlargest(10)
                       .reset_index()
                       .sort_values('runs'))
        fig = px.bar(
            top_batters, x='runs', y='batter',
            orientation='h',
            color='runs',
            color_continuous_scale='Greens',
            text='runs'
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(
            xaxis_title="Total Runs",
            yaxis_title="",
            plot_bgcolor='white',
            height=350,
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Top 10 Wicket Takers — All Time")
        top_bowlers = (bowler.groupby('bowler')['wickets']
                       .sum()
                       .nlargest(10)
                       .reset_index()
                       .sort_values('wickets'))
        fig = px.bar(
            top_bowlers, x='wickets', y='bowler',
            orientation='h',
            color='wickets',
            color_continuous_scale='Oranges',
            text='wickets'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            xaxis_title="Total Wickets",
            yaxis_title="",
            plot_bgcolor='white',
            height=350,
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏟️ Highest Scoring Venues")
        venue_runs = (batter.groupby('venue')['runs']
                      .mean()
                      .nlargest(10)
                      .reset_index()
                      .sort_values('runs'))
        venue_runs.columns = ['venue', 'avg_runs']
        # Shorten venue names
        venue_runs['venue'] = venue_runs['venue'].str[:25]
        fig = px.bar(
            venue_runs, x='avg_runs', y='venue',
            orientation='h',
            color='avg_runs',
            color_continuous_scale='Blues',
            text='avg_runs'
        )
        fig.update_traces(
            texttemplate='%{text:.0f}',
            textposition='outside'
        )
        fig.update_layout(
            xaxis_title="Avg Runs per Match",
            yaxis_title="",
            plot_bgcolor='white',
            height=350,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — PLAYER COMPARISON
# ══════════════════════════════════════════════════════════
elif page == "⚔️ Player Comparison":
    st.markdown('<p class="main-header">⚔️ Player Comparison Engine</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Compare any two players across 10 dimensions</p>',
                unsafe_allow_html=True)

    # Player selector
    all_batters = sorted(batter['batter'].unique())
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("Select Player 1",
                          all_batters,
                          index=all_batters.index('V Kohli')
                          if 'V Kohli' in all_batters else 0)
    with col2:
        p2 = st.selectbox("Select Player 2",
                          all_batters,
                          index=all_batters.index('RG Sharma')
                          if 'RG Sharma' in all_batters else 1)

    if p1 == p2:
        st.warning("Please select two different players.")
        st.stop()

    # Get stats for both players
    def get_player_stats(name):
        df = batter[batter['batter'] == name]
        return {
            'matches'      : df['match_id'].nunique(),
            'total_runs'   : int(df['runs'].sum()),
            'avg_runs'     : round(df['runs'].mean(), 1),
            'strike_rate'  : round(df['strike_rate'].mean(), 1),
            'fifties'      : int(df['is_fifty'].sum()),
            'hundreds'     : int(df['is_hundred'].sum()),
            'avg_fantasy'  : round(df['fantasy_pts'].mean(), 1),
            'form_score'   : round(df['form_score'].iloc[-1], 1),
            'best_score'   : int(df['runs'].max()),
            'fours'        : int(df['fours'].sum()),
            'sixes'        : int(df['sixes'].sum()),
        }

    s1 = get_player_stats(p1)
    s2 = get_player_stats(p2)

    # Metric comparison row
    st.markdown("---")
    metrics = ['matches','total_runs','avg_runs','strike_rate',
               'fifties','hundreds','avg_fantasy','best_score']
    labels  = ['Matches','Total Runs','Avg Runs','Strike Rate',
               'Fifties','Hundreds','Avg Fantasy Pts','Best Score']

    cols = st.columns(4)
    for i, (metric, label) in enumerate(zip(metrics, labels)):
        with cols[i % 4]:
            v1, v2 = s1[metric], s2[metric]
            delta = round(v1 - v2, 1)
            winner = p1 if v1 > v2 else p2
            color = "normal" if v1 == v2 else "normal"
            st.metric(
                label=f"{label}",
                value=f"{p1}: {v1}",
                delta=f"vs {p2}: {v2}"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🕸️ Head to Head Radar")
        # Normalize for radar
        categories = ['Avg Runs','Strike Rate','Fifties',
                      'Hundreds','Avg Fantasy','Form Score']

        def normalize(val, min_val, max_val):
            if max_val == min_val:
                return 50
            return round((val - min_val) / (max_val - min_val) * 100, 1)

        ranges = {
            'avg_runs'    : (0, 60),
            'strike_rate' : (80, 180),
            'fifties'     : (0, 80),
            'hundreds'    : (0, 20),
            'avg_fantasy' : (0, 60),
            'form_score'  : (0, 80),
        }
        keys = list(ranges.keys())

        v1_norm = [normalize(s1[k], *ranges[k]) for k in keys]
        v2_norm = [normalize(s2[k], *ranges[k]) for k in keys]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=v1_norm + [v1_norm[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=p1,
            line_color='#0F6E56',
            fillcolor='rgba(15,110,86,0.2)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=v2_norm + [v2_norm[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=p2,
            line_color='#E84393',
            fillcolor='rgba(232,67,147,0.2)'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            showlegend=True,
            height=400,
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Season-wise Run Comparison")
        p1_season = (batter[batter['batter']==p1]
                     .groupby('season')['runs'].sum().reset_index())
        p2_season = (batter[batter['batter']==p2]
                     .groupby('season')['runs'].sum().reset_index())

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=p1_season['season'], y=p1_season['runs'],
            mode='lines+markers', name=p1,
            line=dict(color='#0F6E56', width=2),
            marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=p2_season['season'], y=p2_season['runs'],
            mode='lines+markers', name=p2,
            line=dict(color='#E84393', width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(
            xaxis_title="Season",
            yaxis_title="Total Runs",
            plot_bgcolor='white',
            height=400,
            legend=dict(orientation="h", y=-0.2)
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # Auto-generated insight
    st.markdown("---")
    st.subheader("🔍 Data Insight")

    better_avg    = p1 if s1['avg_runs'] > s2['avg_runs'] else p2
    better_sr     = p1 if s1['strike_rate'] > s2['strike_rate'] else p2
    better_consis = p1 if s1['fifties'] > s2['fifties'] else p2
    better_form   = p1 if s1['form_score'] > s2['form_score'] else p2

    st.markdown(f"""
    <div class="insight-box">
    <b>📊 Auto Analysis: {p1} vs {p2}</b><br><br>
    • <b>{better_avg}</b> has the higher batting average
      ({s1['avg_runs']} vs {s2['avg_runs']})<br>
    • <b>{better_sr}</b> scores faster
      (SR: {s1['strike_rate']} vs {s2['strike_rate']})<br>
    • <b>{better_consis}</b> is more consistent
      ({s1['fifties']} fifties vs {s2['fifties']})<br>
    • <b>{better_form}</b> is in better current form
      (Form score: {s1['form_score']} vs {s2['form_score']})
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — PHASE INTELLIGENCE
# ══════════════════════════════════════════════════════════
elif page == "📊 Phase Intelligence":
    st.markdown('<p class="main-header">📊 Phase Intelligence</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyse team strengths and weaknesses by match phase</p>',
                unsafe_allow_html=True)

    selected_team = st.selectbox(
        "Select Opposition Team to Analyse",
        sorted(phase['batting_team'].unique())
    )

    team_data = phase[phase['batting_team'] == selected_team]

    col1, col2, col3 = st.columns(3)
    for col, ph, color in zip(
        [col1, col2, col3],
        ['Powerplay', 'Middle', 'Death'],
        ['#0F6E56', '#185FA5', '#E84393']
    ):
        ph_data = team_data[team_data['phase'] == ph]
        avg_rr = round(ph_data['run_rate'].mean(), 2)
        avg_runs = round(ph_data['runs'].mean(), 1)
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color:{color}">{ph}</h4>
                <h2 style="color:{color}">{avg_rr}</h2>
                <p style="color:#666">Avg Run Rate</p>
                <p style="color:#999">{avg_runs} avg runs/match</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📈 {selected_team} — Run Rate by Phase over Seasons")
        phase_season = (team_data.groupby(['season','phase'])
                        ['run_rate'].mean().reset_index())
        fig = px.line(
            phase_season, x='season', y='run_rate',
            color='phase',
            markers=True,
            color_discrete_map={
                'Powerplay': '#0F6E56',
                'Middle'   : '#185FA5',
                'Death'    : '#E84393'
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
        pivot = (phase.groupby(['batting_team','phase'])
                 ['run_rate'].mean()
                 .unstack()
                 [['Powerplay','Middle','Death']]
                 .round(2))
        fig = px.imshow(
            pivot,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            text_auto=True
        )
        fig.update_layout(
            height=400,
            xaxis_title="Phase",
            yaxis_title="Team"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Insight
    weak_phase = team_data.groupby('phase')['run_rate'].mean().idxmin()
    strong_phase = team_data.groupby('phase')['run_rate'].mean().idxmax()

    st.markdown(f"""
    <div class="insight-box">
    <b>💡 Scout Report: {selected_team}</b><br><br>
    • Their <b>weakest phase is {weak_phase}</b> —
      bowl your best bowlers here<br>
    • Their <b>strongest phase is {strong_phase}</b> —
      expect aggressive batting<br>
    • Target their {weak_phase} with your most economical bowler
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 4 — CAREER RANKINGS
# ══════════════════════════════════════════════════════════
elif page == "🏆 Career Rankings":
    st.markdown('<p class="main-header">🏆 Career Rankings</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">All-time IPL player rankings across key metrics</p>',
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏏 Batting Rankings", "🎯 Bowling Rankings"])

    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
            min_matches = st.slider("Min Matches Played", 5, 50, 10)
            metric = st.selectbox(
                "Rank by",
                ['total_runs','avg_runs','strike_rate',
                 'fifties','hundreds','avg_fantasy']
            )

        bat_career = (batter.groupby('batter').agg(
            total_runs   =('runs','sum'),
            avg_runs     =('runs','mean'),
            strike_rate  =('strike_rate','mean'),
            fifties      =('is_fifty','sum'),
            hundreds     =('is_hundred','sum'),
            avg_fantasy  =('fantasy_pts','mean'),
            matches      =('match_id','nunique'),
        ).round(2).reset_index())

        bat_career = bat_career[bat_career['matches'] >= min_matches]
        bat_career = bat_career.nlargest(20, metric)
        bat_career['rank'] = range(1, len(bat_career)+1)

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
            fig.update_traces(
                texttemplate='%{text:.1f}',
                textposition='outside'
            )
            fig.update_layout(
                height=550,
                plot_bgcolor='white',
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title=metric.replace('_',' ').title()
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns([1, 3])
        with col1:
            min_matches_b = st.slider("Min Matches", 5, 50, 10)
            bowl_metric = st.selectbox(
                "Rank by",
                ['total_wickets','avg_economy',
                 'avg_fantasy','matches']
            )

        bowl_career = (bowler.groupby('bowler').agg(
            total_wickets =('wickets','sum'),
            avg_economy   =('economy','mean'),
            avg_fantasy   =('fantasy_pts','mean'),
            matches       =('match_id','nunique'),
        ).round(2).reset_index())

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
            fig.update_traces(
                texttemplate='%{text:.1f}',
                textposition='outside'
            )
            fig.update_layout(
                height=550,
                plot_bgcolor='white',
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title=bowl_metric.replace('_',' ').title()
            )
            st.plotly_chart(fig, use_container_width=True)