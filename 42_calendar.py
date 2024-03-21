import random
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import random
import os

def random_delay(min=3, max=7):
    sleep(random.uniform(min, max))

def login(calendar_url, email, password):
    driver.get(calendar_url)
    random_delay()
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
    except TimeoutException:
        print("Login page did not load in time")
        return

    # Locate the form elements
    random_delay()
    username_input = driver.find_element(By.ID, 'username')
    random_delay()
    password_input = driver.find_element(By.ID, 'password')
    random_delay() 

    # Enter your login credentials
    username_input.send_keys(email)
    random_delay() 
    password_input.send_keys(password)
    random_delay() 
    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type=submit]')
    random_delay() 
    submit_button.click()

    # Wait for the redirect to the calendar page
    WebDriverWait(driver, 10).until(
        EC.url_contains(calendar_url)
    )

def parse_user_input():
    day_input = input("Enter the day for the booking (e.g., '2024-03-21'): ")
    start_time_input = input("Enter the start time (HH:MM, 24-hour format): ")
    end_time_input = input("Enter the end time (HH:MM, 24-hour format): ")
    
    # Parse the user input
    day = datetime.strptime(day_input, "%Y-%m-%d").date()
    start_time = datetime.strptime(start_time_input, "%H:%M").time()
    end_time = datetime.strptime(end_time_input, "%H:%M").time()

    return day, start_time, end_time


def check_for_slots(day, start_time, end_time):
    random_delay() 
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-time]"))
    )

    try:
        available_slots_elements = driver.find_elements(By.CSS_SELECTOR, f"[data-date='{day}'] [data-time]")

        for slot_element in available_slots_elements:
            slot_time_str = slot_element.get_attribute('data-time')
            if slot_time_str and is_time_in_range(slot_time_str, start_time, end_time):
                slot_element.click()
                handle_confirmation_popup()
                seen_slots.add(slot_time_str)
                print(f"Slot booked at {slot_time_str}")
                return

    except NoSuchElementException:
        print("No available slots found.")

def handle_confirmation_popup():
    try:
        popup = WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        popup.accept()
    except:
        pass  

def find_chrome_profile_path():
    home_dir = os.path.expanduser("~")
    profile_names = ['Profile 4', 'Default', 'Profile 1', 'Profile 2', 'Profile 3']
    for profile_name in profile_names:
        chrome_profile_dir = os.path.join(home_dir, '.config', 'google-chrome', profile_name)
        if os.path.exists(chrome_profile_dir):
            return chrome_profile_dir
    default_profile_dir = os.path.join(home_dir, '.config', 'google-chrome', 'Default')
    if os.path.exists(default_profile_dir):
        return default_profile_dir
    print("Chrome profile directory not found.")
    return None



# Get Credentials
calendar_url = input("Please enter the calendar URL: ")
email = os.getenv('INTRAUSER')
if not email:
    email = input("Enter INTRAUSER (your username or email): ")
password = os.getenv('INTRAPASS')
if not password:
    password = input("Enter INTRAPASS (your password): ")
options = Options()
profile_path = find_chrome_profile_path()
print(f"Using Chrome profile at {profile_path}")
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=options)
login(calendar_url, email, password)

# Main Execution
day, start_time, end_time = parse_user_input()
while True:
    check_for_slots(day, start_time, end_time)
    sleep(3)

driver.quit()
