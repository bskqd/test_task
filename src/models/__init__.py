from sqlalchemy import MetaData

from models.tickets import *
from models.users import *

"""
This module is used to import all the models declared in the project,
so it's possible to import all the modules, for example, in alembic env.py and tests to use the proper "Base" instance
"""


def get_metadata() -> MetaData:
    """Returns metadata that is used in all models, used in tests"""
    for i, j in globals().copy().items():
        metadata = getattr(j, "metadata", None)
        if metadata:
            return metadata
