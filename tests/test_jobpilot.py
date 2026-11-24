import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["LLM_PROVIDER"] = "mock"

from jobpilot.pii import restore, sanitize  # noqa: E402
from jobpilot.pipeline import run  # noqa: E402

CV = open(os.path.join(os.path.dirname(__file__), "..", "examples", "sample_cv.txt")).read()
JOB = "Data Engineer. Python, SQL."


def test_pii_masks_and_restores():
    clean, m = sanitize(CV)
    for secret in ("sara.benali@example.com", "+212 6 12 34 56 78", "linkedin.com/in/sarabenali", "Sara Benali"):
        assert secret not in clean
    assert restore(clean, m) == CV


def test_dates_are_not_phone_numbers():
    clean, _ = sanitize("Worked 2019 - 2023 at Acme")
    assert "2019 - 2023" in clean


def test_pipeline_restores_private_data_in_outputs():
    res = run(CV, JOB, "Acme")
    assert "[NAME_1]" not in res["tailored_cv"]
    assert "Sara Benali" in res["tailored_cv"]
    assert 0 <= res["match"]["score"] <= 100
    assert res["interview"]
