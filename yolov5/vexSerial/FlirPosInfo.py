import logging
import VexConfig

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

#------------------------------------------------------------------------------
class FlirPosInfo:
    "This class contains information on robot position, as determined by the \
     FLIR camera using the Game Position System VAIC strips."

    def __init__(self):
        "Constructor for this object."
        # TBD - Finish

    def display(self):
        "Display contents of the current object."
        # TBD - Finish

