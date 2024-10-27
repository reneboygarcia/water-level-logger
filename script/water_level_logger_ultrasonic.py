from prefect import task, flow
import RPi.GPIO as GPIO
import time
from oauth2client.service_account import ServiceAccountCredentials
from prefect.blocks.system import Secret
import json
import gspread

# Google sheets URL
secret_block_gsheets_url = Secret.load("google-sheets-url")
SHEET_URL = secret_block_gsheets_url.get()
SHEET_NAME = "Sheet3"  # change this as necessary

#  Setup GPIO
TRIG_PIN = 23
ECHO_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setwarnings(False)


@task(log_prints=True, name="get_distance")
def get_distance(temp=20):
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time
    sound_speed = 331.3 + 0.606 * temp
    distance = (time_elapsed * sound_speed) / 2  # Speed of sound is 343 m/s @ 20C
    return distance


@task(log_prints=True, name="get_credentials")
def get_credentials(block_name):
    secret_block = Secret.load(block_name)
    secret_value = secret_block.get()
    parsed_secret = json.loads(secret_value)
    return parsed_secret


@task(log_prints=True, name="initialize_gspread")
def initialize_gspread(sheet_url, sheet_name=None, sheet_index=None):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            get_credentials("google-sheets-credentials"), scopes=scope
        )
        client_email = creds.service_account_email
        print(f"Service account email: {client_email}")
        client = gspread.authorize(creds)

        # Open the spreadsheet by URL
        spreadsheet = client.open_by_url(sheet_url)

        # Open the sheet by name or index
        if sheet_name:
            sheet = spreadsheet.worksheet(sheet_name)
        elif sheet_index is not None:
            sheet = spreadsheet.get_worksheet(sheet_index)
        else:
            sheet = spreadsheet.sheet1  # Default to the first sheet

        # Check if the sheet is empty (no headers)
        if not sheet.get_all_values():
            # Add header row
            sheet.insert_row(["timestamp", "distance"], index=1)
            print("Added header row")

        return sheet
    except gspread.exceptions.SpreadsheetNotFound:
        print("Spreadsheet not found. Please check the sheet ID and permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@task(log_prints=True, name="log_to_sheets")
def log_to_sheets(distance, sheet):
    try:
        # Append data
        sheet.append_row([time.strftime("%Y-%m-%d %H:%M:%S"), distance])
    except Exception as e:
        print(f"An error occurred while logging to sheets: {e}")


@task(log_prints=True, name="water_level_logger")
def water_level_logger(sheet):
    distance = get_distance(temp=20)
    log_to_sheets(distance, sheet)


@flow(log_prints=True, name="run_water_level_logging")
def run_water_level_logging(sheet):
    start_time = time.time()
    end_time = start_time + 24 * 60 * 60  # 24 hours

    try:
        while time.time() < end_time:
            water_level_logger(sheet)
            time.sleep(300)  # Sleep for 5 minutes
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        GPIO.cleanup()


# Run Main
if __name__ == "__main__":
    sheet = initialize_gspread(SHEET_URL, sheet_name=SHEET_NAME)
    if sheet is None:
        print("Initialization of Google Sheets failed. Exiting...")
    else:
        run_water_level_logging(sheet)
