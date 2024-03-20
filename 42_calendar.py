import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

options = Options()
driver = webdriver.Chrome(options=options)

def login(calendar_url, email, password):
    driver.get(calendar_url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
    except TimeoutException:
        print("Login page did not load in time")
        return

    # Locate the form elements
    username_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')

    # Enter your login credentials
    username_input.send_keys(email)
    password_input.send_keys(password)

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type=submit]')
    submit_button.click()

    # Wait for the redirect to the calendar page
    WebDriverWait(driver, 10).until(
        EC.url_contains(calendar_url)
    )

seen_slots = set()  # This set will keep track of slots we have already seen
def check_for_slots():

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-time]"))
    )

    try:
        available_slots_elements = driver.find_elements(By.CSS_SELECTOR, "[data-time] .class-indicating-availability")

        new_slots = []
        for slot_element in available_slots_elements:
            slot_time = slot_element.get_attribute('data-time')
            if slot_time not in seen_slots:
                seen_slots.add(slot_time)
                new_slots.append(slot_time)
        
        if new_slots:
            print("New available slots found:")
            for slot_time in new_slots:
                print(f"Available slot at {slot_time}")

    except NoSuchElementException:
        print("No available slots found.")


# Calendar URL and credentials (replace with your actual information)
calendar_url = 'https://projects.intra.42.fr/projects/42cursus-minishell/slots?team_id=5593867'


print("Export the envs INTRAUSER and INTRAPASS with your 42 credentials")
print("Only for this shell session!")
# Get the username and password from environment variables
email = os.getenv('INTRAUSER')
password = os.getenv('INTRAPASS')
if not email or not password:
    print("Email or password environment variable is not set.")

# Start by logging in
login(calendar_url, email, password)

while True:
    check_for_slots()
    time.sleep(3)

driver.quit()
