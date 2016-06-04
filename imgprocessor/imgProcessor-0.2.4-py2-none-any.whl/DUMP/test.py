import audioop
import pyaudio

chunk = 1024

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=chunk)

while True:
    data = stream.read(chunk)
    
    rms = audioop.rms(data, 2)  #width=2 for format=paInt16
    print rms