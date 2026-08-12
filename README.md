# Dastabbej (v2.0.0)

A powerful FastAPI-based backend system designed to scrape, process, and make institutional notices interactable via an AI-powered chat interface.

## 🚀 Overview

The **Notice Chat API** automates the ingestion of notices from web sources, processing them to extract valuable information from various formats (HTML, PDF, Images, Google Drive links). It then stores this data and provides a chat API that allows users to query specific notices using an LLM (Large Language Model) context.

## ✨ Features

- **Automated Scraping**: Fetches and parses notices from configured sources.
- **Intelligent Processing**:
  - Handles various link types: Internal downloads, Google Drive files, Google Docs.
  - **OCR & Text Extraction**: Extracts text from PDFs and Images for searchability.
  - **Cloud Storage**: Uploads attachments to Cloudinary for persistent access.
- **AI-Powered Analysis**:
  - **Summarization**: Auto-generates concise summaries for notices.
  - **Tagging**: Automatically categorizes notices with relevant tags.
  - **Contextual Chat**: Ask questions about specific notices (e.g., "What is the deadline mentioned in this notice?").
- **API Capabilities**:
  - RESTful endpoints for listing and retrieving notices.
  - Chat history management.
  - Background task support for scheduled updates.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: MongoDB
- **Language**: Python 3.9+
- **AI/LLM**: Google GenAI (Gemini), Mistral, OpenAI (via OpenRouter/LangChain)
- **Cloud Storage**: Cloudinary
- **Scraping**: BeautifulSoup4, Requests

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🔐 Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Cloudinary Configuration (for file storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# AI Model Keys
MISTRAL_API_KEY=your_mistral_key
OPENROUTER_API_KEY=your_openrouter_key
GOOGLE_API_KEY=your_google_api_key

# Database
MONGODB_URI=your_mongodb_connection_string
```

## 🚀 Usage

### 1. Run the Server
Start the FastAPI server using Uvicorn:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`.

### 2. Trigger Data Update (Scraping)
To start the scraping process manually (or via cron):
```bash
curl -X POST http://localhost:8000/api/cron/update-notices
```

### 3. API Documentation
Once the server is running, visit the interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📡 Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/notices` | List all processed notices. |
| `GET` | `/notices/{id}` | Get details of a specific notice. |
| `POST` | `/chat` | Chat with an LLM about a specific notice. |
| `GET` | `/chat/history/{uid}/{nid}` | Retrieve chat history. |
| `POST` | `/api/cron/update-notices` | Trigger background scraping task. |

## 📂 Project Structure

```
.
├── backend/
│   ├── main.py            # API Entry point
│   ├── run_scraper.py     # Scraper orchestration
│   ├── processor.py       # Content processing logic
│   ├── chat_service.py    # LLM Chat interface
│   ├── database.py        # MongoDB interactions
│   └── ...
├── static/                # Static assets (if applicable)
├── notices_final.json     # Local cache/output of scraped notices
├── requirements.txt       # Project dependencies
└── .env                   # Environment variables
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.
