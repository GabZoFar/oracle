# 🎲 Oracle - RPG Session Management Tool

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
   MAX_FILE_SIZE_MB=200
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
- AAC (automatically converted to MP3)

### 🔄 AAC Format Handling (NEW!)

Since OpenAI Whisper doesn't support AAC format, the application now includes **automatic AAC to MP3 conversion**:

- **Automatic detection** of AAC files during upload
- **Lossless conversion** to high-quality MP3 (320 kbps)
- **Seamless integration** with FFmpeg
- **Automatic processing** - no manual intervention required
- **Quality preservation** - maintains original audio quality
- **Transparent workflow** - happens automatically when you click "🚀 Traiter la session"

When you upload an AAC file:
1. 🔍 App detects AAC format automatically
2. ⚠️ Shows what will be done (conversion + optional compression)
3. 🚀 Click "Traiter la session" - everything happens automatically
4. 🔄 Converts to high-quality MP3 (320 kbps)
5. 🗜️ Compresses if needed to fit under 25MB
6. ✅ Processes the final optimized file
7. 🧹 Cleans up temporary files

**Requirements**: FFmpeg must be installed for automatic conversion. See [FFmpeg Installation](#ffmpeg-installation) section below.

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
3. Upload your audio file (any supported format including AAC)
4. App automatically detects if conversion/compression is needed
5. Click "🚀 Traiter la session" - all processing happens automatically
6. Wait for transcription and AI analysis to complete

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
| `MAX_FILE_SIZE_MB` | Maximum file size in MB | `200` |
| `DEBUG` | Enable debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Audio Settings
- Maximum file size: 200MB (configurable)
- ⚠️ **OpenAI Whisper API limit: 25MB** - files larger than this will need compression
- Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC (auto-converted to MP3)
- Language: French (configurable in transcription service)
- **Built-in compression recommendations** for oversized files
- **Automatic AAC conversion** for Whisper compatibility

## 🗜️ Intelligent File Processing

The application includes **fully automatic** handling for all audio files:

### 🤖 Automatic Processing Pipeline
When you upload any audio file, the app automatically:

1. **🔍 Detects file format and size**
2. **🔄 Converts AAC to MP3** (if needed) - OpenAI doesn't support AAC
3. **🗜️ Applies aggressive compression** (if > 24MB) - to fit Whisper's 25MB limit
4. **⚡ Merges conversion + compression** (for AAC files > 24MB) - one-step processing
5. **✅ Validates final file** - ensures compatibility
6. **🚀 Processes immediately** - transcription and AI analysis

**No manual intervention required** - just click "🚀 Traiter la session" and everything happens automatically!

### File Size Limits
- **Application limit**: 200MB (configurable via `MAX_FILE_SIZE_MB`)
- **Whisper API limit**: 25MB (OpenAI's hard limit)
- **Automatic compression**: Files > 24MB are automatically compressed

### 🎯 Smart Compression Settings
The app uses aggressive compression by default for optimal results:

- **WAV files**: Convert to MP3 (~90% size reduction)
- **All large files**: Direct aggressive compression (32kbps, 24kbps, or 16kbps bitrates)
- **Stereo to mono**: Automatic conversion for maximum compression
- **Sample rate reduction**: 44.1kHz → 16kHz or 11kHz for extreme cases
- **AAC + Large files**: Combined conversion and compression in one step
- **No standard compression**: Goes directly to aggressive settings for efficiency

### 📦 FFmpeg Installation
Automatic processing requires FFmpeg. The app will detect if it's available:

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

If FFmpeg is not available, the app will show an error and suggest manual compression alternatives.

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