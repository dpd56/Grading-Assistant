import openai
import os
import streamlit as st
import csv
import pandas as pd
from io import StringIO
from dotenv import load_dotenv  # Load environment variables from .env file

load_dotenv()  # Load environment variables from .env file

openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure OpenAI API key is set

# ----------- GRADING ASSISTANT LOGIC ----------- #
def grade_essay_with_feedback(essay_text: str, level: str) -> str:
    level_instructions = {
        "High School": "Evaluate as a high school teacher focusing on basic structure, clarity, and grammar.",
        "College": "Evaluate as a college professor emphasizing argument strength, evidence, and academic tone.",
        "Professional": "Evaluate as a professional editor, emphasizing critical thinking, precision, and polish."
    }

    prompt = (
        f"You are an expert writing instructor grading a student essay. {level_instructions[level]}\n"
        "Use the rubric below to assign a detailed score out of 100 and provide constructive feedback.\n\n"
        "Rubric Criteria (each scored out of 20 points):\n"
        "1. Thesis Clarity (20 points):\n"
        "   - 17-20: Clear, specific, and consistently supported thesis.\n"
        "   - 13-16: Clear thesis but may lack depth or consistent support.\n"
        "   - 9-12: Weak or vague thesis.\n"
        "   - 0-8: Unclear or missing thesis.\n\n"
        "2. Evidence and Examples (20 points):\n"
        "   - 17-20: Strong, relevant, and persuasive evidence throughout.\n"
        "   - 13-16: Adequate evidence, but may lack specificity or depth.\n"
        "   - 9-12: Weak or minimal evidence.\n"
        "   - 0-8: Lacks supporting evidence.\n\n"
        "3. Organization and Flow (20 points):\n"
        "   - 17-20: Clear structure and excellent flow between paragraphs.\n"
        "   - 13-16: Generally logical structure with minor issues.\n"
        "   - 9-12: Some disorganization or weak transitions.\n"
        "   - 0-8: Poor or confusing structure.\n\n"
        "4. Grammar and Style (20 points):\n"
        "   - 17-20: Virtually no errors, strong and effective style.\n"
        "   - 13-16: Some grammar/style issues that don't significantly distract.\n"
        "   - 9-12: Noticeable issues that detract from clarity.\n"
        "   - 0-8: Frequent grammar/style issues.\n\n"
        "5. Critical Thinking and Insight (20 points):\n"
        "   - 17-20: Deep analysis and original insight.\n"
        "   - 13-16: Reasonable insight with some depth.\n"
        "   - 9-12: Basic analysis, lacks depth.\n"
        "   - 0-8: Superficial or absent analysis.\n\n"
        "Instructions:\n"
        "- Provide a score for each category (out of 20).\n"
        "- Sum the scores to calculate the final grade out of 100.\n"
        "- Provide the corresponding letter grade using this scale:\n"
        "   A = 93-100, A- = 90-92, B+ = 87-89, B = 83-86, B- = 80-82,\n"
        "   C+ = 77-79, C = 73-76, C- = 70-72, D = 60-69, F = below 60\n"
        "- Give overall feedback and suggestions for improvement.\n"
        "- Highlight specific sentences that need revision and explain why.\n"
        "- If grammar issues are present, suggest how to rewrite the sentences."
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

# --- Custom CSS for blue/white theme --- #
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #f7fbff;
        color: #1e293b !important;
    }
    .main, .block-container {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        padding: 2rem 2rem 1rem 2rem;
        color: #1e293b !important;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
        font-weight: 600;
        font-size: 1.1em;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #1e40af;
        color: #fff;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        background: #f0f6ff;
        border-radius: 6px;
        border: 1px solid #2563eb22;
        color: #1e293b !important;
    }
    .stSelectbox>div>div>div>div {
        background: #f0f6ff;
        border-radius: 6px;
        border: 1px solid #2563eb22;
        color: #1e293b !important;
    }
    .stRadio>div>label {
        color: #2563eb;
        font-weight: 600;
    }
    .stProgress>div>div>div {
        background-color: #2563eb !important;
    }
    .stDownloadButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        font-size: 1.1em;
        transition: background 0.2s;
    }
    .stDownloadButton>button:hover {
        background-color: #1e40af;
        color: #fff;
    }
    .stAlert {
        border-radius: 8px;
    }
    /* Removed universal selector to avoid unintended side effects */
    /* Ensure all text in main content is dark */
    .main, .block-container, .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div>div, .stDownloadButton>button, .stButton>button {
        color: #1e293b !important;
    }
)

# --- Logo/Hero Section --- #
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 1.2em; margin-bottom: 0.5em;">
        <img src="https://img.icons8.com/color/96/000000/grade.png" width="60" height="60" style="border-radius: 12px; box-shadow: 0 2px 8px rgba(37,99,235,0.08);"/>
        <div>
            <h1 style="margin-bottom: 0.1em; color: #2563eb; font-size: 2.3em; font-weight: 800; letter-spacing: -1px;">Grading Assistant AI</h1>
            <div style="color: #1e293b; font-size: 1.1em; font-weight: 500;">Grade and improve student essays with AI-powered feedback</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

upload_mode = st.radio("Choose input mode:", ("Single Essay", "Batch Upload (CSV)"))
level = st.selectbox("Select Evaluation Level:", ("High School", "College", "Professional"))

grades = []

if upload_mode == "Single Essay":
    essay_input = st.text_area("Paste Essay Here:", height=300)
    if st.button("Grade Essay"):
        if essay_input.strip():
            with st.spinner("Grading essay..."):
                output = grade_essay_with_feedback(essay_input, level)
            grades.append([essay_input[:30] + "...", output])
            st.subheader("Results")
            st.markdown(output)
        else:
            st.warning("Please enter an essay before grading.")

elif upload_mode == "Batch Upload (CSV)":
    uploaded_csv = st.file_uploader("Upload a CSV with a column named 'Essay'", type="csv")
    if uploaded_csv:
        try:
            df = pd.read_csv(uploaded_csv)
            if "Essay" in df.columns:
                progress_bar = st.progress(0)
                for idx, row in df.iterrows():
                    feedback = grade_essay_with_feedback(row["Essay"], level)
                    grades.append([row["Essay"][:30] + "...", feedback])
                    progress_bar.progress((idx + 1) / len(df))
                st.success("Batch grading completed.")
            else:
                st.error("CSV must contain a column labeled 'Essay'.")
        except Exception as e:
            st.error(f"Error processing CSV: {e}")

# ----------- CSV Export Option ----------- #
if grades:
    csv_data = export_grades_csv(grades)
    st.download_button("📥 Download Feedback as CSV", csv_data, "graded_essays.csv", "text/csv")