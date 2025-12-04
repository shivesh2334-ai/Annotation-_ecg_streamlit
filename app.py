import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.signal import find_peaks
# --- LIBRARIES FOR GOOGLE SHEET CONNECTION ---
import gspread
from google.oauth2.service_account import Credentials
import copy # Used to create a deep copy of the secrets


# --- 1. CORE ECG ANNOTATION LOGIC ---

def simulate_ecg_and_annotate(sampling_rate=200, duration=5):
    """
    Simulates a simplified ECG signal and attempts to detect key features.
    """
    t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)
    # A simple wave simulation
    ecg_signal = 0.8 * np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.random.randn(len(t))

    r_peaks_indices, _ = find_peaks(ecg_signal, distance=int(sampling_rate * 0.5), height=0.5)

    if len(r_peaks_indices) < 2:
        return None, None, None, None

    annotations = []
    time_unit = 1 / sampling_rate

    for i in range(len(r_peaks_indices) - 1):
        r_idx = r_peaks_indices[i]
        next_r_idx = r_peaks_indices[i+1]

        # Simplified QRS Boundaries
        q_idx = max(0, r_idx - int(0.05 * sampling_rate))
        s_idx = min(len(ecg_signal) - 1, r_idx + int(0.05 * sampling_rate))

        # Placeholder values
        p_amp, t_amp = 0.15, 0.3
        p_dur, qrs_dur, t_dur = 0.10, 0.08, 0.16 # duration in seconds

        # Calculate Intervals (in seconds)
        rr_dur = (next_r_idx - r_idx) * time_unit
        pr_dur = 0.15
        st_dur = 0.08
        rp_dur = rr_dur - pr_dur
        
        # Calculate Amplitudes
        p_amp_val = p_amp
        qrs_amp_val = ecg_signal[r_idx] - ecg_signal[q_idx]
        t_amp_val = t_amp
        
        # Simplified Diagnosis
        diagnosis = "Normal Sinus Rhythm" if 0.6 < rr_dur < 1.0 else "Tachycardia/Bradycardia"
        
        beat_data = {
            'Beat_Index': i + 1,
            'P_Amp_mV': round(p_amp_val, 3),
            'QRS_Amp_mV': round(qrs_amp_val, 3),
            'T_Amp_mV': round(t_amp_val, 3),
            'P_Dur_s': round(p_dur, 3),
            'QRS_Dur_s': round(qrs_dur, 3),
            'T_Dur_s': round(t_dur, 3),
            'PR_Dur_s': round(pr_dur, 3),
            'ST_Dur_s': round(st_dur, 3),
            'RP_Dur_s': round(rp_dur, 3),
            'RR_Dur_s': round(rr_dur, 3),
            'Diagnosis': diagnosis
        }
        annotations.append(beat_data)

    return pd.DataFrame(annotations), t, ecg_signal, r_peaks_indices


# --- 2. LIVE GOOGLE SHEET CONNECTION (Uses st.secrets) ---

def save_data_to_google_sheets_live(df):
    """Connects and saves the DataFrame to Google Sheets using Streamlit Secrets."""
    if df is None or df.empty:
        st.warning("⚠️ No data to upload to Google Sheets.")
        return

    # --- 1. Load and Prepare Credentials from Streamlit Secrets ---
    try:
        # Load the service account credentials dictionary from st.secrets
        # CRITICAL FIX: Use copy.deepcopy() to create a writable dictionary object
        creds_json = copy.deepcopy(st.secrets["gcp_service_account"])
        
        # Convert the private_key string (with escaped newlines \n) back to a proper key.
        # This modification is now safe because we are editing a copy of the secrets.
        if 'private_key' in creds_json and isinstance(creds_json['private_key'], str):
            creds_json['private_key'] = creds_json['private_key'].replace('\\n', '\n') 
        
        creds = Credentials.from_service_account_info(creds_json)

    except KeyError:
        st.error("❌ Configuration Error: Streamlit secrets key `gcp_service_account` not found.")
        st.caption("Please ensure you have configured your secrets file correctly under the key `gcp_service_account`.")
        return
    except Exception as e:
        st.error(f"❌ Failed to load or parse credentials from secrets: {e}")
        st.caption("Double-check the formatting of your JSON data, especially the private key.")
        return

    # --- 2. Connect to Google Sheets ---
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_NAME = "ECG Annotation Data"
    WORKSHEET_NAME = "Annotations"

    try:
        with st.spinner('Connecting to Google Sheets...'):
            gc = gspread.authorize(creds)
            
            sh = gc.open(SPREADSHEET_NAME) 
            worksheet = sh.worksheet(WORKSHEET_NAME)
            
            # 3. Clear and Update
            worksheet.clear()
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        st.success(f"☁️ **Success!** Data uploaded to Google Sheet: {SPREADSHEET_NAME}.")
        st.caption(f"View Data: {sh.url}")

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Spreadsheet Not Found: Ensure the Google Sheet is named '{SPREADSHEET_NAME}'.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred during Google Sheet sync: {e}")
        st.caption("Verify that the Service Account email has 'Editor' access to the spreadsheet.")


