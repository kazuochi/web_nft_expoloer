import os
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import deque
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Constants
SCREENSHOTS_DIR = 'screenshots'
INITIAL_URL = "?id=e744528e2ca1556e16a28088b7b290c2"
BASE_URL = "https://web.leegte.org/"
MAX_IDS = 1000

# Create screenshots directory if it doesn't exist
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)

# Setup webdriver
driver = webdriver.Chrome(service=Service('./chromedriver'))

# Initialize the queue and IDs set
queue = deque([INITIAL_URL])
IDs = set()


def handle_links():
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if href.startswith("?id=") and href not in IDs:
            queue.append(href)


def handle_dropdowns():
    processed_dropdowns = set()
    dropdown_index = 0

    while True:
        dropdown_elements = driver.find_elements(By.TAG_NAME, "select")

        if dropdown_index >= len(dropdown_elements):
            break  # No more dropdowns to process

        dropdown = dropdown_elements[dropdown_index]
        dropdown_outerHTML = dropdown.get_attribute('outerHTML')

        if dropdown_outerHTML not in processed_dropdowns:
            original_url = driver.current_url  # Remember the original URL
            options = dropdown.find_elements(By.TAG_NAME, "option")
    
            # Click on the first non-selected option
            for option in options:
                if not option.is_selected():
                    option.click()
                    time.sleep(2)
                
                    current_url = driver.current_url
                    current_id = "?id=" + current_url.rsplit('=', 1)[-1]
                    if current_id not in IDs:
                        print("ID added from dropdown.")
                        queue.append(current_id)
                        IDs.add(current_id)
                
                    # Navigate back to the original page
                    driver.get(original_url)
                    time.sleep(2)
                    break  # break after clicking one option
    
            # Mark this dropdown as processed
            processed_dropdowns.add(dropdown_outerHTML)

        dropdown_index += 1




def handle_radio_buttons():
    processed_divs = set()
    radio_index = 0

    while True:
        radio_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
    
        if radio_index >= len(radio_elements):
            break  # Exit the loop if no more radio buttons are found
    
        radio_button = radio_elements[radio_index]
    
        # Get the immediate parent of the radio button
        parent_div = radio_button.find_element(By.XPATH, "./..")
        div_outer_html = parent_div.get_attribute('outerHTML')
    
        if not radio_button.is_selected() and div_outer_html not in processed_divs:
            original_url = driver.current_url  # Remember the original URL
        
            try:
                driver.execute_script("arguments[0].click();", radio_button)
            
                time.sleep(2)
            
                current_url = driver.current_url
                current_id = "?id=" + current_url.rsplit('=', 1)[-1]
                if current_id not in IDs:
                    print("ID added from radio button.")
                    queue.append(current_id)
                    IDs.add(current_id)
                
                # Navigate back to the original page
                driver.get(original_url)
                time.sleep(2)
            
            except Exception as e:
                print(f"Failed to click radio button: {str(e)}")
        
            # Add this div to the processed set
            processed_divs.add(div_outer_html)
    
        # Move on to the next radio button
        radio_index += 1



def handle_text_fields():
    processed_inputs = set()  # To keep track of text fields that have been clicked

    while True:  # Continue until no input fields are left to handle
        input_elements = driver.find_elements(By.CSS_SELECTOR, 'div.container input[type="text"]')

        if not input_elements:
            break  # If no input fields are left, exit the loop

        # Filter out already clicked input fields
        input_elements = [inp for inp in input_elements if inp.get_attribute('outerHTML') not in processed_inputs]

        if not input_elements:
            break  # If all input fields on the page have been clicked, exit the loop

        input_field = input_elements[0]  # Interact with the first unclicked input field
        original_url = driver.current_url  # Remember the current URL before interaction
        outerHTML = input_field.get_attribute('outerHTML')
        
        try:
            driver.execute_script("arguments[0].click();", input_field)
            time.sleep(2)

            current_url = driver.current_url
            current_id = "?id=" + current_url.rsplit('=', 1)[-1]
            if current_id not in IDs:
                print("ID added from text field interaction.")
                queue.append(current_id)
                IDs.add(current_id)

            # Mark this input field as processed
            processed_inputs.add(outerHTML)

            # Navigate back to the original page
            driver.get(original_url)
            time.sleep(2)
        except Exception as e:
            print(f"Failed to click text input field: {str(e)}")




def handle_buttons():
    processed_buttons = set()

    while True:
        button_elements = driver.find_elements(By.CSS_SELECTOR, 'div.container button')
        button_elements = [btn for btn in button_elements if btn.get_attribute('outerHTML') not in processed_buttons]

        if not button_elements:
            break  # If all buttons on the page have been clicked, exit the loop

        # Let's just reference the first button in the list
        button = button_elements[0]
        original_url = driver.current_url  # Remember the current URL before interaction
        outerHTML = button.get_attribute('outerHTML')

        try:
            driver.execute_script("arguments[0].click();", button)
            
            current_url = driver.current_url
            current_id = "?id=" + current_url.rsplit('=', 1)[-1]
            if current_id not in IDs:
                print("ID added from button click.")
                queue.append(current_id)
                IDs.add(current_id)

            processed_buttons.add(outerHTML)
            
            # Navigate back to the original page
            driver.get(original_url)
            time.sleep(2)
        except Exception as e:
            print(f"Failed to click button: {str(e)}")





while queue and len(IDs) < MAX_IDS:
    id_ = queue.pop()
    driver.get(BASE_URL + id_)
    IDs.add(id_)

    # Save the screenshot
    driver.save_screenshot(f'{SCREENSHOTS_DIR}/{id_[4:]}.png')

    handle_links()
    handle_dropdowns()
    handle_radio_buttons()
    handle_buttons()
    handle_text_fields()

# Save IDs to a file
with open('ids.txt', 'w') as f:
    for id_ in IDs:
        f.write(id_[4:] + '\n')

driver.quit()
print("Done crawling!")
