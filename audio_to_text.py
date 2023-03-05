from __future__ import annotations
import time
import speech_recognition as sr
# also require pydub, pyaudio

class Audio_to_text:
    def __init__(self) -> None:
        self.r = sr.Recognizer()
        self.input_audio_file_name = 'audio_in.wav'
        self.star_flag = False
        self.stop_program = False

    def start(self, from_mic=False) -> tuple[str, float]:
        '''
        if from_mic=False, listen audio from wav file
        if from_mic=True,  listen audio from microphone

        return (out_text, conf)
        out_text: the results of audio to text
        conf: the results confidence
        '''
        if not from_mic:
            # open the file
            with sr.AudioFile(self.input_audio_file_name) as source:
                # listen for the data (load audio to memory)
                audio_data = self.r.record(source)
                # recognize (convert from speech to text)
                text = self.r.recognize_google(audio_data, language='zh-TW', show_all=True)
                out_text = text['alternative'][0]['transcript']
                conf = text['alternative'][0]['confidence']
                # print(out_text, conf)
        else:
            # Microphone
            while(True):
                if self.star_flag or self.stop_program:
                    break
                else:
                    time.sleep(0.5)
            
            if not self.stop_program:
                with sr.Microphone() as source:
                    # read the audio data from the default microphone
                    print('Start listening...')
                    audio_data = self.r.record(source, duration=5)
                    print("Recognizing...")
                    # convert speech to text
                    text = self.r.recognize_google(audio_data, language='zh-TW', show_all=True)
                    out_text = text['alternative'][0]['transcript']
                    conf = text['alternative'][0]['confidence']
                    # print(out_text, conf)
        
        conf = round(conf, 2)
        return out_text, conf

if __name__ == '__main__':
    test = Audio_to_text()
    out_text, conf = test.start(from_mic=False)
    print(type(out_text))
    print(type(conf))
    print(out_text, conf)