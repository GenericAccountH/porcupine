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
import sys
import io

TS_on = False
V_on = False
command = False
isClear = False

targettext = "TS_on false"
sourcetext = ""

while(True):
    os.system('python3 /home/pi/github/porcupine/demo/python/porcupine_demo_mic.py --keyword_file_paths /home/pi/github/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn')
    
    file1 = open('out.txt','r+')
    print("Output of read by line function:")
    lines = file1.readlines()
    print(lines[0])
    print(lines[1])
    sourcetext = lines[0]
    if(targettext in sourcetext):
        print(True)
    else:
        print(False)
        
    os.system('echo "Welcome to Gwen. How may I help you today?" | festival --tts')
    
#     ou = os.popen('python3 /home/pi/github/porcupine/demo/python/porcupine_demo_mic.py --keyword_file_paths /home/pi/github/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn').read()
#     ou.close()
#     print(ou)
#     proc = subprocess.Popen(["python3", "/home/pi/github/porcupine/demo/python/porcupine_demo_mic.py --keyword_file_paths /home/pi/github/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn"], stdout=subprocess.PIPE, shell=True)
#     (out, err) = proc.communicate()
#     print("program output:", out)
    
    os.system('python3 /home/pi/github/speech/mic_vad_streaming/mic_vad_streaming.py -m output_graph.tflite -l lm.binary -t trie -v 3')
