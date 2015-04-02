import urllib2
import time
import math
import json

def getReviewForRestaurant(id, page, query_size, publisher):
    url = 'https://api.citygridmedia.com/content/reviews/v2/search/where?' \
          'listing_id=%d&rpp=%d&page=%d&format=json&publisher=%d'
    req = url % (id, query_size, page, publisher)
    print req
    try:
        response = urllib2.urlopen(req)
        data = json.load(response)
        return data
    except urllib2.HTTPError, err: # invalid zip code
        return None

def queryAndSaveReviewJsonFiles(c, dump_folder, county_id, query_size, publisher):
    comm = 'SELECT id, review_count FROM restaurants WHERE county_id = ' + str(county_id) + ' ORDER BY id'
    for row in c.execute(comm):
        if row[0] < 0: # change 0 to other number when continue a interrupted job
            continue
        if row[1] == 0:
            continue
        pages = int(math.ceil(float(row[1]) / query_size))
        for p in range(1, pages + 1):
            data = getReviewForRestaurant(row[0], p, query_size, publisher)
            with open(('%s/%d-page%d.json' % (dump_folder, row[0], p)), 'w') as outfile:
                json.dump(data, outfile)
            time.sleep(0.3)
