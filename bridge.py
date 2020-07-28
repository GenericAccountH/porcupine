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

targettext1 = "TS_on false"
targettext2 = '1'
sourcetext = ""

os.system('echo "Welcome to Gwen. How may I help you today?" | festival --tts')

while(True):
    os.system('python3 /home/pi/github/porcupine/demo/python/porcupine_demo_mic.py --keyword_file_paths /home/pi/github/porcupine/resources/keyword_files/raspberry-pi/picovoice_raspberry-pi.ppn')
    
#     file1 = open('out.txt','r+')
#     print("Output of read by line function:")
#     lines = file1.readlines()
#     print(lines[0])
#     sourcetext = lines[0]
#     if(targettext1 in sourcetext):
#         print(True)
#         TS_on = True
#     else:
#         print(False)
#         TS_on = False
        
#     file1.close()
    
    #os.system('echo "Yes?" | festival --tts')
 
    os.system('python3 /home/pi/github/speech/mic_vad_streaming/mic_vad_streaming.py -m output_graph.tflite -l lm.binary -t trie -v 3')
    
    file2 = open('out.txt','r+')
    lines = file2.readlines()
    sourcetext = lines[0]
    if(targettext2 in sourcetext):
        V_on = True
    else:
        V_on = False
    file2.close()
    
    sys.stdout = open('/home/pi/github/porcupine/out.txt', 'w')
    if(V_on == True):
        print("V_on True")
    else:
        print("V_on False")
    sys.stdout.close()
    