# --- 3. STREAMLIT UI/UX DESIGN ---

def main():
    st.set_page_config(layout="wide", page_title="ECG Annotation Platform")
    
    st.title("❤️ Automated ECG Annotation and Analysis Platform")
    st.markdown("---")
    
    # --- Sidebar for File Upload and Settings ---
    with st.sidebar:
        st.header("Input Controls")
        
        # File Uploader (currently dummy)
        uploaded_file = st.file_uploader(
            "Upload ECG Data File (e.g., .csv, .txt)", 
            type=['csv', 'txt']
        )
        
        st.subheader("Analysis Parameters")
        sampling_rate = st.slider("Sampling Rate (Hz)", min_value=100, max_value=500, value=200, step=10)
        duration = st.slider("Analysis Duration (s)", min_value=1, max_value=10, value=5, step=1)
        
        process_button = st.button("Run Annotation", type="primary")
        
        st.markdown("---")
        st.markdown("© 2025 ECG Analyzer")
        
    # Initialize DataFrame in session state
    if 'annotations_df' not in st.session_state:
        st.session_state.annotations_df = pd.DataFrame() 
    
    # --- Main Content Area ---
    
    if process_button:
        # 1. Run the simulation/annotation
        with st.spinner('Analyzing ECG signal...'):
            annotations_df, time_series, signal, r_indices = simulate_ecg_and_annotate(sampling_rate, duration)
        
        st.session_state.annotations_df = annotations_df # Store result in state

        if annotations_df is None or annotations_df.empty:
            st.error("❌ Analysis failed: Could not detect enough beats for annotation.")
            return 

        # --- A. Visualization Section ---
        st.header("1️⃣ ECG Tracing Visualization")
        
        # Create Plotly figure
        plot_df = pd.DataFrame({'Time (s)': time_series, 'Amplitude (mV)': signal})
        fig = px.line(
            plot_df, 
            x='Time (s)', 
            y='Amplitude (mV)', 
            title=f"ECG Tracing (Sampling Rate: {sampling_rate} Hz)"
        )
        
        # Highlight R-peaks on the plot
        r_times = time_series[r_indices]
        r_amps = signal[r_indices]
        fig.add_scatter(
            x=r_times, 
            y=r_amps, 
            mode='markers', 
            name='R-Peaks', 
            marker={'color': 'red', 'size': 8}
        )
        fig.update_layout(hovermode="x unified", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
    # Display results if they exist in the session state
    if not st.session_state.annotations_df.empty:
        annotations_df = st.session_state.annotations_df
        
        # --- B. Annotation and Diagnosis Table ---
        st.header("2️⃣ Annotation and Diagnosis Results")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("Beat-by-Beat Annotations")
            st.dataframe(annotations_df.set_index('Beat_Index'), use_container_width=True, height=350)

        with col2:
            st.subheader("Summary Diagnosis")
            mode_diagnosis = annotations_df['Diagnosis'].mode().iloc[0]
            st.metric(label="Overall Heart Rhythm", value=mode_diagnosis)
            
            avg_rr = annotations_df['RR_Dur_s'].mean()
            st.metric(label="Average RR Interval", value=f"{avg_rr:.3f} s")
            
            bpm = 60 / avg_rr
            st.metric(label="Estimated Heart Rate (BPM)", value=f"{bpm:.0f} bpm")
        
        st.markdown("---")
        
        # --- C. Export and Save Section ---
        st.header("3️⃣ Data Management")
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.signal import find_peaks
import gspread
from google.oauth2.service_account import Credentials
import json


# --- 1. CORE ECG ANNOTATION LOGIC ---

def simulate_ecg_and_annotate(sampling_rate=200, duration=5):
    """
    Simulates a simplified ECG signal and attempts to detect key features.
    """
    t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)
    # A simple wave simulation
    ecg_signal = 0.8 * np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.random.randn(len(t))

    r_peaks_indices, _ = find_peaks(ecg_signal, distance=int(sampling_rate * 0.5), height=0.5)

    if len(r_peaks_indices) < 2:
        return None, None, None, None

    annotations = []
    time_unit = 1 / sampling_rate

    for i in range(len(r_peaks_indices) - 1):
        r_idx = r_peaks_indices[i]
        next_r_idx = r_peaks_indices[i+1]

        # Simplified QRS Boundaries
        q_idx = max(0, r_idx - int(0.05 * sampling_rate))
        s_idx = min(len(ecg_signal) - 1, r_idx + int(0.05 * sampling_rate))

        # Placeholder values
        p_amp, t_amp = 0.15, 0.3
        p_dur, qrs_dur, t_dur = 0.10, 0.08, 0.16

        # Calculate Intervals (in seconds)
        rr_dur = (next_r_idx - r_idx) * time_unit
        pr_dur = 0.15
        st_dur = 0.08
        rp_dur = rr_dur - pr_dur
        
        # Calculate Amplitudes
        p_amp_val = p_amp
        qrs_amp_val = ecg_signal[r_idx] - ecg_signal[q_idx]
        t_amp_val = t_amp
        
        # Simplified Diagnosis
        diagnosis = "Normal Sinus Rhythm" if 0.6 < rr_dur < 1.0 else "Tachycardia/Bradycardia"
        
        beat_data = {
            'Beat_Index': i + 1,
            'P_Amp_mV': round(p_amp_val, 3),
            'QRS_Amp_mV': round(qrs_amp_val, 3),
            'T_Amp_mV': round(t_amp_val, 3),
            'P_Dur_s': round(p_dur, 3),
            'QRS_Dur_s': round(qrs_dur, 3),
            'T_Dur_s': round(t_dur, 3),
            'PR_Dur_s': round(pr_dur, 3),
            'ST_Dur_s': round(st_dur, 3),
            'RP_Dur_s': round(rp_dur, 3),
            'RR_Dur_s': round(rr_dur, 3),
            'Diagnosis': diagnosis
        }
        annotations.append(beat_data)

    return pd.DataFrame(annotations), t, ecg_signal, r_peaks_indices


