# Oracle - RPG Session Management Tool

## Project Overview
A Streamlit application for Game Masters to transcribe, summarize, and manage RPG session recordings with AI-powered analysis.

## Core Features

### Phase 1 - Core Functionality ✅ COMPLETED
1. **Audio Upload & Transcription** ✅
   - Upload audio files (MP3, WAV, M4A, FLAC, OGG)
   - Transcribe using OpenAI Whisper API
   - Display transcript with timestamps

2. **AI-Powered Analysis** ✅
   - Narrative summary (2-5 paragraphs)
   - TL;DR format for session start
   - Structured extraction:
     - NPCs encountered
     - Items collected
     - Locations visited
     - Key events

3. **Session Logging** ✅
   - Generate session logs with metadata
   - Date, session number, title
   - SQLite database storage

### Phase 2 - Enhanced Features (TODO)
4. **Session Management**
   - Edit summaries and add comments
   - Session history browser ✅ (basic version completed)
   - Search functionality

5. **Wiki Generation**
   - Campaign overview
   - Character tracking
   - Location database
   - Item inventory
   - Export to markdown/wiki format

## Technical Architecture

### Backend Components ✅ IMPLEMENTED
- **Transcription Service**: OpenAI Whisper API integration ✅
- **AI Analysis Service**: OpenAI GPT-4o for content extraction ✅
- **Data Storage**: SQLite database for session data ✅
- **File Management**: Local storage for audio files ✅

### Frontend Components ✅ IMPLEMENTED
- **Upload Interface**: Streamlit file uploader ✅
- **Transcript Viewer**: Scrollable text display ✅
- **Summary Dashboard**: Tabbed interface for different summary types ✅
- **Session Browser**: List/grid view of past sessions ✅
- **Editor Interface**: Rich text editing for summaries (Phase 2)

### Data Models ✅ IMPLEMENTED
```python
Session:
  - id: UUID ✅
  - title: str ✅
  - date: datetime ✅
  - session_number: int ✅
  - audio_file_path: str ✅
  - audio_file_name: str ✅
  - audio_file_size: int ✅
  - transcript: str ✅
  - narrative_summary: str ✅
  - tldr_summary: str ✅
  - npcs: List[str] ✅
  - items: List[str] ✅
  - locations: List[str] ✅
  - key_events: List[str] ✅
  - comments: str ✅
  - processing_status: str ✅
  - created_at: datetime ✅
  - updated_at: datetime ✅
```

## File Structure ✅ IMPLEMENTED
```
maitre-joueur/
├── .env                          # Environment variables (API keys) ✅
├── .gitignore                   # Git ignore file ✅
├── pyproject.toml               # UV project configuration ✅
├── README.md                    # Project documentation ✅
├── PROJECT_STRUCTURE.md         # This file ✅
├── .cursor-rules                # Cursor IDE rules ✅
├── uv.lock                      # Dependencies lock file ✅
├── app.py                       # Main Streamlit application ✅
├── src/
│   ├── __init__.py ✅
│   ├── config.py               # Configuration management ✅
│   ├── database/
│   │   ├── __init__.py ✅
│   │   ├── models.py           # SQLAlchemy models ✅
│   │   └── database.py         # Database connection and setup ✅
│   ├── services/
│   │   ├── __init__.py ✅
│   │   ├── transcription.py    # Audio transcription service ✅
│   │   ├── ai_analysis.py      # AI-powered content analysis ✅
│   │   └── file_manager.py     # File upload and management (integrated in app.py)
│   ├── components/
│   │   ├── __init__.py ✅
│   │   ├── upload.py           # Upload interface components (integrated in app.py)
│   │   ├── transcript.py       # Transcript display components (integrated in app.py)
│   │   ├── summary.py          # Summary display components (integrated in app.py)
│   │   └── session_browser.py  # Session management components (integrated in app.py)
│   └── utils/
│       ├── __init__.py ✅
│       ├── helpers.py          # Utility functions (future)
│       └── validators.py       # Input validation (future)
├── data/
│   ├── audio/                  # Uploaded audio files ✅
│   ├── sessions.db             # SQLite database ✅
│   └── exports/                # Generated exports ✅
└── tests/
    ├── __init__.py ✅
    ├── test_transcription.py   # Tests (future)
    ├── test_ai_analysis.py     # Tests (future)
    └── test_database.py        # Tests (future)
```

