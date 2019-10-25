from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave

THRESHOLD = 800
CHUNK_SIZE = 8000
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(snd_data):
    "Returns true if below the silent THRESHOLD"
    print(max(snd_data))
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average out the volume"
    MAXIMUM = 16384
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')
        for i in snd_data:
            if not snd_started and abs(i) > THRESHOLD:
                snd_started = True
                r.append(i)
            elif snd_started:
                r.append(i)
        return r

    #first left
    snd_data = _trim(snd_data)

    #then left
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()

    return snd_data

def add_silence(snd_data, seconds):
    "add silence to the ends"
    r = array('h', [0 for i in range(int(seconds * RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds * RATE))])
    return r

def record():
    """
    Record a word or words from the microphone and returns the data as an
    array of signed shorts.

    Normalizes the audio, trims silence from the start and end, and pads
    with 0.5 seconds of blank sound to make sure VLC et al can play it without
    it getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, input_device_index=0, channels=1, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)
    num_silent = 0
    snd_started = False

    r = array('h')
    while 1:
        snd_data = array('h', stream.read(CHUNK_SIZE, exception_on_overflow = False))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)
        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            print("Sound started.")
            snd_started = True

        if snd_started and num_silent> 10:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    #r = trim(r)
    #r = add_silence(r, 0.5)
    return sample_width, r

def record_to_file(path):
    "Records from the microphone and ouputs the resulting data to path"
    print("Recording...")
    sample_width, data = record()

    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    print("Done.")

def play(path):
    wf = wave.open(path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, input_device_index=0, channels=1, rate=RATE, input=True, output=True, frames_per_buffer=512)
    data = wf.readframes(CHUNK_SIZE)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK_SIZE)
    stream.close()
    p.terminate()

if __name__ == '__main__':
    print("Please speak a word into the microphone")
    record_to_file('demo.wav')
    print("done - result written to demo.wav")
