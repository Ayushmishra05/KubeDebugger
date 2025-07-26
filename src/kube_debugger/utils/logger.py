import logging 
import os 
from datetime import datetime 



os.makedirs('logs' , exist_ok=True) 
filename = f"logs/{datetime.now().strftime(r"%H_%M_%S-%d_%M_%Y")}.log"
# print(fil)
logging.basicConfig(
    filename = filename, 
    format="%(asctime)s %(message)s", 
    filemode='w'
)

logger = logging.getLogger() 

logger.setLevel(logging.DEBUG) 
