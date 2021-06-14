import logging
import threading
import time
import VexConfig
import VexLogic

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

#------------------------------------------------------------------------------
class VexFlir:
    __instance = None

    def __init__(self):
        "Constructor for this object."
        if VexFlir.__instance != None:
            raise Exception("VexFlir - Singleton error in __init__")
        else:
            VexFlir.__instance = self
            self.vexLogic = VexLogic.VexLogic.getInstance()

    def getInstance():
        "Static access method to get the Singleton instance."
        logging.info("VexFlir.getInstance()")
        if VexFlir.__instance == None:
            VexFlir()
        return VexFlir.__instance

    def threadEntry(self):
        "Entry point for the VEX FLIR Camera thread."
        threading.current_thread().name = "tFlir"
        logging.info("")
        logging.info("------------------------")
        logging.info("--- Thread starting ---")
        logging.info("------------------------")
        logging.info("")
        logging.info("Thread sleep")
        time.sleep(4)
        logging.info("Thread slept")
        logging.info("")
        logging.info("------------------------")
        logging.info("--- Thread finishing ---")
        logging.info("------------------------")
        logging.info("")

