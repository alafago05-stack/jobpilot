from .llm import chat, extract_json
from .search import web_search

PH = "Placeholders like [EMAIL_1] or [NAME_1] stand for private data: keep them exactly as written."


def parse_cv(cv: str) -> dict:
    default = {"titles": ["Software Engineer"], "skills": ["Python", "SQL"],
               "years_experience": 3, "education": ["BSc"], "highlights": ["Built a data pipeline"]}
    out = chat(
        "You extract structured data from a resume. Reply with JSON only: "
        '{"titles":[],"skills":[],"years_experience":0,"education":[],"highlights":[]}. ' + PH,
        cv, mock=__import__("json").dumps(default))
    return extract_json(out, default)


def research_company(company: str, job: str) -> str:
    hits = web_search(f"{company} company products news culture", 5)
    ctx = "\n".join(f"- {h.get('title','')}: {h.get('body','')}" for h in hits) or "(no web results)"
    return chat(
        "You are a company researcher preparing a candidate. Write a concise brief: what the company does, "
        "recent news, culture signals, likely tech stack, 3 smart questions to ask. Only use the provided "
        "snippets and the job text; say when something is unknown.",
        f"Company: {company}\n\nJob posting:\n{job}\n\nWeb snippets:\n{ctx}",
        mock=f"## {company} brief (demo)\n- What they do: (demo mode)\n- Questions to ask: What does success look like in 6 months?")


def score_match(profile: dict, job: str) -> dict:
    default = {"score": 72, "strengths": ["Relevant skills"], "gaps": ["Domain experience"]}
    out = chat(
        'Compare a candidate profile to a job. JSON only: {"score":0-100,"strengths":[],"gaps":[]}. '
        "Be honest, do not inflate the score.",
        f"Profile: {profile}\n\nJob:\n{job}", mock=__import__("json").dumps(default))
    d = extract_json(out, default)
    try:
        d["score"] = max(0, min(100, int(d.get("score", 0))))
    except (TypeError, ValueError):
        d["score"] = 0
    return d


def tailor_cv(cv: str, job: str, match: dict) -> str:
    return chat(
        "Rewrite the resume to fit the job. Never invent experience, employers, degrees or numbers. "
        "Reorder and reword truthfully, mirror the job's keywords where honest. Markdown output. " + PH,
        f"Resume:\n{cv}\n\nJob:\n{job}\n\nGaps to handle honestly: {match.get('gaps')}",
        mock="# [NAME_1]\n[EMAIL_1] | [PHONE_1]\n\n## Summary\nTailored resume (demo mode).")


def cover_letter(cv: str, job: str, company: str) -> str:
    return chat(
        "Write a specific, human cover letter (max 250 words). No cliches, no invented facts. " + PH,
        f"Company: {company}\nResume:\n{cv}\n\nJob:\n{job}",
        mock=f"Dear {company} team,\n\nI am excited to apply... (demo mode)\n\nBest,\n[NAME_1]")


def application_email(company: str, job: str) -> str:
    return chat(
        "Write a short application email (subject line + 90 words max). " + PH,
        f"Company: {company}\nJob:\n{job}",
        mock="Subject: Application - demo\n\nHello,\nPlease find my application attached.\n[NAME_1]")


def followup_email(company: str) -> str:
    return chat(
        "Write a polite follow-up email to send 7 days after applying (subject + 70 words max). " + PH,
        f"Company: {company}", mock="Subject: Following up\n\nHello, just checking in... [NAME_1]")


def interview_prep(profile: dict, job: str, brief: str, rounds: int = 2) -> str:
    transcript = []
    for i in range(rounds):
        q = chat("You are a skeptical recruiter. Ask ONE hard, specific interview question "
                 "that probes the weakest point. Do not repeat earlier questions.",
                 f"Profile: {profile}\nJob:\n{job}\nAsked so far: {transcript}",
                 mock=f"Q{i+1}: Tell me about a project that failed (demo).")
        a = chat("You are an interview coach. Draft a strong, truthful answer in STAR format "
                 "using only facts from the profile.", f"Profile: {profile}\nQuestion: {q}",
                 mock=f"A{i+1}: Situation... Task... Action... Result... (demo)")
        transcript.append((q, a))
    return chat(
        "Using the debate transcript, company brief and job, produce a markdown interview prep sheet: "
        "10 likely questions, each with a short suggested answer outline, plus 3 risks to prepare for.",
        f"Transcript: {transcript}\nBrief:\n{brief}\nJob:\n{job}",
        mock="## Interview prep (demo)\n1. Why this company?\n2. Tell me about a failure.\n...")
