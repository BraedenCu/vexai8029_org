

def getLoggingFormat():
    "Return the format to be used by all the logger for all the threads."
    format = "%(asctime)s.%(msecs)03d: %(threadName)12s : %(message)s"
    return format

#------------------------------------------------------------------------------
class VexConfig:

    def __init__(self):
        "Constructor for this object."

