

import numpy
from scipy.spatial import cKDTree
import math,random,sys,bisect,time
import numpy,scipy.spatial.distance
import cProfile,pstats
import sys
import sqlite3
 
class LinRegLearner:
	def __init__(self):
		self.Xtrain = None
		self.Ytrain = None
		self.coeff = None
		self.res = None
		

	def addEvidence(self,Xtrain,Ytrain=None):
		self.Xtrain = Xtrain
		self.Ytrain = Ytrain
		xTrainIdentityMatrix = numpy.hstack([self.Xtrain, numpy.ones((len(self.Xtrain), 1))])	
		self.coeff = numpy.zeros(5)
		linReg = numpy.linalg.lstsq(xTrainIdentityMatrix, Ytrain)
		self.coeff[0] = linReg[0][0]
		self.coeff[1] = linReg[0][1]
		self.coeff[2] = linReg[0][2]
		self.coeff[3] = linReg[0][3]
		self.coeff[4] = linReg[0][4]
		self.res = linReg[0][5]	
    	def query(self,XTest):
		Y = numpy.dot(XTest, self.coeff) + self.res
		return Y			


def getDBData():
    print "Getting training data"
   
    #trainingData=c.execute('select county_id as countyId,asian as popAsian,african_american as popAfricanAmerican,white as  popWhite,american_indian as popAmericanIndian,pacific_islander as popPacificIslander,popularity_Mexican_11208 as popularityMexican, popularity_Pizza_11299 as popularityPizza, popularity_Chinese_11252 as popularityChinese from training_data')
    c.execute('select * from training_data')

    npTrainingData = numpy.array(c.fetchall(),dtype=float)
    return npTrainingData


def testLinRegLearner(data, sampleType, cuisineIndex):
	learner = LinRegLearner()
	xTrainData = data[0:0.6*len(data),1:6]
	yTrainData = data[0:0.6*len(data),cuisineIndex]
	learner.addEvidence(xTrainData,yTrainData)
	if(sampleType == "Out Of Sample"):
		yResult = learner.query(data[0.6*len(data):len(data),1:6])
		yActual = data[0.6*len(data):len(data),cuisineIndex]
	else:
		yResult = learner.query(data[0:0.6*len(data),1:6])
		yActual = data[0:0.6*len(data),cuisineIndex]

	rmse = calculateRMSError(yResult,yActual)
	corrCoeff= numpy.corrcoef(yResult, yActual)[0,1]
	return rmse,corrCoeff,yActual,yResult





	


def calculateRMSError(yResult,yActual):
	#print len(yResult)
	#print len(yActual)
	sumVal=0
	for i in range(0,len(yResult)):
		#print yResult[i]
		#print yActual[i]
		sumVal = sumVal + (yResult[i]-yActual[i])**2
	rmse=math.sqrt(float(sumVal)/len(yResult))
	return rmse



conn = sqlite3.connect('dva.db')
c = conn.cursor()
data = getDBData()
cuisineIndexMap = dict()
cuisineIndexMap['Mexican']=6
cuisineIndexMap['Pizza']=7
cuisineIndexMap['Chinese']=8
cuisineIndexMap['American']=9

for cuisine in cuisineIndexMap.keys():
  
  print "For cuisine: "+cuisine
  print "-----------------------"
  k=3
  sampleType = "Out Of Sample"
  rmse,corrCoeff,yActual,yResult = testLinRegLearner(data,sampleType,cuisineIndexMap[cuisine])
  print "\n\tLearner: Linear Regression"
  print "\t\tSample type= "+str(sampleType)+"\n"
  print "\t\tRMS Error = "+str(rmse)
  print "\t\tCorrelation Coefficient = "+str(corrCoeff)+"\n\n"


  k=3
  sampleType = "In Sample"
  rmse,corrCoeff,yActual,yResult = testLinRegLearner(data,sampleType,cuisineIndexMap[cuisine])
  print "\n\tLearner: Linear Regression"
  print "\t\tSample type= "+str(sampleType)+"\n"
  print "\t\tRMS Error = "+str(rmse)
  print "\t\tCorrelation Coefficient = "+str(corrCoeff)+"\n\n"
  
  

conn.close()
