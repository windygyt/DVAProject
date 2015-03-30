import csv

def createTables(c):
    c.execute('create table restaurants (id INT PRIMARY KEY NOT NULL, name text, county_id integer,'\
              'rating integer, review_count integer)')
    c.execute('create table counties (id INT PRIMARY KEY NOT NULL, name text, state_id integer)')
    c.execute('create table states (id INT PRIMARY KEY NOT NULL, code text, name text)')
    c.execute('create table tags (id INT PRIMARY KEY NOT NULL, name text)')
    c.execute('create table restaurant_tag (restaurant_id integer, tag_id integer, '\
              'UNIQUE(restaurant_id, tag_id) ON CONFLICT REPLACE)')
    c.execute('create table reviews (id TEXT PRIMARY KEY NOT NULL, restaurant_id integer,'\
              'rating integer, date text)')

def buildCountiesTable(c):
    with open('counties.txt', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        state_id = 1
        for row in reader:
            id = int(row['id'])
            if id % 1000 == 0:
                state_id = id / 1000
                continue
            comm = 'INSERT OR IGNORE INTO counties VALUES (%d, \"%s\", %d)' % (id, row['name'], state_id)
            print comm
            c.execute(comm)

def buildStatesTable(c):
    with open('states.txt', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            id = int(row['id'])
            comm = 'INSERT INTO states VALUES (%d, \"%s\", \"%s\")' % \
                (int(row['id']), row['code'], row['name'])
            print comm
            c.execute(comm)