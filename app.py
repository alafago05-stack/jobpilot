import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from jobpilot.pipeline import run  # noqa: E402

st.set_page_config(page_title="JobPilot", page_icon="🧭", layout="wide")
st.title("🧭 JobPilot")
st.caption("Your CV is masked locally before any AI sees it.")

c1, c2 = st.columns(2)
cv_file = c1.file_uploader("CV (.txt or .pdf)", type=["txt", "pdf"])
cv = c1.text_area("...or paste your CV", height=250)
job = c2.text_area("Job posting", height=250)
company = c2.text_input("Company name")

if cv_file is not None:
    if cv_file.name.endswith(".pdf"):
        from pypdf import PdfReader
        cv = "\n".join(p.extract_text() or "" for p in PdfReader(cv_file).pages)
    else:
        cv = cv_file.read().decode("utf-8", "ignore")

if st.button("Prepare my application", type="primary", disabled=not (cv and job)):
    with st.spinner("Agents at work..."):
        res = run(cv, job, company)
    st.metric("Match score", f"{res['match']['score']}/100")
    st.write("**Strengths:**", ", ".join(res["match"]["strengths"]))
    st.write("**Gaps:**", ", ".join(res["match"]["gaps"]))
    tabs = st.tabs(["Tailored CV", "Cover letter", "Emails", "Company brief", "Interview prep"])
    tabs[0].markdown(res["tailored_cv"]); tabs[0].download_button("Download", res["tailored_cv"], "cv.md")
    tabs[1].markdown(res["letter"])
    tabs[2].markdown(res["email"] + "\n\n---\n\n" + res["followup"])
    tabs[3].markdown(res["brief"])
    tabs[4].markdown(res["interview"])
