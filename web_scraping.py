
########################## Web scraping ##########################

from bs4 import BeautifulSoup
import requests

# url of the wikipedia page 
url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"

# page of the url
page = requests.get(url)

soup = BeautifulSoup(page.text, "html.parser")

# get the first list of the table type
table = soup.find_all('table')[0]

# get the headers in the table
column_names_raw = table.find_all('th')   # h = header (?)

# get the column names of the table
column_names = [title.text.strip() for title in column_names_raw]


########################## Create dataframe ##########################
import pandas as pd

# create datafrme with the column names found
df = pd.DataFrame(columns = column_names)

# get the data of all the table rows 
columns_data = table.find_all('tr') # 'r' = row

# for each row in all the rows of the table
for row in columns_data[1:]: # exclude first empty row
    row_data = row.find_all('td') # get all the data values of the row, 'd' = 'data'
    individual_raw_data = [data.text.strip() for data in row_data] # get the single values from the data of the row, 'strip' to clean the values

    length = len(df)
    df.loc[length] = individual_raw_data # append each row of data at the maximum length of the df up to that point


# write the dataframe in a csv file
# uncomment this to save the file as 'filename' in the 'path' specified:

# df.to_csv(r'path\filename', index=False, sep=";")






