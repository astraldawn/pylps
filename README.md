# pylps
[![CircleCI](https://circleci.com/gh/astraldawn/pylps.svg?style=shield)](https://circleci.com/gh/astraldawn/pylps)
[![codecov](https://codecov.io/gh/astraldawn/pylps/branch/master/graph/badge.svg)](https://codecov.io/gh/astraldawn/pylps)

To run tests: pytest

# Coverage
```rm -rf htmlcov && py.test --cov-report html --cov=pylps tests/```

# Profiling
```python -m cProfile -s tottime file_name.py```
