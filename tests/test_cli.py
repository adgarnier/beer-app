import ci_course.cli


def test_prints_a_summary(capsys):
    assert ci_course.cli.main([]) == 0

    printed = capsys.readouterr().out
    assert "temperature_c" in printed
    assert "mass_g" in printed


def test_writes_a_report_to_a_file(tmp_path):
    out = tmp_path / "report.txt"

    assert ci_course.cli.main(["--output", str(out)]) == 0
    assert out.exists()
