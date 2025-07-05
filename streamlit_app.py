import streamlit as st
import os
import tempfile
import zipfile
import time
from datetime import datetime
import pandas as pd
from io import BytesIO
import base64
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

# Import your existing order processor
from order_processor import process_pdfs, HAZMAT_KEYWORDS

# Set page configuration
st.set_page_config(
    page_title="ZENIA PDF Label Processor",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar
)

# Apply theme-based CSS
def apply_custom_css(is_dark_mode=False):
    theme_colors = {
        "bg_primary": "#0f172a" if is_dark_mode else "#f8fafc",
        "bg_secondary": "#1e293b" if is_dark_mode else "#f1f5f9", 
        "card_bg": "#1e293b" if is_dark_mode else "#ffffff",
        "text_primary": "#f8fafc" if is_dark_mode else "#1e293b",
        "text_secondary": "#cbd5e1" if is_dark_mode else "#475569",
        "text_muted": "#94a3b8" if is_dark_mode else "#64748b",
        "border": "#334155" if is_dark_mode else "#e2e8f0"
    }
    
    st.markdown(f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global styles */
        .main {{
            font-family: 'Inter', sans-serif;
            background-color: {theme_colors["bg_primary"]} !important;
            color: {theme_colors["text_primary"]} !important;
        }}
        
        .stApp {{
            background-color: {theme_colors["bg_primary"]} !important;
        }}
        
        /* Header styling */
        .header-container {{
            background: linear-gradient(135deg, #FF0050 0%, #FF3070 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }}
        
        .header-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .header-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
        }}
        
        /* Stats cards */
        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        
        .stat-card {{
            background: {theme_colors["card_bg"]};
            color: {theme_colors["text_primary"]};
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid {theme_colors["border"]};
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: #FF0050;
        }}
        
        .stat-icon {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        
        .stat-label {{
            color: {theme_colors["text_muted"]};
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        /* Orders stat - TikTok red */
        .stat-orders .stat-value {{ color: #FF0050; }}
        
        /* Pages stat - Cyan */
        .stat-pages .stat-value {{ color: #06b6d4; }}
        
        /* Duplicates stat - Orange */
        .stat-duplicates .stat-value {{ color: #f59e0b; }}
        
        /* Time stat - Green */
        .stat-time .stat-value {{ color: #10b981; }}
        
        /* Progress bar styling */
        .progress-container {{
            background: {theme_colors["bg_secondary"]};
            border-radius: 10px;
            height: 20px;
            margin: 1rem 0;
            overflow: hidden;
        }}
        
        .progress-bar {{
            background: linear-gradient(90deg, #FF0050, #FF3070);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        /* Log styling */
        .log-container {{
            background: {theme_colors["card_bg"]};
            color: {theme_colors["text_primary"]};
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid {theme_colors["border"]};
        }}
        
        /* Sidebar styling - removed since no sidebar */
        .css-1d391kg {{
            display: none !important;
        }}
        
        /* Main content area - full width */
        .main .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}
        
        /* Toggle styling */
        .stToggle > div {{
            background: {theme_colors["card_bg"]} !important;
        }}
        
        /* Center layout */
        .main {{
            background-color: {theme_colors["bg_primary"]} !important;
        }}
        
        /* Download buttons */
        .download-all-button {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            margin-bottom: 1rem !important;
        }}
        
        /* Ensure download section is fully visible */
        .stDownloadButton > button {{
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            border: none !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        }}
        
        .stDownloadButton > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(6, 182, 212, 0.3) !important;
        }}
        
        /* Fix any disabled appearance */
        .stDownloadButton {{
            opacity: 1 !important;
        }}
        
        /* Primary download button styling */
        .stDownloadButton[data-testid="baseButton-primary"] > button {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'total_orders' not in st.session_state:
        st.session_state.total_orders = 0
    if 'duplicate_orders' not in st.session_state:
        st.session_state.duplicate_orders = 0
    if 'total_pages' not in st.session_state:
        st.session_state.total_pages = 0
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = "0.0s"
    if 'duplicate_details' not in st.session_state:
        st.session_state.duplicate_details = []
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    if 'output_files' not in st.session_state:
        st.session_state.output_files = {}
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'hazmat_sticker_enabled' not in st.session_state:
        st.session_state.hazmat_sticker_enabled = True  # Enabled by default

def log_message(message):
    """Add a message to the log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    st.session_state.log_messages.append(formatted_message)

def create_header():
    """Create the application header"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📦 ZENIA PDF Label Processor</div>
        <div class="header-subtitle">Made by Zurain & Danish • Version 1.5 (Web Edition)</div>
    </div>
    """, unsafe_allow_html=True)

def create_stats_dashboard():
    """Create the stats dashboard"""
    st.markdown("### 📊 Batch Statistics")
    
    # Stats cards
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card stat-orders">
            <div class="stat-icon">📦</div>
            <div class="stat-value">{st.session_state.total_orders}</div>
            <div class="stat-label">Orders</div>
        </div>
        <div class="stat-card stat-pages">
            <div class="stat-icon">📄</div>
            <div class="stat-value">{st.session_state.total_pages}</div>
            <div class="stat-label">Pages</div>
        </div>
        <div class="stat-card stat-duplicates">
            <div class="stat-icon">⚠️</div>
            <div class="stat-value">{st.session_state.duplicate_orders}</div>
            <div class="stat-label">Duplicates</div>
        </div>
        <div class="stat-card stat-time">
            <div class="stat-icon">⚡</div>
            <div class="stat-value">{st.session_state.processing_time}</div>
            <div class="stat-label">Time</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_progress_bar(progress_value):
    """Create a progress bar"""
    st.markdown("### 🚀 Processing Progress")
    
    # Ensure progress is between 0 and 100
    progress_value = max(0, min(100, progress_value))
    
    # Create progress bar
    progress_bar = st.progress(progress_value / 100)
    
    # Status text
    if progress_value == 100:
        st.success(f"✅ {progress_value}% Complete - Processing Finished!")
    else:
        st.info(f"⏳ {progress_value}% Complete")
    
    return progress_bar

def create_download_all_zip():
    """Create a ZIP file containing all output files for download"""
    if not st.session_state.output_files:
        return None
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, file_data in st.session_state.output_files.items():
            zip_file.writestr(filename, file_data)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def save_uploaded_files(uploaded_files, temp_dir):
    """Save uploaded files to temporary directory"""
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(file_path)
    return saved_files

def create_download_zip(output_dir):
    """Create a zip file containing all output files"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, output_dir)
                zip_file.write(file_path, arc_name)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def process_files_async(input_dir, output_dir, keywords, auto_open=False, hazmat_sticker_enabled=True):
    """Process files and update session state"""
    try:
        # Initialize progress
        progress_placeholder = st.empty()
        
        # Custom status callback for Streamlit
        def status_callback(message):
            log_message(message)
            # Update progress based on message content with better tracking
            if "Starting" in message or "Looking for" in message:
                with progress_placeholder.container():
                    create_progress_bar(5)
            elif "Processing:" in message or "Found" in message:
                with progress_placeholder.container():
                    create_progress_bar(25)
            elif "Sorting" in message:
                with progress_placeholder.container():
                    create_progress_bar(50)
            elif "Warehouse labels saved" in message:
                with progress_placeholder.container():
                    create_progress_bar(75)
            elif "Packingroom labels saved" in message:
                with progress_placeholder.container():
                    create_progress_bar(85)
            elif "pick list saved" in message:
                with progress_placeholder.container():
                    create_progress_bar(95)
        
        # Process PDFs with hazmat sticker setting
        result = process_pdfs(
            input_dir,
            output_dir,
            keywords,
            auto_open,
            status_callback,
            hazmat_sticker_enabled  # Pass the hazmat sticker setting
        )
        
        # Update session state with results
        if isinstance(result, dict) and result.get('success', False):
            # FIX: Calculate total orders correctly from log messages
            warehouse_count = 0
            packingroom_count = 0
            
            # Parse the log messages to get correct counts
            for message in st.session_state.log_messages:
                if "Warehouse Orders:" in message:
                    warehouse_count = int(message.split("Warehouse Orders:")[1].strip())
                elif "Packingroom Orders:" in message:
                    packingroom_count = int(message.split("Packingroom Orders:")[1].strip())
            
            # Calculate correct total
            actual_total_orders = warehouse_count + packingroom_count
            
            # Update session state with corrected values
            st.session_state.total_orders = actual_total_orders if actual_total_orders > 0 else result.get('total_orders', 0)
            st.session_state.duplicate_orders = result.get('duplicate_orders', 0)
            st.session_state.duplicate_details = result.get('duplicate_details', [])
            st.session_state.processing_time = result.get('processing_time', "")
            st.session_state.total_pages = st.session_state.total_orders * 2
            
            # FINAL PROGRESS - Set to 100% when completely done
            with progress_placeholder.container():
                create_progress_bar(100)
            
            log_message("✅ Processing completed successfully!")
            log_message(f"📊 Updated stats: {st.session_state.total_orders} total orders")
            
            # Find and store output files
            timestamp_dirs = [d for d in os.listdir(os.path.join(output_dir, "Output")) 
                            if os.path.isdir(os.path.join(output_dir, "Output", d))]
            
            if timestamp_dirs:
                latest_dir = max(timestamp_dirs)
                output_files_dir = os.path.join(output_dir, "Output", latest_dir)
                
                # Store output files in session state
                st.session_state.output_files = {}
                for file in os.listdir(output_files_dir):
                    file_path = os.path.join(output_files_dir, file)
                    if os.path.isfile(file_path):
                        with open(file_path, 'rb') as f:
                            st.session_state.output_files[file] = f.read()
            
            return True
        else:
            # Set progress to 0 if failed
            with progress_placeholder.container():
                create_progress_bar(0)
            log_message("❌ Processing failed")
            return False
            
    except Exception as e:
        # Set progress to 0 if error
        with progress_placeholder.container():
            create_progress_bar(0)
        log_message(f"❌ Error: {str(e)}")
        return False

def main():
    """Main application function"""
    initialize_session_state()
    
    # Apply dynamic CSS based on theme
    apply_custom_css(st.session_state.dark_mode)
    
    # Header
    create_header()
    
    # Main content container
    main_container = st.container()
    
    with main_container:
        # Top controls row
        controls_col1, controls_col2, controls_col3 = st.columns([1, 1, 1])
        
        with controls_col1:
            # Theme toggle
            if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode", 
                        key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        with controls_col2:
            # Hazmat sticker toggle
            hazmat_sticker = st.toggle(
                "🏷️ Add Hazmat Stickers", 
                value=st.session_state.hazmat_sticker_enabled,
                help="When enabled, hazmat warning stickers will be added to qualifying labels"
            )
            st.session_state.hazmat_sticker_enabled = hazmat_sticker
        
        with controls_col3:
            # Reset button
            if st.button("🔄 Reset All", key="reset_all"):
                # Reset session state
                for key in ['total_orders', 'duplicate_orders', 'total_pages', 
                          'processing_time', 'duplicate_details', 'log_messages', 'output_files']:
                    st.session_state[key] = [] if key in ['duplicate_details', 'log_messages'] else (0 if 'orders' in key or 'pages' in key else ({} if key == 'output_files' else "0.0s"))
                st.rerun()
        
        st.markdown("---")
        
        # Configuration section
        st.markdown("## ⚙️ Configuration")
        
        config_col1, config_col2 = st.columns([2, 1])
        
        with config_col1:
            # File upload section
            st.markdown("### 📁 Upload PDF Files")
            uploaded_files = st.file_uploader(
                "Select PDF files to process",
                type=['pdf'],
                accept_multiple_files=True,
                help="Upload all the PDF files you want to process (Max 200MB per file)"
            )
            
            if uploaded_files:
                st.markdown(f"**📋 {len(uploaded_files)} files selected:**")
                for i, file in enumerate(uploaded_files[:5], 1):  # Show first 5 files
                    st.markdown(f"**{i}.** {file.name} ({file.size:,} bytes)")
                if len(uploaded_files) > 5:
                    st.markdown(f"... and {len(uploaded_files) - 5} more files")
        
        with config_col2:
            # Hazmat keywords section
            st.markdown("### ⚠️ Hazmat Keywords")
            hazmat_keywords = st.text_area(
                "Keywords (comma-separated)",
                value=", ".join(HAZMAT_KEYWORDS),
                height=100,
                help="Keywords to identify hazmat items for special processing"
            )
            
            # Processing controls
            st.markdown("### 🎮 Process Control")
            
            process_col1, process_col2 = st.columns(2)
            
            with process_col1:
                process_button = st.button(
                    "🚀 Start Processing",
                    disabled=not uploaded_files or st.session_state.processing,
                    help="Begin processing the uploaded PDF files",
                    type="primary"
                )
            
            with process_col2:
                auto_open = st.checkbox(
                    "Auto-open results",
                    value=False,
                    help="Note: Not available in web version"
                )
        
        st.markdown("---")
        
        # Stats and Progress section
        stats_col1, stats_col2 = st.columns([2, 1])
        
        with stats_col1:
            # Stats dashboard
            create_stats_dashboard()
            
            # Progress section (only show when processing or when just completed)
            if st.session_state.processing or st.session_state.total_orders > 0:
                # Show appropriate progress based on state
                if st.session_state.processing:
                    # Show dynamic progress during processing
                    pass  # Progress updates are handled in the callback
                elif st.session_state.total_orders > 0:
                    # Show completion status when done
                    create_progress_bar(100)
        
        with stats_col2:
            # Processing log
            st.markdown("### 📝 Processing Log")
            
            # Create log container
            log_content = "\n".join(st.session_state.log_messages[-15:])  # Show last 15 messages
            
            st.markdown(f"""
            <div class="log-container">
                {log_content.replace(chr(10), '<br>') if log_content else 'No log messages yet...<br>Upload PDFs and click Process to begin.'}
            </div>
            """, unsafe_allow_html=True)
        
        # Process files
        if process_button and uploaded_files:
            st.session_state.processing = True
            
            # Create temporary directories
            with tempfile.TemporaryDirectory() as temp_input_dir:
                with tempfile.TemporaryDirectory() as temp_output_dir:
                    
                    # Save uploaded files
                    log_message(f"Saving {len(uploaded_files)} uploaded files...")
                    save_uploaded_files(uploaded_files, temp_input_dir)
                    
                    # Parse keywords
                    keywords = [k.strip() for k in hazmat_keywords.split(",") if k.strip()]
                    
                    # Process files with progress indicator
                    with st.spinner("Processing PDF files..."):
                        success = process_files_async(
                            temp_input_dir,
                            temp_output_dir,
                            keywords,
                            auto_open,
                            st.session_state.hazmat_sticker_enabled  # Pass hazmat sticker setting
                        )
                    
                    if success:
                        # Show success message with updated stats
                        st.success(f"""
                        🎉 **Processing Complete!**
                        
                        - **Total Orders:** {st.session_state.total_orders}
                        - **Total Pages:** {st.session_state.total_pages}
                        - **Duplicate Orders:** {st.session_state.duplicate_orders}
                        - **Processing Time:** {st.session_state.processing_time}
                        - **Hazmat Stickers:** {"Added" if st.session_state.hazmat_sticker_enabled else "Disabled"}
                        """)
                        
                        # Show duplicate warnings if any
                        if st.session_state.duplicate_orders > 0:
                            st.warning(f"""
                            ⚠️ **{st.session_state.duplicate_orders} Duplicate Orders Detected!**
                            
                            First few duplicates:
                            """)
                            for detail in st.session_state.duplicate_details[:5]:
                                st.markdown(f"- {detail}")
                            if len(st.session_state.duplicate_details) > 5:
                                st.markdown(f"... and {len(st.session_state.duplicate_details) - 5} more")
                        
                        # Force update the stats display
                        st.rerun()
                    else:
                        st.error("❌ Processing failed. Check the log for details.")
            
            st.session_state.processing = False
        
        # Download section
        if st.session_state.output_files:
            st.markdown("---")
            st.markdown("## 📥 Download Results")
            
            download_col1, download_col2 = st.columns([1, 2])
            
            with download_col1:
                # Download All button - make it prominent
                zip_data = create_download_all_zip()
                if zip_data:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📦 Download All Files (ZIP)",
                        data=zip_data,
                        file_name=f"ZENIA_PDF_Results_{timestamp}.zip",
                        mime="application/zip",
                        key="download_all",
                        help="Download all processed files in a single ZIP archive",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.markdown("**✅ All files ready for download!**")
            
            with download_col2:
                # Individual download buttons in a more compact layout
                st.markdown("**📄 Individual Downloads:**")
                
                # Create download buttons for each output file in a cleaner format
                for filename, file_data in st.session_state.output_files.items():
                    file_ext = os.path.splitext(filename)[1]
                    mime_type = "application/pdf" if file_ext == ".pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_ext == ".xlsx" else "text/csv"
                    
                    # Use container to ensure buttons are fully visible
                    button_container = st.container()
                    with button_container:
                        st.download_button(
                            label=f"📄 {filename}",
                            data=file_data,
                            file_name=filename,
                            mime=mime_type,
                            key=f"download_{filename}",
                            use_container_width=True
                        )
        
        # Auto-refresh log when processing
        if st.session_state.processing:
            time.sleep(0.5)
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 1rem;">
        ZENIA PDF Label Processor • Web Edition • Built with ❤️ and Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()