import pyaudio
import wave
import time

class Record_to_audio:
    def __init__(self):
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.seconds = 4
        self.filename = 'audio_in.wav'
        self.star_flag = False
        self.stop_program = False

        
    def start_recording(self):
        print('wait Recording')
        p = pyaudio.PyAudio()  # Create an interface to PortAudio
        stream = p.open(format=self.sample_format, channels=self.channels, rate=self.fs, frames_per_buffer=self.chunk, input=True)
        frames = []  # Initialize array to store frames
        f = ''
        
        while(True):
            if self.star_flag or self.stop_program:
                break
            else:
                time.sleep(0.5)
        
        if not self.stop_program:
            print('start Recording')
            while(True):
                data = stream.read(self.chunk)
                frames.append(data)
                if self.star_flag == False:
                    break
            
            # # Store data in chunks for self.seconds seconds
            # for i in range(0, int(self.fs / self.chunk * self.seconds)):
            #     data = stream.read(self.chunk)
            #     frames.append(data)

            # Stop and close the stream 
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()

            # Save the recorded data as a WAV file
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()

            print('Finished recording, saved as ' + self.filename)

            # f = open(self.filename, "rb")
        # return f