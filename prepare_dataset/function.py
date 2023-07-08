import string
import re
import glob
import csv
import json
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
from stop_words import get_stop_words
from pythainlp.util import normalize
import pandas as pd


th_stop_origin = tuple(thai_stopwords())
# append tuple thai stop word
th_stop = (th_stop_origin + ("สวัสดี", "ค่ะ", "เลย", "เรย","ๆ", "สุด", "นะคะ", "นะค่ะ", "ค่า", "อีกแล้ว","‼","⁉"))
en_stop = tuple(get_stop_words('en'))


def add_data_to_csv_with_deepcut(text,label):
    data=[]
    flag=0

    clean_text = cleanning(text)
    list_of_word = split_word(clean_text)
        
    temp_data=[list_of_word,str(label)]
    data.append(temp_data)
    with open('prepare_dataset/csv/by_selenium_data2.csv', 'a',encoding="UTF8") as file:
        header = ['text','post_type']
        writer = csv.writer(file)
        if(flag == 0):
            flag=1
            writer.writerow(header)
        writer.writerows(data)

    
def csv_to_csv():
    data=[]
    list_of_csv = get_all_csv_file()
    for name in list_of_csv:
        flag=0
        scrap_data = pd.read_csv(name)
        df = pd.DataFrame(data=scrap_data)
        for i in range(0,df.shape[0]):
            text = df["text"][i] 
            text_list = str_to_list(text)
            date_time = df["date_time"][i]
            post_type = df["post_type"][i]
            username = df['username'][i]
            user_id = df['user_id'][i]
            image = df['image'][i]
            # text_list = split_word(cleanning_except_emoji(text))
            print(str(text_list))
            print(post_type)
            tempdata = [date_time,username,user_id,text_list, post_type,image]
            data.append(tempdata)
        with open('all_scapping_dataasas.csv', 'a',encoding="UTF8") as file:
            header = ['date_time','username','user_id','text','post_type','image']
            writer = csv.writer(file)
            if(flag == 0):
                flag=1
                writer.writerow(header)
            writer.writerows(data)

def json_to_csv():
    data = []
    list_of_json = get_all_json_file()
    print(list_of_json)
    for filename in list_of_json:
        for i in range(1):
            flag=0
            with open(filename,'r',encoding="UTF8") as file:
                json_data = json.load(file)
                data_size = len(json_data["data"])
                for i in range(0,data_size):
                    date_time = json_data["data"][i]["date_time"]
                    username = json_data["data"][i]["username"]
                    user_id = json_data["data"][i]["user_id"]
                    post_type = json_data["data"][i]["post_type"]
                    text = json_data["data"][i]["text"]
                    image = json_data["data"][i]["image"]
                    tempdata = [date_time,username,user_id,text, post_type,image]
                    data.append(tempdata)
                
            with open('csv/temp_scapping_data.csv', 'a',encoding="UTF8") as file:
            # with open('temp_json/bag.csv', 'a',encoding="UTF8") as file:
                header = ['date_time','username','user_id','text','post_type','image']
                writer = csv.writer(file)
                if(flag == 0):
                    flag=1
                    writer.writerow(header)
                writer.writerows(data)
        print("Done converting")
                

def str_to_list(msg):
    for c in string.punctuation:
            msg = re.sub(r'\''.format(c), '', msg)
    msg =msg.strip("][").split(', ')
    return msg

def get_all_csv_file():
    list_of_files = glob.glob('scrap_data_json/*.csv') # * means all if need specific format then *.csv
    return list_of_files #make_json\log_json\scraping_26-12-2022_14.json

def get_all_json_file():
    list_of_files = glob.glob('scrap_data_json/*.json') # * means all if need specific format then *.csv
    # list_of_files = glob.glob('powerbi/*.json') # * means all if need specific format then *.csv
    return list_of_files #make_json\log_json\scraping_26-12-2022_14.json

def split_word(text):
    tokens = word_tokenize(text, engine='deepcut')  # แบ่งคำภาษาไทย

    # Remove stop words ภาษาไทย และภาษาอังกฤษ
    tokens = [i for i in tokens if not i in th_stop and not i in en_stop]

    # ลบช่องว่าง
    tokens = [i for i in tokens if not ' ' in i]

    return tokens

def clean_msg(msg):
    # ลบ text ที่อยู่ในวงเล็บ <> ทั้งหมด
    msg = re.sub(r'<.*?>', '', msg)
    # ลบ hashtag
    msg = re.sub(r'#', '', msg)
    # ลบ เครื่องหมายคำพูด (punctuation)
    for c in string.punctuation:
        msg = re.sub(r'\{}'.format(c), '', msg)
    # ทำให้ทุกคำต่อกัน
    msg = ' '.join(msg.split())
    # ลบ link https
    msg = re.sub(r'http\S+', '', msg)

    return msg

def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def cleanning(text):
    return clean_msg(normalize(remove_emoji(text)))

def cleanning_except_emoji(text):
    return clean_msg(normalize(text))
