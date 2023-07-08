from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from function import add_data_to_csv_with_deepcut

count=0
driver = webdriver.Edge()

##OPEN URL
url_link = "https://www.facebook.com/groups/197822284350539/posts"

driver.get(url_link)
time.sleep(50)
def get_comment_facebooks():
    ##get username who post 
    keys=driver.find_elements(By.XPATH,"//div[@class='x1iorvi4 x1pi30zi x1l90r2v x1swvt13']")
    for key in keys:
        key = key.text
        if key != "":
            add_data_to_csv_with_deepcut(key,3)
            print(f"====\nposted:{key}\n====")

SCROLL_PAUSE_TIME = 5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    get_comment_facebooks()
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height