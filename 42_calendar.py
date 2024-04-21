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
from getpass import getpass
from pynput.keyboard import Listener, Key

slot_check_counter = 0 

def big_random_delay(min=2, max=5):
    sleep(random.uniform(min, max))


def tiny_random_delay(min=0.2, max=0.5):
    sleep(random.uniform(min, max))

def is_time_in_range(slot_time_str, start_time, end_time):
    slot_time = datetime.strptime(slot_time_str, "%H:%M").time()
    return start_time <= slot_time <= end_time



def login(driver, calendar_url, email, password):
    print("Navigating to the calendar URL...")
    driver.get(calendar_url)
    big_random_delay()
    
    try:
        if WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/users/sign_out']"))):
            print("Already logged in.")
            return True
    except TimeoutException:
        print("Not already logged in, proceeding with login.")

    try:
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
    except TimeoutException:
        print("Login page did not load or already logged in.")
        return True  # Assume true because you might be already logged in.

    try:
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        print("Entering login credentials...")
        username_input.send_keys(email)
        big_random_delay()
        password_input.send_keys(password)
        big_random_delay()
        submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type=submit]')
        print("Submitting login form...")
        submit_button.click()

        two_fa_enabled = input("Is Two-Factor Authentication enabled? (y/n): ").lower().startswith('y')
        if two_fa_enabled:
            print("Please complete the Two-Factor Authentication process.")
            print("Press Enter when completed, or wait for the timeout.")
            input()
            print("Assuming 2FA is completed successfully.")
            return True

        WebDriverWait(driver, 5).until(
            EC.url_contains(calendar_url)
        )
        print("Login successful, redirected to calendar page.")
        return True
    except NoSuchElementException:
        print("Login elements not found. Possibly already logged in.")
        return True
    except TimeoutException:
        print("Failed to redirect after login.")
        return False


def parse_user_timeblock():
    day_input = input("Enter the day for the booking (e.g., '2024-03-21'): ")
    start_time_input = input("Enter the start time (HH:MM, 24-hour format): ")
    end_time_input = input("Enter the end time (HH:MM, 24-hour format): ")
    day = datetime.strptime(day_input, "%Y-%m-%d").date()
    start_time = datetime.strptime(start_time_input, "%H:%M").time()
    end_time = datetime.strptime(end_time_input, "%H:%M").time()
    return day, start_time, end_time




def check_for_slots(driver, day, start_time, end_time, re_enter_flag):
    global slot_check_counter
    print(f"Checking for available slots on {day} from {start_time} to {end_time}...")
    if re_enter_flag(): return 
    if slot_check_counter % 2 == 0:
        driver.refresh()
        print("Page refreshed to update slots.")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-time]"))
    )
    slot_check_counter += 1 
    try:
        available_slots_elements = driver.find_elements(By.CSS_SELECTOR, f"[data-date='{day}'] [data-time]")
        if not available_slots_elements:
            print("No slots currently displayed for this date.")
            return

        for slot_element in available_slots_elements:
            if re_enter_flag(): return
            slot_time_str = slot_element.get_attribute('data-time')
            if slot_time_str and is_time_in_range(slot_time_str, start_time, end_time):
                print(f"Attempting to book slot at {slot_time_str}...")
                slot_element.click()
                tiny_random_delay()
                handle_confirmation_popup(driver)
                print(f"Slot booked at {slot_time_str}")
                return

    except NoSuchElementException:
        print("No available slots found.")


def handle_confirmation_popup(driver):
    try:
        popup = WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        popup.accept()
    except:
        pass  

def find_chrome_profile_path():
    home_dir = os.path.expanduser("~")
    chrome_config_path = os.path.join(home_dir, '.config', 'google-chrome')
    profile_names = ['Profile 4', 'Default', 'Profile 1', 'Profile 2', 'Profile 3']

    for profile_name in profile_names:
        chrome_profile_dir = os.path.join(chrome_config_path, profile_name)
        if os.path.exists(chrome_profile_dir):
            print(f"Found Chrome profile at {chrome_profile_dir}")
            return chrome_profile_dir

    print(f"No valid Chrome profile directory found in the usual path: {chrome_config_path}")
    custom_path = input("Please enter the path to your Chrome profile directory or press enter to continue with default: ").strip()
    if custom_path:
        if os.path.exists(custom_path):
            print(f"Found Chrome profile at {custom_path}")
            return custom_path
        else:
            print("The path provided does not exist. Please check the path and try again.")
            return None
    else:
        print("Proceeding with default Chrome configuration...")
        return None

def get_user_credentials():
    calendar_url = input("Please enter the calendar URL: ")
    email = os.getenv('INTRAUSER') or input("Enter INTRAUSER (your username or email): ")
    password = os.getenv('INTRAPASS') or getpass("Enter INTRAPASS (your password): ")
    return calendar_url, email, password

def setup_selenium_options():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    profile_path = find_chrome_profile_path()
    if profile_path:
        print(f"Using Chrome profile at {profile_path}")
        options.add_argument(f"user-data-dir={profile_path}")
    else:
        print("No valid Chrome profile directory found. Using default configuration...")
    return options

def main():
    calendar_url, email, password = get_user_credentials()
    options = setup_selenium_options()
    driver = webdriver.Chrome(options=options)

    login_success = login(driver, calendar_url, email, password)
    re_enter_time_block = False

    if login_success:
        day, start_time, end_time = parse_user_timeblock()
        print("\nPress 'r' at any time to re-enter the time block.\n")
        print("It can take a while for selenium to stop !.\n")

        def on_press(key):
            nonlocal re_enter_time_block
            if hasattr(key, 'char') and key.char == 'R':
                print("Re-entering the time block... R pressed !")
                re_enter_time_block = True

        listener = Listener(on_press=on_press)
        listener.start()
        try:
            while True:
                if re_enter_time_block:
                    print("Re-entering the time block...")
                    day, start_time, end_time = parse_user_timeblock()
                    print("\nUpdated time block. Press 'R' at any time to re-enter the time block.\n")
                    re_enter_time_block = False

                check_for_slots(driver, day, start_time, end_time, lambda: re_enter_time_block)
                sleep(1)  # Loop checking delay
        except Exception as e:
            print(f"An error occurred: {e}")

    else:
        print("Login failed. Please check your credentials or network connection.")

    driver.quit()
    listener.stop()


if __name__ == "__main__":
    main()