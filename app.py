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
        background: linear-gradient(135deg, #0a0b1e 0%, #1a1b3a 25%, #2d1b4e 50%, #1e2c5a 75%, #0f1419 100%) !important;
        color: white !important;
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
        overflow-y: auto;
    }
    .main, .block-container {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 24px;
        box-shadow: 0 32px 64px -12px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(59, 130, 246, 0.1);
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        color: #f1f5f9 !important;
        position: relative;
        overflow: visible;
        max-height: none;
        height: auto;
    }
    .main::before, .block-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 50%, rgba(16, 185, 129, 0.05) 100%);
        pointer-events: none;
        z-index: -1;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 50%, #1e40af 100%);
        color: white;
        border-radius: 16px;
        border: none;
        padding: 0.9em 2.5em;
        font-weight: 700;
        font-size: 1.1em;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4), 0 0 0 1px rgba(59, 130, 246, 0.2);
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
    }
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    .stButton>button:hover::before {
        left: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e3a8a 100%);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.5), 0 0 0 1px rgba(59, 130, 246, 0.3);
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        background: rgba(15, 23, 42, 0.9);
        border-radius: 16px;
        border: 2px solid rgba(59, 130, 246, 0.2);
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        font-size: 1.05em;
    }
    .stTextInput>div>input:focus, .stTextArea>div>textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), 0 8px 25px rgba(59, 130, 246, 0.2);
        background: rgba(15, 23, 42, 0.95);
        transform: scale(1.01);
    }
    .stSelectbox>div>div>div>div {
        background: rgba(15, 23, 42, 0.9);
        border-radius: 16px;
        border: 2px solid rgba(59, 130, 246, 0.2);
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
    }
    .stSelectbox>div>div>div>div>div {
        color: #f1f5f9 !important;
    }
    .stSelectbox option {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    .stRadio>div>label {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1em !important;
        text-shadow: 0 0 10px rgba(241, 245, 249, 0.3) !important;
    }
    .stRadio>div>div>label {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.05em !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
    }
    .stRadio>div>div>label>div {
        color: #f1f5f9 !important;
    }
    .stRadio>div>div {
        color: #f1f5f9 !important;
    }
    .stSelectbox>div>label {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1em !important;
        text-shadow: 0 0 10px rgba(241, 245, 249, 0.3) !important;
    }
    .stTextArea>div>label {
        color: #f1f5f9 !important;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        font-size: 1.1em;
        text-shadow: 0 0 10px rgba(241, 245, 249, 0.3);
    }
    .stFileUploader>div>label {
        color: #f1f5f9 !important;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        font-size: 1.1em;
        text-shadow: 0 0 10px rgba(241, 245, 249, 0.3);
    }
    .stProgress>div>div>div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #06b6d4 100%) !important;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    .stDownloadButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%);
        color: white;
        border-radius: 16px;
        border: none;
        font-weight: 700;
        font-size: 1.1em;
        padding: 0.9em 2.5em;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4), 0 0 0 1px rgba(139, 92, 246, 0.2);
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
    }
    .stDownloadButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    .stDownloadButton>button:hover::before {
        left: 100%;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 50%, #5b21b6 100%);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.5), 0 0 0 1px rgba(139, 92, 246, 0.3);
    }
    .stAlert {
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.9);
        border: 2px solid rgba(59, 130, 246, 0.3);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    /* Ensure text visibility - AGGRESSIVE OVERRIDES */
    .main, .block-container, .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div>div {
        color: #f1f5f9 !important;
    }
    /* Additional text styling for better visibility */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f1f5f9 !important;
    }
    label, .stSelectbox label, .stTextArea label, .stTextInput label, .stFileUploader label {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
    }
    /* FORCE ALL TEXT TO BE VISIBLE */
    * {
        color: #f1f5f9 !important;
    }
    .stApp, .main, .block-container, div, p, span, label, input, textarea, select {
        color: #f1f5f9 !important;
    }
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 12px;
        border: 2px solid rgba(15, 23, 42, 0.3);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    /* File uploader styling */
    .stFileUploader>div>div>div {
        background: rgba(15, 23, 42, 0.9);
        border: 3px dashed rgba(59, 130, 246, 0.4);
        border-radius: 20px;
        transition: all 0.4s ease;
        backdrop-filter: blur(15px);
        position: relative;
        overflow: hidden;
    }
    .stFileUploader>div>div>div::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .stFileUploader>div>div>div:hover {
        border-color: #3b82f6;
        background: rgba(15, 23, 42, 0.95);
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
    }
    .stFileUploader>div>div>div:hover::before {
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo/Hero Section --- #
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 2em; margin-bottom: 1.5em; padding: 2rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.15) 50%, rgba(6, 182, 212, 0.15) 100%); border-radius: 24px; border: 2px solid rgba(59, 130, 246, 0.3); backdrop-filter: blur(20px); box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 50%, rgba(6, 182, 212, 0.1) 100%); opacity: 0.7;"></div>
        <div style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06b6d4 100%); padding: 1.5rem; border-radius: 20px; box-shadow: 0 12px 30px rgba(59, 130, 246, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1); position: relative; z-index: 1;">
            <img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" width="72" height="72" style="filter: brightness(0) invert(1); animation: pulse 2s infinite;"/>
        </div>
        <div style="position: relative; z-index: 1;">
            <h1 style="margin-bottom: 0.3em; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 3.2em; font-weight: 900; letter-spacing: -2px; font-family: 'Inter', sans-serif; text-shadow: 0 0 30px rgba(96, 165, 250, 0.3);">🚀 AI GRADING ASSISTANT 🚀</h1>
            <div style="color: #ffffff; font-size: 1.3em; font-weight: 600; font-family: 'Inter', sans-serif; text-shadow: 0 2px 15px rgba(255, 255, 255, 0.6); opacity: 0.95;">✨ Revolutionary AI-powered essay analysis and intelligent feedback ✨</div>
        </div>
    </div>
    <style>
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Force deployment refresh - text visibility update
st.markdown(
    """
    <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%); 
                border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.15); backdrop-filter: blur(10px);
                box-shadow: 0 8px 25px rgba(59, 130, 246, 0.1);">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">
            <div style="position: relative;">
                <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); 
                                padding: 0.6rem; border-radius: 10px; 
                                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);">
                        <span style="font-size: 1.2rem;">🚀</span>
                    </div>
                    <h3 style="color: #f1f5f9; font-weight: 700; font-size: 1.2rem; margin: 0; 
                               text-shadow: 0 2px 8px rgba(241, 245, 249, 0.3);">Choose Input Mode</h3>
                </div>
            </div>
            
            <div style="position: relative;">
                <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%); 
                                padding: 0.6rem; border-radius: 10px; 
                                box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);">
                        <span style="font-size: 1.2rem;">🎯</span>
                    </div>
                    <h3 style="color: #f1f5f9; font-weight: 700; font-size: 1.2rem; margin: 0; 
                               text-shadow: 0 2px 8px rgba(241, 245, 249, 0.3);">Select Level</h3>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    /* Enhanced Radio Button Styling */
    .stRadio > div > div {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 2px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        margin: 0.4rem 0 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(8px) !important;
    }
    
    .stRadio > div > div:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        background: rgba(15, 23, 42, 0.7) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* Enhanced Selectbox Styling */
    .stSelectbox > div > div > div {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 2px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(8px) !important;
    }
    
    .stSelectbox > div > div > div:hover {
        border-color: rgba(139, 92, 246, 0.4) !important;
        background: rgba(15, 23, 42, 0.7) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.15) !important;
    }
    
    /* Responsive grid */
    @media (max-width: 768px) {
        .stApp div[data-testid="column"] {
            grid-template-columns: 1fr !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

upload_mode = st.radio("", ("📝 Single Essay", "📊 Batch Upload (CSV)"))
level = st.selectbox("", ("🎓 High School", "🎓 College", "💼 Professional"))

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