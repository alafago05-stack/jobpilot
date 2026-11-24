from typing import TypedDict

from langgraph.graph import END, StateGraph

from . import agents
from .pii import restore, sanitize


class State(TypedDict, total=False):
    cv: str
    job: str
    company: str
    names: list
    cv_clean: str
    mapping: dict
    profile: dict
    brief: str
    match: dict
    tailored_cv: str
    letter: str
    email: str
    followup: str
    interview: str


def n_sanitize(s: State):
    clean, mapping = sanitize(s["cv"], s.get("names", ()))
    return {"cv_clean": clean, "mapping": mapping}


def n_parse(s: State):
    return {"profile": agents.parse_cv(s["cv_clean"])}


def n_research(s: State):
    return {"brief": agents.research_company(s["company"], s["job"])}


def n_match(s: State):
    return {"match": agents.score_match(s["profile"], s["job"])}


def n_tailor(s: State):
    return {
        "tailored_cv": agents.tailor_cv(s["cv_clean"], s["job"], s["match"]),
        "letter": agents.cover_letter(s["cv_clean"], s["job"], s["company"]),
    }


def n_mail(s: State):
    return {"email": agents.application_email(s["company"], s["job"]),
            "followup": agents.followup_email(s["company"])}


def n_coach(s: State):
    return {"interview": agents.interview_prep(s["profile"], s["job"], s["brief"])}


def n_restore(s: State):
    m = s["mapping"]
    return {k: restore(s[k], m) for k in ("tailored_cv", "letter", "email", "followup", "interview")}


def build_graph():
    g = StateGraph(State)
    steps = [("sanitize", n_sanitize), ("parse", n_parse), ("research", n_research), ("match", n_match),
             ("tailor", n_tailor), ("mail", n_mail), ("coach", n_coach), ("restore", n_restore)]
    for name, fn in steps:
        g.add_node(name, fn)
    g.set_entry_point("sanitize")
    for (a, _), (b, _) in zip(steps, steps[1:]):
        g.add_edge(a, b)
    g.add_edge("restore", END)
    return g.compile()


def run(cv: str, job: str, company: str = "the company", names=()) -> State:
    return build_graph().invoke({"cv": cv, "job": job, "company": company or "the company",
                                 "names": list(names)})
