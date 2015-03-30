def parseReviewJsonFiles(c, data):
    for review in data['results']['reviews']:
        if review['review_rating'] == None:
            continue
        comm = 'INSERT OR IGNORE INTO reviews VALUES (\"%s\", %d, %d, \"%s\")' % \
               (review['review_id'], int(review['listing_id']), \
                int(review['review_rating']), review['review_date'])
        c.execute(comm)

