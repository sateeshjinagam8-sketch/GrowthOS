import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# ─────────────────────────────────────────────
# Data Directory & File Paths
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
HABITS_FILE = os.path.join(DATA_DIR, "habits.json")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
MOODS_FILE = os.path.join(DATA_DIR, "moods.json")


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
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🚀 GrowthOS")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    module = st.radio(
        "Navigate",
        ["👤 Profile", "✅ Habit Tracker", "🎯 SkillMap", "🧘 MindMate", "🤖 AI Motivator"],
        label_visibility="collapsed",
    )
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")


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

        if st.button("Add Skill", use_container_width=True):
            if s_name.strip():
                skills.append({
                    "name": s_name.strip(),
                    "category": s_category,
                    "goal": s_goal.strip(),
                    "daily_minutes": s_minutes,
                    "added": datetime.now().strftime("%Y-%m-%d"),
                })
                save_json(SKILLS_FILE, skills)
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

        # ── Skills Table ──
        table_data = []
        for s in skills:
            emoji = CATEGORY_EMOJI.get(s["category"], "⭐")
            table_data.append({
                "Skill": s["name"],
                "Category": f"{emoji} {s['category']}",
                "Goal": s.get("goal", "—"),
                "Daily (min)": s.get("daily_minutes", 0),
                "Added": s.get("added", "—"),
            })

        st.dataframe(table_data, use_container_width=True, hide_index=True)

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

    # ── Initialize chat history ──
    if "ai_chat_history" not in st.session_state:
        st.session_state["ai_chat_history"] = []

    # ── Header bar: status + new chat ──
    header_l, header_r = st.columns([6, 1])
    with header_l:
        if backend == "ollama":
            st.markdown('<span class="ai-status-badge ollama">🟢 Ollama · gemma3:1b</span>', unsafe_allow_html=True)
        elif backend == "groq":
            st.markdown('<span class="ai-status-badge groq">🟣 Groq · llama-3.3-70b</span>', unsafe_allow_html=True)
    with header_r:
        if st.button("🗑️ New", key="new_chat", use_container_width=True):
            st.session_state["ai_chat_history"] = []
            for key in ["advice_response", "daily_challenge", "mood_response"]:
                st.session_state.pop(key, None)
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
                st.session_state["_pending_quick"] = f"""{context_block}

Based on the user's profile and progress above, give them specific, personalized motivational advice.
Address them by name. Reference their actual habits, skills, and today's mood.
Be specific — mention which habits they completed or missed, and give actionable tips for the rest of the day."""
                st.session_state["_pending_label"] = "Give me personalized advice"
                st.rerun()
        with q2:
            if st.button("🎯 Give me today's challenge", key="qa2", use_container_width=True):
                st.session_state["_pending_quick"] = f"""{context_block}

Generate ONE specific, actionable daily challenge for this user based on their skills and goals.
The challenge should be achievable today and push them slightly outside their comfort zone.
Format: Start with the challenge title in bold, then explain what to do in 2-3 sentences.
Make it very specific — mention exact skills, durations, and measurable outcomes."""
                st.session_state["_pending_label"] = "Give me today's challenge"
                st.rerun()
        with q3:
            if st.button("🧠 Help me with my mood", key="qa3", use_container_width=True):
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
        # Keep last 20 messages
        if len(st.session_state["ai_chat_history"]) > 20:
            st.session_state["ai_chat_history"] = st.session_state["ai_chat_history"][-20:]
        st.rerun()

    # ── Chat input (Enter sends, Shift+Enter for new line, auto-clears) ──
    user_input = st.chat_input("Message AI Motivator...", key="claude_chat_input")

    if user_input:
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

        # Keep last 20 messages
        if len(st.session_state["ai_chat_history"]) > 20:
            st.session_state["ai_chat_history"] = st.session_state["ai_chat_history"][-20:]
        st.rerun()

