import os
import sys
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip



class VideoProcessing:
    
    def __init__(self, video_file, output_dir='audios'):
        self.video_file = video_file
        self.output_dir = output_dir
        self.extracted_audio_file = os.path.join(output_dir, "audio.mp3")
        self.instrumental_audio_file = os.path.join(output_dir, "audio_Instruments.wav")
        self.muted_video_file = os.path.join('videos', "video1_muted.mp4")
        self.final_video_file = os.path.join('videos', "video1_final.mp4")


    def extract_audio(self):
        """Extract audio from video."""
        video = VideoFileClip(self.video_file)
        audio = video.audio
        audio.write_audiofile(self.extracted_audio_file)


    def remove_vocals(self):
        """Remove vocals using the vocal-remover model."""
        os.makedirs(self.output_dir, exist_ok=True)

        command = [sys.executable, 'inference.py',
            '--input', os.path.abspath(self.extracted_audio_file),
            '--output_dir', os.path.abspath(self.output_dir)
        ]
        subprocess.run(command, cwd="./vocal-remover", check=True)


    def mute_video(self):
        """Mute the original video."""
        video = VideoFileClip(self.video_file)
        muted_video = video.without_audio()
        muted_video.write_videofile(self.muted_video_file, codec='libx264', audio_codec='aac')


    def combine_audio_with_video(self):
        """Combine instrumental audio with the muted video."""
        video = VideoFileClip(self.muted_video_file)
        instrumental_audio = AudioFileClip(self.instrumental_audio_file)
        video_with_instrumental = video.set_audio(instrumental_audio)
        video_with_instrumental.write_videofile(self.final_video_file, codec='libx264', audio_codec='aac')

