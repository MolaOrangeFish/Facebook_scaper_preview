from package.scrap_function import *
from package.firebase_function import *
from package.scrap_function import *
from datetime import datetime
import numpy as np
import joblib

def word_split(text):
    words = re.split(r",",text)
    return words


def text_process_save_comma(text): ##save ,
    text = re.sub("\[|\]|'|"," ",text).replace(" ", "")
    text = re.sub(r'[0-9]+'," ",text).replace(" ", "") ##remove nember
    return text

##############Load model##############
filename  = "prepare_dataset/model/check_type.sav"
filenamevector = "prepare_dataset/model/count_vectorizer.sav"
loaded_model = joblib.load(open(filename,"rb"))
vectorizer = joblib.load(open(filenamevector,"rb"))
##############Load model##############

timelist=["2021-01-10 10:38:42","2021-01-09 10:38:42"]
u_name = 'BUBUMUMU'
u_id = '1000084206102'
url = 'https://www.facebook.com/groups/197822284350539/permalink/1319900752142681/?paipv=0&eav=AfY82l_N49ebEon6EGrOUVYhqnsw4GxtgpJNK3dVrPbCp5VXxWUs1kxGA9NPxsntg-w&_rdr'

txt_data = [
"""sold condo 3000 ครับ"""]
img = ['https://scontent.fbkk29-1.fna.fbcdn.net/v/t39.30808-6/342466875_921411749138707_5628029806854157931_n.jpg?stp=dst-jpg_p720x720&_nc_cat=101&ccb=1-7&_nc_sid=5cd70e&_nc_ohc=Avj2lEAwh9UAX8WEEM5&_nc_ht=scontent.fbkk29-1.fna&oh=00_AfCp9B_55vNHFYbvxTz-QHJWZ3jdev66MlDRN_rtIPDd4w&oe=64492837',
       'https://scontent.fbkk29-6.fna.fbcdn.net/v/t39.30808-6/342356301_219767970749231_6551887983783685860_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=5cd70e&_nc_ohc=G4_YY7ZR0ycAX_15y3O&_nc_ht=scontent.fbkk29-6.fna&oh=00_AfD-8tnzNc-JfXyTuzLcOuwi3w7dsm2ue2es2Dh4k7krIA&oe=644A535D'
            ]
print('--------------------')

count_find=0
count_sell=0

for i in range(1):
    date_dulpicate_check=check_data_in_db_demo(timelist[i])
    start_time = datetime.now()
    if date_dulpicate_check == False: #False mean new data doesnt have in database
        text = cleanning(txt_data[i])
        print(text)
        print('--------------------')

        clean_txt_show = split_word(text)
        clean_txt_ai  = str(split_word(text))
        clean_txt_ai  = text_process_save_comma(clean_txt_ai)  ##clean number 
        text_list = vectorizer.transform([clean_txt_ai]).reshape(1,-1).todense()
        predictions = loaded_model.predict(np.asarray(text_list))
        post_type = predictions[0] ##0:FIND    1:SELL    2:OTHER
   
        try:
            
            skip = False
            print(f"Predicted:{post_type}")
            if (post_type == 0 and img[i] != []):  #when you found lost things  must have photo
                temp_dict = insert_data_to_dict("find",timelist[i],u_name,u_id,clean_txt_show,img,url)
                count_find+=1
            elif (post_type == 0 and img[i] == []): #if the photo was empty
                print("Skip lost post no pictures")
                skip = True
            elif(post_type == 1 and img[i] != []):  #when you wanna sell you must have photo
                temp_dict = insert_data_to_dict("sell",timelist[i],u_name,u_id,clean_txt_show,img,url)
                count_sell+=1
            elif(post_type == 1 and img[i] == []):#if the photo was empty
                print("Skip sell post no pictures")
                skip = True
            # elif(post_type==2):
            #     temp_dict = insert_data_to_dict("muuu",timelist[i],u_name,u_id,clean_txt_show,img[i],post['post_url'])

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
                    check_empty(temp_describe) #if temp place,describe,category are empty it will fill with "-"
                    check_empty(temp_category) #if temp place,describe,category are empty it will fill with "-"

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
                    # temp_dict["image"] = get_img_from_storage_firebase(img,u_id,timelist[0]) #let img take new url
                    # delete_folder_img()
                
                

                #add all data 0,1 and 2 to data_dict for collecting data to make dataset for traing model   
                # if skip == False:
                #     data_dict[str(timelist[i])] = temp_dict
                
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
                    print("Price::"+str(temp_dict["price"]))
                    temp_dict["scrap_day"] = get_curr_day()
                    data_dict[str(timelist[i])] = temp_dict ##for json
                    time = str(temp_dict["date_time"])
                    # put_data_to_firebase_demo(time, temp_dict)

            #####clear list make sure its empty#####
            temp_place.clear()
            temp_describe.clear()
            temp_category.clear()
            # scores = dict.fromkeys(scores,0) #empty when sent max score category
            #####clear list make sure its empty##### 

        except Exception as e:
            print(e)
            send_error(str(e))
    end_time = datetime.now()
    print('\n\nDuration: {}\n\n'.format(end_time - start_time))

"""
#send report after done scrap
count = {"sell":count_sell,"find":count_find}  #variable collecting count of both type
get_current_day_report() #get current day report data if cant it will create new table
put_report_table(get_curr_day(),count) #update data in report table 
"""
# encode list to json
# jsonString = json.dumps(data_dict, ensure_ascii=False, indent=4, default=str)
# Writing to json
# writejson(jsonString)

# TODO TEST DATA_DICT
# print(data_dict)