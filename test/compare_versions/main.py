from pathlib import Path

from compare_versions import VersionConfig, run_algoritmus

flags = ["-vnd"]
version_a = VersionConfig(identifier="local", flags=flags)
run_algoritmus(version_a, Path("/Users/kvaky/prog/iza/OSN-Algoritmus-MS/test/data/example_data_10.csv"))
