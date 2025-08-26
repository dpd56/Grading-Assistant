import openai
import os
import streamlit as st
import csv
import pandas as pd
from io import StringIO
from dotenv import load_dotenv  # Load environment variables from .env file

load_dotenv()  # Load environment variables from .env file

# Get API key from environment or Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY")

# Try multiple ways to get the API key from Streamlit secrets
if not api_key:
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

openai.api_key = api_key

# Check if API key is configured
if not api_key:
    st.error("⚠️ OpenAI API key not found. Please configure it in your environment variables or Streamlit secrets.")
    st.error("Debug info: Make sure your secrets are saved correctly in Streamlit Cloud.")
    st.stop()

# ----------- GRADING ASSISTANT LOGIC ----------- #
def grade_essay_with_feedback(essay_text: str, level: str) -> str:
    level_instructions = {
        "High School": "Evaluate as an experienced high school English teacher. Focus on fundamental writing skills: clear thesis statements, basic paragraph structure, grammar fundamentals, and developing analytical thinking. Encourage growth while being supportive of developing writers.",
        "College": "Evaluate as a college professor with high academic standards. Emphasize sophisticated argumentation, college-level analysis, proper citation and evidence use, advanced writing mechanics, and critical thinking skills appropriate for undergraduate work.",
        "Professional": "Evaluate as a professional editor and writing coach. Apply the highest standards for clarity, precision, persuasiveness, and polish. Expect publication-quality writing with sophisticated analysis, flawless mechanics, and compelling argumentation suitable for professional or graduate-level work."
    }

    prompt = (
        f"You are an expert writing instructor and educational AI assistant grading a student essay. {level_instructions[level]}\n\n"
        
        "🎯 GRADING FRAMEWORK:\n"
        "Use the comprehensive rubric below to provide detailed, constructive feedback that helps students improve their writing skills.\n\n"
        
        "📊 RUBRIC CRITERIA (each scored out of 20 points):\n\n"
        
        "1. 💡 THESIS & ARGUMENT CLARITY (20 points):\n"
        "   • 18-20: Exceptional thesis that is specific, arguable, and sophisticated. Consistently supported throughout.\n"
        "   • 15-17: Strong, clear thesis with good support. Minor inconsistencies.\n"
        "   • 12-14: Adequate thesis but may lack specificity or depth. Some support issues.\n"
        "   • 9-11: Weak or vague thesis. Limited support.\n"
        "   • 0-8: Unclear, missing, or non-arguable thesis.\n\n"
        
        "2. 📚 EVIDENCE & ANALYSIS (20 points):\n"
        "   • 18-20: Compelling, relevant evidence with deep analysis. Multiple types of support.\n"
        "   • 15-17: Good evidence with solid analysis. Most examples are relevant.\n"
        "   • 12-14: Adequate evidence but analysis may be superficial or examples weak.\n"
        "   • 9-11: Limited evidence with minimal analysis.\n"
        "   • 0-8: Little to no supporting evidence or analysis.\n\n"
        
        "3. 🏗️ ORGANIZATION & STRUCTURE (20 points):\n"
        "   • 18-20: Sophisticated organization with seamless transitions. Clear introduction, body, conclusion.\n"
        "   • 15-17: Well-organized with good transitions. Logical flow.\n"
        "   • 12-14: Generally organized but may have some structural issues or weak transitions.\n"
        "   • 9-11: Some organization present but confusing structure.\n"
        "   • 0-8: Poor or no clear organizational pattern.\n\n"
        
        "4. ✍️ WRITING MECHANICS & STYLE (20 points):\n"
        "   • 18-20: Exceptional grammar, varied sentence structure, engaging style.\n"
        "   • 15-17: Strong writing with minor errors. Good sentence variety.\n"
        "   • 12-14: Generally correct with some grammar/style issues that don't impede understanding.\n"
        "   • 9-11: Noticeable errors that occasionally distract from meaning.\n"
        "   • 0-8: Frequent errors that significantly impede comprehension.\n\n"
        
        "5. 🧠 CRITICAL THINKING & ORIGINALITY (20 points):\n"
        "   • 18-20: Original insights, complex thinking, addresses counterarguments.\n"
        "   • 15-17: Good analysis with some original thinking.\n"
        "   • 12-14: Basic analysis with limited original insight.\n"
        "   • 9-11: Minimal critical thinking or originality.\n"
        "   • 0-8: Lacks critical analysis or original thought.\n\n"
        
        "📋 RESPONSE FORMAT:\n"
        "Provide your feedback in this structure:\n\n"
        
        "## 🎯 OVERALL GRADE\n"
        "**Score: [X]/100 | Letter Grade: [X]**\n\n"
        
        "## 📊 DETAILED BREAKDOWN\n"
        "• **Thesis & Argument:** [X]/20 - [brief comment]\n"
        "• **Evidence & Analysis:** [X]/20 - [brief comment]\n"
        "• **Organization:** [X]/20 - [brief comment]\n"
        "• **Writing Mechanics:** [X]/20 - [brief comment]\n"
        "• **Critical Thinking:** [X]/20 - [brief comment]\n\n"
        
        "## 💪 STRENGTHS\n"
        "[Highlight 2-3 specific things the student did well]\n\n"
        
        "## 🎯 AREAS FOR IMPROVEMENT\n"
        "[Identify 2-3 key areas with specific, actionable suggestions]\n\n"
        
        "## ✏️ SPECIFIC REVISIONS\n"
        "[Quote specific sentences/phrases that need work and provide rewritten examples]\n\n"
        
        "## 🚀 NEXT STEPS\n"
        "[Provide 1-2 concrete actions the student can take to improve their writing]\n\n"
        
        "GRADING SCALE:\n"
        "A+ = 97-100, A = 93-96, A- = 90-92, B+ = 87-89, B = 83-86, B- = 80-82,\n"
        "C+ = 77-79, C = 73-76, C- = 70-72, D+ = 67-69, D = 63-66, D- = 60-62, F = below 60\n\n"
        
        "Be encouraging but honest. Focus on growth and specific improvements rather than just pointing out flaws."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": essay_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error grading essay: {str(e)}"

def export_grades_csv(grades: list) -> str:
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Essay (excerpt)", "Feedback"])
    writer.writerows(grades)
    return csv_buffer.getvalue()

# ----------- STREAMLIT UI ----------- #

# --- Custom CSS for modern dark theme with emerald accents --- #
st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    body, .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }
    .main, .block-container {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 20px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        color: #e2e8f0 !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.75em 2em;
        font-weight: 600;
        font-size: 1.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        font-family: 'Inter', sans-serif;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
        transition: border-color 0.2s ease;
    }
    .stTextInput>div>input:focus, .stTextArea>div>textarea:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }
    .stSelectbox>div>div>div>div {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }
    .stRadio>div>label {
        color: #10b981;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    .stProgress>div>div>div {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
        border-radius: 10px;
    }
    .stDownloadButton>button {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        font-size: 1.1em;
        padding: 0.75em 2em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        font-family: 'Inter', sans-serif;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
    }
    .stAlert {
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    /* Ensure text visibility */
    .main, .block-container, .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div>div {
        color: #e2e8f0 !important;
    }
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 10px;
    }
    /* File uploader styling */
    .stFileUploader>div>div>div {
        background: rgba(15, 23, 42, 0.8);
        border: 2px dashed rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stFileUploader>div>div>div:hover {
        border-color: #10b981;
        background: rgba(16, 185, 129, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo/Hero Section --- #
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 1.5em; margin-bottom: 1em; padding: 1.5rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%); border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2);">
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 1rem; border-radius: 16px; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);">
            <img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" width="64" height="64" style="filter: brightness(0) invert(1);"/>
        </div>
        <div>
            <h1 style="margin-bottom: 0.2em; background: linear-gradient(135deg, #10b981 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.8em; font-weight: 800; letter-spacing: -1px; font-family: 'Inter', sans-serif;">🚀 UPDATED GRADING ASSISTANT AI 🚀</h1>
            <div style="color: #94a3b8; font-size: 1.2em; font-weight: 500; font-family: 'Inter', sans-serif;">✨ Intelligent essay grading with AI-powered feedback and insights ✨</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

