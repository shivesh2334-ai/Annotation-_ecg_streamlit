# ECG Annotation Platform

This is a Streamlit web application for basic ECG annotation and Google Sheets data cloud sync.

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Place your Google Service Account credentials in `.streamlit/secrets.toml` as shown below.

3. Run the app:
   ```
   streamlit run app.py
   ```

## Streamlit Cloud Deployment

- Add the files as above.
- Set up the Service Account secrets in `.streamlit/secrets.toml`.
- Deploy via [share.streamlit.io](https://share.streamlit.io/).

## Google Sheets Integration

- Create a Google Sheet named **ECG Annotation Data**, with a worksheet/tab named **Annotations**.
- Share the Google Sheet with your Service Account's email (found in your credentials file) with Editor access.

## Required .streamlit/secrets.toml

Put this in `.streamlit/secrets.toml` (fill with your actual credentials):

```toml
[gcp_service_account]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "YOUR_CLIENT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"
```
See [Streamlit secrets documentation](https://docs.streamlit.io/knowledge-base/tutorials/databases/gsheets) for more.
