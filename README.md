# ❤️ ECG Annotation and Analysis Platform

A Streamlit-based application for automated ECG signal analysis with Google Sheets integration for data storage and collaboration.

## Features

- 📊 **Real-time ECG Signal Analysis**: Simulates and analyzes ECG signals with automatic beat detection
- 📈 **Interactive Visualizations**: Plotly-powered ECG tracings with R-peak detection
- 🔍 **Beat-by-Beat Annotations**: Comprehensive analysis of P, QRS, and T waves
- 💓 **Heart Rate Metrics**: Automatic calculation of RR intervals and heart rate
- ☁️ **Google Sheets Integration**: Save and sync data to Google Sheets
- 💾 **Data Export**: Download annotations as CSV files

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account (for Google Sheets integration)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ecg-annotation-platform.git
   cd ecg-annotation-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Sheets Access** (Optional but recommended)
   
   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project or select existing one
   
   c. Enable Google Sheets API:
      - Navigate to "APIs & Services" > "Library"
      - Search for "Google Sheets API"
      - Click "Enable"
   
   d. Create Service Account:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "Service Account"
      - Fill in the details and create
      - Click on the created service account
      - Go to "Keys" tab > "Add Key" > "Create new key" > JSON
      - Download the JSON file
   
   e. Share your Google Sheet:
      - Create a Google Sheet named "ECG Annotation Data"
      - Add a worksheet named "Annotations"
      - Share the sheet with the service account email (found in the JSON file)
      - Give "Editor" permissions

5. **Configure Secrets**
   
   Create `.streamlit/secrets.toml` file:
   ```bash
   mkdir -p .streamlit
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   
   Edit `.streamlit/secrets.toml` and paste your service account JSON content under `[gcp_service_account]`

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Deployment to Streamlit Cloud

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Choose `app.py` as the main file
   - Click "Advanced settings"
   - Add your secrets from the service account JSON file
   - Click "Deploy"

### Adding Secrets in Streamlit Cloud

In the Advanced Settings, add your secrets in TOML format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

## Usage

1. **Adjust Analysis Parameters**
   - Set sampling rate (100-500 Hz)
   - Set analysis duration (1-10 seconds)

2. **Run Analysis**
   - Click "Run Annotation" button
   - View ECG tracing with detected R-peaks
   - Review beat-by-beat annotations

3. **Export Data**
   - Download results as CSV
   - Save to Google Sheets for cloud storage

## Project Structure

```
ecg-annotation-platform/
├── app.py                          # Main application
├── requirements.txt                # Python dependencies
├── README.md                       # Documentation
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── secrets.toml.example       # Template for secrets
└── LICENSE                        # License file
```

## Features in Detail

### ECG Signal Analysis
- Automatic R-peak detection using scipy signal processing
- P, QRS, and T wave amplitude measurements
- Duration calculations for cardiac intervals (PR, QRS, ST, RR)
- Simplified rhythm diagnosis

### Data Management
- Local CSV export
- Cloud synchronization with Google Sheets
- Persistent storage for collaboration

### Visualization
- Interactive Plotly charts
- R-peak highlighting
- Zoom and pan capabilities

## Troubleshooting

### Google Sheets Integration Issues

**Problem**: "Spreadsheet not found" error
- **Solution**: Ensure the Google Sheet is named exactly "ECG Annotation Data" with a worksheet named "Annotations"

**Problem**: Authentication fails
- **Solution**: Verify service account email has Editor access to the spreadsheet

**Problem**: Private key error
- **Solution**: Ensure private key in secrets.toml contains `\n` for newlines

### Deployment Issues

**Problem**: Module not found errors
- **Solution**: Ensure all dependencies are listed in requirements.txt

**Problem**: Secrets not loading
- **Solution**: Verify secrets.toml format and indentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data visualization by [Plotly](https://plotly.com/)
- Google Sheets integration via [gspread](https://github.com/burnash/gspread)

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is a demonstration application with simulated ECG data. For medical applications, please use validated ECG analysis tools and consult with healthcare professionals.
