"""Run JobPilot over every job in examples/jobs/*.txt and print average score + time.
Put your own results in the README: python benchmark.py --cv examples/sample_cv.txt"""
import argparse, pathlib, time
from dotenv import load_dotenv
load_dotenv()
from jobpilot.pipeline import run

p = argparse.ArgumentParser(); p.add_argument("--cv", required=True); p.add_argument("--jobs", default="examples/jobs")
a = p.parse_args()
cv = pathlib.Path(a.cv).read_text()
jobs = sorted(pathlib.Path(a.jobs).glob("*.txt"))
scores, times = [], []
for j in jobs:
    t = time.time(); r = run(cv, j.read_text(), j.stem); times.append(time.time() - t); scores.append(r["match"]["score"])
    print(f"{j.name}: score={scores[-1]} time={times[-1]:.1f}s")
if jobs:
    print(f"\n{len(jobs)} jobs | avg score {sum(scores)/len(scores):.0f} | avg time {sum(times)/len(times):.1f}s")
