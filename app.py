import streamlit as st
import json
import math
import pandas as pd
import altair as alt
import base64
import os

# -----------------------------------------------------------------------------
# 1. Page Configuration (Changed to WIDE layout)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="토토 분석기 AI Pro",
    page_icon="⚽",
    layout="wide", # Changed to WIDE to use side columns
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. Background Image Logic (Optional)
# -----------------------------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Check for background image
bg_file = None
if os.path.exists('background.jpg'): bg_file = 'background.jpg'
elif os.path.exists('background.png'): bg_file = 'background.png'

if bg_file:
    set_png_as_page_bg(bg_file)

# -----------------------------------------------------------------------------
# 3. Theme Management
# -----------------------------------------------------------------------------
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'

# Theme CSS
dark_css = """
<style>
    .stMarkdown, .stMarkdown p, h1, h2, h3, h4, h5, h6, span, div { color: #ecf0f1 !important; }
    
    .match-card {
        background-color: rgba(45, 45, 45, 0.95);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #444;
        color: #ecf0f1;
    }
    span.league-badge {
        background-color: #34495e !important;
        color: #ffffff !important;
        border: 1px solid #555;
    }
    .team-name { color: #ffffff !important; }
    .score-pred {
        background-color: rgba(61, 61, 61, 0.8);
        color: #ecf0f1 !important;
        border: 1px solid #555;
    }
    .streamlit-expanderHeader {
        background-color: rgba(61, 61, 61, 0.9) !important;
        color: #ecf0f1 !important;
        border: 1px solid #555;
    }
    .streamlit-expanderContent {
        background-color: rgba(45, 45, 45, 0.9) !important;
        color: #ecf0f1 !important;
        border: 1px solid #555;
        border-top: none;
    }
    div[data-testid="stPills"] button {
        background-color: rgba(45, 45, 45, 0.8) !important;
        color: #ecf0f1 !important;
        border: 1px solid #555 !important;
    }
    div[data-testid="stPills"] button[aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
        border: 1px solid #3498db !important;
    }
    
    /* Photo styling */
    .side-photo {
        width: 100%;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        border: 2px solid #555;
        transition: transform 0.3s ease;
    }
    .side-photo:hover {
        transform: scale(1.02);
    }
</style>
"""

light_css = """
<style>
    .stMarkdown, .stMarkdown p, h1, h2, h3, h4, h5, h6 { color: #2c3e50 !important; }
    
    .match-card {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        color: #2c3e50;
    }
    span.league-badge {
        background-color: #2c3e50 !important;
        color: #ffffff !important;
        border: 1px solid #2c3e50;
    }
    .team-name { color: #2c3e50 !important; }
    .score-pred {
        background-color: rgba(241, 243, 245, 0.8);
        color: #495057 !important;
    }
    .streamlit-expanderHeader {
        background-color: rgba(233, 236, 239, 0.9) !important;
        color: #2c3e50 !important;
        border: 1px solid #dee2e6;
    }
    .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #2c3e50 !important;
        border: 1px solid #dee2e6;
        border-top: none;
    }
    div[data-testid="stPills"] button {
        background-color: rgba(255, 255, 255, 0.8) !important;
        color: #2c3e50 !important;
        border: 1px solid #ddd !important;
    }
    div[data-testid="stPills"] button[aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
        border: 1px solid #3498db !important;
    }
    
    .side-photo {
        width: 100%;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 4px solid white;
    }
</style>
"""

common_css = """
<style>
    span.league-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .team-name {
        font-size: 1.3rem; 
        font-weight: 800; 
        margin-bottom: 5px;
    }
    .score-pred {
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
        font-size: 1.1rem;
    }
    div.rec-badge {
        padding: 8px 12px;
        border-radius: 6px;
        color: #ffffff !important; 
        font-weight: bold;
        text-align: center;
        display: block;
        margin-top: 10px;
        font-size: 0.95rem;
    }
    .rec-home { background-color: #e74c3c; }
    .rec-away { background-color: #3498db; }
    .rec-draw { background-color: #95a5a6; }
    .stButton button { border-color: #555; color: white; }
</style>
"""

st.markdown(common_css, unsafe_allow_html=True)
if not bg_file:
    if st.session_state.theme == 'dark':
        st.markdown("""<style>[data-testid="stAppViewContainer"] { background-color: #1e1e1e; }</style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>[data-testid="stAppViewContainer"] { background-color: #f8f9fa; }</style>""", unsafe_allow_html=True)

