import urllib2
import json
import time
import math
import csv

def getRestaurants(zip, page, query_size, publisher):
    url = 'https://api.citygridmedia.com/content/places/v2/search/where?'\
            'type=restaurant&where=%d&rpp=%d&page=%d&format=json&publisher=%d'
    req = url % (zip, query_size, page, publisher)
    print req
    try:
        response = urllib2.urlopen(req)
        data = json.load(response)
        return data
    except urllib2.HTTPError, err: # invalid zip code
        return None


def getZips(state, county):
    zips = []
    with open('zip-county.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['state'] == state and row['county'] == county:
                zips.append(int(row['zip']))
    return zips


def queryAndSaveRestaurantsJsonFiles(zips, dump_folder, query_size, publisher):
    # manually change zips when start from an interrupted job
    # zips = [xxx, xxx, xxx]
    for zip in zips:
        data = getRestaurants(zip, 1, query_size, publisher)
        if data == None:
            continue
        with open(('%s/%d-page%d.txt' % (dump_folder, zip, 1)), 'w') as outfile:
            json.dump(data, outfile)
        time.sleep(0.3)
        hits = int(data['results']['total_hits'])
        pages = int(math.ceil(float(hits) / query_size))
        for p in range(2, pages + 1):
            data = getRestaurants(zip, p, query_size, publisher)
            with open(('%s/%d-page%d.txt' % (dump_folder, zip, p)), 'w') as outfile:
                json.dump(data, outfile)
            time.sleep(0.3)



