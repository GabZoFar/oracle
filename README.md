# 🎲 Maître Joueur - RPG Session Management Tool

A modern Streamlit application for Game Masters to transcribe, analyze, and manage RPG session recordings using AI-powered analysis.

## ✨ Features

### 🎯 Core Functionality
- **Audio Upload & Transcription**: Upload audio files and get automatic transcription using OpenAI Whisper
- **AI-Powered Analysis**: Extract structured information from sessions:
  - Narrative summaries (2-5 paragraphs)
  - TL;DR summaries for quick session recaps
  - NPCs encountered
  - Items found/mentioned
  - Locations visited
  - Key events
- **Session Management**: Browse, view, and manage your session history
- **Beautiful UI**: Modern, responsive interface with French localization

### 🔮 Planned Features (Phase 2)
- Session editing and comments
- Campaign management
- Wiki generation
- Export functionality
- Search and filtering

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key
- `uv` package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd maitre-joueur
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=sqlite:///data/sessions.db
   UPLOAD_DIR=data/audio
   MAX_FILE_SIZE_MB=500
   DEBUG=False
   LOG_LEVEL=INFO
   ```

4. **Run the application**
   ```bash
   uv run streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📁 Supported Audio Formats

- MP3
- WAV
- M4A
- FLAC
- OGG
- AAC

## 🏗️ Project Structure

```
maitre-joueur/
├── app.py                       # Main Streamlit application
├── src/
│   ├── config.py               # Configuration management
│   │   ├── models.py           # SQLAlchemy models
│   │   └── database.py         # Database connection
│   ├── services/
│   │   ├── transcription.py    # OpenAI Whisper integration
│   │   └── ai_analysis.py      # AI-powered content analysis
│   └── components/             # UI components (future)
├── data/
│   ├── audio/                  # Uploaded audio files
│   ├── sessions.db             # SQLite database
│   └── exports/                # Generated exports
└── tests/                      # Test files
```

## 🛠️ Technology Stack

- **Framework**: Streamlit
- **Package Manager**: uv
- **Database**: SQLite with SQLAlchemy
- **AI Services**: OpenAI (Whisper, GPT-4o)
- **Data Validation**: Pydantic
- **Language**: Python 3.12

## 📖 Usage

### 1. Upload a Session
1. Navigate to "📁 Nouvelle Session"
2. Enter session number and date
3. Upload your audio file
4. Click "🚀 Traiter la session"
5. Wait for transcription and AI analysis to complete

### 2. View Sessions
1. Navigate to "📚 Sessions Existantes"
2. Browse your session history
3. Expand sessions to view details
4. Read summaries, structured data, and full transcripts

### 3. Session Information
Each processed session includes:
- **TL;DR**: Quick summary for session recaps
- **Narrative Summary**: Detailed story-like summary
- **Structured Data**: 
  - NPCs encountered
  - Items found
  - Locations visited
  - Key events
- **Full Transcript**: Complete transcription with timestamps

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MISTRAL_API_KEY` | Mistral API key (optional) | - |
| `DATABASE_URL` | Database connection string | `sqlite:///data/sessions.db` |
| `UPLOAD_DIR` | Audio files directory | `data/audio` |
| `MAX_FILE_SIZE_MB` | Maximum file size in MB | `500` |
| `DEBUG` | Enable debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Audio Settings
- Maximum file size: 500MB (configurable)
- ⚠️ **OpenAI Whisper API limit: 25MB** - files larger than this will need compression
- Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC
- Language: French (configurable in transcription service)
- **Built-in compression recommendations** for oversized files

## 🗜️ Large File Handling

The application includes intelligent handling for large audio files:

### File Size Limits
- **Application limit**: 500MB (configurable via `MAX_FILE_SIZE_MB`)
- **Whisper API limit**: 25MB (OpenAI's hard limit)

### 🤖 Automatic Compression (NEW!)
When you upload a file larger than 25MB, the app now offers **automatic compression** if FFmpeg is installed:

- **One-click compression** with optimal settings
- **Smart parameter detection** based on file size and format
- **Real-time progress** and compression statistics
- **Automatic processing** after successful compression

#### FFmpeg Installation
The app will detect if FFmpeg is available. If not installed:

**macOS (recommended):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
# or
winget install FFmpeg
```

**Installation Helper:**
```bash
uv run python install_ffmpeg.py
```

### Automatic Compression Guidance
When you upload a file larger than 25MB, the app provides:
- **Estimated compressed size** based on your file format
- **Step-by-step compression instructions** for Audacity
- **FFmpeg commands** for advanced users
- **Format-specific recommendations** (WAV→MP3 can reduce size by 90%)

### Supported Compression Methods
- **WAV to MP3**: ~90% size reduction
- **FLAC to MP3**: ~70% size reduction  
- **Bitrate reduction**: 320kbps → 128kbps or lower
- **Mono conversion**: ~50% reduction for stereo files
- **Sample rate reduction**: 44.1kHz → 22kHz

## 🧪 Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black src/ tests/
uv run isort src/ tests/
```

### Type Checking
```bash
uv run mypy src/
```

## 📝 API Costs

This application uses OpenAI APIs:
- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4o API**: ~$0.03 per 1K tokens for analysis

Typical costs per session:
- 2-hour session: ~$0.72 for transcription + ~$0.15 for analysis = **~$0.87 total**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [OpenAI](https://openai.com/) for Whisper and GPT-4 APIs
- The RPG community for inspiration

## 🐛 Issues & Support

If you encounter any issues or have questions:
1. Check the logs in the Streamlit interface
2. Verify your API keys are correctly set
3. Ensure audio files are in supported formats
4. **For large files**: Use the built-in compression recommendations
5. Create an issue on GitHub with details

---

**Happy Gaming! 🎲**