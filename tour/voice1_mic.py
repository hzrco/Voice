from __future__ import annotations

import sounddevice as sd
import soundfile as sf
import time
from pathlib import Path
import sys
import os
import numpy as np


# mic
device_id = 0 # 

mic_channels = 1
sample_rate = 16000
segment_duration = 1 # 1 second

# speaker
device_id_spk = 0
play_sample_rate = 16000

# sound data
seg_full = np.array([])
rec_sconds = 0
save_file = 1

# path helper
class PathHelper:
    @classmethod
    def get_script_path(self):
        script_dir = ''

        # 获取上级目录
        if getattr(sys, 'frozen', False):
            # 脚本被打包为可执行文件
            script_dir = os.path.dirname(sys.executable)
        else:
            # 普通脚本运行
            script_dir = os.path.dirname(os.path.abspath(__file__))

        script_dir = Path(script_dir).resolve()

        return script_dir
    pass

# enum mic and speaker
def enum_devices():
    global device_id, device_id_spk, play_sample_rate, mic_channels

    device_info = sd.query_devices()

    name = ''

    # print device info
    for i, info in enumerate(device_info):
        
        print(f"Device {i}: {info['name']}, Default samplerate: {info.get('default_samplerate')}")
        if info['name'].find('ReSpeaker') != -1:
            device_id = i
            device_id_spk = i
            name = info["name"]
            mic_channels = 6
            play_sample_rate = 16000

        if info['name'].find('Yundea') != -1:
            device_id = i
            device_id_spk = i
            name = info["name"]
            mic_channels = 1
            play_sample_rate = 48000

        # MacBook Pro mic
        if info['name'].find('MacBook Pro麦克风') != -1:
            device_id = i
            name = info["name"]
            mic_channels = 1
            play_sample_rate = 44100

        # MacBook Pro speaker
        if info['name'].find('MacBook Pro扬声器') != -1:
            device_id_spk = i
            name = info["name"]
            mic_channels = 1
            play_sample_rate = 44100

    print(f'{device_id}={name}')
    
enum_devices()

# Play an audio clip to test AEC
# Ensure that the microphone supports AEC and that the feature is enabled.
# AEC should prevent the playback audio from being captured in the "mic_file"
def play_voice():

    path = PathHelper.get_script_path()

    file = os.path.join(path, 'wav', 'ttm_here.wav')

    seg, sr = sf.read(file)

    sd.play(seg, sr, device=device_id_spk)
    sd.wait()

    pass


def proc_mic(indata, frames, ftime, status):
    global rec_sconds, seg_full
                
    seg0 = indata[:, 0].copy()

    seg_full = np.append(seg_full, seg0)

    rec_sconds += 1

    print('got seg: ', rec_sconds)


def on_exit():
    global save_file

    if save_file:
        path = PathHelper.get_script_path()

        p = os.path.join(path, 'tmp')

        if os.path.exists(p) == False:
            os.makedirs(p)

        mic_file = os.path.join(p,  'mic.wav')

        sf.write(mic_file, seg_full, sample_rate)

        print(mic_file)

    pass

def main():

    size = (int)(sample_rate*segment_duration)

    with sd.InputStream(samplerate=sample_rate, channels=mic_channels, callback=proc_mic, 
                blocksize=size, device=device_id):
        
        print(f'mic ready, channels: {mic_channels}')

        try:
            # main loop
            while True:

                text = input()

                if text == 'play':
                    print('play voice')
                    play_voice()

                continue

        except KeyboardInterrupt:

            pass

        finally:
            on_exit()

            pass


if __name__ == "__main__":
    main()