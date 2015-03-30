import RestaurantCollector
import RestaurantJsonFileParser
import ReviewCollector
import ReviewJsonFileParser
import SetupDataBase

import sqlite3
from os import listdir
import json
import os

publisher = xxxxxxxxx # replace with your own publisher id
restaurant_file_folder = 'json/CobbCounty GA/'
review_file_folder = 'json/CobbCounty GA reviews/'
query_size = 50 # 50 is the maximum
query_state = 'GA' # match zip-county.csv file
query_county = 'Cobb County' # match zip-county.csv file
short_county_name = 'Cobb' # match counties file

# Step1: using zip code searching for all restaurants and find their id
# Example: https://api.citygridmedia.com/content/places/v2/search/where?type=restaurant&where=90045&publisher=xxxx
# Step2: using id to find all reviews for that restaurant
# Example: https://api.citygridmedia.com/content/reviews/v2/search/where?listing_id=44537579&publisher=xxxx
# Note: searching is based on radius on distance, which means using zip does not mean all the result restaurants'
# addresses match the zip,

# county id 1001 Autauga County
# zips = [36003, 36006, 36008, 36051, 36066, 36067, 36068, 36749]

# Info: sqlite date: https://www.sqlite.org/lang_datefunc.html

def initDataBase(c):
    SetupDataBase.createTables(c);
    SetupDataBase.buildCountiesTable(c);
    SetupDataBase.buildStatesTable(c);

def getCountyID(c, state, county):
    comm = 'SELECT c.id from counties as c, states as s where c.state_id = s.id and'\
            ' s.code = \"%s\" and c.name = \"%s\"' % (state, county)
    c.execute(comm)
    result = c.fetchone()
    if result:
        return result[0]
    else:
        print("Cannot find county id!")
        exit(0)



if not os.path.exists(restaurant_file_folder):
    os.makedirs(restaurant_file_folder)
if not os.path.exists(review_file_folder):
    os.makedirs(review_file_folder)


zips = RestaurantCollector.getZips(query_state, query_county)
print zips
# save all restaurants information to Json files according to their zip code
# If interrupted, try restart from a certain zip code
RestaurantCollector.queryAndSaveRestaurantsJsonFiles(zips, restaurant_file_folder, query_size, publisher)

conn = sqlite3.connect('dva.db')
c = conn.cursor()
# initDataBase(c) # call only when recreating the database from empty

# Parse the restaurants Json file and insert contents into db
county_id = getCountyID(c, query_state, short_county_name)
print('county id: ' + str(county_id))
for file_name in listdir(restaurant_file_folder):
    with open(restaurant_file_folder + file_name) as json_file:
        data = json.load(json_file)
        zip = int(file_name[0:file_name.find('-')])
        RestaurantJsonFileParser.parseRestaurantJsonFiles(c, data, zip, county_id)
        print("Finish parsing " + file_name)

# Gather the restaurant list and get reviews for each one, then save them to Json files
ReviewCollector.queryAndSaveReviewJsonFiles(c, review_file_folder, county_id, query_size, publisher)

# Parse the reviews Json file and insert contents into db
for file_name in listdir(review_file_folder):
    with open(review_file_folder + file_name) as json_file:
        data = json.load(json_file)
        zip = int(file_name[0:file_name.find('-')])
        ReviewJsonFileParser.parseReviewJsonFiles(c, data)
        print("Finish parsing " + file_name)

conn.commit()
conn.close()