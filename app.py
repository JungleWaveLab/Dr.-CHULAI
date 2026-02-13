import streamlit as st
import json
import math
import os
import sys

# Page Config
st.set_page_config(
    page_title="토토 분석기 AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .big-font { font-size: 24px !important; font-weight: bold; }
    .vs-badge { background-color: #f0f2f6; padding: 5px 10px; border-radius: 10px; font-weight: bold; color: #555; }
    .rec-card { padding: 10px; border-radius: 5px; color: white; text-align: center; font-weight: bold; }
    .rec-home { background-color: #e74c3c; }
    .rec-away { background-color: #3498db; }
    .rec-draw { background-color: #95a5a6; }
    .analysis-box { background-color: #fef9e7; padding: 15px; border-radius: 5px; border-left: 5px solid #f1c40f; margin-top: 10px; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #e74c3c, #95a5a6, #3498db); }
</style>
""", unsafe_allow_html=True)

# Prediction Logic (Same as before)
def predict_match(match):
    home_name = match['home_team']
    away_name = match['away_team']
    is_volleyball = "V-리그" in match['league']
    
    avg_pts = 35 
    h_pts = match['home_stats']['points']
    a_pts = match['away_stats']['points']
    h_gd = match['home_stats']['goals_for'] - match['home_stats']['goals_against']
    a_gd = match['away_stats']['goals_for'] - match['away_stats']['goals_against']
    
    rating_home = 1500 + (h_pts - avg_pts) * 10 + (h_gd * 4)
    rating_away = 1500 + (a_pts - avg_pts) * 10 + (a_gd * 4)
    rating_home += 100 
    
    def calc_form(form_str):
        score = 0
        for char in form_str:
             if char == 'W': score += 15
             elif char == 'D': score += 5
             elif char == 'L': score -= 10
        return score

    rating_home += calc_form(match['home_stats'].get('recent_form', ''))
    rating_away += calc_form(match['away_stats'].get('recent_form', ''))
    
    h2h = match.get('h2h_last_5', [])
    for res in h2h:
        if "Home Win" in res or home_name in res: rating_home += 20
        elif "Away Win" in res or away_name in res: rating_away += 20
             
    prob_home_win = 1 / (1 + math.pow(10, (rating_away - rating_home) / 400))
    rating_diff = abs(rating_home - rating_away)
    
    prob_draw = 0.28 * math.exp(-rating_diff / 500)
    if is_volleyball: prob_draw = 0
    
    final_home_win = prob_home_win - 0.5 * prob_draw
    final_away_win = (1 - prob_home_win) - 0.5 * prob_draw
    
    if final_home_win < 0.01: final_home_win = 0.01
    if final_away_win < 0.01: final_away_win = 0.01
    
    total = final_home_win + prob_draw + final_away_win
    final_home_win /= total
    prob_draw /= total
    final_away_win /= total

    # Score Prediction
    if is_volleyball:
        if final_home_win > 0.8: score_h, score_a = 3, 0
        elif final_home_win > 0.6: score_h, score_a = 3, 1
        elif final_home_win > 0.5: score_h, score_a = 3, 2
        elif final_away_win > 0.8: score_h, score_a = 0, 3
        elif final_away_win > 0.6: score_h, score_a = 1, 3
        else: score_h, score_a = 2, 3
    else:
        home_attack = match['home_stats']['goals_for'] / match['home_stats']['played']
        away_defense = match['away_stats']['goals_against'] / match['away_stats']['played'] 
        if match['away_stats']['played'] == 0: away_defense = 1 
        
        away_attack = match['away_stats']['goals_for'] / match['away_stats']['played']
        home_defense = match['home_stats']['goals_against'] / match['home_stats']['played']
        lg_avg = 1.4
        
        exp_h_goals = (home_attack / lg_avg) * (away_defense / lg_avg) * lg_avg * 1.15
        exp_a_goals = (away_attack / lg_avg) * (home_defense / lg_avg) * lg_avg 
        score_h, score_a = exp_h_goals, exp_a_goals
    
    return {
        "home_win": final_home_win,
        "draw": prob_draw,
        "away_win": final_away_win,
        "score_h": score_h,
        "score_a": score_a,
        "is_volleyball": is_volleyball
    }

# Load Data
@st.cache_data
def load_data():
    try:
        with open('data/weekly_fixtures.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

fixtures = load_data()

# Header
st.title("⚽ 토토 분석기 AI (주간 리포트)")
st.caption("2026년 2월 2주차 빅매치 심층 분석")

# Sidebar Filters
st.sidebar.header("🔍 필터 옵션")
all_leagues = sorted(list(set([m['league'] for m in fixtures])))
selected_leagues = st.sidebar.multiselect("리그 선택", all_leagues, default=all_leagues)

st.sidebar.markdown("---")
st.sidebar.info("이 분석기는 Elo Rating과 Poisson 분포 모델을 기반으로 승률을 계산합니다.")

# Main Content
if not fixtures:
    st.error("데이터 파일을 찾을 수 없습니다.")
else:
    # Filter matches
    matches_to_show = [m for m in fixtures if m['league'] in selected_leagues]
    
    # Group by League
    grouped = {}
    for m in matches_to_show:
        l = m['league']
        if l not in grouped: grouped[l] = []
        grouped[l].append(m)
        
    for league, matches in grouped.items():
        st.subheader(f"🏆 {league}")
        
        for m in matches:
            with st.container():
                pred = predict_match(m)
                
                # Recommendation Logic
                h_prob = pred['home_win'] * 100
                d_prob = pred['draw'] * 100
                a_prob = pred['away_win'] * 100
                
                rec_text = "박빙/무승부"
                rec_bg = "rec-draw"
                if h_prob > 60:
                    rec_text = f"{m['home_team']} 승리 유력"
                    rec_bg = "rec-home"
                elif a_prob > 60:
                    rec_text = f"{m['away_team']} 승리 유력"
                    rec_bg = "rec-away"
                elif h_prob > 45:
                    rec_text = f"{m['home_team']} 우세"
                    rec_bg = "rec-home"
                elif a_prob > 45:
                    rec_text = f"{m['away_team']} 우세"
                    rec_bg = "rec-away"

                # Layout
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"**{m['date']} {m['time']}**")
                    st.markdown(f"### {m['home_team']}")
                    st.markdown(f"<div class='vs-badge' style='text-align:center'>VS</div>", unsafe_allow_html=True)
                    st.markdown(f"### {m['away_team']}")
                    
                    if pred['is_volleyball']:
                         st.markdown(f"**예상 스코어: {int(pred['score_h'])} : {int(pred['score_a'])}**")
                    else:
                         st.markdown(f"**예상 스코어: {int(pred['score_h']+0.4)} - {int(pred['score_a']+0.4)}**")

                with col2:
                    # Probability Bar using Progress Bar (Hack for single color, but we use metrics)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("홈 승", f"{h_prob:.1f}%")
                    c2.metric("무승부", f"{d_prob:.1f}%")
                    c3.metric("원정 승", f"{a_prob:.1f}%")
                    
                    st.markdown(f"#### 추천: <span class='rec-card {rec_bg}'>{rec_text}</span>", unsafe_allow_html=True)
                    
                    with st.expander("💡 상세 분석 코멘트 보기", expanded=True):
                        st.markdown(f"{m.get('analysis_note', '데이터 분석 중')}")
                        st.caption(f"최근 5경기: 홈({m['home_stats']['recent_form']}) vs 원정({m['away_stats']['recent_form']})")
                
                st.divider()

# Footer
st.markdown("---")
st.markdown("Developed by Toto Analyzer AI | Data source: Web Search & Simulation")
