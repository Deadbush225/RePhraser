import os

basedir = os.path.dirname(__file__)
# print(basedir) # RePhraser\src\rephraser

parts = basedir.split("\\")
project_dir = "\\".join(parts[:-2])
# print(project_dir) # RePhraser
