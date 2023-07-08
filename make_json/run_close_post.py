from package.close_post_function import *
from package.check_connection import ping
import time 


def check_internet_then_run_selenium(d,url,scrap_day):  #check internet before run selenium
    if ping() is True:  #if can connect to facebook
                get_text_facebook(d,url,scrap_day)
    else:                       #if cant connect to facebook
            print("No internet connection will try to run selenium again in 5 mins.")
            time.sleep(300)
            check_internet_then_run_selenium(d,url,scrap_day)


year = db.reference("/scraper")
##get in to all path and recheck the data in that path by get_text_facebook(d,url)
for y in year.get(): #Year
    month = db.reference(f"/scraper/{y}")
    for m in month.get():  #Month
        day = db.reference(f"/scraper/{y}/{m}")
        for d in day.get(): #day
            url = db.reference(f"/scraper/{y}/{m}/{d}/post_url").get()
            scrap_day = db.reference(f"/scraper/{y}/{m}/{d}/scrap_day").get()

            if scrap_day == None: #if the data doest have scrapday variable(old data)
                scrap_day = "2023-03-20"  ##scrap_day="2023-03-22" permenemt var

            check_internet_then_run_selenium(d,url,scrap_day)

print("Done checking closed post")




