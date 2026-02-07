#!/usr/bin/env python3
"""
Interactive script to help set up Google Sheets authentication.
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_step(step_num, title):
    """Print a formatted step header."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print('='*60)


def main():
    """Guide user through Google Sheets setup."""
    print("\n🔧 Google Sheets Authentication Setup\n")
    print("This script will guide you through setting up Google Sheets access.")

    # Step 1: Create Google Cloud Project
    print_step(1, "Create Google Cloud Project")
    print("1. Go to: https://console.cloud.google.com")
    print("2. Click 'Create Project'")
    print("3. Enter a project name (e.g., 'vc-fund-bot')")
    print("4. Click 'Create'")
    input("\nPress Enter once you've created the project...")

    # Step 2: Enable Google Sheets API
    print_step(2, "Enable Google Sheets API")
    print("1. In the Google Cloud Console, click the hamburger menu (≡)")
    print("2. Go to 'APIs & Services' → 'Library'")
    print("3. Search for 'Google Sheets API'")
    print("4. Click on it and press 'ENABLE'")
    input("\nPress Enter once you've enabled the API...")

    # Step 3: Create Service Account
    print_step(3, "Create Service Account")
    print("1. Go to 'APIs & Services' → 'Credentials'")
    print("2. Click 'Create Credentials' → 'Service Account'")
    print("3. Enter a name (e.g., 'telegram-bot-sheets-access')")
    print("4. Click 'Create and Continue'")
    print("5. Skip the optional steps and click 'Done'")
    input("\nPress Enter once you've created the service account...")

    # Step 4: Create and Download Key
    print_step(4, "Create and Download JSON Key")
    print("1. In the Credentials page, find your service account")
    print("2. Click on it to open details")
    print("3. Go to the 'Keys' tab")
    print("4. Click 'Add Key' → 'Create new key'")
    print("5. Choose 'JSON' format")
    print("6. Click 'Create' - a JSON file will download")
    input("\nPress Enter once you've downloaded the JSON file...")

    # Step 5: Move the credentials file
    print_step(5, "Move Credentials File")

    # Create credentials directory
    creds_dir = "config/credentials"
    os.makedirs(creds_dir, exist_ok=True)

    print(f"\nPlease move your downloaded JSON file to:")
    print(f"  {os.path.abspath(creds_dir)}/google_service_account.json")

    while True:
        input("\nPress Enter once you've moved the file...")

        creds_file = os.path.join(creds_dir, "google_service_account.json")
        if os.path.exists(creds_file):
            print("✅ Credentials file found!")

            # Read and validate
            try:
                with open(creds_file) as f:
                    creds = json.load(f)

                service_account_email = creds.get("client_email")
                if service_account_email:
                    print(f"\n📧 Service Account Email: {service_account_email}")
                    break
                else:
                    print("❌ Invalid credentials file. Please try again.")
            except Exception as e:
                print(f"❌ Error reading credentials: {e}")
        else:
            print(f"❌ File not found at: {creds_file}")
            print("Please make sure the file is named 'google_service_account.json'")

    # Step 6: Share Google Sheets
    print_step(6, "Share Your Google Sheets")
    print(f"\nYou need to share your Google Sheets with the service account:")
    print(f"\n📧 Email: {service_account_email}")
    print("\nFor EACH of your Google Sheets:")
    print("1. Open the Google Sheet")
    print("2. Click 'Share' button")
    print("3. Paste the service account email above")
    print("4. Set permission to 'Viewer' (read-only)")
    print("5. Uncheck 'Notify people'")
    print("6. Click 'Share'")
    input("\nPress Enter once you've shared your sheets...")

    # Step 7: Get Sheet IDs
    print_step(7, "Get Google Sheet IDs")
    print("\nFor each sheet, get the Sheet ID from the URL:")
    print("URL format: https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit")
    print("\nYou need:")
    print("1. Fund Metrics Sheet ID")
    print("2. Portfolio Sheet ID")

    fund_sheet_id = input("\nEnter Fund Metrics Sheet ID: ").strip()
    portfolio_sheet_id = input("Enter Portfolio Sheet ID: ").strip()

    fund_range = input("Enter Fund Metrics range (e.g., 'Fund Performance!A1:Z100'): ").strip()
    portfolio_range = input("Enter Portfolio range (e.g., 'Portfolio!A1:Z100'): ").strip()

    # Step 8: Update .env file
    print_step(8, "Update Environment Variables")

    env_file = ".env"
    env_example = ".env.example"

    if not os.path.exists(env_file):
        # Create .env from .env.example
        if os.path.exists(env_example):
            with open(env_example) as f:
                env_content = f.read()

            # Update with values
            env_content = env_content.replace("your_google_sheet_id_here", fund_sheet_id)
            env_content = env_content.replace("Portfolio!A1:Z100", portfolio_range)

            # Update second sheet ID (for portfolio)
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('PORTFOLIO_SHEET_ID='):
                    lines[i] = f'PORTFOLIO_SHEET_ID={portfolio_sheet_id}'
                elif line.startswith('FUND_METRICS_RANGE='):
                    lines[i] = f'FUND_METRICS_RANGE={fund_range}'

            env_content = '\n'.join(lines)

            with open(env_file, 'w') as f:
                f.write(env_content)

            print(f"✅ Created {env_file} with your Google Sheets configuration")
        else:
            print(f"⚠️  {env_example} not found. Please create {env_file} manually")
    else:
        print(f"ℹ️  {env_file} already exists. Please update it manually with:")
        print(f"   FUND_METRICS_SHEET_ID={fund_sheet_id}")
        print(f"   FUND_METRICS_RANGE={fund_range}")
        print(f"   PORTFOLIO_SHEET_ID={portfolio_sheet_id}")
        print(f"   PORTFOLIO_RANGE={portfolio_range}")

    # Final summary
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file and add:")
    print("   - TELEGRAM_BOT_TOKEN")
    print("   - ALLOWED_TELEGRAM_IDS")
    print("   - OPENAI_API_KEY")
    print("\n2. Run the test script:")
    print("   python scripts/test_connections.py")
    print("\n3. Start the bot:")
    print("   python src/main.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
