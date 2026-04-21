"""
Hi there, LordOfPolls here. I almost guarantee this isnt how an __init__.py is supposed to be written, but *shrugs*, it works
"""

from .objectClasses import Rule34Post  # A class representing a rule34 post

# Both rule34 api run modes
from .rule34 import Rule34  # Async
from .rule34 import Sync  # Sync

# Error Types
from .rule34 import Request_Rejected
from .rule34 import Rule34_Error
from .rule34 import SelfTest_Failed