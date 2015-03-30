# tags need to be cleaned : remove duplicated contents (eg. restaurant), remove useless contents (eg. credit card)
# Should change table tags and restaurant_tag, suggest clean up using tools such as google refine first
def parseRestaurantJsonFiles(c, data, zip, county_id):
    for location in data['results']['locations']:
        if location['address']['postal_code'] == None:
            continue
        if int(location['address']['postal_code']) != zip:
            continue
        # None rating when no review, insert rating 0 in this case
        comm = 'INSERT OR IGNORE INTO restaurants VALUES (%d, \"%s\", %d, %d, %d)' % \
               (int(location['id']), location['name'], county_id, \
                0 if location['rating'] == None else int(location['rating']) , \
                int(location['user_review_count']))
        c.execute(comm)
        for tag in location['tags']:
            comm = 'INSERT OR IGNORE INTO tags VALUES (%d, \"%s\")' % (int(tag['id']), tag['name'])
            c.execute(comm)
            comm = 'INSERT INTO restaurant_tag VALUES (%d, %d)' % (int(location['id']), int(tag['id']))
            c.execute(comm)