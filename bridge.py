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
from subprocess import run
import tempfile


callsign = False
counter = 2
i = 0

while(True):
    animal = os.system('python3 /home/pi/github/porcupine/demo/python/porcupine_demo_mic.py --keyword_file_paths /home/pi/github/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn')
    print(animal)

    proc=subprocess.Popen('echo "to stdout"', shell=True, stdout=subprocess.PIPE, )
    output=proc.communicate()[0]
    print output
    
    os.system('python3 /home/pi/github/speech/mic_vad_streaming/mic_vad_streaming.py -m output_graph.tflite -l lm.binary -t trie -v 3')
