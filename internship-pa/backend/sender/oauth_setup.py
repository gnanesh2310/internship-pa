"""
One-time script to get Gmail OAuth refresh tokens.
Run this ONCE on your local machine:
    python oauth_setup.py

It will open a browser, ask you to log in to Gmail,
then print the refresh token to store in your .env
"""
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_refresh_token(account_label: str, client_id: str, client_secret: str) -> str:
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)
    print(f"\n{'='*60}")
    print(f"✓ Refresh token for {account_label}:")
    print(creds.refresh_token)
    print(f"{'='*60}\n")
    return creds.refresh_token

if __name__ == "__main__":
    client_id = input("Enter your OAuth Client ID: ").strip()
    client_secret = input("Enter your OAuth Client Secret: ").strip()

    print("\n--- Authorising Company Email (kgnanesh98@gmail.com) ---")
    print("A browser will open. Log in with kgnanesh98@gmail.com")
    input("Press Enter to continue...")
    company_token = get_refresh_token("kgnanesh98@gmail.com", client_id, client_secret)

    print("\n--- Authorising Research Email (kgnanesh52@gmail.com) ---")
    print("A browser will open. Log in with kgnanesh52@gmail.com")
    input("Press Enter to continue...")
    research_token = get_refresh_token("kgnanesh52@gmail.com", client_id, client_secret)

    print("\nAdd these to your backend/.env file:")
    print(f"GMAIL_CLIENT_ID={client_id}")
    print(f"GMAIL_CLIENT_SECRET={client_secret}")
    print(f"GMAIL_COMPANY_REFRESH_TOKEN={company_token}")
    print(f"GMAIL_RESEARCH_REFRESH_TOKEN={research_token}")
