import os
from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()
whisper_endpoint = os.getenv("WHYSPER_ENDPOINT")
whisper_api_key = os.getenv("WHYSPER_API_KEY")

client = AzureOpenAI(
    api_key=whisper_api_key,
    azure_endpoint=whisper_endpoint,
    api_version="2024-06-01", 
    azure_deployment="whisper"  
)

def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes an audio file using the OpenAI Whisper API and returns
    timestamped segments.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        dict: The full transcription object from the API, which includes
              the list of segments with timestamps.
    """
    print(f"Starting transcription for: {file_path}")
    
    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return transcription.model_dump()

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        raise


if __name__ == "__main__":
    
    sample_file_path = "uploads/test1.mp3" 
    
    if not os.path.exists(sample_file_path):
        print(f"Error: Test file not found at '{sample_file_path}'")
        print("Please add an audio file there to run this test.")
    else:
        transcription_result = transcribe_audio(sample_file_path)
        print("\n--- Transcription Complete ---")
        print(f"Duration: {transcription_result['duration']} seconds")
        print("Full Text:", transcription_result['text'])
        
        print("\n--- Segments ---")
        for segment in transcription_result['segments']:
            start_time = round(segment['start'], 2)
            end_time = round(segment['end'], 2)
            text = segment['text']
            print(f"[{start_time}s -> {end_time}s] {text}")
    