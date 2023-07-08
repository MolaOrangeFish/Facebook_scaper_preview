from function import json_to_csv,csv_to_csv,add_data_to_csv_with_deepcut
import pandas as pd
from storage import data5

# df = pd.read_csv('data.csv')
# print(df.shape)
# df.drop_duplicates(keep='last',ignore_index=False,inplace=True)

# print(df.shape)

# df.to_csv("sample.csv")


json_to_csv()


####################
### Import data by hand##
"""
data = data5
size = len(data)
print(size)

for i in range (0,size,2):
# for i in range (1):
    print(f"{data[i]} , {data[i+1]}")
    add_data_to_csv_with_deepcut(data[i],data[i+1])
"""

### Import data by hand##
####################
            
    
    

           
