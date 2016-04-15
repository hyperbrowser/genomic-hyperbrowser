import os

from setup.InstallFunctions import executePythonFile
from config.Config import GALAXY_BASE_DIR, GALAXY_COLOR_DEFINITION_FILE, GALAXY_COMPILE_COLORS

if GALAXY_COMPILE_COLORS:
    executePythonFile(os.sep.join([GALAXY_BASE_DIR, 'static', 'june_2007_style', 'make_style.py']),\
                      GALAXY_COLOR_DEFINITION_FILE + ' HB True', setPythonPath=True)

    executePythonFile(os.sep.join([GALAXY_BASE_DIR, 'static', 'june_2007_style', 'make_style.py']),\
                      GALAXY_COLOR_DEFINITION_FILE + ' HB', setPythonPath=True)
