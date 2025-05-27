import os
import sys
from email import message_from_file
from email.generator import Generator
from email.policy import default
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

try:
    import gnupg
except ImportError:
    print("[!] Error: python-gnupg package is not installed.")
    print("    Install it with: pip install python-gnupg")
    sys.exit(1)

# Load environment variables from .env one directory up from this script
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Setup
INPUT_DIR = os.path.join(os.path.dirname(__file__), "../emails")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../encrypted")
SELF_KEY = os.getenv("SELF_KEY")

if not SELF_KEY:
    print("[!] Error: SELF_KEY environment variable is not set in .env file")
    sys.exit(1)

KEY_IDS = [SELF_KEY]

# Initialize GPG with error handling
try:
    gpg = gnupg.GPG()  # Let gnupg use the default GPG home directory
    # Test if GPG is working by listing keys
    gpg.list_keys()
except OSError as e:
    print(f"[!] Error: GPG is not available or not properly installed.")
    print(f"    Error details: {e}")
    print("    Please install GPG:")
    print("    - Windows: Download from https://www.gnupg.org/download/")
    print("    - Or install via chocolatey: choco install gnupg")
    print("    - Or install via winget: winget install GnuPG.GnuPG")
    sys.exit(1)
except Exception as e:
    print(f"[!] Error initializing GPG: {e}")
    sys.exit(1)

# Create output directory
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except OSError as e:
    print(f"[!] Error creating output directory {OUTPUT_DIR}: {e}")
    sys.exit(1)

def encrypt_eml(file_path, output_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            msg = message_from_file(f, policy=default)
    except (OSError, UnicodeDecodeError) as e:
        print(f"[!] Error reading file {file_path}: {e}")
        return False

    # Extract and encrypt the plain text body
    try:
        if msg.is_multipart():
            part = msg.get_body(preferencelist=('plain'))
            if part is None:
                print(f"[!] No plain text body found in {file_path}")
                return False
            plaintext = part.get_content()
        else:
            plaintext = msg.get_payload()
        
        if not plaintext:
            print(f"[!] No content to encrypt in {file_path}")
            return False
            
    except Exception as e:
        print(f"[!] Error extracting content from {file_path}: {e}")
        return False

    # Encode plaintext as utf-8 bytes
    try:
        if isinstance(plaintext, str):
            plaintext_bytes = plaintext.encode('utf-8')
        else:
            plaintext_bytes = str(plaintext).encode('utf-8')
            
        encrypted = gpg.encrypt(plaintext_bytes, recipients=KEY_IDS, always_trust=True)
        if not encrypted.ok:
            print(f"[!] Encryption failed for {file_path}: {encrypted.status}")
            return False
    except Exception as e:
        print(f"[!] Error during encryption of {file_path}: {e}")
        return False

    # Build a new PGP/MIME email
    try:
        pgp_msg = MIMEMultipart(_subtype="encrypted", protocol="application/pgp-encrypted")
        pgp_msg["From"] = msg.get("From", SELF_KEY)
        pgp_msg["To"] = msg.get("To", SELF_KEY)
        pgp_msg["Subject"] = msg.get("Subject", "Encrypted Email")
        pgp_msg["Date"] = msg.get("Date")
        pgp_msg["Message-ID"] = msg.get("Message-ID")

        version_part = MIMEApplication("Version: 1\n", _subtype="pgp-encrypted")
        data_part = MIMEApplication(str(encrypted), _subtype="octet-stream")

        pgp_msg.attach(version_part)
        pgp_msg.attach(data_part)
    except Exception as e:
        print(f"[!] Error building PGP/MIME message for {file_path}: {e}")
        return False

    # Write to output .eml
    try:
        with open(output_path, 'w', encoding='utf-8') as out_file:
            gen = Generator(out_file)
            gen.flatten(pgp_msg)
        print(f"[+] Encrypted: {output_path}")
        return True
    except (OSError, UnicodeEncodeError) as e:
        print(f"[!] Error writing encrypted file {output_path}: {e}")
        return False

# Process all .eml files
try:
    if not os.path.exists(INPUT_DIR):
        print(f"[!] Error: Input directory {INPUT_DIR} does not exist")
        sys.exit(1)
    
    eml_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".eml")]
    
    if not eml_files:
        print(f"[!] No .eml files found in {INPUT_DIR}")
        sys.exit(0)
    
    print(f"[*] Found {len(eml_files)} .eml files to process")
    
    success_count = 0
    for filename in eml_files:
        src = os.path.join(INPUT_DIR, filename)
        dest = os.path.join(OUTPUT_DIR, filename)
        if encrypt_eml(src, dest):
            success_count += 1
    
    print(f"[*] Successfully encrypted {success_count}/{len(eml_files)} files")
    
except OSError as e:
    print(f"[!] Error accessing input directory {INPUT_DIR}: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[!] Unexpected error: {e}")
    sys.exit(1)
