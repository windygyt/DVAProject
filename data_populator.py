import csv
import sqlite3
tagsToExamine={}
countyPrefScoreAllCuisines={}
countyList=[]
countyWisePopulation={}
populationTable='year_2012'
def getTags():
    tagDict={}
    with open('tag_code_mapping.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            tagDict[row[0]]=row[1]
    return tagDict

def getAverageCuisinePopularity():
    print "Getting average cuisine popularity per county"

    for ind,cuisineTag in enumerate(tagsToExamine):
        print "cuisine %d of %d"%(ind,len(tagsToExamine))
        countyPrefScoreForThis=c.execute('select county_id, AVG(restaurants.rating) from restaurants join restaurant_tag on restaurants.id=restaurant_tag.restaurant_id where tag_id = '+cuisineTag+' group by county_id')
        countyPreferencesForCuisine={}
        for county in countyPrefScoreForThis:
            if county[0] not in countyList:
                countyList.append(county[0])
            countyPreferencesForCuisine[county[0]]=county[1]
        countyPrefScoreAllCuisines[cuisineTag]=countyPreferencesForCuisine

    # print countyPrefScoreAllCuisines


def getPopulationRepresentation():
    for county in countyList:
        countyPopulation=c.execute('select * from '+populationTable+' where county_id='+str(county))
        for row in countyPopulation:
            asians=row[3]
            afrAm=row[4]
            white=row[5]
            indian=row[6]
            pacIsl=row[7]
            total=asians+afrAm+white+indian+pacIsl
        countyWisePopulation[county]={}
        countyWisePopulation[county]['asian']=asians*1.0/total
        countyWisePopulation[county]['afrAm']=afrAm*1.0/total
        countyWisePopulation[county]['white']=white*1.0/total
        countyWisePopulation[county]['indian']=indian*1.0/total
        countyWisePopulation[county]['pacIsl']=pacIsl*1.0/total
        # print countyWisePopulation[county]
    # print countyWisePopulation
        # print countyPopulation[0]
        # asians=countyPopulation[3]
def populateDb():
    c.execute('DELETE FROM training_data')
    for index,county in enumerate(countyList):
        print "Populating Training Data: county "+str(index)+' of '+str(len(countyList))
        cuisineValString=''
        for cuisine in tagsToExamine:
            if county in countyPrefScoreAllCuisines[cuisine]:
                cuisineValString+=str(countyPrefScoreAllCuisines[cuisine][county])+','
            else:
                cuisineValString+='0,'


        # print 'insert into training_data values('+str(county)+','+str(countyWisePopulation[county]['asian'])+','+\
        #                                  str(countyWisePopulation[county]['afrAm'])+','+\
        #                                  str(countyWisePopulation[county]['white'])+','+\
        #                                  str(countyWisePopulation[county]['indian'])+','+\
        #                                  str(countyWisePopulation[county]['pacIsl'])+','+cuisineValString[:-1]+');'


        c.execute('insert into training_data values('+str(county)+','+str(countyWisePopulation[county]['asian'])+','+\
                                         str(countyWisePopulation[county]['afrAm'])+','+\
                                         str(countyWisePopulation[county]['white'])+','+\
                                         str(countyWisePopulation[county]['indian'])+','+\
                                         str(countyWisePopulation[county]['pacIsl'])+','+cuisineValString[:-1]+');')


def getCuisineString():
    createAttr=''
    for cuisine in tagsToExamine:
        createAttr+='tag'+cuisine+' float,'
    return createAttr


conn = sqlite3.connect('dva.db')
c = conn.cursor()
tagsToExamine=getTags()
c.execute('create table training_data (county_id int primary key not null, asian float, african_american float, '\
    'white float, american_indian float, pacific_islander float,'+getCuisineString()+' foreign key(county_id) references counties(id))')
getAverageCuisinePopularity()
getPopulationRepresentation()
populateDb()
print countyPrefScoreAllCuisines
conn.commit()
conn.close()
# print tagsToExamine
