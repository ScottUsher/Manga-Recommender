#**********************************************************************
# Author: Scott usher
# Date Created: 9/20/2026
# Purpose: This file is used to initialize an interactable user interface in the file manga_recomendation.py
#          This file also exists with the perpose of using pyinstaller and getting the whole package into a .exe
#
#**********************************************************************

import os
import sys
import time
import threading
import tempfile
import webbrowser

IDLE_TIMEOUT = 30 * 60
CHECK_INTERVAL = 5

runtime_dir = os.path.join(tempfile.gettempdir(), "MyRecommenderApp")
os.makedirs(runtime_dir, exist_ok=True)

shutdown_file = os.path.join(runtime_dir, "shutdown")
heartbeat_file = os.path.join(runtime_dir, "heartbeat")

for file in (shutdown_file, heartbeat_file):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

os.environ["APP_RUNTIME_DIR"] = runtime_dir

app_path = os.path.join(
    sys._MEIPASS if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__)),
    "manga_recomendation.py"
)

#**********************************************************************
# Purpose: shutting down the streamlit server when needed
#
# Precondition: initializes a heartbeat to comunicate when the user has interacted with the streamlit appp
#               
# Postcondition: if the user has not interacted for the length of IDLE_TIMEOUT then the server is stopped and the browser app becomes nonfunctional unless opened again
#
#***********************************************************************
def monitor_application():
    last_activity = time.time()
 
    while True:
        if os.path.exists(shutdown_file):
            os._exit(0)

        try:
            heartbeat_time = os.path.getmtime(heartbeat_file)

            if heartbeat_time > last_activity:
                last_activity = heartbeat_time

        except FileNotFoundError:
            pass

        if time.time() - last_activity >= IDLE_TIMEOUT:
            os._exit(0)

        time.sleep(CHECK_INTERVAL)

with open(heartbeat_file, "w"):
    pass

threading.Thread(
    target=monitor_application,
    daemon=True
).start()

#**********************************************************************
# Purpose: Opening a browser to display the streamlit app
#
# Precondition: while this code is being run the streamlit app is initializing and is hopefully stated after the wait period has passed
#               
# Postcondition: the streamlit app is displaied in a browser
#
#***********************************************************************
def open_browser():
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

threading.Thread(
    target=open_browser,
    daemon=True
).start()

from streamlit.web import cli

sys.argv = [
    "streamlit",
    "run",
    app_path,
    "--global.developmentMode=false",
    "--server.headless=true",
    "--browser.serverPort=8501",
]

cli.main()