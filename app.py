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
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure file handler for logging
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
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
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier audio",
        type=settings.supported_audio_formats,
        help=f"Formats supportés: {', '.join(settings.supported_audio_formats)}"
    )
    
    if uploaded_file is not None:
        # Display file info on one line
        file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
        file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
        
        # Compact file info display
        st.info(f"📄 **{uploaded_file.name}** • {file_size_mb:.1f} MB")
        
        # Validate file size against our limits
        if file_size_mb > settings.max_file_size_mb:
            st.error(f"❌ Fichier trop volumineux (max: {settings.max_file_size_mb} MB)")
            return
        
        # Determine processing needs - ALWAYS use aggressive compression for optimal results
        needs_aac_conversion = file_extension == "aac"
        needs_compression = file_size_mb > 5  # Use aggressive compression for files > 5MB for optimal results
        
        # Show processing info if needed
        if needs_aac_conversion or needs_compression:
            if needs_aac_conversion and needs_compression:
                st.warning("🔄 Conversion AAC + Compression requise")
            elif needs_aac_conversion:
                st.warning("🔄 Conversion AAC → MP3 requise")
            else:
                st.warning("🗜️ Compression agressive requise")
            
            if not audio_helper.is_ffmpeg_available():
                st.error("❌ FFmpeg requis pour le traitement automatique")
                return
        
        # Single process button - handles everything automatically
        if st.button("🚀 Traiter la session", type="primary"):
            # Save uploaded file
            audio_file_path = save_uploaded_file(uploaded_file)
            if not audio_file_path:
                return
            
            final_audio_path = audio_file_path
            final_filename = uploaded_file.name
            
            try:
                # Step 1: Process file if needed (compression/conversion)
                if needs_aac_conversion or needs_compression:
                    if needs_aac_conversion and needs_compression:
                        # AAC + Large file: Convert directly to compressed MP3
                        with st.spinner("🔄 Conversion et compression..."):
                            optimal_settings = audio_helper.get_optimal_compression_settings(file_size_mb, "aac")
                            
                            success, message, processed_path = audio_helper.compress_audio_file(
                                audio_file_path,
                                target_bitrate=optimal_settings['target_bitrate'],
                                target_format="mp3",
                                mono=optimal_settings['mono'],
                                sample_rate=optimal_settings['sample_rate'],
                                ultra_aggressive=True
                            )
                            
                            if success and processed_path:
                                processed_size_mb = processed_path.stat().st_size / (1024 * 1024)
                                
                                if processed_size_mb <= 25:
                                    st.success(f"✅ Traitement réussi ({processed_size_mb:.1f} MB)")
                                    try:
                                        audio_file_path.unlink()
                                    except:
                                        pass
                                    final_audio_path = processed_path
                                    final_filename = f"{Path(uploaded_file.name).stem}_processed.mp3"
                                else:
                                    st.error(f"❌ Fichier encore trop volumineux ({processed_size_mb:.1f} MB)")
                                    try:
                                        audio_file_path.unlink()
                                        processed_path.unlink()
                                    except:
                                        pass
                                    
                                    # Add instructions for manual compression and show logs
                                    st.error("""
                                    ### Compression plus intense requise
                                    Ce fichier est particulièrement difficile à compresser.
                                    
                                    **Solutions:**
                                    1. Réduire la durée de l'enregistrement
                                    2. Utiliser un autre format (WAV ou FLAC)
                                    3. Compresser manuellement avec Audacity (mono + 16kbps)
                                    """)
                                    
                                    # Add a button to try extreme compression as a last resort
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("🔥 Essayer compression extrême (8kbps)", type="primary", key="extreme_compression_btn"):
                                            st.session_state.extreme_compression_clicked = True
                                            st.rerun()
                                    
                                    # Use session state to execute the compression logic after rerun
                                    if st.session_state.extreme_compression_clicked:
                                        with st.spinner("Compression extrême en cours..."):
                                            try:
                                                # Try extreme compression
                                                success, message, extreme_path = audio_helper.extreme_compress_audio_file(audio_file_path)
                                                
                                                # Reset the state after processing
                                                st.session_state.extreme_compression_clicked = False
                                                
                                                if success and extreme_path:
                                                    extreme_size_mb = extreme_path.stat().st_size / (1024 * 1024)
                                                    
                                                    if extreme_size_mb <= 25:
                                                        st.success(f"✅ Compression extrême réussie ({extreme_size_mb:.1f} MB)")
                                                        # Use this file for processing
                                                        final_audio_path = extreme_path
                                                        final_filename = f"{Path(uploaded_file.name).stem}_extreme.mp3"
                                                        
                                                        # Process this file
                                                        # Create session in database
                                                        with get_db_session() as db:
                                                            new_session = Session(
                                                                title=f"Session {session_number}",
                                                                session_number=session_number,
                                                                date=datetime.combine(session_date, datetime.min.time()),
                                                                audio_file_path=str(final_audio_path),
                                                                audio_file_name=final_filename,
                                                                audio_file_size=final_audio_path.stat().st_size,
                                                                processing_status="uploaded"
                                                            )
                                                            db.add(new_session)
                                                            db.commit()
                                                            
                                                            session_id = str(new_session.id)
                                                        
                                                        # Process the session
                                                        st.success("✅ Fichier prêt - Démarrage du traitement...")
                                                        process_session(session_id, final_audio_path)
                                                        
                                                    else:
                                                        st.error(f"❌ Échec - Fichier encore trop volumineux même avec compression extrême ({extreme_size_mb:.1f} MB)")
                                                        logger.error(f"EXTREME COMPRESSION STILL TOO LARGE: {extreme_size_mb:.2f} MB")
                                                else:
                                                    st.error(f"❌ Échec de la compression extrême: {message}")
                                            except Exception as e:
                                                st.error(f"❌ Erreur: {str(e)}")
                                                logger.error(f"EXTREME COMPRESSION ERROR: {str(e)}")
                                    
                                    # Add a button to show logs
                                    with col2:
                                        if st.button("📋 Afficher les logs de débogage", key="show_logs_btn2"):
                                            # Set a session state variable to show logs
                                            st.session_state.show_debug_logs = True
                                            st.rerun()
                                    
                                    return
                    
                    elif needs_aac_conversion:
                        # AAC only: Convert with aggressive compression
                        with st.spinner("🔄 Conversion AAC → MP3 agressive..."):
                            optimal_settings = audio_helper.get_optimal_compression_settings(file_size_mb, "aac")
                            
                            success, message, converted_path = audio_helper.compress_audio_file(
                                audio_file_path,
                                target_bitrate=optimal_settings['target_bitrate'],
                                target_format="mp3",
                                mono=optimal_settings['mono'],
                                sample_rate=optimal_settings['sample_rate'],
                                ultra_aggressive=True
                            )
                            
                            if success and converted_path:
                                converted_size_mb = converted_path.stat().st_size / (1024 * 1024)
                                st.success(f"✅ Conversion agressive réussie ({converted_size_mb:.1f} MB)")
                                try:
                                    audio_file_path.unlink()
                                except:
                                    pass
                                final_audio_path = converted_path
                                final_filename = f"{Path(uploaded_file.name).stem}_compressed.mp3"
                            else:
                                st.error(f"❌ Échec de la conversion : {message}")
                                try:
                                    audio_file_path.unlink()
                                except:
                                    pass
                                return
                    
                    else:
                        # Any file: Direct aggressive compression
                        with st.spinner("🗜️ Compression agressive..."):
                            optimal_settings = audio_helper.get_optimal_compression_settings(file_size_mb, file_extension)
                            
                            success, message, compressed_path = audio_helper.compress_audio_file(
                                audio_file_path,
                                target_bitrate=optimal_settings['target_bitrate'],
                                target_format=optimal_settings['target_format'],
                                mono=optimal_settings['mono'],
                                sample_rate=optimal_settings['sample_rate'],
                                ultra_aggressive=True
                            )
                            
                            if success and compressed_path:
                                compressed_size_mb = compressed_path.stat().st_size / (1024 * 1024)
                                
                                if compressed_size_mb <= 25:
                                    st.success(f"✅ Compression agressive réussie ({compressed_size_mb:.1f} MB)")
                                    try:
                                        audio_file_path.unlink()
                                    except:
                                        pass
                                    final_audio_path = compressed_path
                                    final_filename = f"{Path(uploaded_file.name).stem}_compressed.{optimal_settings['target_format']}"
                                else:
                                    st.error(f"❌ Fichier encore trop volumineux ({compressed_size_mb:.1f} MB)")
                                    try:
                                        audio_file_path.unlink()
                                        compressed_path.unlink()
                                    except:
                                        pass
                                    
                                    # Add instructions for manual compression and show logs
                                    st.error("""
                                    ### Compression plus intense requise
                                    Ce fichier est particulièrement difficile à compresser.
                                    
                                    **Solutions:**
                                    1. Réduire la durée de l'enregistrement
                                    2. Utiliser un autre format (WAV ou FLAC)
                                    3. Compresser manuellement avec Audacity (mono + 16kbps)
                                    """)
                                    
                                    # Add a button to try extreme compression as a last resort
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("🔥 Essayer compression extrême (8kbps)", type="primary", key="extreme_compression_btn"):
                                            st.session_state.extreme_compression_clicked = True
                                            st.rerun()
                                    
                                    # Use session state to execute the compression logic after rerun
                                    if st.session_state.extreme_compression_clicked:
                                        with st.spinner("Compression extrême en cours..."):
                                            try:
                                                # Try extreme compression
                                                success, message, extreme_path = audio_helper.extreme_compress_audio_file(audio_file_path)
                                                
                                                # Reset the state after processing
                                                st.session_state.extreme_compression_clicked = False
                                                
                                                if success and extreme_path:
                                                    extreme_size_mb = extreme_path.stat().st_size / (1024 * 1024)
                                                    
                                                    if extreme_size_mb <= 25:
                                                        st.success(f"✅ Compression extrême réussie ({extreme_size_mb:.1f} MB)")
                                                        # Use this file for processing
                                                        final_audio_path = extreme_path
                                                        final_filename = f"{Path(uploaded_file.name).stem}_extreme.mp3"
                                                        
                                                        # Process this file
                                                        # Create session in database
                                                        with get_db_session() as db:
                                                            new_session = Session(
                                                                title=f"Session {session_number}",
                                                                session_number=session_number,
                                                                date=datetime.combine(session_date, datetime.min.time()),
                                                                audio_file_path=str(final_audio_path),
                                                                audio_file_name=final_filename,
                                                                audio_file_size=final_audio_path.stat().st_size,
                                                                processing_status="uploaded"
                                                            )
                                                            db.add(new_session)
                                                            db.commit()
                                                            
                                                            session_id = str(new_session.id)
                                                        
                                                        # Process the session
                                                        st.success("✅ Fichier prêt - Démarrage du traitement...")
                                                        process_session(session_id, final_audio_path)
                                                        
                                                    else:
                                                        st.error(f"❌ Échec - Fichier encore trop volumineux même avec compression extrême ({extreme_size_mb:.1f} MB)")
                                                        logger.error(f"EXTREME COMPRESSION STILL TOO LARGE: {extreme_size_mb:.2f} MB")
                                                else:
                                                    st.error(f"❌ Échec de la compression extrême: {message}")
                                            except Exception as e:
                                                st.error(f"❌ Erreur: {str(e)}")
                                                logger.error(f"EXTREME COMPRESSION ERROR: {str(e)}")
                                    
                                    # Add a button to show logs
                                    with col2:
                                        if st.button("📋 Afficher les logs de débogage", key="show_logs_btn2"):
                                            # Set a session state variable to show logs
                                            st.session_state.show_debug_logs = True
                                            st.rerun()
                                    
                                    return
                            else:
                                st.error(f"❌ Échec de la compression : {message}")
                                try:
                                    audio_file_path.unlink()
                                except:
                                    pass
                                return
                
                # Show debug logs if requested (outside any expander)
                if 'show_debug_logs' in st.session_state and st.session_state.show_debug_logs:
                    st.session_state.show_debug_logs = False  # Reset the state
                    with st.expander("Logs de compression (débogage)"):
                        # Get the log file path
                        log_path = Path("logs/app.log") if Path("logs/app.log").exists() else None
                        
                        if log_path:
                            try:
                                # Read the last 50 lines of the log file
                                with open(log_path, "r") as f:
                                    log_lines = f.readlines()
                                    recent_logs = log_lines[-50:]
                                
                                # Display the logs
                                st.code("".join(recent_logs), language="bash")
                            except Exception as e:
                                st.warning(f"Impossible de lire les logs: {e}")
                        else:
                            # Try to get info from the logger directly
                            st.code(f"""
COMPRESSION INFO:
- Fichier: {final_filename}
- Taille initiale: {file_size_mb:.2f} MB
- Format: {file_extension}
- Paramètres: Compression agressive {optimal_settings if 'optimal_settings' in locals() else 'N/A'}
- Résultat: Fichier encore trop volumineux ({compressed_size_mb if 'compressed_size_mb' in locals() else 'N/A'} MB)
                            """, language="bash")
                
                # Step 2: Validate the final file
                is_valid, validation_message = transcription_service.validate_audio_file(final_audio_path)
                if not is_valid:
                    st.error(f"❌ Validation échouée: {validation_message}")
                    try:
                        final_audio_path.unlink()
                    except:
                        pass
                    return
                
                # Step 3: Create session in database
                with get_db_session() as db:
                    new_session = Session(
                        title=f"Session {session_number}",  # Will be updated after analysis
                        session_number=session_number,
                        date=datetime.combine(session_date, datetime.min.time()),
                        audio_file_path=str(final_audio_path),
                        audio_file_name=final_filename,
                        audio_file_size=final_audio_path.stat().st_size,
                        processing_status="uploaded"
                    )
                    db.add(new_session)
                    db.commit()
                    
                    session_id = str(new_session.id)
                
                # Step 4: Automatically process the session (transcription + analysis)
                st.success("✅ Fichier prêt - Démarrage du traitement...")
                process_session(session_id, final_audio_path)
                
            except Exception as e:
                logger.error(f"Failed to process uploaded file: {e}")
                st.error(f"Erreur lors du traitement : {e}")
                # Clean up any files
                try:
                    if final_audio_path and final_audio_path.exists():
                        final_audio_path.unlink()
                except:
                    pass