# --- 2. GOOGLE SHEET CONNECTION ---

def save_data_to_google_sheets(df):
    """Connects and saves the DataFrame to Google Sheets using credentials."""
    if df is None or df.empty:
        st.warning("⚠️ No data to upload to Google Sheets.")
        return

    try:
        # Load credentials from Streamlit secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Fix the private key formatting
        if 'private_key' in creds_dict:
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        # Define scopes
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    except KeyError:
        st.error("❌ Configuration Error: Streamlit secrets key `gcp_service_account` not found.")
        st.info("💡 Please configure your secrets in `.streamlit/secrets.toml`")
        return
    except Exception as e:
        st.error(f"❌ Failed to load credentials: {e}")
        return

    # Google Sheets settings
    SPREADSHEET_NAME = "ECG Annotation Data"
    WORKSHEET_NAME = "Annotations"

    try:
        with st.spinner('Connecting to Google Sheets...'):
            gc = gspread.authorize(creds)
            
            # Open spreadsheet
            sh = gc.open(SPREADSHEET_NAME)
            worksheet = sh.worksheet(WORKSHEET_NAME)
            
            # Clear and update
            worksheet.clear()
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        st.success(f"☁️ **Success!** Data uploaded to Google Sheet: {SPREADSHEET_NAME}")
        st.caption(f"📊 [View Spreadsheet]({sh.url})")

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Spreadsheet '{SPREADSHEET_NAME}' not found.")
        st.info("Please create a Google Sheet with this name and share it with your service account.")
    except Exception as e:
        st.error(f"❌ Error during Google Sheet sync: {e}")


