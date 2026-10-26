import numpy as np

import ci_course


def test_loads_every_column_of_the_sample_data():
    data = ci_course.load_measurements()

    assert set(data) == {"temperature_c", "mass_g"}
    assert data["temperature_c"].size == 8
    assert data["mass_g"].size == 8


def test_blank_cells_are_read_as_missing():
    data = ci_course.load_measurements()

    assert np.isnan(data["temperature_c"]).sum() == 1
    assert np.isnan(data["mass_g"]).sum() == 1


def test_reads_a_file_given_by_path(tmp_path):
    csv = tmp_path / "measurements.csv"
    csv.write_text("sample_id,height_m\nA,1.5\nB,2.5\n", encoding="utf-8")

    data = ci_course.load_measurements(csv)

    assert list(data) == ["height_m"]
    assert data["height_m"].tolist() == [1.5, 2.5]
