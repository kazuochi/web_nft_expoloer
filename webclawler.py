import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import Select

# First create screenshots directory if it doesn't exist
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

# Setup webdriver (this is for Firefox, but you can use Chrome or others)
driver = webdriver.Chrome(service=Service('./chromedriver'))

# Use a queue to avoid stack overflow from recursion
queue = deque(["?id=bef14019056992a29a863b717e0d815f"])
IDs = set()  # Use a set to avoid duplicate IDs

while queue and len(IDs) < 1000:
    id_ = queue.pop()
    url = "https://web.leegte.org/" + id_
    IDs.add(id_)  # add the id to the IDs set
    
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Save the screenshot
    driver.save_screenshot(f'screenshots/{id_[4:]}.png')  # Save screenshot with ID as name
    
    # Extract all links with IDs on this page
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']
        # check if the link is already visited by looking into the IDs set 
        if href.startswith("?id=") and href not in IDs:
            queue.append(href)
    
    # Handle dropdown
    dropdown_index = 0
    while True:
        dropdown_elements = driver.find_elements(By.TAG_NAME, "select")
    
        # Break out of the loop if we've processed all dropdowns
        if dropdown_index >= len(dropdown_elements):
            break
    
        dropdown = dropdown_elements[dropdown_index]
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
                break  # break after clicking one option, as we need to refetch the dropdown and its options
    
        # Move on to the next dropdown
        dropdown_index += 1

    # Handle radio buttons
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



# Save IDs to a file
with open('ids.txt', 'w') as f:
    for id_ in IDs:
        f.write(id_[4:] + '\n')  # Save ID without "?id=" part

driver.quit()

print("Done crawling!")