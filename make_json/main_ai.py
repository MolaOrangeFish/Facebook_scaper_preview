from package.nlp_function import *
from package.scrap_function import *
from package.firebase_function import *
from facebook_scraper import get_posts
import numpy as np
import joblib
import json


def word_split(text):
    words = re.split(r",",text)
    return words


def text_process_save_comma(text): ##save ,
    text = re.sub("\[|\]|'|"," ",text).replace(" ", "")
    text = re.sub(r'[0-9]+'," ",text).replace(" ", "") ##remove nember
    return text


group_id = '197822284350539' #KMUTNB Community


##############Load model##############
filename  = "prepare_dataset/model/check_type.sav"
filenamevector = "prepare_dataset/model/count_vectorizer.sav"
loaded_model = joblib.load(open(filename,"rb"))
vectorizer = joblib.load(open(filenamevector,"rb"))
##############Load model##############

####Collecting cout for scrap per day wont collect dulpicate data####
count_find=0
count_sell=0
#########################


for post in get_posts(group=group_id, pages=3, extra_info=True, 
                      option={"comment": False,"posts_per_page": 3,"reactors": True},
                      credentials=("*************@hotmail.com","password") #login facebook account
                      ):
    start_time = datetime.now()
    date_dulpicate_check=check_data_in_db(str(post['time'])) #check dulpicate of post data(False mean no dulpicate)

    if date_dulpicate_check == False: #False mean new data doesnt have in database
        print('++++++++++++++++++++++++++++++++++++++++++++')
        text = cleanning(post['post_text'])
        print(text)

        clean_txt_show = split_word(text)
        clean_txt_ai  = str(split_word(text))
        clean_txt_ai  = text_process_save_comma(clean_txt_ai)  ##clean number 
        text_list = vectorizer.transform([clean_txt_ai]).reshape(1,-1).todense()
        predictions = loaded_model.predict(np.asarray(text_list))
        post_type = predictions[0] ##0:FIND    1:SELL    2:OTHER

        try:
            skip = False  #Skip false mean wont skip it have images!!
            print(f"Predicted:{post_type}")
            if (post_type == 0 and post['images'] != []):  #when you found lost things  must have photo
                temp_dict = insert_data_to_dict("find",post['time'],post['username'],post['user_id'],clean_txt_show,post['images'],post['post_url'])
                count_find+=1
            elif (post_type == 0 and post['images'] == []): #if the photo was empty
                print("Skip lost post no pictures")
                skip = True
            elif(post_type == 1 and post['images'] != []):  #when you wanna sell you must have photo
                temp_dict = insert_data_to_dict("sell",post['time'],post['username'],post['user_id'],clean_txt_show,post['images'],post['post_url'])
                count_sell+=1
            elif(post_type == 1 and post['images'] == []):#if the photo was empty
                print("Skip sell post no pictures")
                skip = True
            # elif(post_type==2):
            #     temp_dict = insert_data_to_dict("muuu",post['time'],post['username'],post['user_id'],clean_txt_show,post['images'],post['post_url'])

            # find the detail of place & describe (color) if data is not 2
            if skip == False:
                if(post_type == 0 or post_type == 1):
                    get_all_detail(clean_txt_show,post_type)

                    ######################
                    ###get max score category###
                    max_score_cate = max(scores,key=scores.get)
                    if scores[max_score_cate] == 0:  #if category is none
                        print("no category")
                        print(scores)
                    else:                                                       #if category not none
                        print(max_score_cate)
                        print(scores)
                        temp_category.append(max_score_cate) 
                    ###get max score category###
                    ######################

                    check_empty(temp_place) #if temp place,describe,category are empty it will fill with "-"
                    check_empty(temp_describe)
                    check_empty(temp_category) 
                    
                    #make data in list not duplicate            
                    temp_place_rm_dp = list(set(temp_place))
                    temp_describe_rm_dp = list(set(temp_describe))
                    temp_category_rm_dp = list(set(temp_category))

                    print(f'temp_place = {str(temp_place_rm_dp)}\ntemp_describe = {str(temp_describe_rm_dp)}\ntemp_category =  {str(temp_category_rm_dp)}')
                    # send data in temp_list to dict
                    for data in temp_place_rm_dp:
                        temp_dict["place"].extend({data})
                    for data in temp_describe_rm_dp:
                        temp_dict["describe"].extend({data})
                    for data in temp_category_rm_dp:
                        temp_dict["category"].extend({data})

                    ##############
                    ##send img here#
                    ##############
                    temp_dict["image"] = get_img_from_storage_firebase(post["images"],post["user_id"],str(post["time"])) #let img take new url
                    delete_folder_img()

                #add all data 0,1 and 2 to data_dict for collecting data to make dataset for (traing model) 
                # if skip == False:
                #     data_dict[str(temp_dict['time'])] = temp_dict
                
                #if data is not 2 will put data to firebase 
                if(post_type == 0 or post_type == 1):
                    ########################
                    ###check price condition here###
                    if (post_type == 1 and temp_dict["category"] [0] == "apartment_condo" and temp_dict["price"] != "-"):
                        if  int(temp_dict["price"]) < 3000:
                            temp_dict["price"] = "-"     ##set the price to "-"
                            print("empty price (price for conda or apartment <3000 bath)")
                    ###check price condition here###
                    ########################
                    temp_dict["scrap_day"] = get_curr_day()
                    data_dict[str(temp_dict['date_time'])] = temp_dict
                    time = str(temp_dict["date_time"])
                    put_data_to_firebase(time, temp_dict)

            #####clear list make sure its empty out s#####
            temp_place.clear()
            temp_describe.clear()
            temp_category.clear()
            #####clear list make sure its empty##### 

        except Exception as e:
            print(e)
            send_error(str(e))
    
    end_time = datetime.now()
    print('\n\nDuration: {}\n\n'.format(end_time - start_time))


#send report after done scrap
count = {"sell":count_sell,"find":count_find}  #variable collecting count of both type
get_current_day_report() #get current day report data if cant it will create new table
put_report_table(get_curr_day(),count) #update data in report table 


#save log that scrap
jsonString = json.dumps(data_dict,ensure_ascii=False, indent=4,default=str)
# Writing to json
writejson(jsonString,"scrap")

##check time its 18:00? if yes save db backup
now = datetime.now()
current_hrs = now.strftime("%H")
if current_hrs == "18":
    backup = db.reference(f"/").get()
    jsonString = json.dumps(backup,ensure_ascii=False, indent=4,default=str)
    writejson(jsonString,"db_backup")
