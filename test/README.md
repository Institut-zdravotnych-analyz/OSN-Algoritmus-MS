# Test

This directory contains various functionality for testing and checking outputs of the OSN-Algoritmus-MS project.

## `compare_versions/`

This subdirectory contains notebook [`compare_versions.ipynb`](compare_versions/compare_versions.ipynb) used for comparing outputs between different versions and configurations of the algoritmus. The notebook uses functionality defined in [`compare_versions.py`](compare_versions/compare_versions.py)

## `test_main.py`

Pytest file executing end-to-end test scenarios covering the whole functionality of the algoritmus. Run with
```bash
pytest test_main.py 
```
