
import numpy
from scipy.spatial import cKDTree
import math,random,sys,bisect,time
import numpy,scipy.spatial.distance
import cProfile,pstats
import sys
import numpy as np
import sqlite3

def getDBData():
    print "Getting training data"
   
    #trainingData=c.execute('select county_id as countyId,asian as popAsian,african_american as popAfricanAmerican,white as  popWhite,american_indian as popAmericanIndian,pacific_islander as popPacificIslander,popularity_Mexican_11208 as popularityMexican, popularity_Pizza_11299 as popularityPizza, popularity_Chinese_11252 as popularityChinese from training_data')
    c.execute('select * from training_data')

    npTrainingData = numpy.array(c.fetchall(),dtype=float)
    return npTrainingData



class RandomForestLearner:
	def __init__(self, k=3,method='mean',leafsize=10):
		self.k= k;
		self.data = None;
		self.forest = []
		self.tree = None;
		self.xTrain = None;
		self.yTrain = None;
    		self.index=0;
  
	def addEvidence(self,xTrain,yTrain):
		self.xTrain = xTrain;
   	 	self.yTrain = yTrain;
		for i in range(self.k):
                        tree = []			
			xMatrix,yMatrix = getRandomArray(xTrain,yTrain) 
			self.index=0
			self.buildDecisionTree(xMatrix,yMatrix,tree)
			self.forest.append(tree)

  	def buildDecisionTree(self, xTrain, yTrain, tree):
   
    		if(len(xTrain) == 1):
      			tree.append([self.index,-1, float(yTrain), -1,  -1]);
      			return;
      
    		randomFeature = np.random.random_integers(0,len(xTrain[1, :])-1);
  
    		if(allValuesInListSame(xTrain[:,randomFeature]) == True):
			tree.append([self.index,-1, int(np.mean(yTrain)), -1,  -1]);
      			return;
      
    		splitValArray = np.random.choice(xTrain[:, randomFeature], 2);
   
    		while(splitValArray[0] == splitValArray[1]):
      			splitValArray = np.random.choice(xTrain[:, randomFeature], 2);
            
    		splitVal = np.mean(splitValArray);
    		xLeft = [];
    		xRight = [];
    		yLeft = [];
    		yRight = [];
    
    		for i in range(len(xTrain[:, randomFeature])):
      			if(xTrain[i, randomFeature] <= splitVal):
        			xLeft.append(list(xTrain[i, :]));
        			yLeft.append(yTrain[i]);
     			else:
        			xRight.append(list(xTrain[i, :]));
        			yRight.append(yTrain[i]);
        
      
    		xLeft = np.array(xLeft);
    		yLeft = np.array(yLeft);
    		xRight = np.array(xRight);
    		yRight = np.array(yRight);
    
    		if(len(xLeft) == 0 or len(xRight) == 0):
      			print("randomFeature=", randomFeature);
      			print("splitValArray=", splitValArray);
     		 	print("splitVal=", splitVal);
      			print(xTrain[:, randomFeature]);
      			print(">>>>>>>>>>>>>>One of the parts became zero");
      			print(xLeft);
      			print(xRight);
      			tree.append([self.index,-1, int(np.mean(yTrain)), -1,  -1]);
      			return;
      
    		thisNode = self.index;
    		self.index +=1;
    		leftChild = self.index;
    		tree.append([thisNode, randomFeature, splitVal, leftChild, None]);
    		self.buildDecisionTree(xLeft, yLeft, tree);
    		self.index +=1;
    		rightChild = self.index;
    		tree[thisNode][4] = rightChild;
    		self.buildDecisionTree(xRight, yRight, tree);


        def query(self, xTestArray):
                yTestColl = []
		for xTest in xTestArray:
			yTestArray= []
			for tree in self.forest:          		
			#print tree
			#print xTest
				yTest = self.getYValueFromTree(tree,xTest)
				yTestArray.append(yTest)
                      	yTestMean = numpy.mean(yTestArray)
			#print yTestArray
                        yTestColl.append(yTestMean)
                
                return yTestColl

		
        def getYValueFromTree(self, tree,xTest):
                 
                        index = 0
                        while(1):
                                feature = tree[index][1]
                                splitVal = tree[index][2]
				#print feature
				#print splitVal
				
                                if(feature == -1):
                                        yTest = splitVal
                                        break;
                                if(xTest[feature] <= splitVal):
                                        index = tree[index][3]
                                else:
                                        index = tree[index][4]
                	return numpy.array(yTest)
                                	

def allValuesInListSame(arrList):
		for i in range(0,len(arrList)-1):
			if(arrList[i] != arrList[i+1]):
				return False
		return True
  

def testRandomForestLearner(k,data, sampleType, cuisineIndex):
	learner = RandomForestLearner(k)
	xTrain = data[0:0.6*len(data),1:6]
	yTrain = data[0:0.6*len(data),cuisineIndex]
	learner.addEvidence(xTrain,yTrain)
	if(sampleType == "Out Of Sample"):
		yResult = learner.query(data[0.6*len(data):len(data),1:6])
		yActual = data[0.6*len(data):len(data),cuisineIndex]
	else:
		yResult = learner.query(data[0:0.6*len(data),1:6])
		yActual = data[0:0.6*len(data),cuisineIndex]
	rmse = calculateRMSError(yActual,yResult)	
	corrCoeff= numpy.corrcoef(yResult, yActual)[0,1]
	return rmse,corrCoeff,yActual,yResult
        
	

def calculateRMSError(yResult,yActual):
	rmse = numpy.sqrt(numpy.mean((yResult - yActual)**2));
	return rmse

def getRandomArray(xTrain,yTrain):
	iList=[]
	iList.append(5000);
	rIndex=5000
	b =  np.zeros(((0.6*len(xTrain)),len(xTrain[0])))
	c =  np.zeros(((0.6*len(yTrain)),1))
	for i in range(int(0.6*len(xTrain))):
		while(rIndex in iList):
			rIndex = np.random.random_integers(0,len(xTrain)-1);
		b = np.vstack([b,xTrain[rIndex,:]])
		c = np.vstack([c,yTrain[rIndex]])
		iList.append(rIndex)
		
	return b,c



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
  rmse,corrCoeff,yActual,yResult = testRandomForestLearner(k,data,sampleType,cuisineIndexMap[cuisine])
  print "\n\tLearner: RandomForestLearner"
  print "\t\tNumber of trees= "+str(k)+"\n"
  print "\t\tSample type= "+str(sampleType)+"\n"
  print "\t\tRMS Error = "+str(rmse)
  print "\t\tCorrelation Coefficient = "+str(corrCoeff)+"\n\n"


  k=3
  sampleType = "In Sample"
  rmse,corrCoeff,yActual,yResult = testRandomForestLearner(k,data,sampleType,cuisineIndexMap[cuisine])
  print "\n\tLearner: RandomForestLearner"
  print "\t\tNumber of trees= "+str(k)+"\n"
  print "\t\tSample type= "+str(sampleType)+"\n"
  print "\t\tRMS Error = "+str(rmse)
  print "\t\tCorrelation Coefficient = "+str(corrCoeff)+"\n\n"