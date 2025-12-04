# Setup Guide: Google Sheets Integration

This guide walks you through setting up Google Sheets integration for the ECG Annotation Platform.

## Step-by-Step Guide

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "ECG Annotation App")
5. Click "Create"

### 2. Enable Google Sheets API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Wait for the API to be enabled (usually takes a few seconds)

### 3. Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" at the top
3. Select "Service Account"
4. Fill in the service account details:
   - **Service account name**: `ecg-annotation-service`
   - **Service account ID**: (auto-generated)
   - **Description**: Service account for ECG annotation app
5. Click "Create and Continue"
6. Skip the optional permissions (click "Continue")
7. Skip granting users access (click "Done")

### 4. Create and Download Service Account Key

1. In the "Credentials" page, find your newly created service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Choose "JSON" format
6. Click "Create"
7. The JSON file will be downloaded automatically
8. **Keep this file secure!** It contains your credentials

### 5. Prepare Your Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it **exactly**: `ECG Annotation Data`
4. Create a worksheet named **exactly**: `Annotations` (or rename Sheet1)
5. Open the JSON file you downloaded
6. Find the `client_email` field (looks like `xxx@xxx.iam.gserviceaccount.com`)
7. Copy this email address
8. In your Google Sheet, click "Share"
9. Paste the service account email
10. Give it "Editor" permissions
11. Uncheck "Notify people"
12. Click "Share" or "Send"

### 6. Configure Application Secrets

#### For Local Development:

1. Open the downloaded JSON file in a text editor
2. Create the `.streamlit` directory in your project:
   ```bash
   mkdir -p .streamlit
   ```
3. Create `.streamlit/secrets.toml` file
4. Copy the following template and fill in values from your JSON:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_ACTUAL_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

**Important**: Keep the `\n` characters in the private_key - they represent newlines!

#### For Streamlit Cloud Deployment:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Select your app
3. Click on "Settings" (gear icon)
4. Go to "Secrets"
5. Paste the same TOML content from above
6. Click "Save"

### 7. Verify the Connection

1. Run your Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Process some ECG data
3. Click "Save to Google Sheets"
4. Check your Google Sheet - data should appear!

## Troubleshooting

### Error: "Spreadsheet not found"

**Cause**: The spreadsheet name doesn't match exactly

**Solution**:
- Verify your Google Sheet is named exactly `ECG Annotation Data`
- Check for extra spaces or different capitalization
- Ensure the worksheet is named `Annotations`

### Error: "Permission denied"

**Cause**: Service account doesn't have access to the spreadsheet

**Solution**:
- Open your Google Sheet
- Click "Share"
- Verify the service account email is listed with "Editor" access
- If not, add it again with Editor permissions

### Error: "Invalid private key"

**Cause**: Private key formatting issue in secrets.toml

**Solution**:
- Ensure your private_key in secrets.toml includes `\n` for newlines
- Don't add extra spaces or line breaks
- The key should be one long string with `\n` characters

Example of correct format:
```toml
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...\n-----END PRIVATE KEY-----\n"
```

### Error: "API not enabled"

**Cause**: Google Sheets API is not enabled for your project

**Solution**:
- Go to Google Cloud Console
- Navigate to "APIs & Services" > "Library"
- Search for "Google Sheets API"
- Click "Enable"

## Security Best Practices

1. **Never commit secrets.toml to Git**
   - It's already in .gitignore
   - Double-check before pushing

2. **Rotate credentials periodically**
   - Create new service account keys every few months
   - Delete old keys

3. **Limit service account permissions**
   - Only give access to necessary spreadsheets
   - Use Editor access, not Owner

4. **Monitor usage**
   - Check Google Cloud Console for API usage
   - Set up billing alerts

## Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [gspread Documentation](https://docs.gspread.org/)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

## Need Help?

If you're still experiencing issues:
1. Check the application logs for detailed error messages
2. Verify all steps in this guide
3. Open an issue on GitHub with:
   - Error message (remove any sensitive information)
   - Steps you've taken
   - Your environment (OS, Python version, etc.)
