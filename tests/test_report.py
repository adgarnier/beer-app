import numpy as np

import ci_course


def summaries():
    return {"height_m": ci_course.summarise(np.array([1.0, 2.0, 3.0]))}


def test_writes_a_report(tmp_path):
    out = tmp_path / "report.txt"

    ci_course.write_report(summaries(), out)

    assert out.read_text(encoding="utf-8").startswith("Measurement summary")


def test_replaces_an_existing_report(tmp_path):
    out = tmp_path / "report.txt"
    later = {"height_m": ci_course.summarise(np.array([10.0, 20.0, 30.0]))}

    ci_course.write_report(summaries(), out)
    ci_course.write_report(later, out)

    assert "mean=20.000" in out.read_text(encoding="utf-8")
