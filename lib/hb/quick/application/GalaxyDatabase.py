import galaxy.config
import galaxy.model.mapping
from config.Config import getGalaxyConfiguration

def getGalaxyDatabaseModel():
    """
    Returns a SQLAlchemy model and session --
    """
    config = getGalaxyConfiguration()

    model = galaxy.model.mapping.init( config.file_path, config.database_connection, engine_options={}, create_tables=False)
    return model

