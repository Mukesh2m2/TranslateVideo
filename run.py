import os
import json
import librosa

from google.cloud import texttospeech

from video_processing import VideoProcessing
from ASR_translation_TTS import SpeechToTextProcessor
from ASR_translation_TTS import TextTranslator
from ASR_translation_TTS import TextToSpeechConverter
from combine_audio_video import AudioVideoProcessor
from clear import ClearSpace


'''Set up your Google Cloud credentials'''
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"


if __name__ == "__main__":
    input_file = "Speech.mp4"                       # change the video file you want to process here
    audio_folder ="audios/"
    
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)

    '''Process a video to separate the vocal audio and create a version with only the background ambiance.'''
    video_processor = VideoProcessing(video_file=os.path.join("videos", input_file))
    video_processor.extract_audio()
    video_processor.remove_vocals()
    video_processor.mute_video()
    video_processor.combine_audio_with_video()

    '''Process the vocal audio file to obtain a text transcription, then translate the text, and finally 
    convert the translated text into audio files.'''
    service_account_file = "key.json"                # put your google service account key to acccess APIs 
    output_folder = "output/"
    audio_file_path = "audios/audio_Vocals.wav"
    info_file = "vocal_segments_info.json"

    input_language = "en-US"                          # put the input language code here
    target_language = "hi"                            # put the output language here      
    language_code = "hi-IN"                           # put the output language code here  
    gender = texttospeech.SsmlVoiceGender.MALE        # change gender here

    # Speech to text Converter
    processor = SpeechToTextProcessor(audio_file_path, info_file)
    processor.transcribe_audio(input_language)

    translator = TextTranslator(service_account_file)
    converter = TextToSpeechConverter(service_account_file)
        
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Frame rate for audio input
    y, sr = librosa.load(audio_file_path, sr=None)

    with open(info_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    for segment_name, segment_info in data.items():
        transcript = segment_info.get("transcript")
        segment_name = segment_name

        output_audiofile = os.path.join(output_folder, f"{segment_name}.wav")
        data[segment_name]["audio_file"] = output_audiofile

        # Text translation
        data[segment_name]["translated_transcript"] = translator.translate_text(
            transcript, info_file, segment_name, target_language
        )
        with open(info_file, "w") as file:
            json.dump(data, file, indent=4)

        # Text to Speech conversion
        converter.convert_text_to_speech(
            info_file, segment_name, output_audiofile, language_code, gender, sr
        )

    """Combine translated audio segments based on their start and end frame information, then merge the 
    resulting audio with the video containing only background noise."""
    with open(info_file, "r") as f:
        vocal_segments_info = json.load(f)

    # store start frame and end frame for start and end times
    AudioVideoProcessor.frame_start_end_time(vocal_segments_info, info_file, sr)

    # Combine audio files based on the segments info
    output_audio_file = "audios/audios_output.wav"
    AudioVideoProcessor.combine_audio_files(vocal_segments_info, output_audio_file, sr)

    # Combine audio with video
    video_file = "videos/video1_final.mp4"
    output_video_file = "com_vid_aud.mp4"             
    AudioVideoProcessor.combine_audio_video(
        output_audio_file, video_file, output_video_file
    )

    '''Clear the audio segments generated and other audio files that are separated from video'''
    ClearSpace.clear_folder("output")
    ClearSpace.clear_folder("audios")
