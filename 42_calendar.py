import curses
from getters import get_user_credentials
from curses import wrapper
import random
from time import sleep
from utils import tiny_random_delay
from utils import big_random_delay
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import random
from getpass import getpass
from pynput.keyboard import Listener, Key
import requests
from getters import get_timeblock
from getters import get_chrome_profile_path

slot_check_counter = 0 


def check_for_slots(driver, day, start_time, end_time, re_enter_flag, stdscr):
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
    except TimeoutException:
        print("Timeout occurred while waiting for the necessary elements to load.")

def login(driver, calendar_url, email, password, stdscr):
    print("Navigating to the calendar URL...")
    driver.get(calendar_url)
    big_random_delay()
    
    try:
        if WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/users/sign_out']"))):
            print("Already logged in.")
            return True
    except TimeoutException:
        print("Already logged in, proceeding with login.")

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

def handle_confirmation_popup(driver):
    try:
        popup = WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        popup.accept()
    except:
        pass  

def setup_selenium_options():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    profile_path = get_chrome_profile_path()
    if profile_path:
        print(f"Using Chrome profile at {profile_path}")
        options.add_argument(f"user-data-dir={profile_path}")
    else:
        print("No valid Chrome profile directory found. Using default configuration...")
    return options

def main(stdscr):
    curses.curs_set(0)
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(False)
    stdscr.clear()
    calendar_url, email, password = get_user_credentials(stdscr)

    # Initialize Selenium
    options = setup_selenium_options()
    driver = webdriver.Chrome(options=options)

    # Attempt login
    login_success = login(driver, calendar_url, email, password, stdscr)

    if login_success:
        day, start_time, end_time = get_timeblock(stdscr)
        stdscr.addstr(14, 0, "Press 'r' at any time to re-enter the time block.")
        
        re_enter_time_block = False

        while True:
            try:
                if stdscr.getch() == ord('r'):
                    day, start_time, end_time = get_timeblock(stdscr)

                check_for_slots(driver, day, start_time, end_time, lambda: re_enter_time_block, stdscr)
                time.sleep(1)  # Loop checking delay
            except Exception as e:
                stdscr.addstr(16, 0, f"An error occurred: {e}")
                break

    else:
        stdscr.addstr(16, 0, "Login failed. Please check your credentials or network connection.")

    driver.quit()
    stdscr.getch()  # Wait for user to press a key

wrapper(main)