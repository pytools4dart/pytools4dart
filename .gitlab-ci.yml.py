# This file is a template, and might need editing before it works on your project.
# Official language image. Look for the different tagged releases at:
# https://hub.docker.com/r/library/python/tags/
image: python:3.6

# Change pip's cache directory to be inside the project directory since we can
# only cache local items.
variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
#  APT_CACHE_DIR: "$CI_PROJECT_DIR/.cache/apt"

# Pip's cache doesn't store the python packages
# https://pip.pypa.io/en/stable/reference/pip_install/#caching
#
# If you want to also cache the installed packages, you have to install
# them in a virtualenv and cache it as well.
cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - ls pytools4dart
  - apt-get update -qy
  - python -V  # Print out python version for debugging
  - pip install virtualenv
  - virtualenv venv
  - source venv/bin/activate
  #- mkdir -v $APT_CACHE_DIR
  - apt-get install -y libudunits2-dev libnetcdf-dev libproj-dev libgeos-dev libgdal-dev gfortran libspatialindex-dev # -o dir::cache::archives="$APT_CACHE_DIR"
  - pip install pybind11 pygdal==2.4.0.5 geopandas Cython
  - pip install -r requirements.txt
  - pip install portray


pages:
  stage: deploy
  script:
    - rm -r site
    - portray as_html -c pyproject.toml
    - mv site public
  artifacts:
    paths:
     - public
  only:
   - master

