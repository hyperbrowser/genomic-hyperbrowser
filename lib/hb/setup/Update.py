import os

from setup.CopyFiles import CopyFiles
from setup.PatchFiles import PatchFiles

from config.Config import HB_SETUP_CONFIG_BASE_DIR

CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'copy_files.common.setup').update()
CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'copy_files.setup').update()
PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.common.setup').update()
PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.installation.setup').update()
PatchFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'patch_files.setup').update()

CopyFiles(HB_SETUP_CONFIG_BASE_DIR + os.sep + 'style_copy_files.common.setup').update()