# --- 3. STREAMLIT UI ---

def main():
    st.set_page_config(
        layout="wide", 
        page_title="ECG Annotation Platform",
        page_icon="❤️"
    )
    
    st.title("❤️ Automated ECG Annotation and Analysis Platform")
    st.markdown("---")
    
    # --- Sidebar ---
    with st.sidebar:
        st.header("Input Controls")
        
        uploaded_file = st.file_uploader(
            "Upload ECG Data File (e.g., .csv, .txt)", 
            type=['csv', 'txt']
        )
        
        st.subheader("Analysis Parameters")
        sampling_rate = st.slider(
            "Sampling Rate (Hz)", 
            min_value=100, 
            max_value=500, 
            value=200, 
            step=10
        )
        duration = st.slider(
            "Analysis Duration (s)", 
            min_value=1, 
            max_value=10, 
            value=5, 
            step=1
        )
        
        process_button = st.button("🔬 Run Annotation", type="primary")
        
        st.markdown("---")
        st.markdown("### About")
        st.caption("ECG Annotation Platform v1.0")
        st.caption("© 2025 ECG Analyzer")
        
    # Initialize session state
    if 'annotations_df' not in st.session_state:
        st.session_state.annotations_df = pd.DataFrame()
    if 'time_series' not in st.session_state:
        st.session_state.time_series = None
    if 'signal' not in st.session_state:
        st.session_state.signal = None
    if 'r_indices' not in st.session_state:
        st.session_state.r_indices = None
    
    # --- Main Content ---
    
    if process_button:
        with st.spinner('🔄 Analyzing ECG signal...'):
            annotations_df, time_series, signal, r_indices = simulate_ecg_and_annotate(
                sampling_rate, 
                duration
            )
        
        if annotations_df is None or annotations_df.empty:
            st.error("❌ Analysis failed: Could not detect enough beats for annotation.")
            return
        
        # Store in session state
        st.session_state.annotations_df = annotations_df
        st.session_state.time_series = time_series
        st.session_state.signal = signal
        st.session_state.r_indices = r_indices
        
        st.success("✅ ECG analysis completed successfully!")

    # Display results if available
    if not st.session_state.annotations_df.empty:
        annotations_df = st.session_state.annotations_df
        time_series = st.session_state.time_series
        signal = st.session_state.signal
        r_indices = st.session_state.r_indices
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.signal import find_peaks
import gspread
from google.oauth2.service_account import Credentials
import json


# --- 1. CORE ECG ANNOTATION LOGIC ---

