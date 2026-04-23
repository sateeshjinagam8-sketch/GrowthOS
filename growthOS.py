import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random
import requests
import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

# Get API key - works both locally and 
# on Streamlit Cloud
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ─────────────────────────────────────────────
# Data Directory & File Paths
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
HABITS_FILE = os.path.join(DATA_DIR, "habits.json")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
MOODS_FILE = os.path.join(DATA_DIR, "moods.json")
CHATS_FILE = os.path.join(DATA_DIR, "ai_chats.json")
GAMIFICATION_FILE = os.path.join(DATA_DIR, "gamification.json")


# ─────────────────────────────────────────────
# JSON Helpers
# ─────────────────────────────────────────────
def load_json(filepath, default=None):
    if default is None:
        default = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
# Gamification Helpers
# ─────────────────────────────────────────────
def get_gamification():
    default_state = {"total_xp": 0, "history": [], "badges": []}
    return load_json(GAMIFICATION_FILE, default_state)

def save_gamification(state):
    save_json(GAMIFICATION_FILE, state)

def add_xp(amount, reason):
    state = get_gamification()
    today = datetime.now().strftime("%Y-%m-%d")
    state["total_xp"] += amount
    state["history"].append({"date": today, "amount": amount, "reason": reason})
    save_gamification(state)
    return state

def get_level_info(xp):
    if xp <= 100:
        return 1, "Beginner 🌱", 100
    elif xp <= 300:
        return 2, "Explorer 🚀", 300
    elif xp <= 600:
        return 3, "Achiever ⚡", 600
    elif xp <= 1000:
        return 4, "Champion 🏆", 1000
    else:
        return 5, "Legend 🔥", xp + 1

def check_and_award_badges():
    state = get_gamification()
    awarded = set(state.get("badges", []))
    new_badges = []
    
    habits = load_json(HABITS_FILE, [])
    skills = load_json(SKILLS_FILE, [])
    moods = load_json(MOODS_FILE, [])
    chats = load_json(CHATS_FILE, [])
    
    if "Streak Master" not in awarded:
        for h in habits:
            streak = 0
            day = datetime.now()
            comps = set(h.get("completions", []))
            while day.strftime("%Y-%m-%d") in comps:
                streak += 1
                day -= timedelta(days=1)
            if streak >= 7:
                new_badges.append("Streak Master")
                break
                
    if "Skill Collector" not in awarded and len(skills) >= 5:
        new_badges.append("Skill Collector")
        
    if "Mind Guardian" not in awarded and len(moods) >= 7:
        new_badges.append("Mind Guardian")
        
    if "Consistency King" not in awarded:
        total_comps = sum(len(h.get("completions", [])) for h in habits)
        if total_comps >= 30:
            new_badges.append("Consistency King")
            
    if "AI Explorer" not in awarded:
        total_msgs = sum(sum(1 for m in c.get("messages", []) if m["role"] == "user") for c in chats)
        if total_msgs >= 10:
            new_badges.append("AI Explorer")
            
    if new_badges:
        state["badges"].extend(new_badges)
        save_gamification(state)
        for b in new_badges:
            st.toast(f"🏆 New Badge Unlocked: {b}!")


