import logging
import threading
import time
import VexConfig
import VexBrain
import VexRealSense
import VexFlir
import VexLogic

threading.current_thread().name = "tMain"

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

logging.info("")
logging.info("VexAiJetson - Get Logic instance")
vl = VexLogic.VexLogic.getInstance()
logging.info("VexAiJetson - Get Brain instance")
vb = VexBrain.VexBrain.getInstance()
logging.info("VexAiJetson - Get RealSense instance")
vrs = VexRealSense.VexRealSense.getInstance()
logging.info("VexAiJetson - Get FLIR instance")
vf = VexFlir.VexFlir.getInstance()
logging.info("VexAiJetson - Set instances")
vl.setInstances(vb, vf, vrs)
threadEntry = [vb.threadEntry, vrs.threadEntry, vf.threadEntry, vl.threadEntry]
threads = []

logging.info("")
logging.info("--- Creating Threads")
for i in range(len(threadEntry)):
    #t = threading.Thread(target=threadEntry[i], args=(index,))
    t = threading.Thread(target=threadEntry[i], args=())
    threads.append(t)

logging.info("")
logging.info("--- Starting Threads")
for t in threads:
    #logging.info("Thread start : %s", t.name)
    t.start()
    #logging.info("Thread started : %s", t.name)

logging.info("")
logging.info("--- Joining Threads")
for t in threads:
    #logging.info("Thread join : %s", t.name)
    t.join()
    #logging.info("Thread joined : %s", t.name)

logging.info("")
logging.info("--- Back to main")
logging.info("")