def simulate_ecg_and_annotate(sampling_rate=200, duration=5):
    """
    Simulates a simplified ECG signal and attempts to detect key features.
    """
    t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)
    # A simple wave simulation
    ecg_signal = 0.8 * np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.random.randn(len(t))

    r_peaks_indices, _ = find_peaks(ecg_signal, distance=int(sampling_rate * 0.5), height=0.5)

    if len(r_peaks_indices) < 2:
        return None, None, None, None

    annotations = []
    time_unit = 1 / sampling_rate

    for i in range(len(r_peaks_indices) - 1):
        r_idx = r_peaks_indices[i]
        next_r_idx = r_peaks_indices[i+1]

        # Simplified QRS Boundaries
        q_idx = max(0, r_idx - int(0.05 * sampling_rate))
        s_idx = min(len(ecg_signal) - 1, r_idx + int(0.05 * sampling_rate))

        # Placeholder values
        p_amp, t_amp = 0.15, 0.3
        p_dur, qrs_dur, t_dur = 0.10, 0.08, 0.16

        # Calculate Intervals (in seconds)
        rr_dur = (next_r_idx - r_idx) * time_unit
        pr_dur = 0.15
        st_dur = 0.08
        rp_dur = rr_dur - pr_dur
        
        # Calculate Amplitudes
        p_amp_val = p_amp
        qrs_amp_val = ecg_signal[r_idx] - ecg_signal[q_idx]
        t_amp_val = t_amp
        
        # Simplified Diagnosis
        diagnosis = "Normal Sinus Rhythm" if 0.6 < rr_dur < 1.0 else "Tachycardia/Bradycardia"
        
        beat_data = {
            'Beat_Index': i + 1,
            'P_Amp_mV': round(p_amp_val, 3),
            'QRS_Amp_mV': round(qrs_amp_val, 3),
            'T_Amp_mV': round(t_amp_val, 3),
            'P_Dur_s': round(p_dur, 3),
            'QRS_Dur_s': round(qrs_dur, 3),
            'T_Dur_s': round(t_dur, 3),
            'PR_Dur_s': round(pr_dur, 3),
            'ST_Dur_s': round(st_dur, 3),
            'RP_Dur_s': round(rp_dur, 3),
            'RR_Dur_s': round(rr_dur, 3),
            'Diagnosis': diagnosis
        }
        annotations.append(beat_data)

    return pd.DataFrame(annotations), t, ecg_signal, r_peaks_indices


# --- 2. GOOGLE SHEET CONNECTION ---

def save_data_to_google_sheets(df):
    """Connects and saves the DataFrame to Google Sheets using credentials."""
    if df is None or df.empty:
        st.warning("⚠️ No data to upload to Google Sheets.")
        return

    try:
        # Load credentials from Streamlit secrets
        # Create a mutable copy of the secrets
        creds_dict = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"],
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
        }
        
        # Fix the private key formatting - handle both cases
        if 'private_key' in creds_dict:
            # Replace literal \n with actual newlines
            private_key = creds_dict['private_key']
            if '\\n' in private_key:
                private_key = private_key.replace('\\n', '\n')
            # Ensure proper formatting
            if not private_key.startswith('-----BEGIN'):
                st.error("❌ Private key format error: Key should start with '-----BEGIN PRIVATE KEY-----'")
                return
            creds_dict['private_key'] = private_key
        
        # Define scopes
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    except KeyError as e:
        st.error(f"❌ Configuration Error: Missing key in secrets: {e}")
        st.info("💡 Please configure your secrets in `.streamlit/secrets.toml`")
        with st.expander("📋 Show Required Keys"):
            st.code("""
Required keys in secrets.toml:
- type
- project_id
- private_key_id
- private_key
- client_email
- client_id
- auth_uri
- token_uri
- auth_provider_x509_cert_url
- client_x509_cert_url
            """)
        return
    except Exception as e:
        st.error(f"❌ Failed to load credentials: {e}")
        return

    # Google Sheets settings
    SPREADSHEET_NAME = "ECG Annotation Data"
    WORKSHEET_NAME = "Annotations"

    try:
        with st.spinner('Connecting to Google Sheets...'):
            gc = gspread.authorize(creds)
            
            # Open spreadsheet
            sh = gc.open(SPREADSHEET_NAME)
            worksheet = sh.worksheet(WORKSHEET_NAME)
            
            # Clear and update
            worksheet.clear()
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        st.success(f"☁️ **Success!** Data uploaded to Google Sheet: {SPREADSHEET_NAME}")
        st.caption(f"📊 [View Spreadsheet]({sh.url})")

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Spreadsheet '{SPREADSHEET_NAME}' not found.")
        st.info("Please create a Google Sheet with this name and share it with your service account.")
    except Exception as e:
        st.error(f"❌ Error during Google Sheet sync: {e}")


# --- 3. STREAMLIT UI ---