# ─────────────────────────────────────────────
# Page Config & Custom CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GrowthOS",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #e0e0ff !important;
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
    }
    .metric-card h2 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
    }
    .metric-card p {
        margin: 4px 0 0 0;
        font-size: 0.95rem;
        opacity: 0.85;
    }

    .metric-card.green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 8px 32px rgba(17, 153, 142, 0.3);
    }
    .metric-card.orange {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        box-shadow: 0 8px 32px rgba(247, 151, 30, 0.3);
    }
    .metric-card.pink {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        box-shadow: 0 8px 32px rgba(238, 9, 121, 0.3);
    }

    /* Habit item */
    .habit-row {
        background: #1e1e2f;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
    }
    .habit-row:hover {
        background: #2a2a40;
        border-left-color: #38ef7d;
    }
    .habit-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: #e0e0ff;
    }
    .streak-badge {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: #1e1e2f;
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 8px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Quote card */
    .quote-card {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 100%);
        border-radius: 16px;
        padding: 28px 32px;
        color: #e0e0ff;
        font-size: 1.15rem;
        font-style: italic;
        line-height: 1.7;
        border-left: 4px solid #667eea;
        box-shadow: 0 8px 32px rgba(48, 43, 99, 0.4);
        margin: 12px 0;
    }

    /* Divider */
    .glow-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
        border: none;
        margin: 24px 0;
        border-radius: 2px;
    }

    /* Profile card */
    .profile-card {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 20px;
        padding: 36px 32px;
        color: #e0e0ff;
        text-align: center;
        box-shadow: 0 12px 40px rgba(48, 43, 99, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.25);
        margin-bottom: 20px;
    }
    .profile-card .avatar {
        font-size: 4.5rem;
        margin-bottom: 8px;
    }
    .profile-card .name {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 4px 0;
    }
    .profile-card .detail {
        font-size: 0.92rem;
        opacity: 0.8;
        margin: 3px 0;
    }
    .profile-card .motto {
        font-style: italic;
        margin-top: 14px;
        padding-top: 14px;
        border-top: 1px solid rgba(102, 126, 234, 0.2);
        font-size: 1rem;
        opacity: 0.9;
    }

    /* Avatar selector grid */
    .avatar-btn {
        font-size: 2.2rem;
        cursor: pointer;
        padding: 10px;
        border-radius: 14px;
        border: 2px solid transparent;
        background: rgba(102, 126, 234, 0.08);
        transition: all 0.2s ease;
        text-align: center;
    }
    .avatar-btn:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: scale(1.1);
    }
    .avatar-btn.selected {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.2);
        box-shadow: 0 0 16px rgba(102, 126, 234, 0.35);
    }

    /* ── Claude-style Chat UI ── */
    .claude-chat-container {
        display: flex;
        flex-direction: column;
        height: 65vh;
        overflow-y: auto;
        padding: 20px 8px;
        scroll-behavior: smooth;
        scrollbar-width: thin;
        scrollbar-color: rgba(102,126,234,0.3) transparent;
    }
    .claude-chat-container::-webkit-scrollbar { width: 6px; }
    .claude-chat-container::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.3); border-radius: 3px; }

    .claude-msg { max-width: 720px; width: 100%; margin: 0 auto; padding: 0 16px; }

    .claude-msg-user {
        padding: 20px 0;
        border-bottom: 1px solid rgba(102,126,234,0.1);
    }
    .claude-msg-user .claude-msg-inner {
        display: flex; align-items: flex-start; gap: 14px;
    }
    .claude-msg-user .claude-avatar {
        width: 32px; height: 32px; border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem; flex-shrink: 0; color: white; font-weight: 700;
    }
    .claude-msg-user .claude-text {
        color: #e0e0ff; font-size: 0.95rem; line-height: 1.65;
        padding-top: 4px; white-space: pre-wrap;
    }

    .claude-msg-ai {
        padding: 24px 0;
        background: rgba(102,126,234,0.04);
        border-bottom: 1px solid rgba(102,126,234,0.08);
    }
    .claude-msg-ai .claude-msg-inner {
        display: flex; align-items: flex-start; gap: 14px;
    }
    .claude-msg-ai .claude-avatar {
        width: 32px; height: 32px; border-radius: 10px;
        background: linear-gradient(135deg, #38ef7d, #11998e);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem; flex-shrink: 0;
    }
    .claude-msg-ai .claude-text {
        color: #e0e0ff; font-size: 0.95rem; line-height: 1.75;
        padding-top: 4px; white-space: pre-wrap;
    }

    .claude-welcome {
        text-align: center; padding: 80px 20px; color: #8888aa;
    }
    .claude-welcome h2 {
        font-size: 1.8rem; font-weight: 700; margin-bottom: 8px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .claude-welcome p { font-size: 1rem; opacity: 0.7; }

    .claude-quick-btn {
        background: rgba(102,126,234,0.1); border: 1px solid rgba(102,126,234,0.2);
        border-radius: 12px; padding: 12px 18px; color: #c0c0dd;
        font-size: 0.88rem; cursor: pointer; transition: all 0.2s;
        text-align: left;
    }
    .claude-quick-btn:hover {
        background: rgba(102,126,234,0.2); border-color: #667eea;
        color: #e0e0ff; transform: translateY(-2px);
    }

    .ai-status-badge {
        display: inline-block; padding: 5px 14px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600;
    }
    .ai-status-badge.ollama {
        background: linear-gradient(135deg, #11998e, #38ef7d); color: #0f0c29;
    }
    .ai-status-badge.groq {
        background: linear-gradient(135deg, #667eea, #764ba2); color: white;
    }

    .ai-response-card {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 100%);
        border-radius: 16px; padding: 24px 28px; color: #e0e0ff;
        font-size: 1rem; line-height: 1.75; border-left: 4px solid #38ef7d;
        box-shadow: 0 8px 32px rgba(48, 43, 99, 0.4); margin: 12px 0;
    }

    /* Hide default Streamlit footer */
    footer {visibility: hidden;}

    /* Hide Streamlit Sidebar toggle on desktop */
    @media (min-width: 768px) {
        section[data-testid="stSidebar"] { display: none !important; width: 0 !important; }
        button[data-testid="collapsedControl"] { display: none !important; }
    }

    /* Main title */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 20px;
        background: linear-gradient(90deg, #e0e0ff, #667eea, #e0e0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Dashboard Cards */
    .dashboard-card {
        background: linear-gradient(135deg, rgba(15,12,41,0.8) 0%, rgba(48,43,99,0.8) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        color: #e0e0ff;
        box-shadow: 0 8px 32px rgba(48, 43, 99, 0.4);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .dashboard-card h3 {
        margin-top: 0;
        font-size: 1.4rem;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .dashboard-stat {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38ef7d;
        margin: 10px 0;
    }

    /* Top Nav Container */
    .top-nav-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    @media (max-width: 767px) {
        .top-nav-container { display: none !important; }
    }

    /* Floating Profile Button Hook */
    .float-profile-anchor + div {
        position: fixed;
        top: 20px;
        left: 30px;
        z-index: 9999;
    }
    .float-profile-anchor + div button {
        width: auto !important;
        height: auto !important;
        border-radius: 30px !important;
        background: linear-gradient(135deg, #1e1e2f, #2a2a40) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: 2px solid rgba(102, 126, 234, 0.4) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 10px 20px !important;
    }
    .float-profile-anchor + div button:hover {
        transform: scale(1.05) !important;
        border-color: #667eea !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    .float-profile-anchor + div button p {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 16px !important;
    }
    @media (max-width: 767px) {
        .float-profile-anchor + div { display: none !important; }
    }

    /* Hide top nav Streamlit buttons default styling to make them look like tabs */
    .top-nav-container div[data-testid="stButton"] button {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: #e0e0ff;
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .top-nav-container div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-color: transparent;
        transform: translateY(-2px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# Navigation & Layout State
# ─────────────────────────────────────────────
if "module" not in st.session_state:
    st.session_state.module = "🏠 Dashboard"

# Floating Profile Button (Top Left)
profile_data = load_json(PROFILE_FILE, {})
user_avatar = profile_data.get("avatar", "👤")
with st.container():
    st.markdown('<div class="float-profile-anchor"></div>', unsafe_allow_html=True)
    if st.button(f"{user_avatar} Profile", key="float_profile_btn"):
        st.session_state.module = "👤 Profile"
        st.rerun()

st.markdown('<div class="main-title">🚀 GrowthOS</div>', unsafe_allow_html=True)

# Top Navigation (Desktop)
st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
nav_options = ["🏠 Dashboard", "✅ Habit Tracker", "🎯 SkillMap", "🧘 MindMate", "🎮 Achievements", "🤖 AI Motivator"]
cols = st.columns(len(nav_options))
for i, opt in enumerate(nav_options):
    if cols[i].button(opt, use_container_width=True, key=f"topnav_{opt}"):
        st.session_state.module = opt
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar Navigation (Mobile)
with st.sidebar:
    st.markdown("# 🚀 GrowthOS")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    
    def on_sidebar_change():
        st.session_state.module = st.session_state.sidebar_nav
        
    sidebar_opts = ["🏠 Dashboard", "👤 Profile", "✅ Habit Tracker", "🎯 SkillMap", "🧘 MindMate", "🤖 AI Motivator", "🎮 Achievements"]
    
    st.radio(
        "Navigate",
        sidebar_opts,
        label_visibility="collapsed",
        key="sidebar_nav",
        index=sidebar_opts.index(st.session_state.module) if st.session_state.module in sidebar_opts else 0,
        on_change=on_sidebar_change
    )
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")

    # Calculate today's XP
    gamification = get_gamification()
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_xp = sum(item.get("amount", 0) for item in gamification.get("history", []) if item.get("date") == today_str)
    
    st.markdown(f"""
    <div style="background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 8px; margin-top: 10px; text-align: center; border: 1px solid rgba(102, 126, 234, 0.3);">
        <div style="font-size: 0.8rem; color: #e0e0ff; opacity: 0.8;">XP Earned Today</div>
        <div style="font-size: 1.2rem; font-weight: bold; color: #38ef7d;">+{today_xp} XP</div>
    </div>
    """, unsafe_allow_html=True)

module = st.session_state.module

# ═══════════════════════════════════════════════
#  MODULE: 🏠 Dashboard
# ═══════════════════════════════════════════════
if module == "🏠 Dashboard":
    st.markdown('<p class="section-header">🏠 Dashboard</p>', unsafe_allow_html=True)
    st.markdown("Overview of your growth journey.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    
    habits = load_json(HABITS_FILE, [])
    skills = load_json(SKILLS_FILE, [])
    moods = load_json(MOODS_FILE, [])
    state = get_gamification()
    today = datetime.now().strftime("%Y-%m-%d")
    
    completed_habits_today = sum(1 for h in habits if today in h.get("completions", []))
    mood_logged_today = any(m["date"] == today for m in moods)
    level, level_name, _ = get_level_info(state.get("total_xp", 0))
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'''
        <div class="dashboard-card">
            <h3>✅ Habits</h3>
            <div class="dashboard-stat">{completed_habits_today} / {len(habits)}</div>
            <p>Completed Today</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Open Habits", use_container_width=True, key="dash_habits"):
            st.session_state.module = "✅ Habit Tracker"
            st.rerun()
            
    with c2:
        st.markdown(f'''
        <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(17,153,142,0.8) 0%, rgba(56,239,125,0.8) 100%);">
            <h3>🎯 SkillMap</h3>
            <div class="dashboard-stat" style="color: white;">{len(skills)}</div>
            <p>Active Skills</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Open Skills", use_container_width=True, key="dash_skills"):
            st.session_state.module = "🎯 SkillMap"
            st.rerun()
            
    with c3:
        mood_status = "Done ✅" if mood_logged_today else "Pending ⏳"
        st.markdown(f'''
        <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(238,9,121,0.8) 0%, rgba(255,106,0,0.8) 100%);">
            <h3>🧘 MindMate</h3>
            <div class="dashboard-stat" style="color: white; font-size: 1.5rem;">{mood_status}</div>
            <p>Today's Check-in</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Open MindMate", use_container_width=True, key="dash_moods"):
            st.session_state.module = "🧘 MindMate"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        st.markdown(f'''
        <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(247,151,30,0.8) 0%, rgba(255,210,0,0.8) 100%);">
            <h3>🎮 Achievements</h3>
            <div class="dashboard-stat" style="color: white;">Level {level}</div>
            <p>{level_name}</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("View Achievements", use_container_width=True, key="dash_achieve"):
            st.session_state.module = "🎮 Achievements"
            st.rerun()
            
    with c5:
        profile = load_json(PROFILE_FILE, {})
        user_name = profile.get("name", "Learner")
        avatar = profile.get("avatar", "🌟")
        st.markdown(f'''
        <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(102,126,234,0.8) 0%, rgba(118,75,162,0.8) 100%);">
            <h3>👤 Profile</h3>
            <div class="dashboard-stat" style="color: white; font-size: 1.8rem;">{avatar} {user_name}</div>
            <p>Your Identity</p>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("View Profile", use_container_width=True, key="dash_profile"):
            st.session_state.module = "👤 Profile"
            st.rerun()


# ═══════════════════════════════════════════════
#  MODULE 0 — 👤 Profile
# ═══════════════════════════════════════════════
AVATARS = ["🧑‍💻", "👩‍🎓", "🧑‍🎨", "🦸", "🧑‍🚀", "🧙", "🐱", "🌟"]

if module == "👤 Profile":
    st.markdown('<p class="section-header">👤 User Profile</p>', unsafe_allow_html=True)
    st.markdown("Set up your identity. Own your growth journey.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    profile = load_json(PROFILE_FILE, {})
    has_profile = bool(profile)

    # ── Display existing profile ──
    if has_profile:
        avatar = profile.get("avatar", "🌟")
        name = profile.get("name", "Learner")
        age = profile.get("age", "")
        student_type = profile.get("student_type", "")
        study_goal = profile.get("study_goal", 0)
        motto = profile.get("motto", "")

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="avatar">{avatar}</div>
                <div class="name">{name}</div>
                <div class="detail">🎂 Age: {age}  ·  🎓 {student_type}</div>
                <div class="detail">📖 Daily Study Goal: {study_goal} hour{"s" if study_goal != 1 else ""}</div>
                {f'<div class="motto">💬 "{motto}"</div>' if motto else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick stats from other modules
        habits = load_json(HABITS_FILE, [])
        skills = load_json(SKILLS_FILE, [])
        moods = load_json(MOODS_FILE, [])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="metric-card"><h2>{len(habits)}</h2><p>Habits Tracked</p></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card green"><h2>{len(skills)}</h2><p>Skills Mapped</p></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card orange"><h2>{len(moods)}</h2><p>Mood Check-ins</p></div>',
                unsafe_allow_html=True,
            )

    # ── Profile Setup / Edit Form ──
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    form_label = "✏️ Edit Profile" if has_profile else "🚀 Set Up Your Profile"
    with st.expander(form_label, expanded=not has_profile):
        p_name = st.text_input("Full Name", value=profile.get("name", ""), placeholder="e.g. Rahul Sharma")
        p_age = st.number_input("Age", min_value=5, max_value=100, value=profile.get("age", 18), step=1)
        p_type = st.selectbox(
            "Student Type",
            ["ECE", "CSE", "Mechanical", "Arts", "Sports", "Other"],
            index=["ECE", "CSE", "Mechanical", "Arts", "Sports", "Other"].index(
                profile.get("student_type", "CSE")
            ) if profile.get("student_type", "CSE") in ["ECE", "CSE", "Mechanical", "Arts", "Sports", "Other"] else 1,
        )
        p_goal = st.number_input(
            "Daily Study Goal (hours)", min_value=1, max_value=12,
            value=profile.get("study_goal", 4), step=1,
        )
        p_motto = st.text_input(
            "Personal Motto / Quote",
            value=profile.get("motto", ""),
            placeholder="e.g. Stay curious, stay humble.",
        )

        # Avatar selection
        st.markdown("**Choose your Avatar:**")
        current_avatar = profile.get("avatar", "🌟")
        avatar_cols = st.columns(8)
        selected_avatar = current_avatar

        for i, av in enumerate(AVATARS):
            with avatar_cols[i]:
                if st.button(av, key=f"av_{i}", use_container_width=True):
                    selected_avatar = av
                    st.session_state["_selected_avatar"] = av

        # Persist avatar selection in session state across reruns
        if "_selected_avatar" in st.session_state:
            selected_avatar = st.session_state["_selected_avatar"]

        st.markdown(f"Selected: **{selected_avatar}**")

        if st.button("💾 Save Profile", use_container_width=True):
            if p_name.strip():
                new_profile = {
                    "name": p_name.strip(),
                    "age": p_age,
                    "student_type": p_type,
                    "study_goal": p_goal,
                    "motto": p_motto.strip(),
                    "avatar": selected_avatar,
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                save_json(PROFILE_FILE, new_profile)
                if "_selected_avatar" in st.session_state:
                    del st.session_state["_selected_avatar"]
                st.success(f"✨ Profile saved for **{p_name.strip()}**!")
                st.rerun()
            else:
                st.warning("Please enter your name.")


# ═══════════════════════════════════════════════
#  MODULE 1 — ✅ Habit Tracker
# ═══════════════════════════════════════════════
elif module == "✅ Habit Tracker":
    st.markdown('<p class="section-header">✅ Habit Tracker</p>', unsafe_allow_html=True)
    st.markdown("Build consistency, one day at a time.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    habits = load_json(HABITS_FILE, [])
    today = datetime.now().strftime("%Y-%m-%d")

    # ── Add Habit ──
    with st.expander("➕ Add a New Habit", expanded=False):
        new_habit = st.text_input("Habit name", placeholder="e.g. Read 30 minutes")
        if st.button("Add Habit", use_container_width=True):
            if new_habit.strip():
                habits.append({
                    "name": new_habit.strip(),
                    "created": today,
                    "completions": [],
                })
                save_json(HABITS_FILE, habits)
                st.success(f"🎉 **{new_habit.strip()}** added!")
                st.rerun()
            else:
                st.warning("Please enter a habit name.")

    if not habits:
        st.info("No habits yet. Add one above to get started! 🌱")
    else:
        # ── Summary Cards ──
        total = len(habits)
        completed_today = sum(1 for h in habits if today in h.get("completions", []))
        best_streak = 0
        for h in habits:
            streak = 0
            day = datetime.now()
            comps = set(h.get("completions", []))
            while day.strftime("%Y-%m-%d") in comps:
                streak += 1
                day -= timedelta(days=1)
            best_streak = max(best_streak, streak)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="metric-card"><h2>{total}</h2><p>Total Habits</p></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card green"><h2>{completed_today}/{total}</h2><p>Done Today</p></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card orange"><h2>🔥 {best_streak}</h2><p>Best Streak</p></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
        st.markdown("### Today's Habits")

        # ── Habit List ──
        for idx, habit in enumerate(habits):
            comps = set(habit.get("completions", []))

            # Calculate streak
            streak = 0
            day = datetime.now()
            while day.strftime("%Y-%m-%d") in comps:
                streak += 1
                day -= timedelta(days=1)

            done_today = today in comps
            col1, col2, col3 = st.columns([5, 2, 1])

            with col1:
                icon = "✅" if done_today else "⬜"
                st.markdown(f"#### {icon} {habit['name']}")

            with col2:
                if streak > 0:
                    st.markdown(
                        f'<span class="streak-badge">🔥 {streak} day{"s" if streak != 1 else ""}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("No streak yet")

            with col3:
                if not done_today:
                    if st.button("Done", key=f"done_{idx}"):
                        habits[idx]["completions"].append(today)
                        save_json(HABITS_FILE, habits)
                        
                        add_xp(10, f"Completed habit: {habit['name']}")
                        # Check streak
                        new_streak = 0
                        day_check = datetime.now()
                        comps_check = set(habits[idx]["completions"])
                        while day_check.strftime("%Y-%m-%d") in comps_check:
                            new_streak += 1
                            day_check -= timedelta(days=1)
                        if new_streak == 7:
                            add_xp(50, "7-day streak bonus!")
                        check_and_award_badges()
                        
                        st.rerun()
                else:
                    st.caption("✔️")

            # Delete button
            if st.button("🗑️ Remove", key=f"del_{idx}"):
                habits.pop(idx)
                save_json(HABITS_FILE, habits)
                st.rerun()


# ═══════════════════════════════════════════════
#  MODULE 2 — 🎯 SkillMap
# ═══════════════════════════════════════════════
elif module == "🎯 SkillMap":
    st.markdown('<p class="section-header">🎯 SkillMap</p>', unsafe_allow_html=True)
    st.markdown("Map your growth journey across every skill.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    skills = load_json(SKILLS_FILE, [])

    CATEGORIES = ["Academic", "Arts", "Sports", "Tech", "Personal", "Custom"]
    CATEGORY_EMOJI = {
        "Academic": "📚",
        "Arts": "🎨",
        "Sports": "🏅",
        "Tech": "💻",
        "Personal": "🌱",
        "Custom": "⭐",
    }

    # ── Add Skill ──
    with st.expander("➕ Add a New Skill", expanded=False):
        s_name = st.text_input("Skill Name", placeholder="e.g. Python Programming")
        s_category = st.selectbox("Category", CATEGORIES)
        if s_category == "Custom":
            s_category = st.text_input("Custom Category Name", placeholder="e.g. Music")
        s_goal = st.text_input("Goal", placeholder="e.g. Build 3 projects")
        s_minutes = st.number_input("Daily Practice (minutes)", min_value=1, max_value=480, value=30, step=5)
        s_goal_days = st.number_input("How many days is your goal?", min_value=1, max_value=365, value=30, step=1)

        if st.button("Add Skill", use_container_width=True):
            if s_name.strip():
                skills.append({
                    "name": s_name.strip(),
                    "category": s_category,
                    "goal": s_goal.strip(),
                    "daily_minutes": s_minutes,
                    "goal_days": s_goal_days,
                    "completions": [],
                    "added": datetime.now().strftime("%Y-%m-%d"),
                })
                save_json(SKILLS_FILE, skills)
                add_xp(20, "Added a new skill")
                check_and_award_badges()
                st.success(f"🎯 **{s_name.strip()}** added to your SkillMap!")
                st.rerun()
            else:
                st.warning("Please enter a skill name.")

    if not skills:
        st.info("No skills tracked yet. Add your first skill above! 🎯")
    else:
        # ── Summary Cards ──
        cat_counts = {}
        total_minutes = 0
        for s in skills:
            cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1
            total_minutes += s.get("daily_minutes", 0)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="metric-card"><h2>{len(skills)}</h2><p>Skills Tracked</p></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card green"><h2>{len(cat_counts)}</h2><p>Categories</p></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card orange"><h2>{total_minutes} min</h2><p>Daily Commitment</p></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📋 Your Skills")

        # ── Skills Cards ──
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        for idx, s in enumerate(skills):
            emoji = CATEGORY_EMOJI.get(s["category"], "⭐")
            goal_days = s.get("goal_days", 30)
            comps = s.get("completions", [])
            done_today = today_str in comps
            completed_days = len(comps)
            
            # Generate circles
            circles = "⬤ " * completed_days + "○ " * max(0, goal_days - completed_days)
            circles = circles.strip()
            
            with st.container():
                st.markdown(f"""
                <div style="background: rgba(30,30,47,0.5); border: 1px solid rgba(102,126,234,0.3); border-radius: 12px; padding: 20px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 1.2rem; font-weight: bold; color: #e0e0ff;">{emoji} {s["name"]}</div>
                        <div style="background: rgba(102,126,234,0.2); padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; color: #e0e0ff;">{s.get("daily_minutes", 0)} min/day</div>
                    </div>
                    <div style="font-size: 0.9rem; color: #a0a0c0; margin-bottom: 10px;">Goal: {s.get("goal", "—")}</div>
                    <div style="font-size: 0.85rem; color: #38ef7d; font-weight: bold; margin-bottom: 5px;">{completed_days}/{goal_days} days completed</div>
                    <div style="font-size: 1.2rem; letter-spacing: 2px; color: #667eea; word-break: break-all; margin-bottom: 10px;">{circles}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    if not done_today:
                        if st.button("Practice Done", key=f"skill_done_{idx}"):
                            skills[idx].setdefault("completions", []).append(today_str)
                            save_json(SKILLS_FILE, skills)
                            add_xp(15, f"Practiced skill: {s['name']}")
                            check_and_award_badges()
                            st.rerun()
                    else:
                        st.button("Done Today ✅", key=f"skill_done_{idx}", disabled=True)
                st.markdown("<br>", unsafe_allow_html=True)

        # ── Remove Skill ──
        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
        with st.expander("🗑️ Remove a Skill"):
            skill_names = [s["name"] for s in skills]
            to_remove = st.selectbox("Select skill to remove", skill_names)
            if st.button("Remove Skill", use_container_width=True):
                skills = [s for s in skills if s["name"] != to_remove]
                save_json(SKILLS_FILE, skills)
                st.success(f"Removed **{to_remove}**.")
                st.rerun()


# ═══════════════════════════════════════════════
#  MODULE 3 — 🧘 MindMate
# ═══════════════════════════════════════════════
elif module == "🧘 MindMate":
    st.markdown('<p class="section-header">🧘 MindMate</p>', unsafe_allow_html=True)
    st.markdown("Check in with yourself. Your mind matters.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    moods = load_json(MOODS_FILE, [])
    today = datetime.now().strftime("%Y-%m-%d")

    MOOD_EMOJI = {"Happy": "😊", "Neutral": "😐", "Stressed": "😰"}
    MOOD_COLORS = {"Happy": "#38ef7d", "Neutral": "#667eea", "Stressed": "#ee0979"}

    QUOTES = {
        "Happy": [
            "Happiness is not something ready-made. It comes from your own actions. — Dalai Lama",
            "The purpose of our lives is to be happy. — Dalai Lama",
            "Happiness depends upon ourselves. — Aristotle",
            "Be happy for this moment. This moment is your life. — Omar Khayyam",
            "The most important thing is to enjoy your life — to be happy. — Audrey Hepburn",
        ],
        "Neutral": [
            "In the middle of difficulty lies opportunity. — Albert Einstein",
            "Not all those who wander are lost. — J.R.R. Tolkien",
            "The only way to do great work is to love what you do. — Steve Jobs",
            "Peace comes from within. Do not seek it without. — Buddha",
            "Still waters run deep. Keep going. — Proverb",
        ],
        "Stressed": [
            "You don't have to control your thoughts. You just have to stop letting them control you. — Dan Millman",
            "Almost everything will work again if you unplug it for a few minutes, including you. — Anne Lamott",
            "Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure. — Oprah",
            "It's not stress that kills us, it is our reaction to it. — Hans Selye",
            "You are braver than you believe, stronger than you seem, and smarter than you think. — A.A. Milne",
        ],
    }

    # Check if already logged today
    logged_today = any(m["date"] == today for m in moods)

    # ── Mood Check-in ──
    st.markdown("### How are you feeling today?")
    mood_cols = st.columns(3)
    selected_mood = None

    for i, (mood, emoji) in enumerate(MOOD_EMOJI.items()):
        with mood_cols[i]:
            if st.button(
                f"{emoji}\n{mood}",
                key=f"mood_{mood}",
                use_container_width=True,
                disabled=logged_today,
            ):
                selected_mood = mood

    if logged_today:
        today_mood = next(m["mood"] for m in moods if m["date"] == today)
        st.success(f"You already checked in today as **{MOOD_EMOJI[today_mood]} {today_mood}**")
        selected_mood = today_mood
    elif selected_mood:
        moods.append({"date": today, "mood": selected_mood})
        save_json(MOODS_FILE, moods)
        add_xp(5, "Daily mood check-in")
        check_and_award_badges()
        st.success(f"Logged as **{MOOD_EMOJI[selected_mood]} {selected_mood}** — take care of yourself! 💜")
        st.rerun()

    # ── Motivational Quote ──
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    display_mood = selected_mood if selected_mood else "Neutral"
    quote = random.choice(QUOTES[display_mood])
    st.markdown("### 💬 Your Quote")
    st.markdown(f'<div class="quote-card">"{quote}"</div>', unsafe_allow_html=True)

    # ── Mood History ──
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Mood History")

    if not moods:
        st.info("No mood entries yet. Check in above to start tracking! 🧘")
    else:
        # Summary cards
        mood_count = {"Happy": 0, "Neutral": 0, "Stressed": 0}
        for m in moods:
            mood_count[m["mood"]] = mood_count.get(m["mood"], 0) + 1

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="metric-card green"><h2>😊 {mood_count["Happy"]}</h2><p>Happy Days</p></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card"><h2>😐 {mood_count["Neutral"]}</h2><p>Neutral Days</p></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card pink"><h2>😰 {mood_count["Stressed"]}</h2><p>Stressed Days</p></div>',
                unsafe_allow_html=True,
            )

        # Bar chart — last 14 days
        st.markdown("")
        mood_to_num = {"Happy": 3, "Neutral": 2, "Stressed": 1}
        last_entries = moods[-14:]

        import pandas as pd

        chart_df = pd.DataFrame(last_entries)
        chart_df["value"] = chart_df["mood"].map(mood_to_num)
        chart_df = chart_df.set_index("date")

        st.bar_chart(chart_df["value"], use_container_width=True, color="#667eea")
        st.caption("3 = Happy · 2 = Neutral · 1 = Stressed")

        # ── Clear history ──
        with st.expander("🗑️ Clear Mood History"):
            st.warning("This will delete **all** mood entries.")
            if st.button("Clear All Moods", use_container_width=True):
                save_json(MOODS_FILE, [])
                st.rerun()


# ═══════════════════════════════════════════════
#  MODULE 4 — 🤖 AI Motivator
# ═══════════════════════════════════════════════
elif module == "🤖 AI Motivator":
    st.markdown('<p class="section-header">🤖 AI Motivator</p>', unsafe_allow_html=True)
    st.markdown("Your personal AI growth mentor — powered by intelligence.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── AI Connection Logic ──
    ai_choice = st.radio("⚙️ Select AI Engine:", ["Auto-Detect (Prioritize Local)", "Groq (Cloud)", "Ollama (Local)"], horizontal=True)

    def detect_ai_backend():
        """Detect backend based on user choice."""
        if ai_choice == "Groq (Cloud)":
            return "groq" if os.getenv("GROQ_API_KEY") else None
        elif ai_choice == "Ollama (Local)":
            try:
                if requests.get("http://localhost:11434/api/tags", timeout=2).status_code == 200:
                    return "ollama"
            except Exception:
                pass
            return None
        else:
            # Auto-Detect
            try:
                if requests.get("http://localhost:11434/api/tags", timeout=2).status_code == 200:
                    return "ollama"
            except Exception:
                pass
            if os.getenv("GROQ_API_KEY"):
                return "groq"
            return None

    def ask_ai(prompt, system_prompt="You are a personal growth mentor and motivational coach. Keep responses concise (under 200 words), warm, and actionable. Use emojis sparingly."):
        """Send a prompt to the active AI backend."""
        backend = detect_ai_backend()
        if backend == "ollama":
            try:
                import ollama as ollama_client
                response = ollama_client.chat(
                    model="gemma3:1b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                )
                return response["message"]["content"]
            except Exception as e:
                return f"⚠️ Ollama error: {e}"
        elif backend == "groq":
            try:
                from groq import Groq
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=512,
                    temperature=0.7,
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"⚠️ Groq error: {e}"
        else:
            return "⚠️ No AI backend available. Please run Ollama locally or set GROQ_API_KEY in your .env file."

    # ── Show active backend ──
    backend = detect_ai_backend()
    if backend == "ollama":
        st.markdown('<span class="ai-status-badge ollama">🟢 Connected to Ollama (gemma3:1b)</span>', unsafe_allow_html=True)
    elif backend == "groq":
        st.markdown('<span class="ai-status-badge groq">🟣 Connected to Groq (llama-3.3-70b)</span>', unsafe_allow_html=True)
    else:
        if ai_choice == "Groq (Cloud)":
            st.error("❌ Groq API Key missing. Please check your .env file.")
        elif ai_choice == "Ollama (Local)":
            st.error("❌ Ollama not detected. Is it running?")
        else:
            st.error("❌ No AI backend available. Run Ollama locally or add GROQ_API_KEY to .env")

    # ── Load all user data for context ──
    profile = load_json(PROFILE_FILE, {})
    habits = load_json(HABITS_FILE, [])
    skills = load_json(SKILLS_FILE, [])
    moods = load_json(MOODS_FILE, [])
    today = datetime.now().strftime("%Y-%m-%d")

    user_name = profile.get("name", "Learner")
    student_type = profile.get("student_type", "Student")
    study_goal = profile.get("study_goal", 4)

    # Habit stats
    total_habits = len(habits)
    completed_today = sum(1 for h in habits if today in h.get("completions", []))
    habit_names = [h["name"] for h in habits]

    # Skills summary
    skill_list = [f"{s['name']} ({s['category']}, {s.get('daily_minutes', 0)} min/day)" for s in skills]

    # Today's mood
    today_mood_entry = next((m for m in moods if m["date"] == today), None)
    today_mood = today_mood_entry["mood"] if today_mood_entry else "Not logged yet"

    # Build context string
    context_block = f"""USER CONTEXT:
- Name: {user_name}
- Student Type: {student_type}
- Daily Study Goal: {study_goal} hours
- Habits ({total_habits} total, {completed_today} done today): {', '.join(habit_names) if habit_names else 'None'}
- Skills: {', '.join(skill_list) if skill_list else 'None'}
- Today's Mood: {today_mood}
- Date: {today}"""

    # ── Chat persistence helpers ──
    import uuid as _uuid

    def load_all_chats():
        """Load all saved chat sessions from disk."""
        return load_json(CHATS_FILE, [])

    def save_all_chats(chats):
        """Save all chat sessions to disk."""
        save_json(CHATS_FILE, chats)

    def get_current_chat_id():
        """Get the active chat session ID."""
        return st.session_state.get("active_chat_id", None)

    def create_new_chat():
        """Create a new chat session and make it active."""
        chat_id = str(_uuid.uuid4())[:8]
        st.session_state["active_chat_id"] = chat_id
        st.session_state["ai_chat_history"] = []
        for key in ["advice_response", "daily_challenge", "mood_response"]:
            st.session_state.pop(key, None)
        return chat_id

    def save_current_chat():
        """Save the current chat session to disk."""
        chat_id = get_current_chat_id()
        if not chat_id or not st.session_state.get("ai_chat_history"):
            return
        chats = load_all_chats()
        # Auto-generate a name from the first user message
        first_msg = next((m["content"] for m in st.session_state["ai_chat_history"] if m["role"] == "user"), "New Chat")
        chat_name = first_msg[:50] + ("..." if len(first_msg) > 50 else "")
        # Check if this chat already exists
        existing = next((c for c in chats if c["id"] == chat_id), None)
        if existing:
            existing["messages"] = st.session_state["ai_chat_history"]
            existing["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            if existing.get("name") == "New Chat":
                existing["name"] = chat_name
        else:
            chats.insert(0, {
                "id": chat_id,
                "name": chat_name,
                "messages": st.session_state["ai_chat_history"],
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
        # Keep only last 50 chats
        chats = chats[:50]
        save_all_chats(chats)

    def load_chat_by_id(chat_id):
        """Load a specific chat session by its ID."""
        chats = load_all_chats()
        chat = next((c for c in chats if c["id"] == chat_id), None)
        if chat:
            st.session_state["active_chat_id"] = chat_id
            st.session_state["ai_chat_history"] = chat["messages"]
            return True
        return False

    def delete_chat_by_id(chat_id):
        """Delete a chat session by its ID."""
        chats = load_all_chats()
        chats = [c for c in chats if c["id"] != chat_id]
        save_all_chats(chats)

    # ── Initialize chat state ──
    if "ai_chat_history" not in st.session_state:
        st.session_state["ai_chat_history"] = []
    if "active_chat_id" not in st.session_state:
        st.session_state["active_chat_id"] = None

    # ── Previous chats sidebar (within main area) ──
    all_chats = load_all_chats()

    chat_col, main_col = st.columns([1, 3])

    with chat_col:
        st.markdown("#### 💬 Chats")
        if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
            create_new_chat()
            st.rerun()

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        if not all_chats:
            st.caption("No previous chats yet.")
        else:
            for chat in all_chats:
                chat_id = chat["id"]
                is_active = chat_id == get_current_chat_id()
                msg_count = len(chat.get("messages", []))
                time_str = chat.get("updated", chat.get("created", ""))

                # Chat button with active state styling
                btn_label = f"{'▶ ' if is_active else ''}{chat['name']}"
                col_btn, col_del = st.columns([5, 1])
                with col_btn:
                    if st.button(btn_label, key=f"chat_{chat_id}", use_container_width=True):
                        load_chat_by_id(chat_id)
                        st.rerun()
                with col_del:
                    if st.button("🗑", key=f"del_{chat_id}"):
                        delete_chat_by_id(chat_id)
                        if is_active:
                            create_new_chat()
                        st.rerun()
                st.caption(f"  📝 {msg_count} msgs · {time_str}")

    with main_col:
        # ── Header bar ──
        header_l, header_r = st.columns([6, 1])
        with header_l:
            if backend == "ollama":
                st.markdown('<span class="ai-status-badge ollama">🟢 Ollama · gemma3:1b</span>', unsafe_allow_html=True)
            elif backend == "groq":
                st.markdown('<span class="ai-status-badge groq">🟣 Groq · llama-3.3-70b</span>', unsafe_allow_html=True)
        with header_r:
            if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
                create_new_chat()
                st.rerun()

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Display chat history or welcome screen ──
        if not st.session_state["ai_chat_history"]:
            # Welcome screen with quick actions
            st.markdown(f"""
            <div class="claude-welcome">
                <h2>Hey {user_name} 👋</h2>
                <p>I'm your AI growth mentor. Ask me anything or try a quick action below.</p>
            </div>
            """, unsafe_allow_html=True)

            q1, q2 = st.columns(2)
            q3, q4 = st.columns(2)
            with q1:
                if st.button("💡 Give me personalized advice", key="qa1", use_container_width=True):
                    if not get_current_chat_id():
                        create_new_chat()
                    st.session_state["_pending_quick"] = f"""{context_block}

Based on the user's profile and progress above, give them specific, personalized motivational advice.
Address them by name. Reference their actual habits, skills, and today's mood.
Be specific — mention which habits they completed or missed, and give actionable tips for the rest of the day."""
                    st.session_state["_pending_label"] = "Give me personalized advice"
                    st.rerun()
            with q2:
                if st.button("🎯 Give me today's challenge", key="qa2", use_container_width=True):
                    if not get_current_chat_id():
                        create_new_chat()
                    st.session_state["_pending_quick"] = f"""{context_block}

Generate ONE specific, actionable daily challenge for this user based on their skills and goals.
The challenge should be achievable today and push them slightly outside their comfort zone.
Format: Start with the challenge title in bold, then explain what to do in 2-3 sentences.
Make it very specific — mention exact skills, durations, and measurable outcomes."""
                    st.session_state["_pending_label"] = "Give me today's challenge"
                    st.rerun()
            with q3:
                if st.button("🧠 Help me with my mood", key="qa3", use_container_width=True):
                    if not get_current_chat_id():
                        create_new_chat()
                    if today_mood == "Stressed":
                        mood_instruction = "The user is feeling STRESSED. Give calming, compassionate advice first, then gently motivational guidance. Suggest a breathing exercise and one small win they can achieve today."
                    elif today_mood == "Happy":
                        mood_instruction = "The user is feeling HAPPY. Capitalize on this energy! Give them a growth challenge, suggest leveling up a skill, and encourage them to help someone else today."
                    else:
                        mood_instruction = "The user is feeling NEUTRAL. Give them focus tips, suggest a way to spark motivation, and recommend a small achievable task to build momentum."
                    st.session_state["_pending_quick"] = f"""{context_block}

{mood_instruction}

Address them by name and reference their actual habits and skills."""
                    st.session_state["_pending_label"] = f"Help me with my mood ({today_mood})"
                    st.rerun()
            with q4:
                if st.button("📊 Summarize my progress", key="qa4", use_container_width=True):
                    if not get_current_chat_id():
                        create_new_chat()
                    st.session_state["_pending_quick"] = f"""{context_block}

Give a concise progress summary for this user. Include: habits completion rate today, skills they're building, mood trend, and one encouraging observation. End with one actionable next step."""
                    st.session_state["_pending_label"] = "Summarize my progress"
                    st.rerun()
        else:
            # Render chat messages in Claude-style
            for msg in st.session_state["ai_chat_history"]:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(msg["content"])

        # ── Process pending quick action ──
        if "_pending_quick" in st.session_state:
            prompt = st.session_state.pop("_pending_quick")
            label = st.session_state.pop("_pending_label", "Quick action")
            st.session_state["ai_chat_history"].append({"role": "user", "content": label})
            with st.chat_message("user", avatar="🧑"):
                st.markdown(label)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    response = ask_ai(prompt)
                st.markdown(response)
            st.session_state["ai_chat_history"].append({"role": "assistant", "content": response})
            # Keep last 20 messages per chat
            if len(st.session_state["ai_chat_history"]) > 20:
                st.session_state["ai_chat_history"] = st.session_state["ai_chat_history"][-20:]
            save_current_chat()
            
            add_xp(5, "Asked AI Motivator (Quick Action)")
            check_and_award_badges()
            
            st.rerun()

        # ── Chat input ──
        user_input = st.chat_input("Message AI Motivator...", key="claude_chat_input")

        if user_input:
            # Ensure we have an active chat
            if not get_current_chat_id():
                create_new_chat()

            # Add user message
            st.session_state["ai_chat_history"].append({"role": "user", "content": user_input})

            # Build the AI prompt with context
            prompt = f"""{context_block}

User asks: {user_input}

Respond as a personal growth mentor. Be supportive, specific, and reference their data where relevant."""

            # Get AI response
            with st.chat_message("user", avatar="🧑"):
                st.markdown(user_input)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    response = ask_ai(prompt)
                st.markdown(response)

            st.session_state["ai_chat_history"].append({"role": "assistant", "content": response})

            # Keep last 20 messages per chat
            if len(st.session_state["ai_chat_history"]) > 20:
                st.session_state["ai_chat_history"] = st.session_state["ai_chat_history"][-20:]

            # Save chat to disk
            save_current_chat()
            
            add_xp(5, "Asked AI Motivator")
            check_and_award_badges()
            
            st.rerun()


# ═══════════════════════════════════════════════
#  MODULE 5 — 🎮 Achievements
# ═══════════════════════════════════════════════
elif module == "🎮 Achievements":
    st.markdown('<p class="section-header">🎮 Gamification Dashboard</p>', unsafe_allow_html=True)
    st.markdown("Level up your life. Track your growth journey.")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    state = get_gamification()
    total_xp = state.get("total_xp", 0)
    level, level_name, next_goal = get_level_info(total_xp)
    
    # Top Section: Level and XP
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(
            f"""
            <div class="profile-card" style="padding: 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">{level_name.split()[-1]}</div>
                <div class="name">Level {level}</div>
                <div style="font-size: 1.2rem; opacity: 0.9; margin-top: 5px;">{level_name.split()[0]}</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c2:
        st.markdown("### Total Experience")
        st.markdown(f"<h1 style='color: #38ef7d; font-size: 3.5rem; margin: 0;'>{total_xp} XP</h1>", unsafe_allow_html=True)
        
        if level < 5:
            progress = min(1.0, total_xp / next_goal)
            st.progress(progress)
            st.caption(f"{total_xp} / {next_goal} XP to reach Level {level + 1}")
        else:
            st.progress(1.0)
            st.caption("Max level reached! You are a legend.")
            
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    
    # Middle Section: Badges
    st.markdown("### 🏅 Your Badges")
    awarded_badges = state.get("badges", [])
    
    ALL_BADGES = {
        "Streak Master": ("🔥", "7 day habit streak"),
        "Skill Collector": ("🎯", "5+ skills added"),
        "Mind Guardian": ("🧘", "7 mood check-ins"),
        "Consistency King": ("💪", "30 habits completed"),
        "AI Explorer": ("🤖", "Used AI Motivator 10 times")
    }
    
    badge_cols = st.columns(5)
    for i, (b_name, (b_emoji, b_desc)) in enumerate(ALL_BADGES.items()):
        with badge_cols[i % 5]:
            if b_name in awarded_badges:
                # Earned
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2)); border: 1px solid #667eea; border-radius: 12px; padding: 15px 10px; text-align: center; height: 100%;">
                        <div style="font-size: 2.5rem; margin-bottom: 5px;">{b_emoji}</div>
                        <div style="font-weight: 600; font-size: 0.9rem; color: #e0e0ff;">{b_name}</div>
                        <div style="font-size: 0.75rem; color: #a0a0c0; margin-top: 5px;">{b_desc}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                # Locked
                st.markdown(
                    f"""
                    <div style="background: rgba(30,30,47,0.5); border: 1px solid rgba(102,126,234,0.1); border-radius: 12px; padding: 15px 10px; text-align: center; height: 100%; opacity: 0.5; filter: grayscale(100%);">
                        <div style="font-size: 2.5rem; margin-bottom: 5px;">🔒</div>
                        <div style="font-weight: 600; font-size: 0.9rem; color: #e0e0ff;">Locked</div>
                        <div style="font-size: 0.75rem; color: #a0a0c0; margin-top: 5px;">{b_desc}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
                
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    
    # Bottom Section: XP History Chart
    c3, c4 = st.columns([2, 1])
    with c3:
        st.markdown("### 📈 XP History (Last 7 Days)")
        import pandas as pd
        history = state.get("history", [])
        if not history:
            st.info("No XP earned yet. Start completing habits!")
        else:
            # Group by date
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            # Get last 7 days
            last_7_days = datetime.now() - timedelta(days=7)
            df = df[df['date'] >= last_7_days]
            if not df.empty:
                daily_xp = df.groupby(df['date'].dt.strftime('%Y-%m-%d'))['amount'].sum()
                st.bar_chart(daily_xp, color="#38ef7d", use_container_width=True)
            else:
                st.info("No XP earned in the last 7 days.")
                
    with c4:
        st.markdown("### 💡 How to earn XP")
        st.markdown("- **+10 XP** Completing a habit\n- **+50 XP** 7-day habit streak\n- **+20 XP** Adding a new skill\n- **+5 XP** Daily mood check-in\n- **+5 XP** Asking AI Motivator")