if st.session_state.theme == 'dark':
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    st.markdown(light_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Prediction Logic (Hidden for brevity, same as before)
# -----------------------------------------------------------------------------
def predict_match(match):
    # (Same logic...)
    home_name = match['home_team']
    away_name = match['away_team']
    is_volleyball = "V-리그" in match['league']
    
    avg_pts = 35 
    h_pts = match['home_stats']['points']
    a_pts = match['away_stats']['points']
    h_gd = match['home_stats']['goals_for'] - match['home_stats']['goals_against']
    a_gd = match['away_stats']['goals_for'] - match['away_stats']['goals_against']
    
    rating_home = 1500 + (h_pts - avg_pts) * 10 + (h_gd * 4) + 100
    rating_away = 1500 + (a_pts - avg_pts) * 10 + (a_gd * 4)
    
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
        score_h = (home_attack / lg_avg) * (away_defense / lg_avg) * lg_avg * 1.15
        score_a = (away_attack / lg_avg) * (home_defense / lg_avg) * lg_avg 
    
    return {
        "home_win": final_home_win, "draw": prob_draw, "away_win": final_away_win,
        "score_h": score_h, "score_a": score_a, "is_volleyball": is_volleyball
    }

@st.cache_data
def load_data():
    try:
        with open('data/weekly_fixtures.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

fixtures = load_data()

# -----------------------------------------------------------------------------
# 5. Main Layout (3 Columns)
# -----------------------------------------------------------------------------
# Create 3 columns: Left (Photos), Center (Content), Right (Photos)
# Ratio: 1 : 3 : 1 (Center is 3x wider)
left_col, center_col, right_col = st.columns([1, 2.5, 1])

# --- Left Column Photos ---
with left_col:
    st.write("") # Spacer
    st.write("") 
    # Photos only

    
    if os.path.exists("photo1.jpg"):
        st.image("photo1.jpg", caption="Photo 1", use_container_width=True)
    elif os.path.exists("photo1.png"):
        st.image("photo1.png", caption="Photo 1", use_container_width=True)
    else:
        st.info("왼쪽 사진 1 (photo1.jpg) 없음")
        
    st.write("---")
    
    if os.path.exists("photo2.jpg"):
        st.image("photo2.jpg", caption="Photo 2", use_container_width=True)
    elif os.path.exists("photo2.png"):
        st.image("photo2.png", caption="Photo 2", use_container_width=True)
    else:
        st.info("왼쪽 사진 2 (photo2.jpg) 없음")

# --- Right Column Photos ---
with right_col:
    st.write("") # Spacer
    st.write("") 
    # Photos only

    
    if os.path.exists("photo3.jpg"):
        st.image("photo3.jpg", caption="Photo 3", use_container_width=True)
    elif os.path.exists("photo3.png"):
        st.image("photo3.png", caption="Photo 3", use_container_width=True)
    else:
        st.info("오른쪽 사진 1 (photo3.jpg) 없음")
        
    st.write("---")
    
    if os.path.exists("photo4.jpg"):
        st.image("photo4.jpg", caption="Photo 4", use_container_width=True)
    elif os.path.exists("photo4.png"):
        st.image("photo4.png", caption="Photo 4", use_container_width=True)
    else:
        st.info("오른쪽 사진 2 (photo4.jpg) 없음")

# --- Center Column Content (Main App) ---
with center_col:
    # Header Layout
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.title("🏆 토토 분석기 AI Pro")
        st.markdown("##### ⚡ 데이터 기반 승부 예측 리포트")
    with h_col2:
        if st.session_state.theme == 'dark':
            if st.button("🌞 라이트"):
                toggle_theme()
                st.rerun()
        else:
            if st.button("🌙 다크"):
                toggle_theme()
                st.rerun()

    leagues = sorted(list(set([m['league'] for m in fixtures])))
    selected_league = st.pills("리그 필터", ["전체"] + leagues, selection_mode="single", default="전체")

    matches_to_show = fixtures if selected_league == "전체" else [m for m in fixtures if m['league'] == selected_league]

    for m in matches_to_show:
        pred = predict_match(m)
        h_prob, d_prob, a_prob = pred['home_win']*100, pred['draw']*100, pred['away_win']*100
        
        rec_text = "박빙 / 무승부 예상"
        rec_class = "rec-draw"
        
        if h_prob > 60:
            rec_text = f"🔥 {m['home_team']} 승리 유력"
            rec_class = "rec-home"
        elif a_prob > 60:
            rec_text = f"🔥 {m['away_team']} 승리 유력"
            rec_class = "rec-away"
        elif h_prob > 45:
            rec_text = f"{m['home_team']} 우세"
            rec_class = "rec-home"
        elif a_prob > 45:
            rec_text = f"{m['away_team']} 우세"
            rec_class = "rec-away"

        if pred['is_volleyball']:
            score_str = f"예상 세트 {int(pred['score_h'])} : {int(pred['score_a'])}"
        else:
            score_str = f"예상 스코어 {int(pred['score_h']+0.4)} - {int(pred['score_a']+0.4)}"

        # Match Card
        card_html = f"""
    <div class="match-card">
        <span class="league-badge">{m['league']} | {m['date']} {m['time']}</span>
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 15px 0;">
            <div style="text-align: center; width: 40%;">
                <div class="team-name">{m['home_team']}</div>
            </div>
            <div style="text-align: center; color: #aaa; font-weight: bold;">VS</div>
            <div style="text-align: center; width: 40%;">
                <div class="team-name">{m['away_team']}</div>
            </div>
        </div>
        <div class="score-pred">{score_str}</div>
        <div class="{rec_class} rec-badge">{rec_text}</div>
    </div>
    """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Progress Bar
        progress_html = f"""
    <div style="display: flex; height: 12px; border-radius: 6px; overflow: hidden; margin-top: 5px; margin-bottom: 5px;">
        <div style="width: {h_prob}%; background-color: #e74c3c;"></div>
        <div style="width: {d_prob}%; background-color: #95a5a6;"></div>
        <div style="width: {a_prob}%; background-color: #3498db;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #888; margin-bottom: 15px;">
        <span>홈 {h_prob:.0f}%</span>
        <span>무 {d_prob:.0f}%</span>
        <span>원정 {a_prob:.0f}%</span>
    </div>
    """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Detailed Factors
        factors = m.get('key_factors', [])
        if factors:
             with st.expander("🧐 분석 근거 & 핵심 포인트 보기", expanded=False):
                st.markdown(f"**💡 {m.get('analysis_note', '')}**")
                st.markdown("---")
                for factor in factors:
                    st.markdown(f"- {factor}")
                
                # st.caption(f"최근 5경기 폼: 홈({m['home_stats']['recent_form']}) vs 원정({m['away_stats']['recent_form']})")
        else:
             with st.expander("📊 상세 분석 보기", expanded=False):
                st.write(m.get('analysis_note', '데이터 분석 중...'))
                
        st.write("") 

    st.markdown("---")
    st.caption("Produced by Toto Analyzer AI")