def main():
    st.set_page_config(
        layout="wide", 
        page_title="ECG Annotation Platform",
        page_icon="❤️"
    )
    
    st.title("❤️ Automated ECG Annotation and Analysis Platform")
    st.markdown("---")
    
    # --- Sidebar ---
    with st.sidebar:
        st.header("Input Controls")
        
        uploaded_file = st.file_uploader(
            "Upload ECG Data File (e.g., .csv, .txt)", 
            type=['csv', 'txt']
        )
        
        st.subheader("Analysis Parameters")
        sampling_rate = st.slider(
            "Sampling Rate (Hz)", 
            min_value=100, 
            max_value=500, 
            value=200, 
            step=10
        )
        duration = st.slider(
            "Analysis Duration (s)", 
            min_value=1, 
            max_value=10, 
            value=5, 
            step=1
        )
        
        process_button = st.button("🔬 Run Annotation", type="primary")
        
        st.markdown("---")
        st.markdown("### About")
        st.caption("ECG Annotation Platform v1.0")
        st.caption("© 2025 ECG Analyzer")
        
    # Initialize session state
    if 'annotations_df' not in st.session_state:
        st.session_state.annotations_df = pd.DataFrame()
    if 'time_series' not in st.session_state:
        st.session_state.time_series = None
    if 'signal' not in st.session_state:
        st.session_state.signal = None
    if 'r_indices' not in st.session_state:
        st.session_state.r_indices = None
    
    # --- Main Content ---
    
    if process_button:
        with st.spinner('🔄 Analyzing ECG signal...'):
            annotations_df, time_series, signal, r_indices = simulate_ecg_and_annotate(
                sampling_rate, 
                duration
            )
        
        if annotations_df is None or annotations_df.empty:
            st.error("❌ Analysis failed: Could not detect enough beats for annotation.")
            return
        
        # Store in session state
        st.session_state.annotations_df = annotations_df
        st.session_state.time_series = time_series
        st.session_state.signal = signal
        st.session_state.r_indices = r_indices
        
        st.success("✅ ECG analysis completed successfully!")

    # Display results if available
    if not st.session_state.annotations_df.empty:
        annotations_df = st.session_state.annotations_df
        time_series = st.session_state.time_series
        signal = st.session_state.signal
        r_indices = st.session_state.r_indices
        
        # --- Visualization Section ---
        st.header("1️⃣ ECG Tracing Visualization")
        
        plot_df = pd.DataFrame({
            'Time (s)': time_series, 
            'Amplitude (mV)': signal
        })
        
        fig = px.line(
            plot_df, 
            x='Time (s)', 
            y='Amplitude (mV)', 
            title=f"ECG Tracing (Sampling Rate: {sampling_rate} Hz)"
        )
        
        # Add R-peaks
        r_times = time_series[r_indices]
        r_amps = signal[r_indices]
        fig.add_scatter(
            x=r_times, 
            y=r_amps, 
            mode='markers', 
            name='R-Peaks', 
            marker={'color': 'red', 'size': 10, 'symbol': 'diamond'}
        )
        
        fig.update_layout(
            hovermode="x unified", 
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # --- Annotation Results ---
        st.header("2️⃣ Annotation and Diagnosis Results")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("📋 Beat-by-Beat Annotations")
            st.dataframe(
                annotations_df.set_index('Beat_Index'), 
                use_container_width=True, 
                height=350
            )

        with col2:
            st.subheader("📊 Summary Metrics")
            
            mode_diagnosis = annotations_df['Diagnosis'].mode().iloc[0]
            st.metric(label="Overall Rhythm", value=mode_diagnosis)
            
            avg_rr = annotations_df['RR_Dur_s'].mean()
            st.metric(label="Avg RR Interval", value=f"{avg_rr:.3f} s")
            
            bpm = 60 / avg_rr
            st.metric(label="Heart Rate", value=f"{bpm:.0f} bpm")
        
        st.markdown("---")
        
        # --- Export Section ---
        st.header("3️⃣ Data Management")
        
        col_export, col_save = st.columns(2)
        
        with col_export:
            st.subheader("💾 Export Data")
            csv_data = annotations_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv_data,
                file_name='ecg_annotations.csv',
                mime='text/csv',
                type="secondary"
            )

        with col_save:
            st.subheader("☁️ Cloud Sync")
            if st.button("📤 Save to Google Sheets", type="primary"):
                save_data_to_google_sheets(annotations_df)


if __name__ == '__main__':
    main()
