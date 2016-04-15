import os

from setup.CopyFiles import CopyFiles
from setup.LocalizeFiles import LocalizeFiles
from setup.PatchFiles import PatchFiles
from setup.ShellCommands import ShellCommands

from config.Config import HB_SETUP_CONFIG_BASE_DIR

ShellCommands(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'dirs.common.setup').apply()
ShellCommands(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'dirs.setup').apply()
ShellCommands(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'dirs.2.common.setup').apply()
ShellCommands(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'dirs.2.setup').apply()
# CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'copy_files.common.setup').apply()
# CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'copy_files.setup').apply()
# PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.common.setup').apply()
# PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.installation.setup').apply()
# PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.setup').apply()
# LocalizeFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'localize_files.common.setup').apply()
# LocalizeFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'localize_files.setup').apply()

# ShellCommands(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'permissions.setup').apply()

# CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'style_copy_files.common.setup').apply()
