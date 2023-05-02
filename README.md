## Content

This repository contains my solution for a task called Rebel Rescue. The repo is organized into
- bin
- src (including bin/ with decoder)
- data
- docs (task.md in here)
- results

## Installation

```bash
$ pip install virtualenv
$ cd # to opg_RR/bin/
$ virtualenv venv
$ source # to opg_RR/bin/venv/bin/activate
$ pip install -r requirements.txt
```

## Deploy additional python packages

```bash
$ pip install some-package-here # installing and using a python package
$ cd # to opg_RR/bin/
# either substitute > or add >> requirements
$ pip freeze > requirements.txt
$ pip freeze >> requirements.txt
```
