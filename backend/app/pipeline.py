import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from backend.app.llm import chatClient
import json
from sqlalchemy.orm import Session
from pydantic import ValidationError
from . import crud, models, schemas
from typing import List 

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
    
#summarize the transcript
def transcript_summarize(transcript_text: str) -> dict:
    """
    This function summarize the text into Agenda, Decisions and Risks using the chat model
    """
    
    system_prompt = """
    You are a professional meeting assistant. Your task is to analyze the provided meeting transcript and summarize it.
    The output MUST be a valid JSON object with three keys: "agenda", "decisions", and "risks".
    - "agenda": Provide a concise list of the main topics discussed.
    - "decisions": List all concrete decisions that were made.
    - "risks": List any potential risks or issues that were raised during the meeting.
    Do not include any text or formatting outside of the JSON object.
    """
    
    try:
        response = chatClient.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": transcript_text,
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=4096,
        temperature=0.0,
        top_p=1.0,
        model=os.getenv('DEPLOYMENT'),
    )
        summary = response.choices[0].message.content
        return json.loads(summary)
    
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        raise

def extract_action_items_with_repair(transcript_text: str, max_retries: int = 3) -> List[dict]:
    
    schema_json = json.dumps(schemas.ActionItem.model_json_schema(), indent=2)
    
    system_prompt = f"""
    You are an expert at extracting structured data from text.
    Analyze the following meeting transcript and extract all action items.
    Your response MUST be a valid JSON array. Each object in the array must conform to this JSON Schema:
    {schema_json}
    If a value for a field (like 'owner' or 'due_date') is not mentioned, omit the key. Do not make up information.
    Return an empty array if no action items are found. Do not output any text outside of the JSON array.
    """

    current_prompt = transcript_text
    for i in range(max_retries):
        print(f"Attempt {i+1} to extract valid action items...")
        response = client.chat.completions.create(
            model=os.getenv('DEPLOYMENT'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": current_prompt}
            ]
        )
        raw_output = response.choices[0].message.content

        try:
            action_items_data = json.loads(raw_output)
            validated_items = [schemas.ActionItem(**item) for item in action_items_data]
            print("Successfully extracted and validated action items.")
            return [item.model_dump() for item in validated_items]
        except (ValidationError, json.JSONDecodeError) as e:
            print(f"Validation failed: {e}. Retrying with repair prompt...")
            # If validation fails, create a new "repair" prompt
            current_prompt = f"""
            The previous attempt to extract action items failed. The output was not valid JSON or did not match the schema.
            Please fix the following output. Remember to only return a valid JSON array conforming to the schema.

            Original Transcript:
            {transcript_text}

            Invalid Output:
            {raw_output}
            """
    
    raise ValueError("Failed to extract valid action items after multiple retries.")

def run_pipeline(meeting_id: int, db: Session):
    """
    This is the main background task. It's designed to be idempotent and re-runnable.
    """
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        return

    try:
        # Transcription
        if meeting.status == models.MeetingStatus.UPLOADED:
            transcript_data = transcribe_audio(meeting.storage_path)
            crud.update_meeting(db, meeting_id, status=models.MeetingStatus.TRANSCRIBED, transcript=transcript_data)
        
        meeting = crud.get_meeting(db, meeting_id)

        # Summarization
        if meeting.status == models.MeetingStatus.TRANSCRIBED:
            full_text = meeting.transcript.get('text', '')
            summary_data = transcript_summarize(full_text)
            crud.update_meeting(db, meeting_id, status=models.MeetingStatus.SUMMARIZED, summary=summary_data)

        meeting = crud.get_meeting(db, meeting_id) # Refresh state

        # Action Item Extraction
        if meeting.status == models.MeetingStatus.SUMMARIZED:
            full_text = meeting.transcript.get('text', '')
            action_items_data = extract_action_items_with_repair(full_text)
            crud.update_meeting(db, meeting_id, status=models.MeetingStatus.DONE, action_items=action_items_data)

    except Exception as e:
        print(f"Pipeline failed for meeting {meeting_id}: {e}")
        crud.update_meeting(db, meeting_id, status=models.MeetingStatus.FAILED, failure_reason=str(e))

if __name__ == "__main__":
    
    sample_file_path = "uploads/test1.mp3" 
    
    if not os.path.exists(sample_file_path):
        print(f"Error: Test file not found at '{sample_file_path}'")
        print("Please add an audio file there to run this test.")
    else:
        transcription_result = transcribe_audio(sample_file_path)
        # print("\n--- Segments ---")
        # for segment in transcription_result['segments']:
        #     start_time = round(segment['start'], 2)
        #     end_time = round(segment['end'], 2)
        #     text = segment['text']
        #     print(f"[{start_time}s -> {end_time}s] {text}")
        
        print(transcript_summarize(transcription_result['text']))
        
