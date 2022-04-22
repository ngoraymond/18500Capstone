from concurrent.futures import thread
import threading

from User_Interface import main
from camera_cv import run_loop

ui = threading.Thread(target=main)
cv = threading.Thread(target=run_loop)

cv.start()
ui.start()