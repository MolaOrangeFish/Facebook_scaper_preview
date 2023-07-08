import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db
from firebase import firebase
from datetime import date,datetime

#get day type(datetime)
def get_curr_day():
    today = date.today()
    current_day = today.strftime("%Y-%m-%d")
    current_day = datetime.strptime(current_day,"%Y-%m-%d").date()
    return current_day


##############################
#declare firebase config
# Fetch the service account key JSON file contents
cred = credentials.Certificate('make_json/kmutnbcommunity-firebase-adminsdk-s8kon-840841827e.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://kmutnbcommunity-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'kmutnbcommunity.appspot.com'
})
################################

#put data dict to firebase
def put_data_to_firebase(post_time:str,detail):
    year = post_time[0:4]
    month=post_time[5:7]
    url = "https://kmutnbcommunity-default-rtdb.asia-southeast1.firebasedatabase.app/"
    messenger = firebase.FirebaseApplication(url)
    messenger.put(f'/scraper/{year}/{month}',str(post_time),detail)

#####for demo#####
def put_data_to_firebase_demo(post_time:str,detail):
    year = post_time[0:4]
    month=post_time[5:7]
    url = "https://kmutnbcommunity-default-rtdb.asia-southeast1.firebasedatabase.app/"
    messenger = firebase.FirebaseApplication(url)
    messenger.put(f'/demo/{year}/{month}',str(post_time),detail)
#####for demo#####


#update data in report table 
def put_report_table(current_day,count):
    try:#update today report (summation the count)
        sell_report_data = db.reference(f"/report/{get_curr_day()}/sell").get()
        find_report_data = db.reference(f"/report/{get_curr_day()}/find").get()
        sum_count_sell = sell_report_data+count["sell"]
        sum_count_find = find_report_data+count["find"]
        newreport = {"sell":sum_count_sell,"find":sum_count_find}
    except: #dict for make newday report
        newreport = {"sell":0,"find":0}
    print(newreport)
    url = "https://kmutnbcommunity-default-rtdb.asia-southeast1.firebasedatabase.app/"
    messenger = firebase.FirebaseApplication(url)
    messenger.put(f'/report',current_day,newreport)


#get current day report data if cant it will create new table
def get_current_day_report():
    sell_report_data = db.reference(f"/report/{get_curr_day()}/sell").get()
    find_report_data = db.reference(f"/report/{get_curr_day()}/find").get()
    data_list = [sell_report_data,find_report_data]

    print(data_list)
    if data_list[0] is None and data_list[1] is None:
        print("Create new day report !!")
        put_report_table(get_curr_day(),{"sell":0,"find":0})
        print(f"report {get_curr_day()} has been created.")

#check post that in db or not
def check_data_in_db(post_time:str):
    year = post_time[0:4]
    month=post_time[5:7]
    target_date = db.reference(f"scraper/{year}/{month}/{post_time}").get()
    if target_date is None:
        print("Date not found")
        return False
    else:
        print("Date found")
        return True

#check post that in db or not (for demo)
def check_data_in_db_demo(post_time:str):
    year = post_time[0:4]
    month=post_time[5:7]
    target_date = db.reference(f"demo/{year}/{month}/{post_time}").get()
    if target_date is not None:
        print("Data found")
        return True
    else:
        print("Date not found")
        return False
    


##remove data
def remove_data_in_firebase(post_time:str):
    year = post_time[0:4]
    month=post_time[5:7]
    wanna_delete = db.reference(f"scraper/{year}/{month}/{post_time}")
    # wanna_delete = db.reference(f"demo/{year}/{month}/{post_time}")
    wanna_delete.delete()
    print("\n\nremoved\n\n")


def send_error(msg):
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y %H:%M:%S")
    url = "https://kmutnbcommunity-default-rtdb.asia-southeast1.firebasedatabase.app/"
    err_msg = firebase.FirebaseApplication(url)
    err_msg.put(f'/error',current_time,msg)


# def update_time_to_firebase(post_time:str):
#     url = "https://kmutnbcommunity-default-rtdb.asia-southeast1.firebasedatabase.app/"
#     messenger = firebase.FirebaseApplication(url)
#     messenger.put(f'/update_time/',"time",post_time)   



####cloud strorage####
from google.cloud import storage
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file("make_json/kmutnbcommunity-firebase-adminsdk-s8kon-840841827e.json")
storage_client = storage.Client(credentials=credentials)
import requests
import glob
import uuid
import re
import os 
import shutil

#delete ./img
def delete_folder_img():
    shutil.rmtree("img")


#upload file & get public url
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    blob.make_public() #make url public 
    return blob.public_url 

#main code to save file and call upload function 
def  get_img_from_storage_firebase(imgs_url,user_id,date_time):
    collecting_url = []
    year = date_time[0:4]
    month=date_time[5:7]
    day = date_time[8:10]
    combine_txt = str(user_id)+"_"+date_time
    combine_txt = re.sub("-|:|T", "", combine_txt).replace(" ", "") #make unique folder
    dir_path=f"img/{year}/{month}/{day}/{combine_txt}/" #set direct path

    # download the image
    for img_url in imgs_url:
        response = requests.get(img_url)
        filename = str(uuid.uuid4())
        if response.status_code == 200:
            os.makedirs(dir_path, exist_ok=True) #make path if not exist
            with open(os.path.join(dir_path, filename+".jpg"), 'wb') as f:
                f.write(response.content)

    #make new path that will get all .jpg file
    dir_img_path=f"img/{year}/{month}/{day}/{combine_txt}**/*.jpg" #set direct path
    for file in glob.iglob(dir_img_path, recursive=True):
            print(file)
            collecting_url.append(
            upload_blob(firebase_admin.storage.bucket().name,file,file.replace('\\', '/'))
            )
            
    return collecting_url
    