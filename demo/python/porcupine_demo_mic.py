#
# Copyright 2018 Picovoice Inc.
#
# You may not use this file except in compliance with the license. A copy of the license is located in the "LICENSE"
# file accompanying this source.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

import argparse
import os
import struct
import sys
from datetime import datetime
from threading import Thread
import RPi.GPIO as GPIO

import numpy as np
import pyaudio
import soundfile

sys.path.append(os.path.join(os.path.dirname(__file__), '../../binding/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../resources/util/python'))

from porcupine import Porcupine
from util import *

TS_on = False # Make this line 1 of input, initially False
touchclear = False # Make this line 2 of input, initially False
isClear = False #Make this line 3 of input, initially False

plcPin = 17
tsPin = 23
inPin = 26 #tsPowerPin

GPIO.setmode(GPIO.BCM) #pin names vs CPU defined names

GPIO.setup(inPin,GPIO.IN) #reads "analog" input
GPIO.setup(plcPin,GPIO.OUT) #17 is PLC output pin
GPIO.setup(tsPin,GPIO.OUT) #supplies constant high signal for ts circuit

GPIO.output(tsPin,GPIO.HIGH) 

class PorcupineDemo(Thread):
    """
    Demo class for wake word detection (aka Porcupine) library. It creates an input audio stream from a microphone,
    monitors it, and upon detecting the specified wake word(s) prints the detection time and index of wake word on
    console. It optionally saves the recorded audio into a file for further review.
    """

    def __init__(
            self,
            library_path,
            model_file_path,
            keyword_file_paths,
            sensitivities,
            input_device_index=None,
            output_path=None):

        """
        Constructor.

        :param library_path: Absolute path to Porcupine's dynamic library.
        :param model_file_path: Absolute path to the model parameter file.
        :param keyword_file_paths: List of absolute paths to keyword files.
        :param sensitivities: Sensitivity parameter for each wake word. For more information refer to
        'include/pv_porcupine.h'. It uses the
        same sensitivity value for all keywords.
        :param input_device_index: Optional argument. If provided, audio is recorded from this input device. Otherwise,
        the default audio input device is used.
        :param output_path: If provided recorded audio will be stored in this location at the end of the run.
        """

        super(PorcupineDemo, self).__init__()

        self._library_path = library_path
        self._model_file_path = model_file_path
        self._keyword_file_paths = keyword_file_paths
        self._sensitivities = sensitivities
        self._input_device_index = input_device_index

        self._output_path = output_path
        if self._output_path is not None:
            self._recorded_frames = []

    def run(self):
        """
         Creates an input audio stream, initializes wake word detection (Porcupine) object, and monitors the audio
         stream for occurrences of the wake word(s). It prints the time of detection for each occurrence and index of
         wake word.
         """
        #Insert TS_on logic here
        global TS_on, touchClear, isClear
        num_keywords = len(self._keyword_file_paths)

        keyword_names = list()
        for x in self._keyword_file_paths:
            keyword_names.append(os.path.basename(x).replace('.ppn', '').replace('_compressed', '').split('_')[0])

        print('listening for:')
        for keyword_name, sensitivity in zip(keyword_names, self._sensitivities):
            print('- %s (sensitivity: %.2f)' % (keyword_name, sensitivity))

        porcupine = None
        pa = None
        audio_stream = None
        try:
            porcupine = Porcupine(
                library_path=self._library_path,
                model_file_path=self._model_file_path,
                keyword_file_paths=self._keyword_file_paths,
                sensitivities=self._sensitivities)

            pa = pyaudio.PyAudio()
            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length,
                input_device_index=self._input_device_index)

            while True:
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                if self._output_path is not None:
                    self._recorded_frames.append(pcm)

                result = porcupine.process(pcm)
                #print("Helo")
                #TS side
                i = GPIO.input(inPin)
                print("Touch pin:",i)
	
                if(i == True and touchClear == False):
                    TS_on = False
                    print("Glass opaque")
                    isClear = False
	
                elif(i == True and touchClear == True):
                    TS_on = False
                    print("Touching glass opaque")
                    touchClear = False
                    isClear = False
	
                elif(i == False and touchClear == True):
                    TS_on = True
                    print("Glass clear")
                    isClear = True
                    
                elif(i == False and touchClear == False):      
                    TS_on = True
                    print("Touching glass clear")
                    touchClear = True
                    isClear = True
                
                if(isClear == True):
                    GPIO.output(plcPin,GPIO.HIGH) 
                else:
                    GPIO.output(plcPin,GPIO.LOW)
                
                if num_keywords == 1 and result:
                    print('[%s] detected keyword' % str(datetime.now()))
                    sys.stdout = open('/home/pi/github/porcupine/out.txt', 'w')
                    if(TS_on == True and touchclear == True): #print("Capture this - line 1")
                        print("TS_on true")
                        print("touchclear true")                        
                    elif(TS_on == False and touchclear == True):
                        print("TS_on false")
                        print("touchclear true")
                    elif(TS_on == True and touchclear == False):
                        print("TS_on true")
                        print("touchclear false")
                    else:
                        print("TS_on false")
                        print("touchclear false")
                        
                    sys.stdout.close()
                    sys.exit()
                   
                elif num_keywords > 1 and result >= 0:
                    print('[%s] detected %s' % (str(datetime.now()), keyword_names[result]))
                    
            #print("The following is output:")
            return output_val    

        except KeyboardInterrupt:
            print('stopping ...')
        finally:
            
            if porcupine is not None:
                porcupine.delete()

            if audio_stream is not None:
                audio_stream.close()

            if pa is not None:
                pa.terminate()

            if self._output_path is not None and len(self._recorded_frames) > 0:
                recorded_audio = np.concatenate(self._recorded_frames, axis=0).astype(np.int16)
                soundfile.write(self._output_path, recorded_audio, samplerate=porcupine.sample_rate, subtype='PCM_16')

    _AUDIO_DEVICE_INFO_KEYS = ['index', 'name', 'defaultSampleRate', 'maxInputChannels']

    @classmethod
    def show_audio_devices_info(cls):
        """ Provides information regarding different audio devices available. """

        pa = pyaudio.PyAudio()

        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            print(', '.join("'%s': '%s'" % (k, str(info[k])) for k in cls._AUDIO_DEVICE_INFO_KEYS))

        pa.terminate()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--keywords', help='comma-separated list of default keywords (%s)' % ', '.join(KEYWORDS))

    parser.add_argument('--keyword_file_paths', help='comma-separated absolute paths to keyword files')

    parser.add_argument('--library_path', help="absolute path to Porcupine's dynamic library", default=LIBRARY_PATH)

    parser.add_argument('--model_file_path', help='absolute path to model parameter file', default=MODEL_FILE_PATH)

    parser.add_argument('--sensitivities', help='detection sensitivity [0, 1]', default=0.5)

    parser.add_argument('--input_audio_device_index', help='index of input audio device', type=int, default=None)

    parser.add_argument(
        '--output_path',
        help='absolute path to where recorded audio will be stored. If not set, it will be bypassed.')

    parser.add_argument('--show_audio_devices_info', action='store_true')

    args = parser.parse_args()

    if args.show_audio_devices_info:
        PorcupineDemo.show_audio_devices_info()
    else:
        if args.keyword_file_paths is None:
            if args.keywords is None:
                raise ValueError('either --keywords or --keyword_file_paths must be set')

            keywords = [x.strip() for x in args.keywords.split(',')]

            if all(x in KEYWORDS for x in keywords):
                keyword_file_paths = [KEYWORD_FILE_PATHS[x] for x in keywords]
            else:
                raise ValueError(
                    'selected keywords are not available by default. available keywords are: %s' % ', '.join(KEYWORDS))
        else:
            keyword_file_paths = [x.strip() for x in args.keyword_file_paths.split(',')]

        if isinstance(args.sensitivities, float):
            sensitivities = [args.sensitivities] * len(keyword_file_paths)
        else:
            sensitivities = [float(x) for x in args.sensitivities.split(',')]

        PorcupineDemo(
            library_path=args.library_path,
            model_file_path=args.model_file_path,
            keyword_file_paths=keyword_file_paths,
            sensitivities=sensitivities,
            output_path=args.output_path,
            input_device_index=args.input_audio_device_index).run()


if __name__ == '__main__':
    main()
