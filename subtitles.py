import json
import pysrt
import datetime
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


def seconds_to_timecode(seconds):
    """Convert seconds to timecode format (hh:mm:ss,ms)"""
    td = datetime.timedelta(seconds=seconds)
    return str(td).replace(".", ",")


def create_srt_file(json_data, srt_filename):
    """Create a srt subtitle file"""
    with open(srt_filename, "w", encoding="utf-8") as srt_file:
        for idx, (key, value) in enumerate(json_data.items(), start=1):
            start_time = seconds_to_timecode(value["start_time"])
            end_time = seconds_to_timecode(value["end_time"])
            transcript = value["transcript"]

            transcript = transcript.encode("utf-8")

            srt_file.write(f"{idx}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{transcript}\n\n")


def add_subtitles(video_path, subtitles_path, output_path):
    """Join subtitles to video file"""
    video = VideoFileClip(video_path)
    subs = pysrt.open(subtitles_path)

    # Create a list to store subtitle clips
    subtitle_clips = []

    for sub in subs:
        start_time = sub.start.to_time()
        end_time = sub.end.to_time()

        # Create TextClip for each subtitle
        subtitle = TextClip(sub.text, font="Arial-Bold", fontsize=24, color="white")
        subtitle = subtitle.set_position(("center", "bottom")).set_duration(
            (end_time - start_time).total_seconds()
        )
        subtitle = subtitle.set_start(start_time)
        subtitle_clips.append(subtitle)


    # Create a CompositeVideoClip with subtitles
    final_video = CompositeVideoClip([video, *subtitle_clips])
    final_video.write_videofile(output_path, codec="libx264", fps=video.fps)

    

if __name__ == "__main__":
    # Load JSON data
    with open("vocal_segments_info.json", "r", encoding="utf-8") as json_file:
        vocal_segment_info = json.load(json_file)

    # Create SRT file
    srt_filename = "subtitles.srt"
    create_srt_file(vocal_segment_info, srt_filename)

    input_video = "com_vid_aud.mp4"
    output_video = "output_video.mp4"
    add_subtitles(input_video, srt_filename, output_video)

