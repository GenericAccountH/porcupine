import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal

import subprocess
import tempfile


callsign = False
counter = 2
i = 0

os.system('python3 /home/pi/github/porcupine/demo/python/porcupine_demo_mic.py --keyword_file_paths /home/pi/github/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn')
print()
with tempfile.TemporaryFile() as tempf:
    proc = subprocess.Popen(['echo', 'a', 'b'], stdout=tempf)
    proc.wait()
    tempf.seek(0)
    print tempf.read()

    #read output, call voice detection from here
#logic should be placed here 
#porcupine should call this, which in turn should call deepspeech
#print("Callsign exit successful. Commence command script")
os.system('python3 /home/pi/github/speech/mic_vad_streaming/mic_vad_streaming.py -m output_graph.tflite -l lm.binary -t trie -v 3')
