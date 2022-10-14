from os import  linesep, listdir
import os
from os.path import exists, isfile, join
from pathlib import Path
import re
import shutil
import azure.cognitiveservices.speech as speechsdk
from moviepy.video.io.VideoFileClip import VideoFileClip, AudioFileClip
from datetime import time
from pydub import AudioSegment

def miliseconds(ticks):
        return ticks/(10*1000)

def miliseconds_from_seconds(seconds):
        return seconds*1000

def time_from_ticks(ticks):
    microseconds_1 = ticks*1000000
    microseconds_2 = microseconds_1 % 1000000
    seconds_1 = microseconds_1 / 1000000
    seconds_2 = seconds_1 % 60
    minutes_1 = seconds_1 / 60
    minutes_2 = minutes_1 % 60
    hours = minutes_1 / 60
    return time(int(hours), int(minutes_2), int(seconds_2), int(microseconds_2))

class reprocess_video():
    def __init__(self,folder_path,from_language,gender,to_languages):
        self.from_language = from_language
        self.folder_path=folder_path
        self.gender=gender
        self.to_languages=to_languages
        self.sequence_number=1
        self.audio_number=1
        self.prev_offset=0
        self.durations=[]
        self.offsets=[]
        self.silences=[]
    
    def write_to_console_or_file(self,path,text, i) :
        file_path = Path(join(path,"caption_"+i+".srt"))
        with open(file_path, mode = "a", newline = "") as f :
            f.write(text)

    def initialize(self,folder,language) :
        path=join(folder,"Cache",language+"_ssml")
        if exists(path):
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            os.mkdir(path)
        path2=join(folder,"Cache",language)
        if exists(path2):
            shutil.rmtree(path2)
            os.mkdir(path2)
        else:
            os.mkdir(path2)
        if os.path.isfile(join(folder,"caption_"+language+".srt")):
            os.remove(join(folder,"caption_"+language+".srt"))

    def write_ssml(self,text, language,path) :
        file_path = Path(join(path,"Cache",(language+"_ssml"),"ssml_"+str(self.audio_number)+".xml"))
        with open(file_path, "w") as f:
            f.write(text)

    def speak_text(self,text,i,duration,path):
        speech_config = speechsdk.SpeechConfig(subscription="53be2989e41041cdb3cbec09f95fe0e8", region="eastus")
        file_name=join(path,"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav")
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
        print(text)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        #ssml_string = open(join(self.destination_path,"Cache/ssml.xml"), "r").read()
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        print("Saved  audio to {}".format(file_name))
        #print(join(path,"Cache/"+i+"/audio_"+i+"_"+str(self.audio_number)+".wav"))
        audio=AudioSegment.from_wav(join(path,"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav"))
        audio_duration=audio.duration_seconds*1000
        #print("Original:"+str(audio_duration))
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
        self.write_ssml(xml,i,path)

    def speak_ssml2(self,i,path):
        speech_config = speechsdk.SpeechConfig(subscription="53be2989e41041cdb3cbec09f95fe0e8", region="eastus")
        file_name=join(path,"Cache",i,"audio_"+i+"_"+str(self.audio_number)+".wav")
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

        ssml_string = open(join(path,"Cache",(i+"_ssml"),"ssml_"+str(self.audio_number)+".xml"), "r").read()
        speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_string).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details

    def join_audios(self,i,path):
        audio_out_file = join(path,"Cache","audio_"+i+".wav")
        audio_files = [f for f in listdir(join(path,"Cache",i)) if isfile(join(path,"Cache",i,f))]
        total_duration=AudioSegment.from_wav(join(path,"Cache","audio.wav")).duration_seconds*1000
        audios=[]
        self.silences=[self.offsets[0]]
        for k in range(len(audio_files)):
            aud=AudioSegment.from_wav(join(path,"Cache",i,"audio_"+i+"_"+str(k+1)+".wav"))
            audios.append(aud)
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
        #print(self.silences)
        #print(self.offsets)
        #print(self.durations)
        for j in range(len(audios)):
            final_audio=final_audio+audios[j]+AudioSegment.silent(duration=self.silences[j+1])

        final_audio.export(audio_out_file, format="wav")

        my_clip = VideoFileClip(join(path,"Cache",os.path.basename(os.path.normpath(path))+".mp4"))
        audio_background = AudioFileClip(audio_out_file)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(join(path,"["+i+"] "+os.path.basename(os.path.normpath(path))+".mp4"),fps=60)

    def reprocess(self):
        subfolders = [ f.path for f in os.scandir(self.folder_path) if f.is_dir() ]
        if exists(join(self.folder_path,"Cache")):
            #Loca Directory
            #print("In subfolder")
            self.translation_from_caption(self.folder_path)
        else:
            for i in subfolders:
                #print("Entering subfolder")
                self.translation_from_caption(i)
            
    def translation_from_caption(self,video_directory):
        for file in os.listdir(join(video_directory,"Cache")):
            if file.endswith(".txt"):
                self.sequence_number=1
                self.audio_number=1
                self.prev_offset=0
                self.durations=[]
                self.offsets=[]
                self.silences=[]
                language=file[8:10]
                if language in self.to_languages:
                    self.initialize(video_directory,language)
                    file1 = open(join(video_directory,"Cache",file), 'r')
                    Lines = file1.readlines()
                    countN = 0
                    contS=0
                    # Strips the newline character
                    for line in Lines:
                        if contS==3:
                            self.result_callback(text,language,duration,offset,video_directory)
                            contS=0
                        line=line.strip()
                        if len(line.strip()):
                            contS+=1
                            if line.strip()[0].isdigit():
                                if countN==0:
                                    countN += 1
                                else:
                                    x = line.replace("-","").replace(">","").replace(",",".").strip()
                                    x=re.split(':| ',x)
                                    contTime=0
                                    offset=0
                                    duration=0
                                    end=0
                                    for i in range(3):
                                        if contTime==0 and float(x[i])!=0:
                                            offset+=float(x[i])*60*60
                                        elif contTime==1 and float(x[i])!=0:
                                            offset+=float(x[i])*60
                                        elif contTime==2 and float(x[i])!=0:
                                            offset+=float(x[i])
                                        contTime+=1
                                    for i in range(3):
                                        if contTime==3 and float(x[i+4])!=0:
                                            end+=float(x[i+4])*60*60
                                        if contTime==4 and float(x[i+4])!=0:
                                            end+=float(x[i+4])*60
                                        if contTime==5 and float(x[i+4])!=0:
                                            end+=float(x[i+4])
                                        contTime+=1
                                    duration=end-offset
                                    countN=0
                            else:
                                text=line.strip()
                    self.join_audios(language,video_directory)
                    shutil.copyfile(join(video_directory,'caption_'+language+'.srt'), join(video_directory,"Cache",'caption_'+language+'.txt'))

    def result_callback(self,text,language,duration,offset,path):
        caption = ""
        caption += str(self.sequence_number) + linesep
        self.sequence_number=self.sequence_number+1
        start_time = time_from_ticks(offset)
        end_time = time_from_ticks(offset + duration)
        time_format = ""
        time_format = "%H:%M:%S,%f"
        caption += "{} --> {}".format(start_time.strftime(time_format)[:-3], end_time.strftime(time_format)[:-3]) + linesep
        caption += text + linesep + linesep
        self.speak_text(text,language,miliseconds_from_seconds(duration),path)
        self.speak_ssml2(language,path)
        self.durations.append(miliseconds_from_seconds(duration))
        self.offsets.append(miliseconds_from_seconds(offset))
        self.prev_offset=offset
        self.audio_number += 1
        self.write_to_console_or_file(path, caption, language)