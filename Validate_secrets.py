"""
Helper script to validate and fix Google Service Account credentials
Run this script to check if your secrets.toml is properly formatted
"""

import json
import sys
from pathlib import Path

def validate_private_key(key):
    """Validate the private key format"""
    issues = []
    
    # Check if key starts correctly
    if not key.startswith('-----BEGIN PRIVATE KEY-----'):
        issues.append("❌ Key should start with '-----BEGIN PRIVATE KEY-----'")
    
    # Check if key ends correctly
    if not key.strip().endswith('-----END PRIVATE KEY-----'):
        issues.append("❌ Key should end with '-----END PRIVATE KEY-----'")
    
    # Check for proper newlines
    if '\\n' in key:
        issues.append("⚠️ Key contains literal '\\n' - these should be actual newlines")
    
    # Check minimum length
    if len(key) < 100:
        issues.append("❌ Key seems too short - might be truncated")
    
    return issues

def convert_json_to_toml(json_path):
    """Convert service account JSON to TOML format"""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Escape newlines in private key for TOML
        private_key = data['private_key'].replace('\n', '\\n')
        
        toml_content = f'''[gcp_service_account]
type = "{data['type']}"
project_id = "{data['project_id']}"
private_key_id = "{data['private_key_id']}"
private_key = "{private_key}"
client_email = "{data['client_email']}"
client_id = "{data['client_id']}"
auth_uri = "{data['auth_uri']}"
token_uri = "{data['token_uri']}"
auth_provider_x509_cert_url = "{data['auth_provider_x509_cert_url']}"
client_x509_cert_url = "{data['client_x509_cert_url']}"
'''
        
        return toml_content
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_path}")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return None
    except KeyError as e:
        print(f"❌ Missing required key in JSON: {e}")
        return None

def main():
    print("🔐 Google Service Account Credentials Validator\n")
    
    # Check if secrets.toml exists
    secrets_path = Path(".streamlit/secrets.toml")
    
    if not secrets_path.exists():
        print("⚠️ .streamlit/secrets.toml not found!")
        print("\nOptions:")
        print("1. Create secrets.toml from service account JSON file")
        print("2. Exit\n")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            json_path = input("\nEnter path to your service account JSON file: ").strip()
            toml_content = convert_json_to_toml(json_path)
            
            if toml_content:
                # Create .streamlit directory if it doesn't exist
                Path(".streamlit").mkdir(exist_ok=True)
                
                # Write to secrets.toml
                with open(secrets_path, 'w') as f:
                    f.write(toml_content)
                
                print(f"\n✅ Created {secrets_path}")
                print("⚠️ IMPORTANT: Never commit this file to Git!")
                print("\nNext steps:")
                print("1. Verify the file was created correctly")
                print("2. Run your Streamlit app: streamlit run app.py")
            else:
                print("\n❌ Failed to convert JSON to TOML")
        
        return
    
    # Read and validate secrets.toml
    print("📄 Reading .streamlit/secrets.toml...\n")
    
    try:
        import toml
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)
        
        if 'gcp_service_account' not in secrets:
            print("❌ Missing [gcp_service_account] section in secrets.toml")
            return
        
        gcp_creds = secrets['gcp_service_account']
        
        # Check required keys
        required_keys = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri',
            'auth_provider_x509_cert_url', 'client_x509_cert_url'
        ]
        
        missing_keys = [key for key in required_keys if key not in gcp_creds]
        
        if missing_keys:
            print(f"❌ Missing required keys: {', '.join(missing_keys)}\n")
            return
        
        print("✅ All required keys present\n")
        
        # Validate private key
        print("🔑 Validating private key format...")
        private_key = gcp_creds['private_key']
        issues = validate_private_key(private_key)
        
        if issues:
            print("\n⚠️ Private Key Issues Found:")
            for issue in issues:
                print(f"  {issue}")
            print("\n💡 Tips:")
            print("  1. Copy the private_key value exactly from your JSON file")
            print("  2. In TOML format, use \\n for newlines (e.g., 'key\\nmore\\n')")
            print("  3. Ensure the key is wrapped in quotes")
            print("  4. Don't add extra spaces or line breaks")
        else:
            print("✅ Private key format looks good!\n")
        
        # Show credential info
        print("📋 Credential Information:")
        print(f"  Project ID: {gcp_creds['project_id']}")
        print(f"  Service Account: {gcp_creds['client_email']}")
        print(f"  Private Key ID: {gcp_creds['private_key_id'][:20]}...")
        
        print("\n✅ Validation complete!")
        print("\n⚠️ Remember:")
        print("  1. Share your Google Sheet with: " + gcp_creds['client_email'])
        print("  2. Give the service account 'Editor' permissions")
        print("  3. Never commit secrets.toml to Git")
        
    except ImportError:
        print("⚠️ 'toml' package not installed. Install with: pip install toml")
        print("\nAlternatively, manually check your secrets.toml format")
    except Exception as e:
        print(f"❌ Error reading secrets.toml: {e}")

if __name__ == "__main__":
    main()
