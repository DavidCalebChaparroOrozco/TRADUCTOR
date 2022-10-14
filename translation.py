from ast import Break
from fileinput import filename
import json
from os import linesep, listdir, path
import os
from os.path import exists, isfile, join
from pathlib import Path
import shutil
from time import sleep
import azure.cognitiveservices.speech as speechsdk
from moviepy.video.io.VideoFileClip import VideoFileClip, AudioFileClip
from datetime import time
from pydub import AudioSegment

def time_from_ticks(ticks):
    microseconds_1 = ticks / 10
    microseconds_2 = microseconds_1 % 1000000
    seconds_1 = microseconds_1 / 1000000
    seconds_2 = seconds_1 % 60
    minutes_1 = seconds_1 / 60
    minutes_2 = minutes_1 % 60
    hours = minutes_1 / 60
    return time(int(hours), int(minutes_2), int(seconds_2), int(microseconds_2))

def miliseconds(ticks):
        return ticks/(10*1000)

class translate_video():
    def __init__(self,video_path,video_name,destination_path,from_language,to_languages,gender):
        self.from_language = from_language
        self.video_name=video_name
        self.to_languages=to_languages
        self.video_path=video_path
        self.gender=gender
        self.destination_path=destination_path
        self.sequence_number=1
        self.audio_number=1
        self.prev_offset=0
        self.durations=[]
        self.offsets=[]
        self.silences=[]
        self.checkpoint1=0
        self.checkpoint2=0

    def video_to_audio(self):
        shutil.copyfile(self.video_path, join(self.destination_path,self.video_name[:-4],"Cache",self.video_name))
        print("Video Copied")
        my_clip = VideoFileClip(self.video_path)
        my_clip.audio.write_audiofile(join(self.destination_path,self.video_name[:-4],"Cache","audio.wav"))
        print("Divided audio.wav")

    def write_to_console_or_file(self,text : str, i:str) :
        file_path = Path(join(self.destination_path,self.video_name[:-4],"caption_"+i+".srt"))
        file_path2 = Path(join(self.destination_path,self.video_name[:-4],"Cache","caption_"+i+".txt"))
        with open(file_path, mode = "a", newline = "") as f :
            f.write(text)
        with open(file_path2, mode = "a", newline = "") as f :
            f.write(text)
        print("Writing Caption...")
        
    def write_ssml(self,text, i) :
        file_path = Path(join(self.destination_path,self.video_name[:-4],"Cache",(i+"_ssml"),"ssml_"+str(self.audio_number)+".xml"))
        with open(file_path, "w") as f:
            f.write(text)

    def initialize(self) :
        if not exists(join(self.destination_path,self.video_name[:-4])):
            os.mkdir(join(self.destination_path,self.video_name[:-4]))
        else:
            shutil.rmtree(join(self.destination_path,self.video_name[:-4]))
            os.mkdir(join(self.destination_path,self.video_name[:-4]))
        if not exists(join(self.destination_path,self.video_name[:-4],"Cache")):
            os.mkdir(join(self.destination_path,self.video_name[:-4],"Cache"))
        else:
            shutil.rmtree(join(self.destination_path,self.video_name[:-4],"Cache"))
            os.mkdir(join(self.destination_path,self.video_name[:-4],"Cache"))
        print("Initialized")
    
    def initialize_i(self,i):
        if not exists(join(self.destination_path,self.video_name[:-4],"Cache",i)):
            os.mkdir(join(self.destination_path,self.video_name[:-4],"Cache",i))
        if not exists(join(self.destination_path,self.video_name[:-4],"Cache",i+"_ssml")):
            os.mkdir(join(self.destination_path,self.video_name[:-4],"Cache",i+"_ssml"))
        if os.path.isfile(join(self.destination_path,self.video_name[:-4],"caption_"+i+".srt")):
            os.remove(join(self.destination_path,self.video_name[:-4],"caption_"+i+".srt"))
        if os.path.isfile(join(self.destination_path,self.video_name[:-4],"Cache","caption_"+i+".txt")):
            os.remove(join(self.destination_path,self.video_name[:-4],"Cache","caption_"+i+".txt"))
        print("Intialized 2")

    def speak_text(self,text,i,duration):
        try:
            speech_config = speechsdk.SpeechConfig(subscription="53be2989e41041cdb3cbec09f95fe0e8", region="eastus")
            file_name=join(self.destination_path,self.video_name[:-4],"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
            lang=""
            voice=""
            if self.gender=="male":
                if i=="en":
                    speech_config.speech_synthesis_voice_name='en-US-GuyNeural'
                    lang="en-ES"
                    voice="en-US-GuyNeural"
                elif i=="it":
                    speech_config.speech_synthesis_voice_name='it-IT-DiegoNeural'
                    lang="it-IT"
                    voice="it-IT-DiegoNeural"
                elif i=="fr":
                    speech_config.speech_synthesis_voice_name='fr-FR-AlainNeural'
                    lang="fr-FR"
                    voice="fr-FR-AlainNeural"
            elif self.gender=="female":
                if i=="en":
                    speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
                    lang="en-ES"
                    voice="en-US-JennyNeural"
                elif i=="it":
                    speech_config.speech_synthesis_voice_name='it-IT-ElsaNeural'
                    lang="it-IT"
                    voice="it-IT-ElsaNeural"
                elif i=="fr":
                    speech_config.speech_synthesis_voice_name='fr-FR-DeniseNeural'
                    lang="fr-FR"
                    voice="fr-FR-DeniseNeural"
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            print(text)
            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
            print("Translating")
            if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
            print(join(self.destination_path,self.video_name[:-4],"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav"))
            audio=AudioSegment.from_wav(join(self.destination_path,self.video_name[:-4],"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav"))
            audio_duration=audio.duration_seconds*1000
            rate=-((duration-audio_duration)/audio_duration)*90
            if abs(rate)>15:
                if rate>0:
                    rate=15.0
                else:
                    rate=-15.0
            if rate<0:
                sign=""
            else:
                sign="+"
            xml= """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">
                        <voice name="{voice}">
                            <prosody rate="{sign}{rate}%">
                                {text}
                            </prosody>
                        </voice>
                    </speak>""".format(lang=lang,voice=voice,sign=sign,rate=str(round(rate, 6)),text=text)
            print("Saved "+file_name)
            self.write_ssml(xml,i)
            
        except Exception as e:
            print(e)
        

    def speak_ssml2(self,i):
        try:
            speech_config = speechsdk.SpeechConfig(subscription="53be2989e41041cdb3cbec09f95fe0e8", region="eastus")
            file_name=join(self.destination_path,self.video_name[:-4],"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
            if self.gender=="male":
                if i=="en":
                    speech_config.speech_synthesis_voice_name='en-US-GuyNeural'
                elif i=="it":
                    speech_config.speech_synthesis_voice_name='it-IT-DiegoNeural'
                elif i=="fr":
                    speech_config.speech_synthesis_voice_name='fr-FR-AlainNeural'
            elif self.gender=="female":
                if i=="en":
                    speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
                elif i=="it":
                    speech_config.speech_synthesis_voice_name='it-IT-ElsaNeural'
                elif i=="fr":
                    speech_config.speech_synthesis_voice_name='fr-FR-DeniseNeural'

            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            ssml_string = open(join(self.destination_path,self.video_name[:-4],"Cache",(i+"_ssml"),"ssml_"+str(self.audio_number)+".xml"), "r").read()
            speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_string).get()
            if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
            print("Saved2 "+file_name)
        except Exception as e:
            print(e)


    def join_audios(self,i):
        print("Joining Audios")
        audio_out_file = join(self.destination_path,self.video_name[:-4],"Cache","audio_"+i+".wav")
        audio_files = [f for f in listdir(join(self.destination_path,self.video_name[:-4],"Cache",i)) if isfile(join(self.destination_path,self.video_name[:-4],"Cache",i,f))]
        audios=[]
        new_audios=[]
        self.silences=[self.offsets[0]]
        print(audio_files)
        for k in range(len(audio_files)):
            print(join(self.destination_path,self.video_name[:-4],"Cache",i,"audio_"+i+"_"+str(k+1)+".wav"))
            aud=AudioSegment.from_wav(join(self.destination_path,self.video_name[:-4],"Cache",i,"audio_"+i+"_"+str(k+1)+".wav"))
            audios.append(aud)
            new_audios.append(aud.duration_seconds*1000)
        total_duration=AudioSegment.from_wav(join(self.destination_path,self.video_name[:-4],"Cache","audio.wav")).duration_seconds*1000
        print("Total Duration: "+str(total_duration))
        for j in range(len(audios)):
            #print("New:"+str(audios[j].duration_seconds*1000))
            if j<len(audios)-1:
                silence=self.offsets[j+1]-self.offsets[j]-audios[j].duration_seconds*1000
                self.silences.append(silence)
            else:
                silence=total_duration-self.offsets[j]-audios[j].duration_seconds*1000
                self.silences.append(silence)
        k=1
        while k<len(self.silences):
            if self.silences[k]<0:
                self.silences[k-1]=self.silences[k-1]+self.silences[k]
                self.silences[k]=0
                k=1
            else:
                k+=1
        
        k=0
        while k<len(self.silences)-1:
            if self.silences[k]<0:
                self.silences[k+1]=self.silences[k+1]+self.silences[k]
                self.silences[k]=0
                k=0
            else:
                k+=1

        final_audio = AudioSegment.empty()
        final_audio=AudioSegment.silent(duration=self.silences[0])
        print("Silences")
        print(self.silences)
        print("Offsets")
        print(self.offsets)
        print("New Durations")
        print(new_audios)
        print("Durations")
        print(self.durations)
        for j in range(len(audios)):
            final_audio=final_audio+audios[j]+AudioSegment.silent(duration=self.silences[j+1])

        final_audio.export(audio_out_file, format="wav")

        my_clip = VideoFileClip(self.video_path)
        audio_background = AudioFileClip(audio_out_file)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(join(self.destination_path,self.video_name[:-4],"["+i+"] "+self.video_name),fps=60)

    def result_callback(self,event_type: str,evt: speechsdk.translation.TranslationRecognitionEventArgs,i: str):
        results=json.loads(evt.result.json)
        if results["RecognitionStatus"]=="Success":
            print("Callback"+str(self.audio_number))
            print(results)
            caption = ""
            caption += str(self.sequence_number) + linesep
            self.sequence_number=self.sequence_number+1
            start_time = time_from_ticks(results["Offset"])
            end_time = time_from_ticks(results["Offset"] + results["Duration"])
            time_format = ""
            time_format = "%H:%M:%S,%f"
            caption += "{} --> {}".format(start_time.strftime(time_format)[:-3], end_time.strftime(time_format)[:-3]) + linesep
            caption += results["Translation"]["Translations"][0]["Text"] + linesep + linesep
            self.speak_text(results["Translation"]["Translations"][0]["Text"],i,miliseconds(results["Duration"]))
            self.speak_ssml2(i)
            self.durations.append(miliseconds(results["Duration"]))
            self.offsets.append(miliseconds(results["Offset"]))
            self.prev_offset=results["Offset"]
            self.audio_number += 1
            self.write_to_console_or_file(caption, i)
            

    def translation_continuous(self):
        self.initialize()
        self.video_to_audio()
        for i in self.to_languages:
            self.sequence_number=1
            self.audio_number=1
            self.prev_offset=0
            self.durations=[]
            self.offsets=[]
            self.silences=[]
            self.initialize_i(i)
            """performs continuous speech translation from input from an audio file"""
            translation_config = speechsdk.translation.SpeechTranslationConfig(subscription="53be2989e41041cdb3cbec09f95fe0e8", region="eastus")
            translation_config.speech_recognition_language=self.from_language

            translation_config.add_target_language(i)
            
            audio_config = speechsdk.audio.AudioConfig(filename=join(self.destination_path,self.video_name[:-4],'Cache','audio.wav'))
            
            # Creates a translation recognizer using and audio file as input.
            recognizer = speechsdk.translation.TranslationRecognizer(
                translation_config=translation_config, audio_config=audio_config)

            done = False

            def stop_cb(evt: speechsdk.SessionEventArgs):
                """callback that signals to stop continuous recognition upon receiving an event `evt`"""
                #print('CLOSING on {}'.format(evt))
                nonlocal done
                done = True

            # connect callback functions to the events fired by the recognizer
            #recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
            #recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
            # event for intermediate results
            #recognizer.recognizing.connect(lambda evt: result_callback('RECOGNIZING', evt))
            # event for final result
            recognizer.recognized.connect(lambda evt: self.result_callback('RECOGNIZED', evt,i))
            # cancellation event
            #recognizer.canceled.connect(lambda evt: print('CANCELED: {} ({})'.format(evt, evt.reason)))

            # stop continuous recognition on either session stopped or canceled events
            recognizer.session_stopped.connect(stop_cb)
            recognizer.canceled.connect(stop_cb)

            def synthesis_callback(evt: speechsdk.translation.TranslationRecognitionEventArgs):
                """
                callback for the synthesis event
                """
                #print('SYNTHESIZING {}\n\treceived {} bytes of audio. Reason: {}'.format(evt, len(evt.result.audio), evt.result.reason))

            # connect callback to the synthesis event
            recognizer.synthesizing.connect(synthesis_callback)

            # start translation
            recognizer.start_continuous_recognition()

            while not done:
                sleep(.5)

            recognizer.stop_continuous_recognition()
            self.join_audios(i)