## Development Phases

### Phase 1: MVP (Minimum Viable Product) ✅ COMPLETED
- [x] Project setup with uv
- [x] Basic Streamlit interface
- [x] Audio upload functionality
- [x] OpenAI Whisper integration
- [x] Basic AI summarization
- [x] Simple session storage

### Phase 2: Enhanced Features (NEXT)
- [ ] Database integration (basic version completed)
- [ ] Session management interface (basic version completed)
- [ ] Advanced AI analysis (completed)
- [ ] Export functionality
- [ ] Search and filtering
- [ ] Session editing and comments
- [ ] Campaign management

### Phase 3: Advanced Features (FUTURE)
- [ ] Rich text editing
- [ ] Wiki generation
- [ ] Campaign management
- [ ] Advanced analytics

## Technology Stack ✅ IMPLEMENTED
- **Framework**: Streamlit ✅
- **Package Manager**: uv ✅
- **Database**: SQLite with SQLAlchemy ✅
- **AI Services**: OpenAI (Whisper, GPT-4o) ✅
- **Audio Processing**: Built-in Streamlit file handling ✅
- **Data Validation**: Pydantic ✅
- **Testing**: pytest ✅ (setup ready)

## Environment Variables Required ✅
```
OPENAI_API_KEY=your_openai_api_key
MISTRAL_API_KEY=your_mistral_api_key (optional)
DATABASE_URL=sqlite:///data/sessions.db
UPLOAD_DIR=data/audio
MAX_FILE_SIZE_MB=100
DEBUG=False
LOG_LEVEL=INFO
```

## Current Status: PHASE 1 COMPLETE + COMPRESSION FEATURE! 🎉

The application is now fully functional with:
- ✅ Audio file upload and validation
- ✅ OpenAI Whisper transcription
- ✅ GPT-4o AI analysis with structured extraction
- ✅ Session storage in SQLite database
- ✅ Beautiful Streamlit UI with French localization
- ✅ Session browsing and management
- ✅ Modern Python 3.12 + uv setup
- ✅ **NEW: Automatic FFmpeg compression for large files**
- ✅ **NEW: Intelligent compression parameter detection**
- ✅ **NEW: One-click compression with real-time progress**

## Compression Features Added ✅

### 1. Automatic Compression System
- **FFmpeg Integration**: Direct compression within the app
- **Smart Parameter Detection**: Optimal settings based on file size/format
- **Real-time Progress**: User feedback during compression
- **Automatic Processing**: Seamless workflow after compression

### 2. Compression Intelligence
- **Format-specific optimization**: WAV→MP3 (90% reduction), FLAC→MP3 (70% reduction)
- **Adaptive compression**: Adjusts parameters if first attempt insufficient
- **Size estimation**: Accurate prediction of compressed file size
- **Compatibility validation**: Ensures result fits Whisper API limits

### 3. User Experience Enhancements
- **One-click compression**: No external tools needed
- **Installation guidance**: FFmpeg setup instructions for all platforms
- **Fallback options**: Manual compression instructions if FFmpeg unavailable
- **Error handling**: Graceful degradation with helpful messages

## Next Steps for Phase 2
1. Add session editing capabilities ✅ (basic version completed)
2. Implement export functionality (Markdown, PDF)
3. Add search and filtering
4. Create campaign management features
5. Build wiki generation system
6. Add comprehensive testing suite ✅ (compression tests added)
7. **NEW: Advanced compression features** (batch processing, cloud compression) 