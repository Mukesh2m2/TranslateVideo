import json
import librosa
import numpy as np
import soundfile as sf
from moviepy.audio.AudioClip import AudioClip
from moviepy.editor import (VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip)


class AudioVideoProcessor:

    @staticmethod
    def frame_start_end_time(audio_info, json_file, sr):
        '''Calculating and storing start and end frame for each segment in json_file'''
        
        for segment in sorted(audio_info.values(), key=lambda x: x["start_time"]):
            start_time = segment["start_time"]
            end_time = segment["end_time"]

            segment["start_frame"] = round(sr * start_time)
            segment["end_frame"] = round(sr * end_time)

        with open(json_file, "w") as f:
            json.dump(audio_info, f, indent=4)


    @staticmethod
    def combine_audio_files(audio_info, output_file, sr):
        '''Combine multiple audio files based on their start frames and insert silence where needed.'''
        
        frame_count = 2 * librosa.load("audios/audio_Vocals.wav")[0].shape[0]
        combined_audio = np.array([0] * frame_count, dtype=np.float32)

        for segment in sorted(audio_info.values(), key=lambda x: x["start_time"]):
            start_frame = segment["start_frame"]
            audio_file = segment["audio_file"]

            # Load the audio segment and sr=sample rate to count frames per segment
            y, _ = librosa.load(audio_file, sr=sr, mono=True)
            frame_cnt = y.shape[0]
            end_frame = segment["start_frame"] + frame_cnt
            combined_audio[start_frame:end_frame] = y

        sf.write(output_file, combined_audio, sr)


    @staticmethod
    def combine_audio_video(audio_file, video_file, output_file):
        '''Combine a new audio file with an existing video file, preserving the original audio in the video.'''
        new_audio_clip = AudioFileClip(audio_file)
        video_clip = VideoFileClip(video_file)

        # Set new audio duration to match video duration if needed
        new_audio_duration = new_audio_clip.duration
        video_duration = video_clip.duration
        if new_audio_duration < video_duration:
            # Create silent audio to match video duration
            silence_duration = video_duration - new_audio_duration
            fps = new_audio_clip.fps

            # Function to generate silence
            def make_frame(t):
                return np.zeros((2,))  

            silence = AudioClip(make_frame, duration=silence_duration, fps=fps)
            new_audio_clip = concatenate_audioclips([new_audio_clip, silence])

        original_audio_clip = video_clip.audio
        combined_audio = CompositeAudioClip([original_audio_clip, new_audio_clip])
        final_clip = video_clip.set_audio(combined_audio)

        final_clip.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )
