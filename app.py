import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.signal import find_peaks

# --- 1. CORE ECG ANNOTATION LOGIC (Integrated from previous response) ---

def simulate_ecg_and_annotate(sampling_rate=200, duration=5):
    """
    Simulates a simplified ECG signal and attempts to detect key features.
    Returns: DataFrame of annotations, Time series array, ECG signal array
    """
    t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)
    # A simple sin wave simulation - NOT a real ECG
    ecg_signal = np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.random.randn(len(t))

    r_peaks_indices, _ = find_peaks(ecg_signal, distance=int(sampling_rate * 0.5), height=0.5)

    if len(r_peaks_indices) < 2:
        return None, None, None

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

# --- 2. GOOGLE SHEET SIMULATION (No live connection here, just UI placeholder) ---

def simulate_google_sheet_save(df):
    """Placeholder function to simulate saving to Google Sheets."""
    if df is not None and not df.empty:
        st.success("☁️ **Success!** Data (simulated) uploaded to Google Drive/Sheets.")
        st.caption("*(Note: Live Google Sheet connection requires separate `gspread` setup outside this UI framework.)*")
    else:
        st.warning("⚠️ No data to upload to Google Sheets.")

# --- 3. STREAMLIT UI/UX DESIGN ---

def main():
    st.set_page_config(layout="wide", page_title="ECG Annotation Platform")
    
    st.title("❤️ Automated ECG Annotation and Analysis Platform")
    st.markdown("---")
    
    # --- Sidebar for File Upload and Settings ---
    with st.sidebar:
        st.header("Input Controls")
        
        # File Uploader (currently dummy, but standard for real platform)
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
        
    # --- Main Content Area ---

    annotations_df = pd.DataFrame() # Initialize empty DataFrame
    
    if process_button:
        # 1. Run the simulation/annotation
        with st.spinner('Analyzing ECG signal...'):
            annotations_df, time_series, signal, r_indices = simulate_ecg_and_annotate(sampling_rate, duration)

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
        
        # --- B. Annotation and Diagnosis Table ---
        st.header("2️⃣ Annotation and Diagnosis Results")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("Beat-by-Beat Annotations")
            st.dataframe(annotations_df.set_index('Beat_Index'), use_container_width=True, height=350)

        with col2:
            st.subheader("Summary Diagnosis")
            # Calculate most frequent diagnosis
            mode_diagnosis = annotations_df['Diagnosis'].mode().iloc[0]
            st.metric(label="Overall Heart Rhythm", value=mode_diagnosis)
            
            # Calculate average RR interval
            avg_rr = annotations_df['RR_Dur_s'].mean()
            st.metric(label="Average RR Interval", value=f"{avg_rr:.3f} s")
            
            # Calculate Heart Rate (BPM = 60 / avg_rr)
            bpm = 60 / avg_rr
            st.metric(label="Estimated Heart Rate (BPM)", value=f"{bpm:.0f} bpm")
        
        st.markdown("---")
        
        # --- C. Export and Save Section ---
        st.header("3️⃣ Data Management")
        
        export_col, save_col = st.columns(2)
        
        with export_col:
            st.subheader("Export Data")
            csv_data = annotations_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Annotations as CSV",
                data=csv_data,
                file_name='ecg_annotations.csv',
                mime='text/csv',
                type="secondary"
            )

        with save_col:
            st.subheader("Cloud Sync")
            if st.button("📤 Save Data to Google Sheets (Simulated)"):
                simulate_google_sheet_save(annotations_df)


if __name__ == '__main__':
    main()

