# FUCK ZALO

A powerful Zalo chatbot, integrating many group management and utility features, built on the `zlapi` library.

## Installation

### Step 1: Prepare the environment
Requires Python 3.8 or later.

A virtual environment (virtualenv) is recommended for better library management.

```bash
# Create a virtual environment (Windows)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```
### Step 2: Install libraries
Install the necessary libraries from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```
### Step 3: Configuration
Create a `config.py` file in the root directory and fill in your account information:

```python
# config.py

# Zalo authentication information
IMEI = "YOUR_IMEI_HERE"
SESSION_COOKIES = "YOUR_SESSION_COOKIES_HERE"

# API Keys (if using external services)
API_KEY = ""
SECRET_KEY = ""

# Bot configuration
PREFIX = "..." # Command start character (e.g., .help, .menu)
ADMIN = "YOUR_ADMIN_ID" # Bot Admin ID
```

### Step 4: Run the Bot

```bash
python main.py
```

## 🧩 Zalo Extension (Recommended)
To make retrieving **IMEI** and **Cookies** easier and more professional, use the extension included in this project.

[**How to install Extension Zalo cookie (Material 3)**](./zlapi-extension-obfuscated/README.md)

## Basic Command List
nuh uh

## ⚠️ Important Note
- The bot runs on your personal Zalo account; use it carefully to avoid account suspension due to spam.

- Do not share the `config.py` file or Cookies/IMEI with others.

---
*Project maintained by Nguyen Hoang*