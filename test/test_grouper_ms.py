from pathlib import Path

import pandas as pd

from OSN_Algoritmus.core import grouper_ms


def test_grouper_ms_all_flags_big():
    """
    Test the grouper_ms function with all flags set to True on a 50 000 row dataset.
    """
    test_data_dir = Path(__file__).parent.absolute() / "data"
    input_file = test_data_dir / "test_data_50000.csv"
    expected_output = test_data_dir / "test_data_50000_output_expected.csv"

    output_file = grouper_ms(
        str(input_file),
        vsetky_vykony_hlavne=True,
        vyhodnot_neuplne_pripady=True,
        ponechaj_duplicity=True,
    )

    actual_df = pd.read_csv(output_file, sep=";")
    expected_df = pd.read_csv(expected_output, sep=";")

    pd.testing.assert_frame_equal(actual_df, expected_df)

    Path(output_file).unlink()

def test_grouper_ms_all_flags_small():
    """
    Test the grouper_ms function with all flags set to True on a 9 row dataset.
    """
    test_data_dir = Path(__file__).parent.absolute() / "data"
    input_file = test_data_dir / "test_data_9.csv"
    expected_output = test_data_dir / "test_data_9_output_expected.csv"

    output_file = grouper_ms(
        str(input_file),
        vsetky_vykony_hlavne=True,
        vyhodnot_neuplne_pripady=True,
        ponechaj_duplicity=True,
    )

    actual_df = pd.read_csv(output_file, sep=";")
    expected_df = pd.read_csv(expected_output, sep=";")

    pd.testing.assert_frame_equal(actual_df, expected_df)

    Path(output_file).unlink()