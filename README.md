## Content

This repository contains my solution for a task called Rebel Rescue. The repo is [organized](https://swcarpentry.github.io/good-enough-practices-in-scientific-computing/) into
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

Write it manually in requirements.txt

```bash
$ pip install some-package-here # installing and using a python package
$ cd # to opg_RR/bin/

$ nano requirements.txt # add new lines for new packages

# either substitute > or add >> requirements:
#$ pip freeze > requirements.txt
#$ pip freeze >> requirements.txt

# or alternatively, use piprequires
# pip install pipreqs
# pipreqs ~/repos/opg_RR/src/
```


### details

in the terminal, activate the virtual environment
```bash
$ source opg_RR/bin/venv/bin/activate
```

"""load tools in rebel_decode.py
 - __init__.py in src/bin/
 - configure vscode paths for directory ctrl+, 
   - "jupyter: notebook file root" e.g. ${fileDirname}
   - "Python › Analysis: Import Format"
   - "Python › Terminal: Execute In File Dir"
   - launch.json # https://stackoverflow.com/a/55072246/3755989
 - cwd is set to find # https://stackoverflow.com/a/51149057/3755989

from pathlib import Path
print(Path.cwd())

os.listdir(os.getcwd())
os.getcwd()
os.chdir('path')
"""