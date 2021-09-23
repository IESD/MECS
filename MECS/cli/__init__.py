"""The MECS cli module

Scripts which are triggerable from the command line interface.
Providing access to the primary functionality of the MECS system.
"""

from .test import test, test2
from .status import status
from .initialise import initialise
from .generate import generate
from .aggregate import aggregate
from .server import register, upload
from .update import update
from .calibrate import calibrate
