from dotenv import load_dotenv
import streamlit as st
import os
import pdf2image
import google.generativeai as genai
import io
import base64
import re
import plotly.graph_objects as go



# Load environment variables
load_dotenv()

# Set page config FIRST
st.set_page_config(page_title="RecruitIQ", page_icon="static\RIQ-BG.png", layout="wide")

tab1, tab2 = st.tabs(["Resume Analyzer", "Employee Sentiment Analysis"])

with tab1:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to call Google Gemini model for resume analysis
    def get_response(input_text, pdf_content, prompt):
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([input_text, pdf_content[0], prompt])
        return response.text

    # Convert uploaded PDF to base64-encoded image for AI input
    def input_pdf(uploaded_file):
        if uploaded_file is not None:
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            first_page = images[0]
            image_byte_arr = io.BytesIO()
            first_page.save(image_byte_arr, format='JPEG')
            image_byte_arr = image_byte_arr.getvalue()
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(image_byte_arr).decode()
                }
            ]
            return pdf_parts
        else:
            raise FileNotFoundError("No File Uploaded.")

    # Custom CSS styling
    st.markdown("""
        <style>
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            .stButton>button {
                width: 100%;
                border-radius: 4px;
                height: 3em;
                font-weight: 500;
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            .stButton>button:hover {
                background-color: #45a049;
            }
            .sidebar .sidebar-content {
                background-color: #f0f2f6;
            }
            .result-box {
                background-color: #f9f9f9;
                color: #262730;  /* black font */
                padding: 15px;
                border-radius: 5px;
                border-left: 5px solid #4CAF50;
                margin-top: 20px;
                white-space: pre-wrap;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar with branding and info
    with st.sidebar:
        st.image("static\RecruitIQ.png", use_container_width=True)
        st.header("About")
        st.markdown("This **Advanced HR Recruiting System** helps you analyze resumes against job descriptions and Employee Sentiment Analysis using AI-powered insights.")
        st.markdown("---")
        st.caption("⚡ Powered by Google Gemini AI")
        st.caption("Developed by Sanketh Singh.")

    # Main app title and instructions
    st.title("📄 Resume Analyzer")
    st.markdown("**Upload your resume and provide a job description to get detailed insights and compatibility scores!**")
    st.markdown("---")

    # Two-column layout for inputs
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.subheader("Job Description")
        input_text = st.text_area(
            "Paste the Job Description here:", 
            height=200, 
            key="input", 
            placeholder="e.g., Looking for a Software Engineer with 3+ years of experience in Python and Java..."
        )

    with col2:
        st.subheader("Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a PDF file:", 
            type=["pdf"], 
            help="Upload your resume in PDF format for analysis."
        )
        if uploaded_file is not None:
            st.success("PDF uploaded successfully! ✅")

    # Analysis prompt template
    prompt1 = """
    You are an Applicant Tracking System (ATS) for a Software Engineer position.

    Given the following job description and resume, analyze the resume and provide:

    Compatibility Score: Assign a score (0-100)/100 reflecting how well the resume matches the job description, based on skills, experience, and qualifications.

    Matched Skills: List the technical skills, programming languages, frameworks, and tools from the resume that directly match the job description requirements.

    Relevant Experience: Summarize the candidate's work experience, projects, and contributions that align with the responsibilities and qualifications in the job description.

    Education & Certifications: Identify any degrees, certifications, or specialized training that match or exceed the job requirements.

    Gaps or Missing Qualifications: Note any important skills or experiences required by the job description that are missing or weak in the resume.
     
    Format your response with clear headings and bullet points by adding bold font to side headings.
    """

    # Analyze button triggers AI call and displays results
    if st.button("Analyze Resume", use_container_width=True):
        if uploaded_file is None or input_text.strip() == "":
            st.warning("Please upload a resume and provide a job description before analysis.")
        else:
            with st.spinner("Analyzing your resume... Please wait."):
                try:
                    # Convert PDF to AI input format
                    pdf_content = input_pdf(uploaded_file)
                    # Get AI analysis response
                    response_text = get_response(input_text, pdf_content, prompt1)
                    st.success("Analysis Completed ✅")
                    # Extract compatibility score using regex
                    match = re.search(r"\*\*Compatibility Score:\*\*\s*(\d+)/100\*\*", response_text)
                    compatibility_score = int(match.group(1)) if match else 0

                    # Display pie chart of compatibility score
                    labels = ['Match', 'Gap']
                    values = [compatibility_score, 100 - compatibility_score]
                    colors = ['#4CAF50', '#FF6F61']

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.5,
                        marker=dict(colors=colors),
                        textinfo='none'
                    )])
                    fig.update_layout(
                        showlegend=False,
                        margin=dict(t=0, b=0, l=0, r=0),
                        annotations=[dict(text=f"{compatibility_score}%", x=0.5, y=0.5, font_size=24, showarrow=False)]
                    )

                    st.subheader("Resume Compatibility Score")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display detailed analysis report with styling
                    st.subheader("Analysis Report")
                    st.markdown(
                        f"<div class='result-box'>{response_text.replace(chr(10), '<br>')}</div>",
                        unsafe_allow_html=True
                    )

                    # Download button for analysis report
                    st.download_button(
                        label="⬇️ Download Analysis Report",
                        data=response_text,
                        file_name="resume_analysis.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")

import streamlit as st
from textblob import TextBlob
from docx import Document
import plotly.graph_objects as go

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to call Google Gemini model for resume analysis
def get_response(input_text, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, prompt])
    return response.text

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text

def extract_sentiment_score(response_text):
    # Extract sentiment score using regex
    score_match = re.search(r"\*\*Sentiment Score \(0–100\):\*\*\s*(\d+)", response_text)
    sentiment_score = int(score_match.group(1)) if score_match else 50  # Default to neutral if not found

    label_match = re.search(r"\*\*Overall Sentiment:\*\*\s*([A-Za-z\s\-to]+)", response_text)
    if label_match:
        sentiment_label = label_match.group(1).strip()
    else:
        sentiment_label = "Unknown"

    # Map score to color and text
    if sentiment_score >= 70:
        sentiment_color = '#4CAF50'  # Green
        #sentiment_label = "Positive"
    elif sentiment_score >= 40:
        sentiment_color = '#FFC107'  # Amber
        #sentiment_label = "Neutral"
    else:
        sentiment_color = '#F44336'  # Red
        #sentiment_label = "Negative"
    return sentiment_label, sentiment_score, sentiment_color


# UI components
with tab2:
    st.title("👨‍💼 Employee Sentiment Analysis")
    st.markdown("**Analyze employee feedback to predict attrition risks and recommend engagement strategies.**")
    st.markdown("---")

    # Inputs
    feedback = st.text_area(
        "Paste employee feedback, survey response, or exit interview here:",
        height=200,
        placeholder="e.g., I feel overwhelmed by my workload and don't see growth opportunities..."
    )

    uploaded_file = st.file_uploader("Or upload a feedback document (.txt or .docx)", type=["txt", "docx"])

    final_feedback = ""

    if uploaded_file:
        if uploaded_file.type == "text/plain":
            final_feedback = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            final_feedback = extract_text_from_docx(uploaded_file)
    elif feedback.strip():
        final_feedback = feedback.strip()

    # Prompt for Gemini
    prompt2 = """
    You are a highly experienced HR analytics expert. Analyze the following employee feedback using sentiment analysis and NLP.

    Provide the following:
    - Sentiment Score (0–100): A number where 0 is extremely negative, 50 is neutral, and 100 is extremely positive.
    - Overall Sentiment: Classify as **Positive**, **Negative**, or **Neutral**.
    - Summary: Briefly summarize the employee's main points.
    - Attrition Risk: High / Medium / Low based on tone and content.
    - Recommendations: Clear bullet points for improving employee engagement.

    Ensure each section has a heading and be concise.
    """


    if st.button("Analyze Feedback", key="analyze_sentiment"):
        if final_feedback == "":
            st.warning("⚠️ Please provide feedback through text area or file upload.")
        else:
            with st.spinner("Analyzing feedback..."):
                try:
                    response_text = get_response(final_feedback, prompt2)
                    sentiment_label, score, sentiment_color = extract_sentiment_score(response_text)
                    st.success("✅ Analysis Complete!")
                    
                    # Result Display
                    st.subheader("📝 Sentiment Analysis Report")
                    st.markdown(
                        f"<div style='background-color:#f9f9f9; color:#000000; padding:15px; border-radius:10px;'>{response_text.replace(chr(10), '<br>')}</div>",
                        unsafe_allow_html=True
                    )

                    # Download option
                    st.download_button(
                        label="⬇️ Download Full Report",
                        data=response_text,
                        file_name="sentiment_analysis.txt",
                        mime="text/plain"
                    )

                    
                    # Show sentiment meter
                    st.subheader("🧭 Sentiment Score")

                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = score,
                        title = {'text': "Sentiment Score"},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "orange"},
                            'steps': [
                                {'range': [0, 40], 'color': "red"},
                                {'range': [40, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': score
                            }
                        }
                    ))

                    st.plotly_chart(fig)
                    def get_label_color(label):
                        if "negative" in label.lower():
                            return "red"
                        elif "positive" in label.lower():
                            return "green"
                        elif "neutral" in label.lower():
                            return "yellow"
                        else:
                            return "white"

                    color = get_label_color(sentiment_label)
                    st.markdown(f"<h4 style='color:{color}'>Overall Sentiment: {sentiment_label}</h4>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")                
                

