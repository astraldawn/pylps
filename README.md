# pylps
[![CircleCI](https://circleci.com/gh/astraldawn/pylps.svg?style=shield)](https://circleci.com/gh/astraldawn/pylps)
[![codecov](https://codecov.io/gh/astraldawn/pylps/branch/master/graph/badge.svg)](https://codecov.io/gh/astraldawn/pylps)
[![Maintainability](https://api.codeclimate.com/v1/badges/cdbd4d0872766e640afb/maintainability)](https://codeclimate.com/github/astraldawn/pylps/maintainability)

# Installation
In a virtualenv run the following commands:

```
pip install -r requirements.txt
python setup.py develop
```
To run tests, run the following command in main directory

```
pytest
```

# Coverage
```
rm -rf htmlcov && py.test --cov-report html --cov=pylps tests/
```

# Profiling
```
python -m cProfile -s tottime file_name.py
```
