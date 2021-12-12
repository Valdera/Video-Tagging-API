import speech_recognition as sr
import shutil
import subprocess
import json
import math
from fastapi import FastAPI, UploadFile, File
from pydub import AudioSegment

AUDIO_FILE = "on.wav"

app = FastAPI()


@app.post("/api/video/tag")
async def home(file: UploadFile = File(...)):
    with open('test.mp4', 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    command = 'ffmpeg -i video.mp4 -ab 160k -ar 44100 -vn audio.wav'
    subprocess.call(command, shell=True)

    text = speech_to_text()

    return {"file_name": file.filename}


def get_duration(filename):
    result = subprocess.check_output(
        f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
        shell=True).decode()
    fields = json.loads(result)['streams'][0]

    duration = fields['tags']['DURATION']
    hour, min, sec = duration.split(':')
    dur = float(hour) * 3600 + float(min) * 60 + float(sec) * 1
    return int(dur)


def split_audio(t1, t2):
    t1 = t1 * 1000
    t2 = t2 * 1000
    newAudio = AudioSegment.from_wav("audio.wav")
    newAudio = newAudio[t1:t2]
    newAudio.export('on.wav', format="wav")


def speech_to_text():
    dur = get_duration('video.mkv')

    split_audio(0, min(120, dur))

    r = sr.Recognizer()

    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
        text = r.recognize_google(audio)
        return text
