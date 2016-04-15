import os

from setup.CopyFiles import CopyFiles
from setup.PatchFiles import PatchFiles

from config.Config import HB_SETUP_CONFIG_BASE_DIR

CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'copy_files.common.setup').cleanup()
CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'copy_files.setup').cleanup()
PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.common.setup').cleanup()
PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.installation.setup').cleanup()
PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.setup').cleanup()

CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'style_copy_files.common.setup').cleanup()
