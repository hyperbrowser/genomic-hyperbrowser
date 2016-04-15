from config.Config import HB_EGGS_FILE_PATH
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.optionxform=str
config.read(HB_EGGS_FILE_PATH)

try:
    from galaxy import eggs
except:
    pass
else:
    import pkg_resources
    
    packagesToImport = config.options('eggs:platform') + config.options('eggs:noplatform')
    for package in packagesToImport:
        pkg_resources.require(package)
