from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def find_index(list_to_find,key):
    return [idx for idx, value in enumerate(list_to_find) if value == key]


def get_post_text_comment(url_link ):
    driver = webdriver.Edge()
    time.sleep(2)

    ##OPEN URL
    driver.get(url_link)

    ##get username who post 
    keys=driver.find_element(By.XPATH,"//div[@class='_4g34']/h3[@class='_52jd _52jb _52jh _5qc3 _4vc- _3rc4 _4vc-']/span/strong")
    key = keys.text
    print(f"====\nUsername that posted:{key}\n====")

    #program to parse user name who posted comment
    def Name_Comment_parse():
        ##GET USERNAME THAT COMMENT
        names = driver.find_elements(By.CLASS_NAME,'_2b05')
        for name in names: 
            name=name.text
            Name.append(name)
        
        Duplicate_Name = find_index(Name,key)
            
        ##GET COMMENT by index of name
        comments=driver.find_elements(By.XPATH,"//div[@class='_2b06']/div[@data-sigil='comment-body']")
        for i in Duplicate_Name:
            try:
                if Name[i] == key:
                    comment=comments[i].text
                    Comment.append(comment)
            except:
                continue

    def get_post_text(url_link ):
        post_text=driver.find_element(By.XPATH,"//div[@class='_5rgt _5nk5']/div/p")
        return post_text.text           
    
    #Program to scrap comments from each page
    Name=[]
    Comment=[]
    post_text = get_post_text(url_link )
    Name_Comment_parse()
    print(f"Comments:: {Comment}")  #print all comment that post owner commented
    return {"post":post_text ,"comment":"".join(Comment)} #will return as str by joining all data in Comment_List
