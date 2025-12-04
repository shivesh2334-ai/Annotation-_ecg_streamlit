#❤️ Automated ECG Annotation and Analysis Platform
​This project provides a Streamlit-based web interface for the automated annotation and analysis of Electrocardiogram (ECG) data. It simulates feature extraction (P, QRS, T waves and intervals) and securely saves the results to a Google Sheet using Streamlit Secrets.
🚀 Getting Started
Follow these steps to set up and run the application.

git clone [your_repo_url]
cd [your_repo_name]
pip install -r requirements.txt
streamlit run app.py
☁️ Secure Google Sheets Integration Setup (MANDATORY)
To enable the "Save Data to Google Sheets" button, you MUST configure a Google Service Account and provide its credentials via Streamlit Secrets.
Step A: Configure Google Service Account
Create Google Sheet: Create a Google Sheet named ECG Annotation Data.
Enable APIs: In the Google Cloud Console, ensure you have enabled the Google Sheets API and Google Drive API for your project.
Create Key: Create a Service Account and download its JSON Key File (e.g., service-account-key.json).
Step B: Share the Spreadsheet
Open the JSON Key File and copy the value of the client_email key.
Go to your ECG Annotation Data Google Sheet, click "Share", paste the Service Account email, and grant it "Editor" access.
Step C: Configure Streamlit Secrets
Instead of using the JSON file directly, you must flatten its contents into the Streamlit secrets system (.streamlit/secrets.toml).
