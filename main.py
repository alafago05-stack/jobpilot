"""CLI: python main.py --cv examples/sample_cv.txt --job examples/sample_job.txt --company Acme"""
import argparse
import pathlib

from dotenv import load_dotenv

load_dotenv()
from jobpilot.pipeline import run  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="JobPilot - privacy-first job application agents")
    p.add_argument("--cv", required=True)
    p.add_argument("--job", required=True)
    p.add_argument("--company", default="")
    p.add_argument("--out", default="output")
    a = p.parse_args()
    res = run(pathlib.Path(a.cv).read_text(), pathlib.Path(a.job).read_text(), a.company)
    out = pathlib.Path(a.out)
    out.mkdir(exist_ok=True)
    files = {"tailored_cv.md": res["tailored_cv"], "cover_letter.md": res["letter"],
             "application_email.md": res["email"], "followup_email.md": res["followup"],
             "company_brief.md": res["brief"], "interview_prep.md": res["interview"]}
    for name, text in files.items():
        (out / name).write_text(text)
    m = res["match"]
    print(f"Match score: {m['score']}/100\nStrengths: {m['strengths']}\nGaps: {m['gaps']}")
    print(f"Files written to {out}/")


if __name__ == "__main__":
    main()
