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
        f"You are an expert writing instructor with 15+ years of experience grading student essays. {level_instructions[level]}\n\n"
        
        "🎯 ENHANCED GRADING FRAMEWORK:\n"
        "Apply this comprehensive rubric to provide detailed, actionable feedback that drives student improvement. Consider consistency, specificity, and developmental appropriateness in your evaluation.\n\n"
        
        "📚 BENCHMARK REFERENCE - EXEMPLARY COLLEGE ESSAY (95/100):\n"
        "Use this high-performing college essay as a reference point for quality standards, but adjust expectations appropriately for developmental level. This benchmark essay demonstrates:\n"
        "- EXCEPTIONAL thesis: Clear stance on NCAA settlement's impact on non-revenue sports\n"
        "- SOPHISTICATED argumentation: Multi-faceted analysis with cause-effect reasoning\n"
        "- STRONG evidence integration: Current events (House v. NCAA), specific data, real examples\n"
        "- EXCELLENT organization: Logical flow from problem to impact to solutions\n"
        "- PROFICIENT writing mechanics: Clear, engaging prose with varied sentence structure\n"
        "- ORIGINAL critical thinking: Nuanced perspective on complex issue with practical solutions\n\n"
        
        "Key strengths to look for based on this benchmark (adjust expectations for student level):\n"
        "• Specific, arguable thesis that takes a clear position\n"
        "• Integration of current events and real-world examples\n"
        "• Logical progression from problem identification to solution proposal\n"
        "• Use of credible sources and specific data/statistics\n"
        "• Consideration of multiple stakeholders and perspectives\n"
        "• Practical, actionable solutions supported by evidence\n"
        "• Engaging introduction that establishes stakes and importance\n"
        "• Strong conclusion that reinforces main argument and broader implications\n\n"
        
        "📊 DETAILED RUBRIC CRITERIA (each scored out of 20 points):\n\n"
        
        "1. 💡 THESIS & ARGUMENT DEVELOPMENT (20 points):\n"
        "   • 18-20 (EXCEPTIONAL): Crystal-clear, sophisticated thesis that takes a compelling, nuanced position (like the NCAA essay's stance on protecting non-revenue sports). Arguments are logically sequenced, well-reasoned, and demonstrate deep understanding. Counter-arguments or complexities addressed thoughtfully.\n"
        "   • 15-17 (PROFICIENT): Strong, specific thesis with clear argument structure. Most claims are well-developed and supported. Shows good understanding of topic complexity and multiple perspectives.\n"
        "   • 12-14 (DEVELOPING): Thesis present and generally clear, though may lack some specificity or sophistication. Arguments are adequate and show understanding, with room for deeper development.\n"
        "   • 9-11 (EMERGING): Basic thesis present but may be unclear or overly broad. Arguments need development but show some effort toward logical structure.\n"
        "   • 0-8 (INADEQUATE): No identifiable thesis or argument structure. Claims are unsupported, contradictory, or missing entirely.\n\n"
        
        "2. 📚 EVIDENCE & ANALYSIS QUALITY (20 points):\n"
        "   • 18-20 (EXCEPTIONAL): Rich, credible evidence from multiple high-quality sources (current events, data, real examples like the Stanford case study). Analysis is sophisticated, insightful, and goes beyond surface-level observations. Evidence seamlessly integrated and supports all major claims.\n"
        "   • 15-17 (PROFICIENT): Good variety of relevant evidence with solid analysis. Sources are credible and mostly well-integrated. Analysis shows clear understanding and some original insight.\n"
        "   • 12-14 (DEVELOPING): Adequate evidence with basic analysis that demonstrates understanding. Some examples provided, though analysis could be deeper. Evidence generally supports the argument.\n"
        "   • 9-11 (EMERGING): Limited evidence but shows effort to support claims. Analysis is basic but present. Some sources may be weak but attempts at integration are made.\n"
        "   • 0-8 (INADEQUATE): Little to no evidence provided. No meaningful analysis present.\n\n"
        
        "3. 🏗️ ORGANIZATION & COHERENCE (20 points):\n"
        "   • 18-20 (EXCEPTIONAL): Masterful organization with seamless transitions and perfect logical flow (problem→impact→solutions structure). Introduction hooks reader and clearly previews structure. Conclusion synthesizes ideas powerfully and addresses broader implications.\n"
        "   • 15-17 (PROFICIENT): Well-organized with effective transitions between ideas. Clear introduction, focused body paragraphs with topic sentences, and strong conclusion that reinforces main argument.\n"
        "   • 12-14 (DEVELOPING): Generally well-organized with basic structure evident. Introduction, body, and conclusion present. Some transitions may be simple but structure is clear and logical.\n"
        "   • 9-11 (EMERGING): Basic organization present with identifiable paragraphs. Structure may be simple but shows understanding of essay format. Some organizational issues but overall coherent.\n"
        "   • 0-8 (INADEQUATE): No clear organizational pattern. Ideas presented randomly or incoherently.\n\n"
        
        "4. ✍️ LANGUAGE MASTERY & STYLE (20 points):\n"
        "   • 18-20 (EXCEPTIONAL): Exceptional command of language with varied, sophisticated sentence structure. Precise, engaging word choice and tone appropriate for audience. Virtually error-free mechanics.\n"
        "   • 15-17 (PROFICIENT): Strong control of language with clear, effective writing. Minor errors don't impede understanding. Good sentence variety and appropriate style.\n"
        "   • 12-14 (DEVELOPING): Generally clear and readable language with adequate word choice. Some mechanical errors but meaning remains clear. Writing communicates ideas effectively with room for refinement.\n"
        "   • 9-11 (EMERGING): Basic language use that conveys meaning adequately. Some errors present but don't significantly interfere with comprehension. Simple but functional style.\n"
        "   • 0-8 (INADEQUATE): Serious mechanical problems that severely impact comprehension. Very limited language control.\n\n"
        
        "5. 🧠 CRITICAL THINKING & INTELLECTUAL DEPTH (20 points):\n"
        "   • 18-20 (EXCEPTIONAL): Demonstrates exceptional critical thinking with original insights and intellectual depth (like analyzing unintended consequences of NCAA settlement on non-revenue sports). Makes connections others might miss. Challenges assumptions thoughtfully and considers multiple stakeholder perspectives with practical solutions.\n"
        "   • 15-17 (PROFICIENT): Shows good critical thinking with some original ideas. Goes beyond obvious interpretations and demonstrates independent thought with consideration of multiple viewpoints.\n"
        "   • 12-14 (DEVELOPING): Basic critical thinking present with some analysis beyond summary. Shows effort to think independently about the topic, though insights may be straightforward or obvious.\n"
        "   • 9-11 (EMERGING): Some attempt at analysis or personal perspective, though may rely heavily on summary. Shows beginning stages of critical thinking development.\n"
        "   • 0-8 (INADEQUATE): No evidence of critical thinking. Purely descriptive or factual with no analysis or original perspective.\n\n"
        
        "📋 ENHANCED RESPONSE FORMAT:\n"
        "Provide detailed, specific feedback using this structure:\n\n"
        
        "## 🎯 OVERALL GRADE\n"
        "**Score: [X]/100 | Letter Grade: [X] | Performance Level: [EXCEPTIONAL/PROFICIENT/DEVELOPING/EMERGING/INADEQUATE]**\n\n"
        
        "## 📊 COMPREHENSIVE BREAKDOWN\n"
        "• **Thesis & Argument Development:** [X]/20 - [Specific explanation with text examples]\n"
        "• **Evidence & Analysis Quality:** [X]/20 - [Specific explanation with text examples]\n"
        "• **Organization & Coherence:** [X]/20 - [Specific explanation with text examples]\n"
        "• **Language Mastery & Style:** [X]/20 - [Specific explanation with text examples]\n"
        "• **Critical Thinking & Depth:** [X]/20 - [Specific explanation with text examples]\n\n"
        
        "## 💪 NOTABLE STRENGTHS\n"
        "[Highlight 2-3 specific accomplishments with quoted examples from the text. Be specific about what makes these elements successful.]\n\n"
        
        "## 🎯 PRIORITY IMPROVEMENT AREAS\n"
        "[Identify 2-3 most impactful areas for improvement, ranked by importance. Explain why these areas matter and how improvement would elevate the overall essay.]\n\n"
        
        "## ✏️ CONCRETE REVISION EXAMPLES\n"
        "[Provide 3-4 specific examples: quote problematic text and offer improved versions. Show, don't just tell.]\n"
        "- ORIGINAL: \"[Quote from essay]\"\n"
        "- REVISED: \"[Your improved version]\"\n"
        "- WHY: [Brief explanation of improvement]\n\n"
        
        "## 🚀 ACTIONABLE NEXT STEPS\n"
        "1. **Immediate Action:** [One specific revision strategy for this essay]\n"
        "2. **Skill Building:** [One practice exercise for future essays]\n"
        "3. **Resource:** [Specific writing resource, technique, or area of study]\n\n"
        
        "## 📈 GROWTH TRACKING\n"
        "[Comment on progress indicators and what to focus on for continued improvement]\n\n"
        
        "GRADING SCALE:\n"
        "A+ = 97-100, A = 93-96, A- = 90-92, B+ = 87-89, B = 83-86, B- = 80-82,\n"
        "C+ = 77-79, C = 73-76, C- = 70-72, D+ = 67-69, D = 63-66, D- = 60-62, F = below 60\n\n"
        
        "**GRADING PRINCIPLES:**\n"
        "- Use the benchmark essay as a reference point while adjusting expectations appropriately for student level\n"
        "- Be encouraging and recognize effort while maintaining standards for growth\n"
        "- Focus on specific, actionable improvements that help students progress toward benchmark quality\n"
        "- Quote directly from the text when providing examples, showing how to build toward benchmark strengths\n"
        "- Consider the writer's developmental stage and celebrate progress while pushing for continued growth\n"
        "- Provide concrete strategies students can immediately implement to improve\n"
        "- Balance constructive criticism with recognition of effort and existing strengths\n"
        "- Look for evidence of benchmark qualities while acknowledging different levels of development\n"
        "- Aim to inspire improvement rather than discourage; be rigorous but fair and supportive"
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* MOBILE-FIRST RESPONSIVE DESIGN */
    html, body {
        -webkit-text-size-adjust: 100%;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Ensure proper mobile viewport */
    .stApp {
        touch-action: manipulation;
    }
    
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
    
    /* MOBILE RESPONSIVE LAYOUT */
    @media (max-width: 768px) {
        .main, .block-container {
            padding: 1.5rem 1rem 1rem 1rem !important;
            border-radius: 16px !important;
            margin: 0.5rem !important;
        }
        
        .stButton>button {
            width: 100% !important;
            padding: 1rem 1.5rem !important;
            font-size: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stTextArea>div>div>textarea {
            min-height: 200px !important;
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
        
        .stTextInput>div>div>input {
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
        
        .stSelectbox>div>div>div>div {
            font-size: 16px !important; /* Prevents zoom on iOS */
            min-height: 48px !important; /* Better touch targets */
        }
        
        .stRadio>div>div {
            margin-bottom: 1rem !important;
        }
        
        .stRadio>div>div>label {
            font-size: 1rem !important;
            padding: 0.75rem !important;
        }
        
        .stFileUploader>div>div>div {
            padding: 2rem 1rem !important;
            margin: 1rem 0 !important;
        }
        
        .stDownloadButton>button {
            width: 100% !important;
            padding: 1rem 1.5rem !important;
            font-size: 1rem !important;
            margin: 1rem 0 !important;
        }
        
        /* Better spacing for mobile */
        .stMarkdown {
            margin-bottom: 1rem !important;
        }
        
        /* Improve form labels on mobile */
        .stSelectbox>div>label,
        .stTextArea>div>label,
        .stTextInput>div>label,
        .stFileUploader>div>label,
        .stRadio>div>label {
            font-size: 1.1rem !important;
            margin-bottom: 0.5rem !important;
            display: block !important;
        }
    }
    
    @media (max-width: 480px) {
        .main, .block-container {
            padding: 1rem 0.75rem 0.75rem 0.75rem !important;
            border-radius: 12px !important;
            margin: 0.25rem !important;
        }
        
        .stButton>button {
            padding: 0.9rem 1.2rem !important;
            font-size: 0.95rem !important;
        }
        
        .stDownloadButton>button {
            padding: 0.9rem 1.2rem !important;
            font-size: 0.95rem !important;
        }
        
        .stTextArea>div>div>textarea {
            min-height: 180px !important;
        }
        
        /* Smaller form elements on very small screens */
        .stSelectbox>div>label,
        .stTextArea>div>label,
        .stTextInput>div>label,
        .stFileUploader>div>label,
        .stRadio>div>label {
            font-size: 1rem !important;
        }
        
        .stRadio>div>div>label {
            font-size: 0.95rem !important;
            padding: 0.6rem !important;
        }
    }
    
    /* TABLET RESPONSIVE */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main, .block-container {
            padding: 2rem 1.5rem 1.5rem 1.5rem !important;
        }
        
        .stButton>button,
        .stDownloadButton>button {
            padding: 0.8rem 2rem !important;
        }
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
        background: rgba(15, 23, 42, 0.9) !important;
        border-radius: 16px;
        border: 2px solid rgba(59, 130, 246, 0.2);
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        font-size: 1.05em;
    }
    .stTextInput input, .stTextArea textarea {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: rgba(241, 245, 249, 0.6) !important;
    }
    .stTextInput>div>input:focus, .stTextArea>div>textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), 0 8px 25px rgba(59, 130, 246, 0.2);
        background: rgba(15, 23, 42, 0.95) !important;
        color: #f1f5f9 !important;
        transform: scale(1.01);
    }
    .stSelectbox>div>div>div>div {
        background: rgba(15, 23, 42, 0.9) !important;
        border-radius: 16px;
        border: 2px solid rgba(59, 130, 246, 0.2);
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
        font-size: 1.05em;
        transition: all 0.3s ease;
    }
    .stSelectbox>div>div>div>div>div {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    .stSelectbox select {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    .stSelectbox option {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    /* Additional selectbox targeting */
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(15, 23, 42, 0.9) !important;
        color: #f1f5f9 !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    /* Dropdown menu styling when expanded */
    .stSelectbox ul[role="listbox"] {
        background: rgba(15, 23, 42, 0.95) !important;
        border: 2px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(15px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
    }
    .stSelectbox li[role="option"] {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.05em !important;
    }
    .stSelectbox li[role="option"]:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        color: #ffffff !important;
    }
    /* Target the dropdown options more aggressively */
    div[data-baseweb="popover"] ul {
        background: rgba(15, 23, 42, 0.95) !important;
        border: 2px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="popover"] li {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    div[data-baseweb="popover"] li:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        color: #ffffff !important;
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
    
    /* AGGRESSIVE TEXT INPUT FIXES */
    .stTextInput input, .stTextArea textarea, 
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    [data-testid="textInput"] input,
    [data-testid="textArea"] textarea {
        color: #f1f5f9 !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
        -webkit-text-fill-color: #f1f5f9 !important;
    }
    
    /* Target Streamlit's specific input classes */
    .st-emotion-cache-1y4p8pa input,
    .st-emotion-cache-1y4p8pa textarea {
        color: #f1f5f9 !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
    }
    
    /* Target Streamlit's specific dropdown classes */
    .st-emotion-cache-1y4p8pa select,
    .st-emotion-cache-1y4p8pa div[data-baseweb="select"],
    .st-emotion-cache-1y4p8pa ul[role="listbox"],
    .st-emotion-cache-1y4p8pa li[role="option"],
    .st-emotion-cache-1y4p8pa div[data-baseweb="popover"],
    [class*="st-emotion-cache"] ul[role="listbox"] li,
    [class*="st-emotion-cache"] div[data-baseweb="popover"] li,
    [class*="st-emotion-cache"] [role="option"] {
        color: #f1f5f9 !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
        -webkit-text-fill-color: #f1f5f9 !important;
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
    
    /* FINAL NUCLEAR OPTION FOR TEXT INPUTS */
    input[type="text"], textarea, select,
    .stTextInput input[type="text"],
    .stTextArea textarea,
    .stSelectbox select,
    div[data-testid="textInput"] input,
    div[data-testid="textArea"] textarea,
    div[data-testid="selectbox"] select,
    div[data-baseweb="select"] > div,
    ul[role="listbox"] li,
    div[data-baseweb="popover"] li {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        -webkit-text-fill-color: #f1f5f9 !important;
        caret-color: #f1f5f9 !important;
    }
    
    /* AGGRESSIVE DROPDOWN TARGETING */
    [data-baseweb="popover"] {
        background: rgba(15, 23, 42, 0.95) !important;
    }
    [data-baseweb="popover"] * {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    [role="listbox"] {
        background: rgba(15, 23, 42, 0.95) !important;
    }
    [role="listbox"] * {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    [role="option"] {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    [role="option"]:hover {
        color: #ffffff !important;
        background: rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Override any Streamlit emotion cache classes */
    [class*="st-emotion-cache"] input,
    [class*="st-emotion-cache"] textarea,
    [class*="st-emotion-cache"] select,
    [class*="st-emotion-cache"] div[data-baseweb="select"],
    [class*="st-emotion-cache"] ul[role="listbox"],
    [class*="st-emotion-cache"] li[role="option"] {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        -webkit-text-fill-color: #f1f5f9 !important;
    }
    
    /* SPECIFIC FIXES FOR SELECTBOX DROPDOWN TEXT */
    .stSelectbox [data-baseweb="select"] {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #f1f5f9 !important;
        -webkit-text-fill-color: #f1f5f9 !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div > div {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* DROPDOWN MENU WHEN OPENED */
    [data-baseweb="popover"] {
        background: rgba(15, 23, 42, 0.98) !important;
        border: 2px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6) !important;
    }
    
    [data-baseweb="popover"] ul {
        background: transparent !important;
        padding: 8px !important;
    }
    
    [data-baseweb="popover"] li {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.7) !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        padding: 12px 16px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        -webkit-text-fill-color: #f1f5f9 !important;
    }
    
    [data-baseweb="popover"] li:hover {
        color: #ffffff !important;
        background: rgba(59, 130, 246, 0.4) !important;
        transform: translateX(4px) !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    [data-baseweb="popover"] li[aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(59, 130, 246, 0.6) !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    /* ADDITIONAL SELECTBOX TARGETING */
    .stSelectbox div[role="button"] {
        color: #f1f5f9 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        -webkit-text-fill-color: #f1f5f9 !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stSelectbox div[role="button"] span {
        color: #f1f5f9 !important;
        -webkit-text-fill-color: #f1f5f9 !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* FORCE ALL DROPDOWN COMPONENTS */
    div[data-testid="stSelectbox"] * {
        color: #f1f5f9 !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
        color: #f1f5f9 !important;
        -webkit-text-fill-color: #f1f5f9 !important;
        cursor: pointer !important;
        caret-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* HIDE CURSOR IN ALL SELECTBOX COMPONENTS */
    .stSelectbox,
    .stSelectbox *,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] *,
    div[data-testid="stSelectbox"],
    div[data-testid="stSelectbox"] * {
        caret-color: transparent !important;
        cursor: pointer !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* REMOVE FOCUS OUTLINES AND SELECTION BORDERS */
    .stSelectbox [data-baseweb="select"]:focus,
    .stSelectbox [data-baseweb="select"]:focus-within,
    .stSelectbox [data-baseweb="select"]:active,
    .stSelectbox div[role="button"]:focus,
    .stSelectbox div[role="button"]:focus-within,
    .stSelectbox div[role="button"]:active,
    div[data-testid="stSelectbox"] *:focus,
    div[data-testid="stSelectbox"] *:focus-within,
    div[data-testid="stSelectbox"] *:active {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* MOBILE DROPDOWN IMPROVEMENTS */
    @media (max-width: 768px) {
        [data-baseweb="popover"] {
            max-height: 60vh !important;
            overflow-y: auto !important;
        }
        
        [data-baseweb="popover"] li {
            padding: 16px 20px !important;
            font-size: 16px !important;
            min-height: 48px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        .stSelectbox [data-baseweb="select"] {
            min-height: 48px !important;
            font-size: 16px !important;
        }
        
        .stSelectbox [data-baseweb="select"] > div > div {
            min-height: 48px !important;
            display: flex !important;
            align-items: center !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo/Hero Section --- #
st.markdown(
    """
    <div class="hero-container" style="display: flex; align-items: center; gap: 2em; margin-bottom: 1.5em; padding: 2rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.15) 50%, rgba(6, 182, 212, 0.15) 100%); border-radius: 24px; border: 2px solid rgba(59, 130, 246, 0.3); backdrop-filter: blur(20px); box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 50%, rgba(6, 182, 212, 0.1) 100%); opacity: 0.7;"></div>
        <div class="hero-icon" style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06b6d4 100%); padding: 1.5rem; border-radius: 20px; box-shadow: 0 12px 30px rgba(59, 130, 246, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1); position: relative; z-index: 1;">
            <img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" width="72" height="72" style="filter: brightness(0) invert(1); animation: pulse 2s infinite;"/>
        </div>
        <div class="hero-text" style="position: relative; z-index: 1;">
            <h1 class="hero-title" style="margin-bottom: 0.3em; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 3.2em; font-weight: 900; letter-spacing: -2px; font-family: 'Inter', sans-serif; text-shadow: 0 0 30px rgba(96, 165, 250, 0.3);">🚀 AI GRADING ASSISTANT 🚀</h1>
            <div class="hero-subtitle" style="color: #ffffff; font-size: 1.3em; font-weight: 600; font-family: 'Inter', sans-serif; text-shadow: 0 2px 15px rgba(255, 255, 255, 0.6); opacity: 0.95;">✨ Revolutionary AI-powered essay analysis and intelligent feedback ✨</div>
        </div>
    </div>
    <style>
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* MOBILE RESPONSIVE STYLES */
    @media (max-width: 768px) {
        .hero-container {
            flex-direction: column !important;
            text-align: center !important;
            gap: 1.5em !important;
            padding: 1.5rem 1rem !important;
            margin-bottom: 1rem !important;
        }
        
        .hero-icon {
            padding: 1rem !important;
        }
        
        .hero-icon img {
            width: 56px !important;
            height: 56px !important;
        }
        
        .hero-title {
            font-size: 2em !important;
            letter-spacing: -1px !important;
            line-height: 1.1 !important;
            margin-bottom: 0.5em !important;
        }
        
        .hero-subtitle {
            font-size: 1em !important;
            line-height: 1.4 !important;
        }
    }
    
    @media (max-width: 480px) {
        .hero-title {
            font-size: 1.6em !important;
            letter-spacing: 0px !important;
        }
        
        .hero-subtitle {
            font-size: 0.9em !important;
        }
        
        .hero-container {
            padding: 1rem 0.75rem !important;
            border-radius: 16px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Force deployment refresh - text visibility update
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Inject aggressive CSS for dropdowns
    const style = document.createElement('style');
    style.textContent = `
        [data-baseweb="popover"] ul,
        [data-baseweb="popover"] li,
        [role="listbox"],
        [role="listbox"] li,
        [role="option"] {
            color: #f1f5f9 !important;
            background: rgba(15, 23, 42, 0.95) !important;
            -webkit-text-fill-color: #f1f5f9 !important;
        }
        [role="option"]:hover {
            color: #ffffff !important;
            background: rgba(59, 130, 246, 0.3) !important;
        }
    `;
    document.head.appendChild(style);
    
    // Force text color on all inputs after page loads
    setTimeout(function() {
        const inputs = document.querySelectorAll('input, textarea, select, div[data-baseweb="select"], ul[role="listbox"] li, div[data-baseweb="popover"] li, [role="option"]');
        inputs.forEach(input => {
            input.style.setProperty('color', '#f1f5f9', 'important');
            input.style.setProperty('background-color', 'rgba(15, 23, 42, 0.9)', 'important');
            input.style.setProperty('-webkit-text-fill-color', '#f1f5f9', 'important');
        });
    }, 100);
    
    // Monitor for new dropdown elements
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    const dropdownElements = node.querySelectorAll('[data-baseweb="popover"], [role="listbox"], [role="option"]');
                    dropdownElements.forEach(element => {
                        element.style.setProperty('color', '#f1f5f9', 'important');
                        element.style.setProperty('background', 'rgba(15, 23, 42, 0.95)', 'important');
                        element.style.setProperty('-webkit-text-fill-color', '#f1f5f9', 'important');
                    });
                    
                    // Also check if the node itself is a dropdown element
                    if (node.matches && (node.matches('[data-baseweb="popover"]') || node.matches('[role="listbox"]') || node.matches('[role="option"]'))) {
                        node.style.setProperty('color', '#f1f5f9', 'important');
                        node.style.setProperty('background', 'rgba(15, 23, 42, 0.95)', 'important');
                        node.style.setProperty('-webkit-text-fill-color', '#f1f5f9', 'important');
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
<style>
/* EMERGENCY TEXT FIX - HIGHEST PRIORITY */
input, textarea, select, div[data-baseweb="select"] > div, ul[role="listbox"] li, div[data-baseweb="popover"] li, [role="option"] {
    color: #f1f5f9 !important;
    background-color: rgba(15, 23, 42, 0.9) !important;
    -webkit-text-fill-color: #f1f5f9 !important;
}

/* EMERGENCY DROPDOWN FIX - SAME PRIORITY */
[class*="st-emotion-cache"] ul[role="listbox"],
[class*="st-emotion-cache"] ul[role="listbox"] li,
[class*="st-emotion-cache"] div[data-baseweb="popover"],
[class*="st-emotion-cache"] div[data-baseweb="popover"] li,
[class*="st-emotion-cache"] [role="option"],
ul[role="listbox"], 
ul[role="listbox"] li,
div[data-baseweb="popover"],
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] ul li {
    color: #f1f5f9 !important;
    background-color: rgba(15, 23, 42, 0.9) !important;
    -webkit-text-fill-color: #f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)

upload_mode = st.radio("🚀 Choose input mode:", ("📝 Single Essay", "📊 Batch Upload (CSV)"))
level = st.selectbox("🎯 Select Evaluation Level:", ("🎓 High School", "🎓 College", "💼 Professional"))

grades = []

if upload_mode == "📝 Single Essay":
    # Custom styled text area with forced colors
    st.markdown("""
    <style>
    .custom-textarea {
        width: 100%;
        height: 300px;
        background: rgba(15, 23, 42, 0.9) !important;
        color: #f1f5f9 !important;
        border: 2px solid rgba(59, 130, 246, 0.2);
        border-radius: 16px;
        padding: 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 1.05em;
        resize: vertical;
        outline: none;
        -webkit-text-fill-color: #f1f5f9 !important;
    }
    .custom-textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
    }
    .custom-textarea::placeholder {
        color: rgba(241, 245, 249, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    essay_input = st.text_area("✍️ Paste Essay Here:", height=300, placeholder="Paste your essay text here for AI analysis...", key="essay_input")
    if st.button("🤖 Grade Essay with AI"):
        # Add continuous color fixing
        st.markdown("""
        <script>
        // Continuous text color fix - AGGRESSIVE VERSION
        function fixTextColors() {
            // Target all possible dropdown selectors
            const selectors = [
                'input', 'textarea', 'select',
                'div[data-baseweb="select"]',
                'div[data-baseweb="select"] > div',
                'div[data-baseweb="select"] span',
                'div[data-baseweb="select"] *',
                'div[role="button"]',
                'div[role="button"] span',
                'ul[role="listbox"]',
                'ul[role="listbox"] li',
                'li[role="option"]',
                '[role="option"]',
                'div[data-baseweb="popover"]',
                'div[data-baseweb="popover"] ul',
                'div[data-baseweb="popover"] li',
                'div[data-baseweb="popover"] *',
                '.stSelectbox *',
                'div[data-testid="stSelectbox"] *'
            ];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    element.style.setProperty('color', '#f1f5f9', 'important');
                    element.style.setProperty('background-color', 'rgba(15, 23, 42, 0.9)', 'important');
                    element.style.setProperty('-webkit-text-fill-color', '#f1f5f9', 'important');
                    element.style.setProperty('background', 'rgba(15, 23, 42, 0.9)', 'important');
                });
            });
            
            // Also inject CSS directly
            if (!document.getElementById('aggressive-dropdown-styles')) {
                const style = document.createElement('style');
                style.id = 'aggressive-dropdown-styles';
                style.textContent = `
                    /* MEGA AGGRESSIVE DROPDOWN FIXES */
                    [data-baseweb="popover"] * {
                        color: #f1f5f9 !important;
                        background: rgba(15, 23, 42, 0.95) !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                    [role="listbox"] * {
                        color: #f1f5f9 !important;
                        background: rgba(15, 23, 42, 0.95) !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                    [role="option"] {
                        color: #f1f5f9 !important;
                        background: rgba(15, 23, 42, 0.9) !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                    .stSelectbox [data-baseweb="select"] {
                        color: #f1f5f9 !important;
                        background: rgba(15, 23, 42, 0.9) !important;
                    }
                    .stSelectbox [data-baseweb="select"] * {
                        color: #f1f5f9 !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                    div[data-testid="stSelectbox"] * {
                        color: #f1f5f9 !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                    div[role="button"] {
                        color: #f1f5f9 !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                    div[role="button"] span {
                        color: #f1f5f9 !important;
                        -webkit-text-fill-color: #f1f5f9 !important;
                    }
                `;
                document.head.appendChild(style);
            }
        }
        
        // Run immediately and every 200ms for faster response
        fixTextColors();
        setInterval(fixTextColors, 200);
        
        // Fix colors on any interaction
        ['click', 'mousedown', 'focus', 'mouseover'].forEach(event => {
            document.addEventListener(event, function() {
                setTimeout(fixTextColors, 50);
                setTimeout(fixTextColors, 200);
            });
        });
        </script>
        """, unsafe_allow_html=True)
        
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