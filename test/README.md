# Test

This directory contains various functionality for testing and checking outputs of the OSN-Algoritmus-MS project.

## `run_with_config/`

This subdirectory contains notebook [`compare_versions.ipynb`](run_with_config/compare_versions.ipynb) used for comparing outputs between different versions and configurations of the algoritmus. The notebook uses functionality defined in [`run_with_config.py`](run_with_config/run_with_config.py)

## `test_main.py`

Pytest file executing end-to-end test scenarios covering the whole functionality of the algoritmus. Run with
```bash
pytest test_main.py 
```
