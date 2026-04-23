import json
import os
from datetime import datetime

# We will use plyer to send native Windows desktop notifications
try:
    from plyer import notification
except ImportError:
    print("Please install plyer by running: pip install plyer")
    exit(1)

# Set up paths to your GrowthOS data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_FILE = os.path.join(BASE_DIR, "data", "skills.json")
HABITS_FILE = os.path.join(BASE_DIR, "data", "habits.json")

def check_progress():
    today = datetime.now().strftime("%Y-%m-%d")
    pending_tasks = []
    
    # Check if there are uncompleted skills today
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            try:
                skills = json.load(f)
                uncompleted_skills = [s["name"] for s in skills if today not in s.get("completions", [])]
                if uncompleted_skills:
                    pending_tasks.append(f"🎯 {len(uncompleted_skills)} skills to practice")
            except Exception:
                pass
                
    # Check if there are uncompleted habits today
    if os.path.exists(HABITS_FILE):
        with open(HABITS_FILE, "r", encoding="utf-8") as f:
            try:
                habits = json.load(f)
                uncompleted_habits = [h["name"] for h in habits if today not in h.get("completions", [])]
                if uncompleted_habits:
                    pending_tasks.append(f"✅ {len(uncompleted_habits)} habits to complete")
            except Exception:
                pass
                
    # If anything is uncompleted, trigger a Windows desktop popup notification!
    if pending_tasks:
        message_body = "You have:\n" + "\n".join(pending_tasks) + "\nTime to level up in GrowthOS!"
        
        notification.notify(
            title="🚀 GrowthOS Daily Reminder",
            message=message_body,
            app_name="GrowthOS",
            timeout=10  # Notification will stay on screen for 10 seconds
        )
        print("Notification sent successfully!")
    else:
        print("All habits and skills are completed for today. No notification needed!")

if __name__ == "__main__":
    check_progress()