upload_mode = st.radio("🚀 Choose input mode:", ("📝 Single Essay", "📊 Batch Upload (CSV)"))
level = st.selectbox("🎯 Select Evaluation Level:", ("🎓 High School", "🎓 College", "💼 Professional"))

grades = []

if upload_mode == "📝 Single Essay":
    essay_input = st.text_area("✍️ Paste Essay Here:", height=300, placeholder="Paste your essay text here for AI analysis...")
    if st.button("🤖 Grade Essay with AI"):
        if essay_input.strip():
            with st.spinner("🔍 AI is analyzing your essay..."):
                output = grade_essay_with_feedback(essay_input, level.split(' ', 1)[1])  # Remove emoji from level
            grades.append([essay_input[:30] + "...", output])
            st.subheader("📋 AI Analysis Results")
            st.markdown(output)
        else:
            st.warning("⚠️ Please enter an essay before grading.")

elif upload_mode == "📊 Batch Upload (CSV)":
    uploaded_csv = st.file_uploader("📁 Upload a CSV with a column named 'Essay'", type="csv")
    if uploaded_csv:
        try:
            df = pd.read_csv(uploaded_csv)
            if "Essay" in df.columns:
                st.info(f"📊 Found {len(df)} essays to process!")
                progress_bar = st.progress(0)
                for idx, row in df.iterrows():
                    feedback = grade_essay_with_feedback(row["Essay"], level.split(' ', 1)[1])  # Remove emoji from level
                    grades.append([row["Essay"][:30] + "...", feedback])
                    progress_bar.progress((idx + 1) / len(df))
                st.success("✅ Batch grading completed successfully!")
            else:
                st.error("❌ CSV must contain a column labeled 'Essay'.")
        except Exception as e:
            st.error(f"💥 Error processing CSV: {e}")

# ----------- CSV Export Option ----------- #
if grades:
    csv_data = export_grades_csv(grades)
    st.download_button("� Download Feedback as CSV", csv_data, "graded_essays.csv", "text/csv")