import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import json

st.set_page_config(
    page_title="JobFit AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
    }
    .skill-tag-green {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 10px;
        border-radius: 20px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .skill-tag-red {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 10px;
        border-radius: 20px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .skill-tag-blue {
        background-color: #cce5ff;
        color: #004085;
        padding: 4px 10px;
        border-radius: 20px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .recommendation-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .stProgress .st-bo {
        background-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)


def create_gauge_chart(score):
    if score >= 75:
        color = "#28a745"
    elif score >= 50:
        color = "#ffc107"
    elif score >= 25:
        color = "#fd7e14"
    else:
        color = "#dc3545"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Match Score", 'font': {'size': 24, 'color': '#333'}},
        delta={'reference': 70, 'increasing': {'color': "#28a745"}, 'decreasing': {'color': "#dc3545"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#333"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#ffe5e5'},
                {'range': [25, 50], 'color': '#fff3cd'},
                {'range': [50, 75], 'color': '#d4edda'},
                {'range': [75, 100], 'color': '#c3e6cb'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333", 'family': "Arial"}
    )
    return fig


def create_skills_bar_chart(matched, missing, extra):
    categories = ['Matched Skills', 'Missing Skills', 'Bonus Skills']
    values = [len(matched), len(missing), len(extra)]
    colors = ['#28a745', '#dc3545', '#17a2b8']

    fig = go.Figure(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=values,
        textposition='auto',
    ))
    fig.update_layout(
        title="Skills Overview",
        xaxis_title="Category",
        yaxis_title="Count",
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333"},
        showlegend=False
    )
    return fig


def create_radar_chart(result):
    skill_score = result.get('skill_match_score', 0)
    text_score = result.get('text_similarity_score', 0) * 100
    overall = result.get('overall_score', 0)
    matched_pct = (len(result.get('matched_skills', [])) /
                   max(len(result.get('matched_skills', [])) + len(result.get('missing_skills', [])), 1)) * 100

    categories = ['Overall Match', 'Skill Match', 'Text Similarity', 'Coverage']
    values = [overall, skill_score, text_score, matched_pct]
    values += values[:1]
    categories += categories[:1]

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=2)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        height=300,
        title="Performance Radar",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

st.markdown('<h1 class="main-header">🎯 JobFit AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#666; font-size:1.1rem;">Resume & Job Description Analyzer — Know your fit before you apply</p>', unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_mode = st.radio("Mode", ["Direct (No API)", "FastAPI Backend"])
    if api_mode == "FastAPI Backend":
        api_url = st.text_input("API URL", "http://localhost:8000")
    st.markdown("---")
    st.markdown("### About")
    st.info("JobFit AI uses NLP and ML to analyze how well your resume matches a job description.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Upload Your Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=['pdf'], help="Upload your resume in PDF format")

    if uploaded_file:
        st.success(f" Uploaded: **{uploaded_file.name}**")

with col2:
    st.markdown("### Paste Job Description")
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the full job description here...\n\nExample:\nWe are looking for a Data Scientist with skills in Python, Machine Learning, TensorFlow, SQL..."
    )

st.markdown("---")

analyze_btn = st.button("Analyze My Fit", use_container_width=True, type="primary")

if analyze_btn:
    if not uploaded_file:
        st.error("Please upload your resume PDF!")
    elif not job_description.strip():
        st.error("Please paste a job description!")
    else:
        with st.spinner("Analyzing your profile... This takes a few seconds."):
            try:
                if api_mode == "FastAPI Backend":
                    
                    files = {"resume": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"job_description": job_description}
                    response = requests.post(f"{api_url}/analyze", files=files, data=data, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                    else:
                        st.error(f"API Error: {response.text}")
                        st.stop()
                else:
                    
                    from src.extractor import extract_skills_from_pdf, extract_skills_from_text
                    from src.scorer import get_overall_score, get_fit_level, get_recommendations

                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name

                    resume_skills = extract_skills_from_pdf(tmp_path)
                    jd_skills = extract_skills_from_text(job_description)
                    result = get_overall_score(resume_skills, jd_skills, "", job_description)
                    result['fit_level'] = get_fit_level(result['overall_score'])
                    result['recommendations'] = get_recommendations(
                        result['missing_skills'], result['overall_score']
                    )
                    os.unlink(tmp_path)

            

                st.markdown("## Your Results")
                st.markdown("---")

                
                m1, m2, m3, m4 = st.columns(4)
                score = result.get('overall_score', 0)
                fit = result.get('fit_level', 'N/A')
                matched = result.get('matched_skills', [])
                missing = result.get('missing_skills', [])

                with m1:
                    st.markdown(f'<div class="metric-card"><h2>{score:.1f}%</h2><p>Overall Match</p></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-card"><h2>{fit}</h2><p>Fit Level</p></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-card"><h2>{len(matched)}</h2><p>Skills Matched</p></div>', unsafe_allow_html=True)
                with m4:
                    st.markdown(f'<div class="metric-card"><h2>{len(missing)}</h2><p>Skills Missing</p></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

            
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.plotly_chart(create_gauge_chart(score), use_container_width=True)
                with c2:
                    st.plotly_chart(create_skills_bar_chart(
                        matched, missing, result.get('extra_skills', [])
                    ), use_container_width=True)
                with c3:
                    st.plotly_chart(create_radar_chart(result), use_container_width=True)

                
                st.markdown("### Skills Breakdown")
                s1, s2, s3 = st.columns(3)

                with s1:
                    st.markdown("#### Matched Skills")
                    if matched:
                        tags = " ".join([f'<span class="skill-tag-green">{s}</span>' for s in sorted(matched)])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.info("No matching skills found")

                with s2:
                    st.markdown("####  Missing Skills")
                    if missing:
                        tags = " ".join([f'<span class="skill-tag-red">{s}</span>' for s in sorted(missing)])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.success("No missing skills! 🎉")

                with s3:
                    st.markdown("#### Bonus Skills")
                    extra = result.get('extra_skills', [])
                    if extra:
                        tags = " ".join([f'<span class="skill-tag-blue">{s}</span>' for s in sorted(extra)])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.info("No extra skills detected")

                
                st.markdown("### Recommendations")
                recs = result.get('recommendations', [])
                if recs:
                    for rec in recs:
                        st.markdown(f'<div class="recommendation-box">💡 {rec}</div>', unsafe_allow_html=True)
                else:
                    st.success("You're a great fit! No major gaps found.")

                
                st.markdown("---")
                export_data = {
                    "overall_score": score,
                    "fit_level": fit,
                    "matched_skills": list(matched),
                    "missing_skills": list(missing),
                    "recommendations": recs
                }
                st.download_button(
                    label="Download Results (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name="jobfit_results.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)