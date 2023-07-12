from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech

def transcribe_long_audio(bucket_name, audio_blob_names):
    # Instantiate the Speech-to-Text client
    client = speech.SpeechClient()

    # Create a storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    transcriptions = {}

    for audio_blob_name in audio_blob_names:
        # Configure the transcription request
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=44100,
            language_code="en-US",
            enable_word_time_offsets=True,
        )
        audio = speech.RecognitionAudio(uri=f"gs://{bucket_name}/{audio_blob_name}")

        # Start the transcription
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result()

        # Process the transcription results
        transcript = ""
        for result in response.results:
            alternative = result.alternatives[0]
            transcript += alternative.transcript + " "

        # Upload the transcription results to the bucket
        transcript_blob_name = f"{audio_blob_name}.txt"
        transcript_blob = bucket.blob(transcript_blob_name)
        transcript_blob.upload_from_string(transcript)

        # Store the transcript for the audio file
        transcriptions[audio_blob_name] = transcript

    return transcriptions

# Replace with your bucket name and audio blob names
bucket_name = "your-bucket-name"
audio_blob_names = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]

transcriptions = transcribe_long_audio(bucket_name, audio_blob_names)

# Print the transcriptions
for audio_blob_name, transcript in transcriptions.items():
    print(f"Transcription for {audio_blob_name}:")
    print(transcript)
    print()
