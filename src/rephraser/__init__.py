import os
from pathlib import Path

t_base = Path(os.path.dirname(__file__))

basedir = t_base.resolve()
# print(basedir)  # RePhraser\src\rephraser

# get the project folder name two levels up (e.g. "RePhraser")
project_dir = t_base.parents[1]
# print(project_dir)  # RePhraser
