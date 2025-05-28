"""
Maître Joueur - RPG Session Management Tool
A Streamlit application for transcribing and analyzing RPG session recordings.
"""

import streamlit as st
import logging
from pathlib import Path
from datetime import datetime
import uuid
import asyncio
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from src.config import settings
from src.database.database import init_database, get_db_session
from src.database.models import Session
from src.services.transcription import transcription_service
from src.services.ai_analysis import ai_analysis_service
from src.utils.audio_compression import audio_helper

# Page configuration
st.set_page_config(
    page_title="Maître Joueur - RPG Session Manager",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .session-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-uploaded { background-color: #ffeaa7; color: #2d3436; }
    .status-transcribing { background-color: #74b9ff; color: white; }
    .status-analyzing { background-color: #fd79a8; color: white; }
    .status-completed { background-color: #00b894; color: white; }
    .status-error { background-color: #e17055; color: white; }
</style>
""", unsafe_allow_html=True)


def init_app():
    """Initialize the application."""
    try:
        init_database()
        logger.info("Application initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize application: {e}")
        logger.error(f"Application initialization failed: {e}")


def save_uploaded_file(uploaded_file) -> Optional[Path]:
    """Save uploaded file to the upload directory."""
    try:
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(uploaded_file.name).suffix
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        file_path = settings.upload_path / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"File saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        st.error(f"Failed to save file: {e}")
        return None


def process_session(session_id: str, audio_file_path: Path):
    """Process a session: transcribe and analyze."""
    try:
        with get_db_session() as db:
            # Get session from database - convert string to UUID
            session = db.query(Session).filter(Session.id == uuid.UUID(session_id)).first()
            if not session:
                st.error("Session not found")
                return
            
            # Update status to transcribing
            session.processing_status = "transcribing"
            db.commit()
            
            # Transcribe audio
            with st.spinner("Transcribing audio... This may take a few minutes."):
                transcription_result = transcription_service.transcribe_audio(audio_file_path)
                
                # Update session with transcript
                session.transcript = transcription_result["transcript"]
                session.processing_status = "analyzing"
                db.commit()
            
            st.success("Transcription completed!")
            
            # Analyze transcript
            with st.spinner("Analyzing transcript with AI..."):
                analysis_result = ai_analysis_service.analyze_transcript(
                    transcription_result["transcript"]
                )
                
                # Update session with analysis
                session.narrative_summary = analysis_result["narrative_summary"]
                session.tldr_summary = analysis_result["tldr_summary"]
                session.npcs = analysis_result["npcs"]
                session.items = analysis_result["items"]
                session.locations = analysis_result["locations"]
                session.key_events = analysis_result["key_events"]
                session.title = analysis_result["session_title"]
                session.processing_status = "completed"
                db.commit()
            
            st.success("Analysis completed!")
            st.rerun()
            
    except Exception as e:
        logger.error(f"Failed to process session: {e}")
        st.error(f"Processing failed: {e}")
        
        # Update session status to error
        try:
            with get_db_session() as db:
                session = db.query(Session).filter(Session.id == uuid.UUID(session_id)).first()
                if session:
                    session.processing_status = "error"
                    db.commit()
        except Exception:
            pass


def upload_page():
    """Upload and process new session page."""
    st.markdown('<h1 class="main-header">🎲 Nouvelle Session</h1>', unsafe_allow_html=True)
    
    # Session metadata input
    col1, col2 = st.columns(2)
    
    with col1:
        session_number = st.number_input(
            "Numéro de session",
            min_value=1,
            value=1,
            help="Numéro de cette session dans votre campagne"
        )
        
    with col2:
        session_date = st.date_input(
            "Date de la session",
            value=datetime.now().date(),
            help="Date à laquelle la session a eu lieu"
        )
    
    # Audio file upload
    st.subheader("📁 Upload du fichier audio")
    
    # Display file size limits and recommendations
    st.info(f"""
    **Limites et recommandations:**
    - Taille maximale: {settings.max_file_size_mb} MB
    - ⚠️ **Important**: L'API OpenAI Whisper a une limite de 25 MB
    - Formats supportés: {', '.join(settings.supported_audio_formats).upper()}
    """)
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier audio",
        type=settings.supported_audio_formats,
        help=f"Formats supportés: {', '.join(settings.supported_audio_formats)}"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
        st.info(f"📄 **Fichier:** {uploaded_file.name}")
        st.info(f"📊 **Taille:** {file_size_mb:.2f} MB")
        
        # Estimate processing time
        estimated_time = transcription_service.estimate_processing_time(file_size_mb)
        st.info(f"⏱️ **Temps estimé:** {estimated_time}")
        
        # Validate file size against our limits
        if file_size_mb > settings.max_file_size_mb:
            st.error(f"❌ Le fichier est trop volumineux. Taille maximale: {settings.max_file_size_mb} MB")
            return
        
        # Check against Whisper API limits and propose compression immediately
        if file_size_mb > 25:
            # Get file extension for recommendations
            file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
            
            # Get compression recommendations
            recommendations = audio_helper.get_compression_recommendations(file_size_mb, file_extension)
            estimated_size = audio_helper.estimate_compressed_size(file_size_mb, file_extension)
            
            st.error(f"""
            ❌ **Fichier trop volumineux pour l'API Whisper**
            
            Votre fichier fait {file_size_mb:.2f} MB, mais l'API OpenAI Whisper a une limite de 25 MB.
            """)
            
            # Check if FFmpeg is available for automatic compression
            if audio_helper.is_ffmpeg_available():
                st.success("🎉 **Compression automatique disponible !**")
                
                # Get optimal compression settings
                optimal_settings = audio_helper.get_optimal_compression_settings(file_size_mb, file_extension)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("### 🤖 Compression automatique (recommandée)")
                    st.info(f"""
                    **Paramètres optimaux détectés :**
                    - Format de sortie : {optimal_settings['target_format'].upper()}
                    - Bitrate : {optimal_settings['target_bitrate']} kbps
                    - Mono : {'Oui' if optimal_settings['mono'] else 'Non'}
                    - Fréquence : {optimal_settings['sample_rate'] or 'Originale'} Hz
                    
                    **Taille estimée après compression :** {optimal_settings['estimated_size_mb']:.1f} MB
                    """)
                
                with col2:
                    if st.button("🚀 Compresser et traiter", type="primary", key="auto_compress_and_process"):
                        # Save the original file first
                        temp_file_path = save_uploaded_file(uploaded_file)
                        if temp_file_path:
                            with st.spinner("Compression en cours... Cela peut prendre quelques minutes."):
                                # Compress the file with aggressive settings
                                success, message, compressed_path = audio_helper.compress_audio_file(
                                    temp_file_path,
                                    target_bitrate=optimal_settings['target_bitrate'],
                                    target_format=optimal_settings['target_format'],
                                    mono=optimal_settings['mono'],
                                    sample_rate=optimal_settings['sample_rate']
                                )
                                
                                if success and compressed_path:
                                    st.success(message)
                                    
                                    # Update file info for the compressed file
                                    compressed_size_mb = compressed_path.stat().st_size / (1024 * 1024)
                                    
                                    if compressed_size_mb <= 25:
                                        st.success(f"✅ Le fichier compressé ({compressed_size_mb:.1f} MB) est maintenant compatible avec l'API Whisper !")
                                        
                                        # Create session with compressed file
                                        try:
                                            with get_db_session() as db:
                                                new_session = Session(
                                                    title=f"Session {session_number}",
                                                    session_number=session_number,
                                                    date=datetime.combine(session_date, datetime.min.time()),
                                                    audio_file_path=str(compressed_path),
                                                    audio_file_name=f"{Path(uploaded_file.name).stem}_compressed.{optimal_settings['target_format']}",
                                                    audio_file_size=compressed_path.stat().st_size,
                                                    processing_status="uploaded"
                                                )
                                                db.add(new_session)
                                                db.commit()
                                                
                                                session_id = str(new_session.id)
                                            
                                            # Clean up original file
                                            try:
                                                temp_file_path.unlink()
                                            except:
                                                pass
                                            
                                            # Process the compressed session
                                            process_session(session_id, compressed_path)
                                            return
                                            
                                        except Exception as e:
                                            logger.error(f"Failed to create session with compressed file: {e}")
                                            st.error(f"Erreur lors de la création de la session : {e}")
                                    else:
                                        st.warning(f"⚠️ Le fichier compressé ({compressed_size_mb:.1f} MB) est encore trop volumineux.")
                                        
                                        # Offer ultra-aggressive compression
                                        st.info("🔥 Tentative de compression ultra-agressive...")
                                        
                                        # Try ultra-aggressive compression
                                        ultra_success, ultra_message, ultra_compressed_path = audio_helper.compress_audio_file(
                                            temp_file_path,
                                            target_bitrate=16,  # Ultra low bitrate
                                            target_format="mp3",
                                            mono=True,
                                            sample_rate=11025,  # Very low sample rate
                                            ultra_aggressive=True
                                        )
                                        
                                        if ultra_success and ultra_compressed_path:
                                            st.success(ultra_message)
                                            ultra_size_mb = ultra_compressed_path.stat().st_size / (1024 * 1024)
                                            
                                            if ultra_size_mb <= 25:
                                                st.success(f"✅ Compression ultra-agressive réussie ! ({ultra_size_mb:.1f} MB)")
                                                
                                                # Clean up first compressed file
                                                try:
                                                    compressed_path.unlink()
                                                except:
                                                    pass
                                                
                                                # Create session with ultra-compressed file
                                                try:
                                                    with get_db_session() as db:
                                                        new_session = Session(
                                                            title=f"Session {session_number}",
                                                            session_number=session_number,
                                                            date=datetime.combine(session_date, datetime.min.time()),
                                                            audio_file_path=str(ultra_compressed_path),
                                                            audio_file_name=f"{Path(uploaded_file.name).stem}_ultra_compressed.mp3",
                                                            audio_file_size=ultra_compressed_path.stat().st_size,
                                                            processing_status="uploaded"
                                                        )
                                                        db.add(new_session)
                                                        db.commit()
                                                        
                                                        session_id = str(new_session.id)
                                                    
                                                    # Clean up original file
                                                    try:
                                                        temp_file_path.unlink()
                                                    except:
                                                        pass
                                                    
                                                    # Process the ultra-compressed session
                                                    process_session(session_id, ultra_compressed_path)
                                                    return
                                                    
                                                except Exception as e:
                                                    logger.error(f"Failed to create session with ultra-compressed file: {e}")
                                                    st.error(f"Erreur lors de la création de la session : {e}")
                                            else:
                                                st.error(f"❌ Même avec la compression ultra-agressive, le fichier ({ultra_size_mb:.1f} MB) reste trop volumineux. Essayez de diviser le fichier en segments plus petits.")
                                        else:
                                            st.error(f"❌ Échec de la compression ultra-agressive : {ultra_message}")
                                else:
                                    st.error(f"❌ Échec de la compression : {message}")
                                
                                # Clean up files on error
                                try:
                                    temp_file_path.unlink()
                                    if compressed_path and compressed_path.exists():
                                        compressed_path.unlink()
                                except:
                                    pass
                
                st.markdown("---")
            else:
                st.warning("⚠️ **FFmpeg non disponible** - La compression automatique n'est pas possible sur ce système.")
                st.info("Pour installer FFmpeg : https://ffmpeg.org/download.html")
            
            # Show manual compression recommendations
            with st.expander("🛠️ Solutions de compression manuelles", expanded=not audio_helper.is_ffmpeg_available()):
                st.markdown("### 📊 Estimation après compression")
                st.success(f"Taille estimée après compression: **{estimated_size:.1f} MB** (réduction de {recommendations['estimated_reduction']})")
                
                st.markdown("### 🔧 Méthodes recommandées")
                for method in recommendations["methods"]:
                    st.write(f"• {method}")
                
                st.markdown("### 🛠️ Outils recommandés")
                for tool in recommendations["tools"]:
                    st.write(f"• {tool}")
                
                # Audacity instructions
                st.markdown("### 📋 Instructions Audacity (étape par étape)")
                audacity_instructions = audio_helper.get_audacity_instructions()
                for instruction in audacity_instructions:
                    st.write(instruction)
                
                # FFmpeg commands
                st.markdown("### 💻 Commandes FFmpeg (utilisateurs avancés)")
                ffmpeg_commands = audio_helper.get_ffmpeg_commands(
                    "votre_fichier." + file_extension,
                    "fichier_compresse.mp3"
                )
                st.code(ffmpeg_commands[0], language="bash")
                
                with st.expander("Voir plus de commandes FFmpeg"):
                    for cmd in ffmpeg_commands[1:]:
                        st.code(cmd, language="bash")
            
            return  # Exit early if file is too big - don't show process button
        
        # Warning for large files (but under 25MB)
        if file_size_mb > 15:
            st.warning(f"""
            ⚠️ **Fichier volumineux détecté** ({file_size_mb:.2f} MB)
            
            Le traitement peut prendre plus de temps. Assurez-vous d'avoir une connexion stable.
            """)
        
        # Process button (only shown if file is valid size)
        if st.button("🚀 Traiter la session", type="primary"):
            # Save uploaded file
            audio_file_path = save_uploaded_file(uploaded_file)
            if not audio_file_path:
                return
            
            # Validate the saved file
            is_valid, validation_message = transcription_service.validate_audio_file(audio_file_path)
            if not is_valid:
                st.error(f"❌ Validation échouée: {validation_message}")
                # Clean up the saved file
                try:
                    audio_file_path.unlink()
                except:
                    pass
                return
            
            # Create session in database
            try:
                with get_db_session() as db:
                    new_session = Session(
                        title=f"Session {session_number}",  # Will be updated after analysis
                        session_number=session_number,
                        date=datetime.combine(session_date, datetime.min.time()),
                        audio_file_path=str(audio_file_path),
                        audio_file_name=uploaded_file.name,
                        audio_file_size=len(uploaded_file.getbuffer()),
                        processing_status="uploaded"
                    )
                    db.add(new_session)
                    db.commit()
                    
                    session_id = str(new_session.id)
                
                # Process the session
                process_session(session_id, audio_file_path)
                
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                st.error(f"Failed to create session: {e}")
                # Clean up the saved file
                try:
                    audio_file_path.unlink()
                except:
                    pass


def sessions_page():
    """View and manage existing sessions page."""
    st.markdown('<h1 class="main-header">📚 Sessions Existantes</h1>', unsafe_allow_html=True)
    
    try:
        with get_db_session() as db:
            sessions = db.query(Session).order_by(Session.date.desc()).all()
            
            if not sessions:
                st.info("Aucune session trouvée. Uploadez votre première session!")
                return
            
            # Display sessions
            for session in sessions:
                with st.expander(f"🎲 {session.title} - Session #{session.session_number}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Date:** {session.date.strftime('%d/%m/%Y')}")
                        st.write(f"**Fichier:** {session.audio_file_name}")
                        if session.audio_file_size:
                            size_mb = session.audio_file_size / (1024 * 1024)
                            st.write(f"**Taille:** {size_mb:.2f} MB")
                    
                    with col2:
                        # Status badge
                        status_class = f"status-{session.processing_status.replace('_', '-')}"
                        st.markdown(
                            f'<span class="status-badge {status_class}">{session.processing_status.upper()}</span>',
                            unsafe_allow_html=True
                        )
                    
                    with col3:
                        if st.button(f"Voir détails", key=f"view_{session.id}"):
                            st.session_state.selected_session = str(session.id)
                            st.rerun()
                    
                    # Show content if session is completed
                    if session.processing_status == "completed":
                        if session.tldr_summary:
                            st.subheader("📝 TL;DR")
                            st.write(session.tldr_summary)
                        
                        if session.narrative_summary:
                            st.subheader("📖 Résumé Narratif")
                            st.write(session.narrative_summary)
                        
                        # Structured information in columns
                        if any([session.npcs, session.items, session.locations, session.key_events]):
                            st.subheader("🗂️ Informations Structurées")
                            
                            info_col1, info_col2 = st.columns(2)
                            
                            with info_col1:
                                if session.npcs:
                                    st.write("**👥 PNJ rencontrés:**")
                                    for npc in session.npcs:
                                        st.write(f"• {npc}")
                                
                                if session.items:
                                    st.write("**🎒 Objets:**")
                                    for item in session.items:
                                        st.write(f"• {item}")
                            
                            with info_col2:
                                if session.locations:
                                    st.write("**🗺️ Lieux visités:**")
                                    for location in session.locations:
                                        st.write(f"• {location}")
                                
                                if session.key_events:
                                    st.write("**⚡ Événements clés:**")
                                    for event in session.key_events:
                                        st.write(f"• {event}")
                        
                        # Transcript (collapsible)
                        if session.transcript:
                            with st.expander("📜 Voir la transcription complète"):
                                st.text_area(
                                    "Transcription",
                                    value=session.transcript,
                                    height=300,
                                    disabled=True
                                )
    
    except Exception as e:
        logger.error(f"Failed to load sessions: {e}")
        st.error(f"Failed to load sessions: {e}")


def main():
    """Main application function."""
    # Initialize app
    init_app()
    
    # Sidebar navigation
    st.sidebar.title("🎲 Maître Joueur")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["📁 Nouvelle Session", "📚 Sessions Existantes"],
        index=0
    )
    
    # Display selected page
    if page == "📁 Nouvelle Session":
        upload_page()
    elif page == "📚 Sessions Existantes":
        sessions_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Outil de gestion de sessions JDR*")
    st.sidebar.markdown("*Powered by OpenAI & Streamlit*")


if __name__ == "__main__":
    main() 