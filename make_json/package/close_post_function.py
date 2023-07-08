from package.nlp_function import *
from package.firebase_function import send_error,db,remove_data_in_firebase,get_curr_day
from package.scrap_function import set_lower
from package.selenium_function import get_post_text_comment
from package.check_connection import ping
from datetime import datetime


def check_internet_then_delete(target_time):   #check internet before delete data
    import time
    if ping() is True:
          remove_data_in_firebase(target_time)
    else:
        print("No internet connection will try to delete again in 5 mins.")
        time.sleep(300)
        check_internet_then_delete(target_time)


def diff_of_days(marked_day):    #post day durations maxage = 60 days
    day_duration = (get_curr_day()-marked_day).days
    print(f"Day durations :{day_duration} day(s)")
    if day_duration >= 60:
         print("Time Expried.")
         return True
    else:
         print("Time Unexpried.")
         return False


##Get text and use deepcut to split the word and check text 
def get_text_facebook(time,URL,scrap_day):
        try:
                print(f"URL:{URL}\nPosttime:{time}")
                text = get_post_text_comment(URL)
                post_text =text["post"]
                comment_text =text["comment"]
                ##POST TEXT###
                text = cleanning_except_emoji(post_text)
                split = split_word(text)
                print(f"Post_text  : {split}\n\n")
                check_post = check_close_post(split,"post") #will return not_found or found as str check the word "sold" in text list
                ##POST TEXT###
                
                ##COMMENT TEXT###
                text = cleanning_except_emoji(comment_text) ##Get comment of poster and check the comment that have word mean this post that closed
                split = split_word(text)
                check_comment = check_close_post(split,"comment")
                ##COMMENT TEXT###

                ##EXPIRE DATE###
                marked_day = datetime.strptime(scrap_day,"%Y-%m-%d").date()
                expire =  diff_of_days(marked_day)
                ##EXPIRE DATE###

                if expire  == True: #check day that not more than 60 days
                     print("date expired")
                     check_internet_then_delete(time)

                if check_post == "found" or check_comment == "found": ##if in post or comment found word that mean like this post is colsed
                    check_internet_then_delete(time)

        except Exception as e:
            try: #page not found  or text not found
                    print("ERR::",e)
                    print("Page NOT found")
                    check_internet_then_delete(time)

            except:
                print(f"Error found::{e}")
                send_error(str(e))
        print("#############################")


def check_close_post(text_list,data_type):
    #make all char. to lower form
    text_list = set_lower(text_list)
    found_check = "not_found"
    if(data_type=="post"):
        bag_of_word = db.reference("close_post") #get the bag of word from firebase 
    elif(data_type=="comment"):
        bag_of_word = db.reference("close_post_comment") #get the bag of word from firebase 
    for word in set(bag_of_word.get()):
        if word in set(text_list):
            print(f"Close Found::{word}")
            found_check = "found"
    return found_check      
    
