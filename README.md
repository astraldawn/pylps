# pylps
[![CircleCI](https://circleci.com/gh/astraldawn/pylps.svg?style=shield)](https://circleci.com/gh/astraldawn/pylps)

To run tests: pytest

# Coverage
```rm -rf htmlcov && py.test --cov-report html --cov=pylps tests/```

# Profiling
```python -m cProfile -s tottime file_name.py```