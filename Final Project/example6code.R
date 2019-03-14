
library(caret)
library(RANN)
library(tidyverse)

library(ROSE)



train=read.csv("example6data.csv",stringsAsFactors = T) # load training data
View(train) # look at it
names(train) # column names
dim(train) # observations and number of variables


train%>%
  is.na() %>%
  any()        # checking if there are NA values
  
train%>%
  is.na() %>%   # how many NA values
  sum()    



# using KNN to fill the NAs with the option of centering and scaling the numerical columns
KNN.fill= preProcess(train, method = c("knnImpute","center","scale"))

train.1 = predict(KNN.fill, train) # applying the KNN

train%>%
  is.na() %>%   # how many NA values
  sum() 


# The y variable (the one to predict) is Loan_Status, Yes and No are the values, let us convert to binary

train.1$Loan_Status=ifelse(train.1$Loan_Status=='N',0,1)
train.1$Loan_ID=NULL # deleting it from the dataset

# Converting categorical variables to numerical (dummy variables)
dummy.var= dummyVars(" ~ .", data = train.1,fullRank = T) #fullRank is used to make the variables start from zero
train.2 = data.frame(predict(dummy.var, newdata = train.1))
# making y a factor
train.2$Loan_Status=as.factor(train.2$Loan_Status)


#splitting the train into train and validation but also keeping the same ratio of y in both datasets

partition= createDataPartition(train.2$Loan_Status, p=0.75, list=FALSE)
train.3 = train.2[ partition,]
validation = train.2[-partition,]


# feature selection with Recursive Feature (crossvalidated)

feat.sel = rfeControl(functions = rfFuncs,
                      method = "repeatedcv", # crossval
                      repeats = 3,
                      verbose = FALSE)

y.variable='Loan_Status'
x.variables=names(train.3)[!names(train.3) %in% y.variable]
rec.feat= rfe(train.3[,x.variables], train.3[,y.variable],rfeControl = feat.sel) # takes a couple of mins
rec.feat 
# i ran feature selections different times and I took the top 6 variables
x.variables= c("Credit_History", "LoanAmount", "Loan_Amount_Term", "ApplicantIncome", "CoapplicantIncome","Property_Area.Semiurban")
# training four models

rf<-train(train.3[,x.variables],train.3[,y.variable],method='rf')
nnet<-train(train.3[,x.variables],train.3[,y.variable],method='nnet')
glm<-train(train.3[,x.variables],train.3[,y.variable],method='glm')
gbm=train(train.3[,x.variables],train.3[,y.variable],method='gbm')

#5-fold crossval (using in tunegrid later)
controll = trainControl(method = "repeatedcv",number = 5,repeats = 5)
#Creating grid for gbm (for parameter optimization)
grid = expand.grid(n.trees=c(10,20,50,100,500,1000),shrinkage=c(0.01,0.05,0.1,0.5),n.minobsinnode = c(3,5,10),interaction.depth=c(1,5,10))
# train gbm using tuneGrid (takes 12 mins)
gbm=train(train.3[,x.variables],train.3[,y.variable],method='gbm',trControl=controll,tuneGrid=grid)
# for the other models we use tuneLength (takes 7 minutes)
rf=train(train.3[,x.variables],train.3[,y.variable],method='rf',trControl=controll,tuneLength=10)
nnet=train(train.3[,x.variables],train.3[,y.variable],method='nnet',trControl=controll,tuneLength=10)
glm=train(train.3[,x.variables],train.3[,y.variable],method='glm',trControl=controll,tuneLength=10)



#GBM
print(gbm) 
gbm %>%
  plot()
# RF
print(rf) 
rf %>%
  plot()
#nnet
print(nnet) 
nnet %>%
  plot()
# GLM
print(glm) 
glm %>%
  plot()

#Variable Importance
print(gbm)
summary(gbm) 


print(nnet)
summary(nnet)
varImp(object=nnet)

print(rf)
summary(rf)
varImp(object=rf)

print(glm)
summary(glm)
varImp(object=glm)


#predictions on test : gbm

predictions.gbm=predict.train(object=gbm,validation[,x.variables],type="raw")

# conf matrix
confusionMatrix(predictions.gbm,validation[,y.variable])

# roc curve
roc.curve(validation[,y.variable], predictions.gbm)


#predictions on test : nnet

predictions.nnet=predict.train(object=nnet,validation[,x.variables],type="raw")

# conf matrix
confusionMatrix(predictions.nnet,validation[,y.variable])

# roc curve
roc.curve(validation[,y.variable], predictions.nnet)


#predictions on test : rf

predictions.rf=predict.train(object=rf,validation[,x.variables],type="raw")

# conf matrix
confusionMatrix(predictions.rf,validation[,y.variable])

# roc curve
roc.curve(validation[,y.variable], predictions.rf)



#predictions on test : glm

predictions.glm=predict.train(object=glm,validation[,x.variables],type="raw")
table(predictions.glm)
# conf matrix
confusionMatrix(predictions.glm,validation[,y.variable])

# roc curve
roc.curve(validation[,y.variable], predictions.glm)











































































































































































































