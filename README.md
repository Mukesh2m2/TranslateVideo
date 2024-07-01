# TranslateVideo
Tool for making lectures accessible by translating videos fron one language to user preferred language.

## Features
- Translates video content while retaining original background music and audio ambiance for an immersive experience.
- Supports multiple input and output language variations to reach diverse audiences.
- Generates subtitle files in SRT format in the user’s chosen language.
- Ensures seamless synchronization between audio and video for an optimal viewing experience.
- Uses Google Speech-to-Text, Translate, and Text-to-Speech APIs for audio translation.
- Utilizes moviepy and librosa for video processing, including removing audio from videos and recombining them after audio translation..
- Integrates vocal-remover to separate instrumental and vocal audio tracks.
- Uses pysrt to generate subtitle files.


`
## Usage
Install dependencies
```
python -m pip install -r requirements.txt
```

We are using vocal-remover to separate vocal and instrumental audios.
#### To setup vocal-remover 
- go to link https://github.com/tsurumeso/vocal-remover/releases/tag/v5.1.0
- From Assets download vocal-remover-v5.1.0.zip
- Then extract and just take folder named vocal-remover and put in this folder


Review and alter `run.py` file as preferences for selecting input file name, input language and output language .

For dubbing the video in different language, run below command
```
python run.py
```

For generating the subtitles , run below command

```
python subtitles.py
```
Note: need to run `run.py` before running `subtitles.py` for generating subtitle file.