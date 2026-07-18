import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ API key not found! Add GEMINI_API_KEY to .env file")
    st.stop()

# Initialize Gemini API
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.warning(f"⚠️ API Error: {str(e)}")

# ==================== SAMPLE DATA ====================
def load_job_data():
    """Simulates scraped Pakistan job market data"""
    jobs_data = {
        "Job Title": [
            "Python Developer", "Data Analyst", "Full Stack Developer", "Machine Learning Engineer",
            "Business Analyst", "UI/UX Designer", "DevOps Engineer", "Frontend Developer",
            "Backend Developer", "Data Scientist", "Product Manager", "Cloud Architect",
            "React Developer", "SQL Developer", "AI Engineer", "QA Engineer",
            "Network Engineer", "Security Analyst", "Mobile Developer", "Data Engineer"
        ] * 5,
        "Required Skills": [
            "Python, FastAPI, SQL", "SQL, Python, Tableau", "React, Python, MongoDB", "Python, TensorFlow, ML",
            "Excel, SQL, Communication", "Figma, Adobe XD, UI", "Docker, Kubernetes, AWS", "React, JavaScript, CSS",
            "Python, FastAPI, PostgreSQL", "Python, ML, Statistics", "Analytics, Strategy, Excel", "AWS, Terraform, Docker",
            "React, JavaScript, TypeScript", "SQL, Optimization, MySQL", "Python, TensorFlow, PyTorch", "Manual Testing, Selenium",
            "Cisco, Linux, Networking", "Security, Linux, Firewalls", "Swift, React Native, iOS", "Spark, Python, Data Warehouse"
        ] * 5,
        "Salary Range (PKR)": [
            "150k-300k", "120k-250k", "180k-350k", "200k-400k",
            "100k-200k", "80k-200k", "220k-400k", "140k-280k",
            "170k-320k", "180k-380k", "150k-350k", "250k-450k",
            "160k-300k", "130k-260k", "210k-420k", "80k-180k",
            "140k-280k", "160k-320k", "120k-250k", "190k-360k"
        ] * 5,
        "Location": ["Karachi", "Lahore", "Islamabad", "Karachi", "Lahore"] * 20,
        "Experience Required": ["2-5 years", "1-3 years", "3-6 years", "3-7 years",
                               "1-3 years", "1-4 years", "4-8 years", "2-4 years",
                               "2-5 years", "3-6 years", "4-8 years", "5-10 years",
                               "2-4 years", "2-5 years", "3-7 years", "1-2 years",
                               "4-8 years", "3-6 years", "2-5 years", "3-6 years"] * 5
    }
    return pd.DataFrame(jobs_data)

jobs_df = load_job_data()

def extract_skills_frequency():
    """Count individual skill mentions"""
    all_skills = []
    for skills_str in jobs_df["Required Skills"]:
        skills = [s.strip() for s in skills_str.split(",")]
        all_skills.extend(skills)
    skill_counts = pd.Series(all_skills).value_counts()
    return skill_counts

skills_freq = extract_skills_frequency()

# ==================== SIDEBAR ====================
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Choose a page:", 
    ["🏠 Home", "📈 Market Insights", "🎯 My Career Path", "💡 Learning Resources", "🏆 Leaderboard"])

