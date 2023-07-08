from make_json.package.check_connection import ping
from datetime import datetime
import time
import os
import schedule


def countdown():
    t=300
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
      

def run_scrap():
    if(ping()==True): #if doest have network problem like no internet, facebook server offline
        for i in range(3,0,-1): #range(start,stop,step)
            print(f"Start Scaping in {i} Second(s).")
            time.sleep(1)
        os.system('python make_json/main_ai.py')
        os.system('python make_json/run_close_post.py')
       
        # now = datetime.now() #get time to save last update time
        # current_time = now.strftime("%a %d %b %Y %H:%M")
        # update_time_to_firebase(current_time)
        
    else:   #have network problem
        os.system('cls') #clear screen
        print("\nTaking a break 5 mins. facebook.com can't be reach.\n")
        countdown() #count down & sleep for 5 mins
        run_scrap()  


schedule.every().day.at("06:00").do(run_scrap)
schedule.every().day.at("18:00").do(run_scrap)
schedule.every().day.at("06:53").do(run_scrap)



while True:
    schedule.run_pending()
    time.sleep(1)        
