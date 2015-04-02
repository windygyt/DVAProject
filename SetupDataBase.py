import csv

def createTables(c):
    c.execute('create table restaurants (id INT PRIMARY KEY NOT NULL, name text, county_id integer, '\
              'rating integer, review_count integer, FOREIGN KEY(county_id) REFERENCES counties(id))')
    c.execute('create table counties (id INT PRIMARY KEY NOT NULL, name text, state_id integer, '\
              'FOREIGN KEY(state_id) REFERENCES states(id))')
    c.execute('create table states (id INT PRIMARY KEY NOT NULL, code text, name text)')
    c.execute('create table tags (id INT PRIMARY KEY NOT NULL, name text)')
    c.execute('create table restaurant_tag (restaurant_id integer, tag_id integer, '\
              'UNIQUE(restaurant_id, tag_id) ON CONFLICT REPLACE, '\
              'FOREIGN KEY(restaurant_id) REFERENCES restaurants(id), '\
              'FOREIGN KEY(tag_id) REFERENCES tags(id))')
    c.execute('create table reviews (id TEXT PRIMARY KEY NOT NULL, restaurant_id integer,'\
              'rating integer, date text, FOREIGN KEY(restaurant_id) REFERENCES restaurants(id))')
    c.execute('create table zips (zip INT PRIMARY KEY NOT NULL, county_id integer, '\
              'FOREIGN KEY(county_id) REFERENCES counties(id))')

def buildCountiesTable(c):
    id = 1;
    with open('all_2013.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        state_id = 1
        for row in reader:
            state = row['State'][1:]
            state_id = getStateID(c, state)
            comm = 'INSERT OR IGNORE INTO counties VALUES (%d, \'%s\', %d)' % (id, row['County'].lower(), state_id)
            print comm
            c.execute(comm)
            id = id + 1

def buildStatesTable(c):
    with open('states.txt', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            id = int(row['id'])
            comm = 'INSERT INTO states VALUES (%d, \'%s\', \'%s\')' % \
                (int(row['id']), row['code'], row['name'])
            print comm
            c.execute(comm)

def getStateID(c, state) :
    if len(state) == 2:
        comm = 'SELECT id from states where code = \'%s\'' % state
    else:
        comm = 'SELECT id from states where name = \'%s\'' % state
    c.execute(comm)
    result = c.fetchone()
    if result:
        return result[0]
    else:
        print("Cannot find state id! %s" % (state))
        exit(0)


def getCountyID(c, state, county):
    #print state+' '+county
    county = county.lower()
    if len(state) == 2:
        comm = 'SELECT c.id from counties as c, states as s where c.state_id = s.id and'\
                ' s.code = \'%s\' and c.name = \'%s\'' % (state, county)
    else:
        comm = 'SELECT c.id from counties as c, states as s where c.state_id = s.id and'\
                ' s.name = \'%s\' and c.name = \'%s\'' % (state, county)
    c.execute(comm)
    result = c.fetchone()
    if result:
        return result[0]
    else:
        print("Cannot find county id! %s %s" % (state, county))
        return -1

def buildDemoTableAtYear(c, year):
    c.execute('create table year_%d (county_id PRIMARY KEY NOT NULL, state TEXT, county_name text, '\
              'Asian integer, African_American integer, White integer, American_Indian integer, '\
              'Pacific_Islander integer, FOREIGN KEY(county_id) REFERENCES counties(id))' % year)
    file_name = "all_" + str(year) + ".csv"
    with open(file_name, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            state = row['State'][1:]
            county = row['County']
            county_id = getCountyID(c, state, county)
            if county_id < 0:
                continue
            comm= 'INSERT OR IGNORE INTO year_%d VALUES(%d, \'%s\', \'%s\', %d, %d, %d, %d, %d)' % \
                  (year, county_id, state, county, int(row['Asian'].replace(',','')), \
                   int(row['Black or African American'].replace(',','')),int(row['White'].replace(',','')), \
                   int(row['American Indian and Alaska Native'].replace(',','')), \
                   int(row['Native Hawaiian and Other Pacific Islander'].replace(',','')))
            print comm
            c.execute(comm)

def buildZipTable(c):
    with open('ZIP_CODES.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            state = row['State']
            county = row['County']
            county_id = getCountyID(c, state, county);
            comm = 'INSERT INTO zips VALUES (%d, %d)' % (int(row['Zip']), county_id)
            print comm
            c.execute(comm)

def getZips(c, state, county):
    county_id = getCountyID(c, state, county)
    print county_id
    zips = []
    for row in c.execute('select zip from zips where county_id = %d' % county_id):
        zips.append(row[0])
    return zips

def buildDemoTables(c):
    for year in [2010, 2011, 2012, 2013]:
        buildDemoTableAtYear(c, year)