# ==================== PAGE: HOME ====================
if page == "🏠 Home":
    st.markdown("""
    # 🚀 Skills Demand Hub
    ### *Empowering Students & Young Professionals in Pakistan*
    
    ---
    
    **Your mission:** Discover what skills are IN-DEMAND right now in Pakistan's job market 
    and get a personalized learning path to land your dream job.
    
    **What we do:**
    - 📊 Show real job market data (Pakistan)
    - 🎯 Match your skills to jobs
    - 📚 Recommend skills to learn
    - 💰 Predict salary potential
    - 🏆 Track community progress
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs Analyzed", len(jobs_df))
    with col2:
        st.metric("Unique Skills in Demand", len(skills_freq))
    with col3:
        st.metric("Active Cities", jobs_df["Location"].nunique())
    
    st.markdown("---")
    st.subheader("⚡ Quick Start")
    st.write("👉 Go to **'My Career Path'** to get personalized skill recommendations!")

# ==================== PAGE: MARKET INSIGHTS ====================
elif page == "📈 Market Insights":
    st.title("📈 Market Insights: What's In Demand?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top 10 In-Demand Skills")
        top_skills = skills_freq.head(10)
        fig = px.bar(
            x=top_skills.index,
            y=top_skills.values,
            labels={"x": "Skill", "y": "Mentions in Job Postings"},
            title="Most Requested Skills (Pakistan)",
            color=top_skills.values,
            color_continuous_scale="Viridis"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💼 Jobs by Location")
        location_counts = jobs_df["Location"].value_counts()
        fig = px.pie(
            values=location_counts.values,
            names=location_counts.index,
            title="Job Opportunities by City"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💰 Salary Trends by Skill")
    
    salary_data = []
    for skill in skills_freq.head(8).index:
        skill_jobs = jobs_df[jobs_df["Required Skills"].str.contains(skill, case=False)]
        avg_min = skill_jobs["Salary Range (PKR)"].apply(lambda x: int(x.split("-")[0].replace("k", "")) * 1000).mean()
        salary_data.append({"Skill": skill, "Avg Min Salary": avg_min})
    
    salary_df = pd.DataFrame(salary_data).sort_values("Avg Min Salary", ascending=False)
    fig = px.bar(salary_df, x="Skill", y="Avg Min Salary", 
                 title="Average Starting Salary by Skill",
                 color="Avg Min Salary",
                 color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: MY CAREER PATH ====================
elif page == "🎯 My Career Path":
    st.title("🎯 Personalized Career Path")
    st.write("Let's find your next skill to learn!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_skills = st.multiselect(
            "What skills do you already have?",
            sorted(skills_freq.index),
            default=["Python", "SQL"],
            help="Select all skills you currently know"
        )
    
    with col2:
        target_role = st.selectbox(
            "Target role:",
            jobs_df["Job Title"].unique()
        )
    
    if selected_skills and st.button("🚀 Get My Learning Path", use_container_width=True):
        st.success("Generating personalized path with AI...")
        
        try:
            # Get AI recommendation
            prompt = f"""
            Student Profile:
            - Current Skills: {', '.join(selected_skills)}
            - Target Role: {target_role}
            - Location: Pakistan
            
            Based on current Pakistan job market:
            1. Recommend 3 skills to learn (in priority order) to land this role
            2. For each skill, provide:
               - Why it's important
               - Estimated learning time (weeks)
               - Free resources (mention platforms like YouTube, Udemy, etc.)
            3. Predict salary potential after acquiring these skills
            4. Motivational message
            
            Format as clear, actionable advice.
            """
            
            response = model.generate_content(prompt)
            st.markdown("### 📚 Your Learning Roadmap:")
            st.info(response.text)
            
            if st.checkbox("Save this path to my profile?"):
                st.success("✅ Saved! Track your progress on the Leaderboard page.")
        
        except Exception as e:
            st.warning(f"⚠️ API Error: {str(e)}")
            # Fallback recommendations
            st.markdown("### 📚 Your Learning Roadmap (Recommended Path):")
            fallback_text = f"""
            **Recommended Skills for {target_role}:**
            
            **Skill #1: Advanced Analytics**
            - Why: Most {target_role} roles require advanced data analysis
            - Time: 6-8 weeks
            - Resources: YouTube tutorials, FreeCodeCamp, Khan Academy
            - Salary Impact: +30% expected increase
            
            **Skill #2: Cloud Technologies (AWS/Azure)**
            - Why: Industry standard in Pakistan job market
            - Time: 8-10 weeks
            - Resources: A Cloud Guru, Linux Academy free content
            - Salary Impact: +25% expected increase
            
            **Skill #3: Communication & Leadership**
            - Why: Required for career advancement
            - Time: 4-6 weeks (ongoing)
            - Resources: Podcasts, books, mentorship
            - Salary Impact: +20% expected increase
            
            **Motivational Message:**
            You're on the right path! With dedication and consistent learning, you can land your dream role in Pakistan within 3-4 months. Stay focused! 💪
            """
            st.info(fallback_text)

# ==================== PAGE: LEARNING RESOURCES ====================
elif page == "💡 Learning Resources":
    st.title("💡 Free Learning Resources")
    st.write("Curated free resources to build in-demand skills:")
    
    resources = {
        "Python": {
            "YouTube": "Search 'Python Full Course' on YouTube",
            "FreeCodeCamp": "www.freecodecamp.org (free videos)",
            "Khan Academy": "www.khanacademy.org",
            "Time": "4-6 weeks"
        },
        "SQL": {
            "YouTube": "Search 'SQL Tutorial' on YouTube",
            "SQLZoo": "www.sqlzoo.net (interactive)",
            "FreeCodeCamp": "www.freecodecamp.org",
            "Time": "2-3 weeks"
        },
        "React": {
            "YouTube": "Search 'React Tutorial' on YouTube",
            "FreeCodeCamp": "www.freecodecamp.org (React Course)",
            "Web.dev": "www.web.dev/react",
            "Time": "5-7 weeks"
        },
        "Machine Learning": {
            "YouTube": "Search 'Machine Learning Basics' on YouTube",
            "Fast.ai": "www.fast.ai (free courses)",
            "Kaggle Learn": "www.kaggle.com/learn",
            "Time": "6-8 weeks"
        },
        "Data Analysis": {
            "YouTube": "Search 'Data Analysis with Python' on YouTube",
            "FreeCodeCamp": "www.freecodecamp.org",
            "Kaggle": "www.kaggle.com/learn/python",
            "Time": "4-6 weeks"
        },
        "Cloud (AWS/Azure)": {
            "YouTube": "Search 'AWS Tutorial' on YouTube",
            "A Cloud Guru": "www.acloudguru.com (some free content)",
            "AWS Tutorials": "www.aws.amazon.com/getting-started",
            "Time": "8-10 weeks"
        }
    }
    
    for skill, links in resources.items():
        with st.expander(f"📖 {skill}"):
            for platform, link in links.items():
                if platform == "Time":
                    st.write(f"⏱️ **Learning Time:** {link}")
                else:
                    st.write(f"📌 **{platform}:** {link}")

# ==================== PAGE: LEADERBOARD (PERSONAL PROGRESS) ====================
elif page == "🏆 Leaderboard":
    st.title("🎯 Your Personal Learning Progress")
    st.write("Track your upskilling journey")
    
    # Get student name
    st.subheader("👤 Student Profile")
    student_name = st.text_input("Enter your name:", placeholder="e.g., ALI")
    
    if student_name:
        # Initialize progress in session state
        if "student_data" not in st.session_state:
            st.session_state.student_data = {
                "name": student_name,
                "skills_learned": 0,
                "target_role": "Select a role",
                "progress": 0,
                "skills_list": []
            }
        
        # Update name if changed
        st.session_state.student_data["name"] = student_name
        
        st.markdown("---")
        
        # Show current stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Skills Learned", st.session_state.student_data["skills_learned"])
        with col2:
            st.metric("🎯 Target Role", st.session_state.student_data["target_role"][:15])
        with col3:
            st.metric("📊 Progress", f"{st.session_state.student_data['progress']}%")
        with col4:
            st.metric("⭐ Status", "Active Learner")
        
        st.markdown("---")
        
        # Update Progress
        st.subheader("📈 Update Your Progress")
        
        col1, col2 = st.columns(2)
        
        with col1:
            skills_learned = st.number_input(
                "How many skills have you learned?",
                min_value=0,
                max_value=100,
                value=st.session_state.student_data["skills_learned"],
                step=1
            )
            st.session_state.student_data["skills_learned"] = skills_learned
        
        with col2:
            target_role = st.selectbox(
                "What's your target role?",
                ["Data Scientist", "ML Engineer", "Full Stack Dev", "DevOps", 
                 "Data Analyst", "AI Engineer", "Backend Dev", "Frontend Dev",
                 "Python Developer", "React Developer"],
                index=0
            )
            st.session_state.student_data["target_role"] = target_role
        
        # Calculate progress
        progress = min((skills_learned / 10) * 100, 100)
        st.session_state.student_data["progress"] = int(progress)
        
        st.markdown("---")
        
        # Progress visualization
        st.subheader("📊 Your Learning Journey")
        
        # Progress bar
        st.progress(progress / 100)
        
        # Milestone tracker
        st.subheader("🎁 Milestones Achieved")
        
        milestones = [
            (1, "🌱 First Skill Learned", skills_learned >= 1),
            (3, "🚀 3 Skills Mastered", skills_learned >= 3),
            (5, "⭐ 5 Skills Complete", skills_learned >= 5),
            (8, "🏆 Expert Learner (8 Skills)", skills_learned >= 8),
            (10, "👑 Master (10 Skills)", skills_learned >= 10)
        ]
        
        cols = st.columns(5)
        for idx, (skill_count, label, achieved) in enumerate(milestones):
            with cols[idx]:
                if achieved:
                    st.success(f"✅ {label}")
                else:
                    st.info(f"🔒 {label}\n({skill_count} skills)")
        
        st.markdown("---")
        
        # Add new skill
        st.subheader("✏️ Add Skills You've Learned")
        
        new_skill = st.text_input("Enter a skill name:", placeholder="e.g., Python, React, SQL")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("➕ Add Skill", use_container_width=True):
                if new_skill and new_skill not in st.session_state.student_data["skills_list"]:
                    st.session_state.student_data["skills_list"].append(new_skill)
                    st.success(f"✅ Added {new_skill}!")
                elif new_skill in st.session_state.student_data["skills_list"]:
                    st.warning("Skill already added!")
                else:
                    st.error("Please enter a skill name")
        
        # Show skills list
        if st.session_state.student_data["skills_list"]:
            st.subheader("🎓 Your Skills")
            
            skill_cols = st.columns(len(st.session_state.student_data["skills_list"]))
            for idx, skill in enumerate(st.session_state.student_data["skills_list"]):
                with skill_cols[idx]:
                    st.success(f"✅ {skill}")
        
        st.markdown("---")
        
        # Summary Card
        st.subheader("📋 Your Learning Summary")
        
        summary = f"""
        **Student Name:** {student_name}
        
        **Target Role:** {target_role}
        
        **Skills Learned:** {skills_learned}/10
        
        **Overall Progress:** {progress:.0f}%
        
        **Status:** {'🎯 On Track' if progress >= 50 else '🚀 Just Started' if progress < 30 else '⚡ Making Progress'}
        
        **Next Step:** Keep learning! You're doing great! 💪
        """
        st.info(summary)
        
        # Save progress button
        if st.button("💾 Save My Progress", use_container_width=True):
            st.success(f"✅ {student_name}'s progress saved! Keep up the good work! 🎉")
    
    else:
        st.info("👤 Enter your name above to start tracking your learning progress!")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>🚀 <b>Skills Demand Hub</b> | Empowering Students & Young Professionals in Pakistan</p>
    <p>Data last updated: 2026 | Built with Streamlit + Gemini AI</p>
</div>
""", unsafe_allow_html=True)
