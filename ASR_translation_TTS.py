import os
import wave
import json
from google.cloud import speech
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate


# Set up your Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"


class SpeechToTextProcessor:
    def __init__(self, audio_file_path, info_file):
        self.audio_file_path = audio_file_path
        self.info_file = info_file
        self.data = {}


    def read_audio_file(self, chunk_size):
        """Reads an audio file in chunks."""
        with open(self.audio_file_path, "rb") as audio_file:
            while True:
                data = audio_file.read(chunk_size)
                if not data:
                    break
                yield data


    def listen_print_loop(self, responses):
        """Iterates through server responses and stores them."""
        i = 0
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            start_time = (
                result.alternatives[0].words[0].start_time.seconds
                + result.alternatives[0].words[0].start_time.microseconds / 1000000
            )
            end_time = (
                result.result_end_time.seconds
                + result.result_end_time.seconds / 1000000
            )

            i += 1
            segment_name = f"segment_{i}"
            self.data[segment_name] = {
                "transcript": transcript,
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
            }

            with open(self.info_file, "w") as file:
                json.dump(self.data, file, indent=4)


    def transcribe_audio(self, input_language_code="en-US"):
        """Transcribes audio file using Google Speech-to-Text API."""
        with wave.open(self.audio_file_path, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()

        client = speech.SpeechClient()

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=input_language_code,
            audio_channel_count=channels,
            enable_word_time_offsets=True,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=False,
        )

        audio_generator = self.read_audio_file(int(sample_rate / 10))
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = client.streaming_recognize(streaming_config, requests)

        self.listen_print_loop(responses)


class TextTranslator:
    def __init__(self, service_account_file):
        self.client = translate.Client.from_service_account_json(service_account_file)

    def translate_text(self, input_transcript, info_file, segment_name, target_language):
        translation = self.client.translate(input_transcript, target_language=target_language)
        translated_text = translation["translatedText"]

        return translated_text
        #data[segment_name]["translated_transcript"] = translated_text


class TextToSpeechConverter:
    def __init__(self, service_account_file):
        self.client = texttospeech.TextToSpeechClient.from_service_account_file(
            service_account_file
        )


    def convert_text_to_speech(self, info_file, segment_name, output_file, language_code, gender, sr):
        with open(info_file, "r") as file:
            data = json.load(file)

        text=data[segment_name]["translated_transcript"]

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, ssml_gender=gender
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16, 
            sample_rate_hertz=sr
        )

        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(output_file, "wb") as out:
            out.write(response.audio_content)
