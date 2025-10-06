# Smart-Meeting-Notes-AIGP-Health

This project is a full-stack web application that takes an audio file of a meeting, processes it through an asynchronous AI pipeline, and produces a timestamped transcript, a structured summary, and a validated list of action items.

### ✨ Key Features-
- 🎙️ Audio Upload: Accepts common audio formats (.mp3, .m4a, .wav) via a robust FastAPI endpoint.

- ✍️ AI Transcription: Generates a detailed, word-for-word transcript with precise timestamps for each segment using Azure's Whisper model.

- 📋 Structured Summarization: Condenses the transcript into key sections: Agenda, Decisions, and Risks.

- ✅ Validated Action Items: Extracts actionable tasks into a clean, validated JSON format, complete with a self-repairing mechanism to ensure reliability.

- 🔄 Asynchronous Processing: Uses FastAPI's BackgroundTasks to process audio without blocking the API, allowing for a responsive user experience.

### 🏁 Getting Started
Follow these steps to get the backend running locally.

### 1. Prerequisites
  - Python 3.11+
  - An Azure Account with an active subscription or OpenAI Account.

### 2. Azure / OpenAI Setup
You need to deploy two models to your Azure OpenAI resource or Use OpenAI to get the API keys for the two models.
#### Whisper Model (for Transcription):
- In Azure AI Studio, go to Deployments and create a new one.
- Select the whisper model.
- Give it a Deployment Name. For this guide, we'll use whisper.
- Alternatively you can use OpenAI models using an API_KEY.

#### Chat Model (for Summaries & Actions):
- Create another new deployment.
- Select a chat model like gpt-35-turbo or gpt-4.
- Give it a Deployment Name. For this guide, we'll use gpt-summarizer.

### 3. Backend Setup
```bash
1. Clone the repository
   git clone https://github.com/ShalikaNuwan/Smart-Meeting-Notes-AIGP-Health.git
   cd Smart-Meeting-Notes-AIGP-Health/backend

2. Create and activate a Python virtual environment.
   python3 -m venv venv
   source venv/bin/activate

3. Install the required dependencies
   pip install -r requirements.txt

4. Set up your Environment Variables
   Copy the example file to create your own .env file
   cp .env.example .env
   actual Azure/OpenAI credentials from the portal.
``` 
### 4. Run the server
```bash
# From the /backend directory, start the FastAPI server
uvicorn app.main:app --reload
```

### AI Processed Pipeline
The background pipeline is designed to be idempotent. Each step checks the current status before running, making it safe to retry a failed job without re-processing completed steps.
```bash
A[POST /meetings] --> B{Save File & Create Job in DB};
B --> C(Status: UPLOADED);
C --> D{Background Task: Transcription};
D --> E(Status: TRANSCRIBED);
E --> F{Background Task: Summarization};
F --> G(Status: SUMMARIZED);
G --> H{Background Task: Action Item Extraction};
H --> I(Status: DONE ✨);
``` 