def display_session_details(session):
    """Display the details of a selected session."""
    st.markdown(f'<h1 class="main-header">📚 {session.title}</h1>', unsafe_allow_html=True)
    
    # Session metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Date:** {session.date.strftime('%d/%m/%Y')}")
    with col2:
        st.write(f"**Fichier:** {session.audio_file_name}")
    with col3:
        if session.audio_file_size:
            size_mb = session.audio_file_size / (1024 * 1024)
            st.write(f"**Taille:** {size_mb:.2f} MB")
    
    # Status badge
    status_class = f"status-{session.processing_status.replace('_', '-')}"
    st.markdown(
        f'<span class="status-badge {status_class}">{session.processing_status.upper()}</span>',
        unsafe_allow_html=True
    )
    
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
        
        # Transcript (collapsible with checkbox)
        if session.transcript:
            show_transcript = st.checkbox("📜 Voir la transcription complète", key=f"transcript_{session.id}")
            if show_transcript:
                st.text_area(
                    "Transcription",
                    value=session.transcript,
                    height=300,
                    disabled=True
                )
    elif session.processing_status == "error":
        st.error("Une erreur s'est produite lors du traitement de cette session.")
    elif session.processing_status in ["transcribing", "analyzing"]:
        st.info(f"Session en cours de traitement: {session.processing_status}")
    else:
        st.info("Session uploadée, en attente de traitement.")


