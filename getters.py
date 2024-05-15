# File: credentials.py
import curses
import requests
from utils import big_random_delay
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import datetime
import os

def get_timeblock(stdscr, input_y, input_x):
    input_y += 7
    stdscr.addstr(input_y, input_x, "Enter the day for the booking (e.g., '2024-03-21'): ")
    day_input = stdscr.getstr(input_y + 1, input_x).decode().strip()
    stdscr.addstr(input_y + 2, input_x, "Enter the start time (HH:MM, 24-hour format): ")
    start_time_input = stdscr.getstr(input_y + 2, input_x + len( "Enter the start time (HH:MM, 24-hour format): ") + 1).decode().strip()
    stdscr.addstr(input_y + 4, input_x, "Enter the end time (HH:MM, 24-hour format): ")
    end_time_input = stdscr.getstr(input_y + 4, input_x + len( "Enter the end time (HH:MM, 24-hour format): ") + 1).decode().strip()

    day = datetime.datetime.strptime(day_input, "%Y-%m-%d").date()
    start_time = datetime.datetime.strptime(start_time_input, "%H:%M").time()
    end_time = datetime.datetime.strptime(end_time_input, "%H:%M").time()

    stdscr.refresh()
    return day, start_time, end_time


def get_user_credentials(stdscr):
    curses.echo()
    input_y, input_x = stdscr.getmaxyx()
    input_y //= 4
    input_x //= 5

    stdscr.clear()
    header = "Calendar Slot Booking System"
    description = "Please enter the required details to start the slot booking process."
    stdscr.addstr(1, 5, header, curses.A_BOLD)  # Applying bold attribute
    stdscr.addstr(3, 5, description)

    stdscr.addstr(input_y, input_x, "Enter the calendar URL: ")
    url = stdscr.getstr(input_y, input_x + len("Enter the calendar URL: ") + 1).decode().strip()
    valid_url = False
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            stdscr.addstr(input_y + 3, input_x, "Valid URL.            ")
            valid_url = True
        else:
            stdscr.addstr(input_y + 3, input_x, "Non-successful status. Press 'r' to retry.")
            stdscr.getch()
    except requests.exceptions.RequestException as e:
        stdscr.addstr(input_y + 3, input_x, f"Error: {str(e)}. Press 'r' to retry.")
    if not valid_url:
        stdscr.addstr(input_y + 5, input_x, "Press 'r' to retry URL or 'c' to continue with invalid URL.")
        key = stdscr.getch()
        if key == ord('r'):
            return get_user_credentials(stdscr)
    stdscr.addstr(input_y + 5, input_x, "Enter INTRAUSER (your username or email): ")
    email = stdscr.getstr(input_y + 5, input_x + len("Enter INTRAUSER (your username or email): ") + 1).decode().strip()
    stdscr.addstr(input_y + 8, input_x, "Enter INTRAPASS (your password): ")
    password = stdscr.getstr(input_y + 8, input_x +  len("Enter INTRAPASS (your password): ") + 1).decode().strip()
    stdscr.refresh()
    curses.noecho()
    return url, email, password

def get_chrome_profile_path():
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