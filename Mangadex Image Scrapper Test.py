import os
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import argparse
import re

def argument_choice():
    """
    Function dedicated to being able to take the input from the user, whether be from the command line or from the python program directly.
    """
    parse = argparse.ArgumentParser(description="Script that allows a user to download all the possible chapters in a manga from Mangadex.org.")
    parse.add_argument('url', help="Enter the Mangadex URL", nargs="?", const=None, default=None)
    arguments = parse.parse_args()

    if arguments.url != None: #If the input is from command line
        answer = arguments.url
    else: #If the input is via python itself
        py_input = input("Enter the full URL from Mangadex: ")
        answer = py_input
    
    if re.match(r"(https:)//(mangadex).(com|org)/(chapter)/(\d{6})/(\d)", answer) is not None: #There is a valid URL
        return answer
    else:
        print("The page is not valid for scraping, please make sure the text is from mangadex's URL.")
        try:
            input("Press Enter to continue")
        except SyntaxError:
            pass
        exit()


def browser_shutdown(web_browser): # Closing Everything
    web_browser.close()
    web_browser.quit()

mangadex_url = argument_choice() # URL source for the manga 

driver = webdriver.Firefox() # Utilizing Firefox as the main driver
driver.get(mangadex_url) # Opening the URL of the manga
start_time = time.perf_counter() # Timer to find out how long this takes

# Fixing the settings to make it Long Scroll
driver.find_element_by_id('settings-button').click() # Goes to the Settings
driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div/div[2]/div[1]/div[4]/div/div/button[3]').click() # Clicks the Long Page
driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div/div[1]/button').click() # Closes the settings

# Page Loading and Jumping
total_manga_pages = int(driver.find_element_by_class_name('total-pages').text) # Get the total amount of pages.
current_manga_pages = int(driver.find_element_by_class_name('current-page').text) # Get the current page from the jump
while current_manga_pages < total_manga_pages: # Keeps scrolling down till it satisfies the condition
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1.5)
    current_manga_pages = int(driver.find_element_by_class_name('current-page').text) # Get the current page from the jump
print(f"Loaded {current_manga_pages} pages our of {total_manga_pages}.\n")
time.sleep(2)

# The Beautiful Soup Scraping Section
html_source = driver.page_source
browser_shutdown(driver) # Closes the Browser, we won't be needing it
soup = BeautifulSoup(html_source, 'html.parser')

# Laddering Down Pt 1: For the images
body = soup.body
content = body.find('div', id='content')
main_row = content.find('div', class_='reader-main col row no-gutters flex-column flex-nowrap noselect')
manga_scraping_zone = main_row.find('div', class_='reader-images col-auto row no-gutters flex-nowrap m-auto text-center cursor-pointer directional')

# Laddering Down Pt 2: For the title
content_2 = content.find('div', class_='container reader-controls-container p-0')
content_3 = content_2.find('div', class_='reader-controls-wrapper bg-reader-controls row no-gutters flex-nowrap')
content_4 = content_3.find('div', class_='reader-controls col row no-gutters flex-column flex-nowrap')
content_5 = content_4.find('div', class_='reader-controls-title col-auto text-center p-2')
content_6 = content_5.find('div', style='font-size:1.25em')
title = content_6.find('a', class_='manga-link')['title']
print(title)

# Folder Creating for the Images to be saved
character_source = (title)
try:
    os.mkdir(character_source) # Makes the directory of the title, the directory is placed where the script was exectuted.
    print("Directory " , character_source ,  " has been created.\n") 
except FileExistsError:
    print("Directory " , character_source ,  " already exists.\n")

for manga_images in manga_scraping_zone.find_all('div', class_='reader-image-wrapper col-auto my-auto justify-content-center align-items-center noselect nodrag row no-gutters'):
    x = manga_images.find('img', class_='noselect nodrag cursor-pointer')['src']
    print(x)
    filename = x.split('/')
    if os.path.exists(f"{character_source}\\" + filename[5]):
        print("File already Exist.\n")
    else:
        # The downloading segment.
        print("Downloading...\n")
        second_request = requests.get(x)
        with open(f"{character_source}\\" + filename[5], 'wb') as f:
            f.write(second_request.content)

# End of the line.
end_time = time.perf_counter()
print(f"all possible images have successfully been downloaded in {round(end_time-start_time, 2)} seconds.")
end = input("Press Enter to end the program \n")