# Email-Encryption

Bulk encrypt your `.eml` email files on Windows using GPG (Gpg4win) and Python.

## 📂 Repository Structure

```
Email-Encryption/         # Project root (Git repo)
├── .env                  # Your PGP key configuration
├── LICENSE               # Project license
├── README.md             # This guide
├── emails/               # Input folder for plaintext .eml files
│   └── README.md         # Notes on email placement
├── encrypted/            # Output folder for encrypted .eml files
│   └── README.md         # Notes on encrypted files
├── scripts/
│   └── encrypt_eml.py    # Main Python encryption script
└── .git/                 # Git metadata (ignore)
```

## 1. Prerequisites

* **Windows 10/11**
* **Python 3.x** ([https://www.python.org/downloads/](https://www.python.org/downloads/)) with **Add to PATH** enabled.
* **Gpg4win** ([https://gpg4win.org](https://gpg4win.org)) for GPG tools and key management.

## 2. Install and Configure Gpg4win

1. Download and install **Gpg4win**, accepting default components (GnuPG, Kleopatra).
2. Open **System Properties → Environment Variables**.
3. Under **System variables**, edit **Path** and add two entries:

   * `C:\Program Files (x86)\Gpg4win\bin`
   * `C:\Program Files (x86)\GnuPG\bin`
4. Click **OK** to apply.
5. Verify in PowerShell/CMD:

   ```powershell
   gpg --version
   ```
6. Run `kleopatra.exe` and import or create your PGP keys.

## 3. Python Dependencies

All required Python packages are pinned in `requirements.txt` for easy setup and reproducibility. From the project root, run:

```powershell
pip install -r requirements.txt
```

## 4. Configure Your .env

At the project root, edit `.env` to include your PGP key ID or email:

```dotenv
# Set this to your own GPG key (email or key ID)
SELF_KEY=your@emailaddress.here
```

## 5. Prepare Your Emails

* Place all plaintext `.eml` files into the `emails/` directory.
* The script will process every `*.eml` found there.

## 6. Run the Encryption Script

1. Open PowerShell/CMD and navigate to the scripts folder:

   ```powershell
   cd path\to\Email-Encryption\scripts
   ```
2. Execute:

   ```powershell
   python encrypt_eml.py
   ```
3. Encrypted files will be created in `../encrypted/` with the same filenames.

## 7. Verify Decryption in Thunderbird

1. Open Thunderbird, go to **Local Folders**.
2. Drag and drop the encrypted `.eml` files from `encrypted/`.
3. Thunderbird’s OpenPGP built-in support will prompt for your passphrase and render the decrypted content.

---

© 2025 Lupton Consulting Inc., LLP. Licensed under the terms in `LICENSE`. Feel free to customize and extend.