def main():
    """Main application function."""
    # Initialize app
    init_app()
    
    # Initialize session state variables if they don't exist
    if 'extreme_compression_clicked' not in st.session_state:
        st.session_state.extreme_compression_clicked = False
    if 'show_debug_logs' not in st.session_state:
        st.session_state.show_debug_logs = False
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "new_session"
    
    # Sidebar navigation
    st.sidebar.title("🎲 Maître Joueur")
    st.sidebar.markdown("---")
    
    # New Session button
    if st.sidebar.button("📁 Nouvelle Session", use_container_width=True):
        st.session_state.current_page = "new_session"
        st.session_state.selected_session = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Load and display previous sessions
    try:
        with get_db_session() as db:
            sessions = db.query(Session).order_by(Session.date.desc()).all()
            
            if sessions:
                st.sidebar.subheader("📚 Sessions Existantes")
                
                for session in sessions:
                    # Create button for each session
                    session_button_text = f"{session.title} - Session #{session.session_number}"
                    
                    # Highlight selected session
                    button_type = "primary" if st.session_state.selected_session == str(session.id) else "secondary"
                    
                    if st.sidebar.button(
                        session_button_text,
                        key=f"session_{session.id}",
                        use_container_width=True,
                        type=button_type
                    ):
                        st.session_state.selected_session = str(session.id)
                        st.session_state.current_page = "session_details"
                        st.rerun()
            
    except Exception as e:
        logger.error(f"Failed to load sessions for sidebar: {e}")
        st.sidebar.error("Erreur lors du chargement des sessions")
    
    # Display selected page
    if st.session_state.current_page == "new_session":
        upload_page()
    elif st.session_state.current_page == "session_details" and st.session_state.selected_session:
        # Display selected session details
        try:
            with get_db_session() as db:
                session = db.query(Session).filter(Session.id == uuid.UUID(st.session_state.selected_session)).first()
                if session:
                    display_session_details(session)
                else:
                    st.error("Session non trouvée")
                    st.session_state.current_page = "new_session"
                    st.session_state.selected_session = None
        except Exception as e:
            logger.error(f"Failed to load session details: {e}")
            st.error("Erreur lors du chargement de la session")
            st.session_state.current_page = "new_session"
            st.session_state.selected_session = None
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Outil de gestion de sessions JDR*")
    st.sidebar.markdown("*Powered by OpenAI & Streamlit*")


if __name__ == "__main__":
    main() 