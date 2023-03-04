from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from audiotsm import wsola
from audiotsm.io.wav import WavReader, WavWriter

class Text_to_audio:
    def __init__(self):
        self.mytext = ''
        self.output_file_name = 'audio_out.mp3'
        self.output_speed_up_file_name = 'audio_out_speed_up.wav'
        self.lang = 'zh-TW'

    def play(self, txt, speed_up=1.0):
        self.mytext = txt
        audio = gTTS(text=self.mytext, lang=self.lang, slow=False)
        audio.save(self.output_file_name)

        # os.system(f'ffmpeg -y -i {self.output_file_name} -af "atempo=1.50" speed_up.mp3')
        sound = AudioSegment.from_mp3(self.output_file_name)

        if speed_up != 1.0:
            sound.export("temp.wav", format="wav")

            with WavReader('temp.wav') as reader:
                with WavWriter(self.output_speed_up_file_name, reader.channels, reader.samplerate) as writer:
                    # tsm = phasevocoder(reader.channels, speed=2.0)
                    tsm = wsola(reader.channels, speed=1.5)
                    tsm.run(reader, writer)

            speed_up_sound = AudioSegment.from_wav(self.output_speed_up_file_name)
            play(speed_up_sound)
        else:
            play(sound)


if __name__ == '__main__':
    test = Text_to_audio()
    test.play('這是google語音系統', speed_up=1.6)
    # call(['ffmpeg', '-y', '-i', 'audio_out.mp3', '-af', '"atempo=1.50"', 'audio_out_speed_up.mp3'], stdout=STDOUT, stderr=STDOUT)