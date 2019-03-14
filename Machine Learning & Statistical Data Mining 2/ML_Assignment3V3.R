# Gastone Riccardo Tolli
# ID: 33506151
# Group : Gastone Riccardo Tolli, Jeremy Ogg and See-hyun Park


library(mlbench)
library(caret)
#library(earth)
library(randomForest)
library(plyr)
library(forcats)
library(DMwR)
#library(mlr)
#library(smotefamily)
#library(party)
library(caret)
#library(ROSE)
library(glmnet)
library(e1071)
library(gbm)
#library(neuralnet)
library(pROC)


rm(list=ls())
#load datasets
trainX = read.table("train_X.csv", sep="\t",na.strings=c("","NA")) 
testX = read.table("test_X.csv",sep="\t",na.strings=c("","NA"))
trainY = read.table("train_Y.csv",sep="\t",header=TRUE)



#---------------------------------------------------------------------------------------------------------------
# 1. PRE-PROCESSING

# this .R script is the modeling for appetency only, therefore dropping the other y variables
trainY$churn=NULL
trainY$upselling=NULL




accumulator=vector(mode="numeric", length=0)
# checking class of variables to get an overview 
for (i in 1:ncol(trainX)){
  variables.class=class(trainX[,i])
  accumulator=append(accumulator, variables.class, after=length(accumulator))
}
accumulator # this vector has the class of all the columns ordered

# glue the vector trainY as a column of trainX
ncol(trainX)
trainX[,231]=trainY
ncol(trainX)



# remove columns with more than x% of NAs
trainX.1=trainX[, -which(colMeans(is.na(trainX)) > 0.20)]
testX.1=testX[, -which(colMeans(is.na(testX)) > 0.20)] 
# remove rows with more than x% of NAs without removing positive y observations 
# split positive obs and negative obs
# first order by appetency
trainX.1.ordered=trainX.1[order(-trainX.1$appetency), ]
# resetting the index
rownames(trainX.1.ordered) <- NULL
table(trainX.1$appetency)
trainX.1.positive=trainX.1.ordered[1:584, ]
trainX.1.negative=trainX.1.ordered[585:33001, ]
# remove negative rows with too many NAs
trainX.1.negative=trainX.1.negative[-which(rowMeans(is.na(trainX.1)) > 0.50), ]
# combine the train dataset again
trainX.1=rbind(trainX.1.negative, trainX.1.positive)
# shuffle dataset row-wise
trainX.1 <- trainX.1[sample(nrow(trainX.1)),]
# resetting the index
rownames(trainX.1) <- NULL




#Return row numbers for positive y
positive.y.rows=which(trainX.1$appetency == 1)
# how many positive y
length(table(positive.y.rows))






# check distribution of variable values
#for (i in 1:ncol(trainX.1)){
#   print(table(trainX.1[,i]))
#}


# checking class of variables to get an overview 
accumulator1=vector(mode="numeric", length=0)
for (i in 1:ncol(trainX.1)){
  variables.class.1=class(trainX.1[,i])
  accumulator1=append(accumulator1, variables.class.1, after=length(accumulator1))
}
#accumulator1 # this vector has the class of all the columns ordered
table(accumulator1)




# remove features that have almost constant values (feature 2,7,11,14,21,28,36,63,66)
# before removing a column checking  if its  particularly correlated with  y
table(trainX.1[,36])# <-I am changin the number to check
colnames(trainX.1)[36]# <-I am changin the number to check
trainX.2.ordered=trainX.1[which(trainX.1$V128!= "uKAI"), ]# <-I am changin the value to check (dominant category goes here)
trainX.3.ordered=trainX.1[which(trainX.1$V128== "uKAI"), ]# <-I am changin the value to check (dominant category goes here)
table(trainX.2.ordered$appetency)
table(trainX.3.ordered$appetency)

table(trainX.2$appetency)

# almost all columns respected the 0.5% ratio between neg and pos y.
# therefore removing all of them


trainX.2 = trainX.1[, -c(2,7,11,14,21,28,36,63,66)]
testX.2 = testX.1[, -c(2,7,11,14,21,28,36,63,66)]
# check for distribution of values in Y variable
table(trainX.2$appetency) # heavily unbalanced
trainX.2$appetency=as.factor(trainX.2$appetency)
# drop unused levels in factor variables
trainX.2 <- droplevels(trainX.2)
testX.2<- droplevels(testX.2)




accumulator1=vector(mode="numeric", length=0)
# checking class of variables to get an overview 
for (i in 1:ncol(trainX.2)){
  variables.class=class(trainX.2[,i])
  accumulator1=append(accumulator1, variables.class, after=length(accumulator1))
}
accumulator1 # this vector has the class of all the columns ordered


# Filling NAs:for numeric and integer columns compute the mean or median depending on if they have large outliers
# checking which column has outliers
OutVals = boxplot(trainX.2[,11]) # I change the number here to visualize the boxplot for different columns

# Create mode function Without Nas
getmode <- function(v) {
  uniqv <- na.omit(unique(v))
  uniqv[which.max(tabulate(match(v, uniqv)))]
}
# Create median function without NAs
medianWithoutNA<-function(x) {
  median(x[which(!is.na(x))])
}

# there are outliers everywhere, doing the median for all integer and numeric columns (can take a few mins)
for (n in 1:ncol(trainX.2)){
  if (is.numeric(trainX.2[,n]) |is.integer(trainX.2[,n])){
    for (i in 1:length(trainX.2[,n])){
      if(is.na(trainX.2[i,n])){
        median.value=medianWithoutNA(trainX.2[,n])
        trainX.2[i,n]=median.value
        
      }
    }
  }
}

# Filling NA:for factors compute the mode

for (n in 1:ncol(trainX.2)){
  if (is.factor(trainX.2[,n])){
    for (i in 1:length(trainX.2[,n])){
      if(is.na(trainX.2[i,n])){
        mode=getmode(trainX.2[,n])
        trainX.2[i,n]=mode
        
      }
    }
  }
}

# Doing the same for test set

# there are outliers everywhere, doing the median for all integer and numeric columns
for (n in 1:ncol(testX.2)){
  if (is.numeric(testX.2[,n]) |is.integer(testX.2[,n])){
    for (i in 1:length(testX.2[,n])){
      if(is.na(testX.2[i,n])){
        median.value=medianWithoutNA(testX.2[,n])
        testX.2[i,n]=median.value
        
      }
    }
  }
}

# Filling NA:for factors compute the mode

for (n in 1:ncol(testX.2)){
  if (is.factor(testX.2[,n])){
    for (i in 1:length(testX.2[,n])){
      if(is.na(testX.2[i,n])){
        mode=getmode(testX.2[,n])
        testX.2[i,n]=mode
        
      }
    }
  }
}






# check wether all NAs have been removed
check.NA.trainX.2=apply(trainX.2, 2, function(x) any(is.na(x)))
unique(check.NA.trainX.2)
check.NA.testX.2=apply(testX.2, 2, function(x) any(is.na(x)))
unique(check.NA.testX.2)
# resetting the index
rownames(trainX.2) <- NULL







#extract and store y variable
trainY.2=trainX.2[,58]
trainX.3=trainX.2[,-58] # not including Y variable
testX.3=testX.2
length(trainY.2)

# the following variables V29,V90,V93,V116,V118,V119,V138,V154,V156,V165,V187,V190,V224,V230
# have too many levels. Replace the least frequent levels with "else"

# get indices of the columns in order to change their factor levels
too.many.levels.var=c("V29","V90","V93","V116","V118","V119","V138","V154","V156","V165","V187","V190","V224")
too.many.levels.var.indeces=which(names(trainX.3) %in% too.many.levels.var)
too.many.levels.var.indeces
# changing the levels of those variables above
for (i in too.many.levels.var.indeces){
  res <- table(trainX.3[,i])
  notkeep <- names(res[res < 450])
  keep <- names(res)[!names(res) %in% notkeep]
  names(keep) <- keep
  #set new levels
  levels(trainX.3[,i]) <- c(keep, list("else" = notkeep))
}




# now need to change it for testX too 
# going to do it separately for each column because each of them has different levels(not elegant solution but it works)

# V29
train.X.3.levels=levels(trainX.3$V29)
test.X.3.levels=levels(testX.3$V29)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V29)){
  if (!(is.element(testX.3$V29[i], train.X.3.levels))){
    testX.3$V29[i]=NA
  }
}
# V90
train.X.3.levels=levels(trainX.3$V90)
test.X.3.levels=levels(testX.3$V90)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V90)){
  if (!(is.element(testX.3$V90[i], train.X.3.levels))){
    testX.3$V90[i]=NA
  }
}
# V93
train.X.3.levels=levels(trainX.3$V93)
test.X.3.levels=levels(testX.3$V93)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V93)){
  if (!(is.element(testX.3$V93[i], train.X.3.levels))){
    testX.3$V93[i]=NA
  }
}
# V116
train.X.3.levels=levels(trainX.3$V116)
test.X.3.levels=levels(testX.3$V116)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V116)){
  if (!(is.element(testX.3$V116[i], train.X.3.levels))){
    testX.3$V116[i]=NA
  }
}
# V118
train.X.3.levels=levels(trainX.3$V118)
test.X.3.levels=levels(testX.3$V118)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V118)){
  if (!(is.element(testX.3$V118[i], train.X.3.levels))){
    testX.3$V118[i]=NA
  }
}
# V119
train.X.3.levels=levels(trainX.3$V119)
test.X.3.levels=levels(testX.3$V119)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V119)){
  if (!(is.element(testX.3$V119[i], train.X.3.levels))){
    testX.3$V119[i]=NA
  }
}
# V138
train.X.3.levels=levels(trainX.3$V138)
test.X.3.levels=levels(testX.3$V138)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V138)){
  if (!(is.element(testX.3$V138[i], train.X.3.levels))){
    testX.3$V138[i]=NA
  }
}
# V154
train.X.3.levels=levels(trainX.3$V154)
test.X.3.levels=levels(testX.3$V154)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V154)){
  if (!(is.element(testX.3$V154[i], train.X.3.levels))){
    testX.3$V154[i]=NA
  }
}
# V156
train.X.3.levels=levels(trainX.3$V156)
test.X.3.levels=levels(testX.3$V156)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V156)){
  if (!(is.element(testX.3$V156[i], train.X.3.levels))){
    testX.3$V156[i]=NA
  }
}
# V165
train.X.3.levels=levels(trainX.3$V165)
test.X.3.levels=levels(testX.3$V165)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V165)){
  if (!(is.element(testX.3$V165[i], train.X.3.levels))){
    testX.3$V165[i]=NA
  }
}

# V187
train.X.3.levels=levels(trainX.3$V187)
test.X.3.levels=levels(testX.3$V187)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V187)){
  if (!(is.element(testX.3$V187[i], train.X.3.levels))){
    testX.3$V187[i]=NA
  }
}
# V190
train.X.3.levels=levels(trainX.3$V190)
test.X.3.levels=levels(testX.3$V190)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V190)){
  if (!(is.element(testX.3$V190[i], train.X.3.levels))){
    testX.3$V190[i]=NA
  }
}
# V224
train.X.3.levels=levels(trainX.3$V224)
test.X.3.levels=levels(testX.3$V224)
# place NAs , then later substitute with "else"
for (i in 1:length(testX.3$V224)){
  if (!(is.element(testX.3$V224[i], train.X.3.levels))){
    testX.3$V224[i]=NA
  }
}
#drop unused levels
trainX.3=droplevels(trainX.3)
testX.3=droplevels(testX.3)

# the columns 118 ,138 ,224 have an extremely high amount of levels
# if the name of the variables was known I could have changed the variables in a better way
# for example if one of the variables is height, and it is encoded as factor I could have created 
# height brakets or made it a numerical variable. But since the names of the variables is unknown
# I will remove these three columns as they will be a problem in algorithms such as random forest
trainX.3=trainX.3[,-c(25,31,57)]
testX.3=testX.3[,-c(25,31,57)]


#Change else to to else1, else 2.... for the modified columns trainX.3 
# which are "V29","V90","V93","V116","V119","V154","V156","V165","V187","V190",)

trainX.3$V29=revalue(trainX.3$V29, c("else"="elseV29"))
trainX.3$V90=revalue(trainX.3$V90, c("else"="elseV90"))
trainX.3$V93=revalue(trainX.3$V93, c("else"="elseV93"))
trainX.3$V116=revalue(trainX.3$V116, c("else"="elseV116"))
trainX.3$V119=revalue(trainX.3$V119, c("else"="elseV119"))
trainX.3$V154=revalue(trainX.3$V154, c("else"="elseV154"))
trainX.3$V156=revalue(trainX.3$V156, c("else"="elseV156"))
trainX.3$V165=revalue(trainX.3$V165, c("else"="elseV165"))
trainX.3$V187=revalue(trainX.3$V187, c("else"="elseV187"))
trainX.3$V190=revalue(trainX.3$V190, c("else"="elseV190"))



#Change NAs to else1,else2... for the modified columns in testX.3
# which are "V29","V90","V93","V116","V119","V154","V156","V165","V187","V190",)
testX.3$V29=fct_explicit_na(testX.3$V29,"elseV29")
testX.3$V90=fct_explicit_na(testX.3$V90,"elseV90")
testX.3$V93=fct_explicit_na(testX.3$V93,"elseV93")
testX.3$V116=fct_explicit_na(testX.3$V116,"elseV116")
testX.3$V119=fct_explicit_na(testX.3$V119,"elseV119")
testX.3$V154=fct_explicit_na(testX.3$V154,"elseV154")
testX.3$V156=fct_explicit_na(testX.3$V156,"elseV156")
testX.3$V165=fct_explicit_na(testX.3$V165,"elseV165")
testX.3$V187=fct_explicit_na(testX.3$V187,"elseV187")
testX.3$V190=fct_explicit_na(testX.3$V190,"elseV190")





# reattach y variable to trainX.3
trainX.3[,55]=trainY.2 # name of y variable is now V55.1



# checking class of variables to get an overview 
accumulator3=vector(mode="numeric", length=0)
for (i in 1:ncol(trainX.2)){
  variables.class.2=class(trainX.2[,i])
  accumulator3=append(accumulator3, variables.class.2, after=length(accumulator3))
}
#accumulator3 # this vector has the class of all the columns ordered
table(accumulator3)
accumulator3




#------------------------------------------------------------------------------------
# 2. DEALING WITH IMBALANCED DATA
# SMOTE

# Apply SMOTE only to a partition of the trainX.3 and keep a test (from trainX.3 not SMOTEd in order to test the models later)
# sample
set.seed(123)
sample0 <- sample.int(n = nrow(trainX.3), size = floor(.75*nrow(trainX.3)), replace = F)
s.trainX<- trainX.3[sample0, ]
s.testX<- trainX.3[-sample0, ]

# apply SMOTE 


attach(s.trainX)
require(DMwR)
ncols<-ncol(s.trainX)

set.seed(100)
dmSmote<-SMOTE(V55.1 ~ . , s.trainX,k=5,perc.over = 3200,perc.under=125) #  tuning perc.over and per.under to reach roughly 50%
s.trainX<-cbind(dmSmote[ncols],dmSmote[1:ncols-1])
dim(s.trainX)
dim(trainX.3)
table(trainX.3[,55]) # before smote
table(s.trainX[,1]) # after smote


# remove too many decimals in numeric columns for s.trainX and s.testX
is.num <- sapply(s.trainX, is.numeric)
s.trainX[is.num] <- lapply(s.trainX[is.num], round, 4)


is.num <- sapply(s.testX, is.numeric)
s.testX[is.num] <- lapply(s.testX[is.num], round, 4)


#table(s.trainX$V55.1)



# Making sure all columns of test and train have the same levels
s.testX=droplevels(s.testX)
s.trainX=droplevels(s.trainX)

s.testX <- rbind(s.trainX[1, ] ,s.testX)
s.testX <- s.testX[-1,]
rownames(s.testX) <- NULL

s.trainX=rbind(s.testX[1,], s.trainX)
s.trainX<-s.trainX[-1,]
rownames(s.testX) <- NULL


#-------------------------------------------------------------------------------------------------------
# 3. MODELING AND FEATURE EXTRACTION

# 3.1 Logistic Regression


# define training control
#train_control<- trainControl(method="cv", number=2)

# train the model 
#glm.train<- train(x=s.trainX[,2:55],y=s.trainX[,1], trControl=train_control, method="glm", family=binomial())
# results are actually worse with Crossvalidation

# remove V196 and V204 because they have levels with such few observations that the train set has them but not the test set

s.trainX$V196=NULL
s.testX$V196=NULL
s.trainX$V204=NULL
s.testX$V204=NULL
# model fit(without crossvalidation)
glm.train = glm(s.trainX$V55.1~.,s.trainX,family = binomial)
#summary(glm.train)
# get probabilities
glm.train.probs=predict (glm.train ,newdata= s.testX,type = "response")   
y_pred_num <- ifelse(glm.train.probs > 0.5, 1, -1)
y_pred <- factor(y_pred_num, levels=c(-1, 1))
y_act <- s.testX$V55.1
#Confusion Matrix
dim(s.testX)
#create vector of n "1" elements
glm.pred=rep("1" ,7441)
#changing the value of the vector when the probability in glm.DF.probs is >0.5
glm.pred[glm.train.probs <.5]="-1"
# obtaining the confusion matrix
table(glm.pred ,s.testX$V55.1 )








# defining the auc trapezoid function
trapezoid.auc= function (sensitivity,specificity){
  return((specificity*(1-sensitivity))/2+(sensitivity*(1-specificity))/2+(sensitivity*specificity))
}


# Checking the following metrics on the prediction model
glm.results <- confusionMatrix(y_pred,  s.testX$V55.1)
glm.accuracy <- glm.results$overall[1]
glm.kappa <- glm.results$overall[2]
glm.sensitivity <- as.numeric(glm.results$byClass[1])
glm.spec <- as.numeric(glm.results$byClass[2])
glm.AUC <- trapezoid.auc(glm.sensitivity, glm.spec)
glm.results
glm.accuracy
glm.kappa
glm.sensitivity
glm.spec
glm.AUC


glm.pred.1 <- predict(glm.train, s.testX[,2:53], type="response")
#Plotting the ROC curve
gbm.ROC <- roc(s.testX[,1], glm.pred.1,levels = levels(s.testX[,1]))
plot(gbm.ROC, legacy.axes=TRUE, col='black', xlim=c(1,0), ylim=c(0,1)) 
# Finding threshold by post processing
gbm.topleft <- coords(gbm.ROC, x = "best", ret="threshold", best.method="closest.topleft") # closest.topleft, youden
gbm.results.topleft <- factor(ifelse(glm.pred.1 > gbm.topleft,
                                     "1", "-1"),levels = levels(s.testX[,1]))
# threshold
gbm.topleft

# checking the metrics with the new threshold
final.result <- confusionMatrix(gbm.results.topleft, s.testX[,1])
glm.accuracy <- final.result$overall[1]
glm.kappa <- final.result$overall[2]
glm.sensitivity <- as.numeric(final.result$byClass[1])
glm.spec <- as.numeric(final.result$byClass[2])
glm.AUC <- trapezoid.auc(glm.sensitivity, glm.spec)
glm.accuracy
glm.kappa
glm.sensitivity
glm.spec
glm.AUC






# 3.2 Logistic regression with selected variables

# using z and p value, I extracted the best features
log.reg.removed.features=c("V15","V21","V42","V71","V75","V79","V81","V95","V101","V107","V115","V121","V124","V125","V134","V141","V143","V150","V151","V154","V155","V156","V161","V165","V168","V190","V191","V192","V202","V206")
log.reg.removed.features.indeces=which(names(s.trainX) %in% log.reg.removed.features)
log.reg.removed.features.indeces
# create dataframe with only those variables
log.reg.selected.df=s.trainX[,-log.reg.removed.features.indeces]
#same for test set
test.log.reg.selected.df=s.testX[,-log.reg.removed.features.indeces]
# redo log reg with these variables only

# model fit
glm.train = glm(log.reg.selected.df$V55.1~.,log.reg.selected.df,family = binomial)
#summary(glm.train)
# get probabilities
glm.train.probs=predict (glm.train ,newdata= test.log.reg.selected.df,type = "response")
# Recode factors
y_pred_num <- ifelse(glm.train.probs > 0.5, 1, -1)
y_pred <- factor(y_pred_num, levels=c(-1, 1))
y_act <- test.log.reg.selected.df$V55.1
#Confusion Matrix
dim(test.log.reg.selected.df)
#create vector of n "1" elements
glm.pred=rep("1" ,7441)
#changing the value of the vector when the probability in glm.DF.probs is >0.5
glm.pred[glm.train.probs <.5]="-1"
# obtaining the confusion matrix
table(glm.pred ,test.log.reg.selected.df$V55.1 )


# Checking the following metrics on the prediction model
glm.results <- confusionMatrix(y_pred,  test.log.reg.selected.df$V55.1)
glm.accuracy <- glm.results$overall[1]
glm.kappa <- glm.results$overall[2]
glm.sensitivity <- as.numeric(glm.results$byClass[1])
glm.spec <- as.numeric(glm.results$byClass[2])
glm.AUC <- trapezoid.auc(glm.sensitivity, glm.spec)
glm.results
glm.accuracy
glm.kappa
glm.sensitivity
glm.spec
glm.AUC

glm.pred.1 <- predict(glm.train, test.log.reg.selected.df[,2:23], type="response")
#Plotting the ROC curve
gbm.ROC <- roc(s.testX[,1], glm.pred.1,levels = levels(s.testX[,1]))
plot(gbm.ROC, legacy.axes=TRUE, col='black', xlim=c(1,0), ylim=c(0,1)) 
# Finding threshold by post processing
gbm.topleft <- coords(gbm.ROC, x = "best", ret="threshold", best.method="closest.topleft") # closest.topleft, youden
gbm.results.topleft <- factor(ifelse(glm.pred.1 > gbm.topleft,
                                     "1", "-1"),levels = levels(s.testX[,1]))
# threshold
gbm.topleft

# checking the metrics with the new threshold
final.result <- confusionMatrix(gbm.results.topleft, s.testX[,1])
glm.accuracy <- final.result$overall[1]
glm.kappa <- final.result$overall[2]
glm.sensitivity <- as.numeric(final.result$byClass[1])
glm.spec <- as.numeric(final.result$byClass[2])
glm.AUC <- trapezoid.auc(glm.sensitivity, glm.spec)
glm.accuracy
glm.kappa
glm.sensitivity
glm.spec
glm.AUC




# this model is selected for submission, testing it on original test set


rownames(testX.3) <- NULL
rownames(log.reg.selected.df) <- NULL


# remove extra predictors from testX.3 by name
testX.4=testX.3
testX.4$V15=NULL
testX.4$V21=NULL
testX.4$V42=NULL
testX.4$V71=NULL
testX.4$V75=NULL
testX.4$V79=NULL
testX.4$V81=NULL
testX.4$V95=NULL
testX.4$V101=NULL
testX.4$V107=NULL
testX.4$V115=NULL
testX.4$V121=NULL
testX.4$V124=NULL
testX.4$V125=NULL
testX.4$V134=NULL
testX.4$V141=NULL
testX.4$V143=NULL
testX.4$V150=NULL
testX.4$V151=NULL
testX.4$V154=NULL
testX.4$V155=NULL
testX.4$V156=NULL
testX.4$V161=NULL
testX.4$V165=NULL
testX.4$V168=NULL
testX.4$V190=NULL
testX.4$V191=NULL
testX.4$V192=NULL
testX.4$V196=NULL
testX.4$V202=NULL
testX.4$V204=NULL
testX.4$V206=NULL




# model fit(without crossvalidation)
# model fit
glm.train = glm(log.reg.selected.df$V55.1~.,log.reg.selected.df,family = binomial)
#summary(glm.train)



# get probabilities
glm.train.probs=predict (glm.train ,newdata= testX.4,type = "response")   
# changing probabilities to outcomes using the threshold obtained through the trapezoid AUC
# threshold
gbm.topleft

y_pred_num <- ifelse(glm.train.probs > gbm.topleft, 1, -1)
y_pred <- factor(y_pred_num, levels=c(-1, 1))
table(y_pred)

# create prediction csv file
write.table(y_pred, file = "appetency.final.csv",row.names=FALSE, sep=",",col.names="appetency")




# 3.3 Random Forest


sqrt(55) # rough formula for deciding mtry (number of predictors to consider at each tree splitting step) is the square root of the number of predictors


optimal.mtry=tuneRF(x=s.trainX[,-1], y=s.trainX$V55.1, mtryStart=7, ntreeTry=500, stepFactor=1, improve=0.05,
       trace=TRUE, plot=TRUE, doBest=TRUE)
#importance(optimal.mtry)
varImpPlot(optimal.mtry)




rand.for.probs = predict(optimal.mtry, newdata=s.testX, type="response")
# get conf matrix
y_act <- s.testX$V55.1
#Confusion Matrix
dim(s.testX)
#create vector of n "1" elements
rf.pred=rep("1" ,7441)
#changing the value of the vector when the prediction in rand.for.probs  =-1
rf.pred[rand.for.probs ==-1]="-1"
# obtaining the confusion matrix
table(rf.pred ,s.testX$V55.1)

# this model looks less promising than the first logistic regression, not going further with this




# 3.4 Support Vector Machine


#Fit model

model_svm <- svm(s.trainX$V55.1 ~ . , s.trainX)

#Use the predictions on the test

pred <- predict(model_svm,s.testX)

# get conf matrix
y_act <- s.testX$V55.1
#Confusion Matrix
dim(s.testX)
#create vector of n "1" elements
SVM.pred=rep("1" ,7441)
#changing the value of the vector when the prediction in pred =-1
SVM.pred[pred ==-1]="-1"
# obtaining the confusion matrix
table(SVM.pred ,s.testX$V55.1) 


# Plotting the ROC curve SVM
SVM.results <- confusionMatrix(pred,  s.testX$V55.1)
SVM.accuracy <- SVM.results$overall[1]
SVM.kappa <- SVM.results$overall[2]
SVM.sensitivity <- as.numeric(SVM.results$byClass[1])
SVM.spec <- as.numeric(SVM.results$byClass[2])
SVM.AUC <- trapezoid.auc(SVM.sensitivity, SVM.spec)
SVM.results
SVM.accuracy
SVM.kappa
SVM.sensitivity
SVM.spec
SVM.AUC





# 3.5 GBM


# Tuning GBM
getModelInfo()$gbm$parameters
library(doParallel)

# Set up training control
ctrl <- trainControl(method = "repeatedcv",   # 10fold cross validation
                     number = 5,							# do 5 repetitions of cv
                     summaryFunction=twoClassSummary,	# Use AUC to pick the best model
                     classProbs=TRUE,
                     allowParallel = TRUE)


# Use the expand.grid to specify the search space	


grid <- expand.grid(interaction.depth=c(7,10.15,20,25), 
                    n.trees=c(1750,2000,2250,2500,2750,3000),	        
                    shrinkage=c(0.1),		
                    n.minobsinnode = c(50,70,75,85,90))

										
set.seed(1951)  # set the seed

# Set up to do parallel processing   
registerDoParallel(4)		# Registrer a parallel backend for train
getDoParWorkers()

# changing the levels of response vriable because GBM tune needs this
GBM.s.trainX=s.trainX
levels(GBM.s.trainX$V55.1) <- c("No", "Yes")


gbm.tune <- train(x=GBM.s.trainX[2:53],y=GBM.s.trainX$V55.1,
                  method = "gbm",
                  metric = "ROC",
                  trControl = ctrl,
                  tuneGrid=grid,
                  verbose=FALSE)






# Look at the tuning results

gbm.tune$bestTune
plot(gbm.tune)  		# Plot the performance of the training model
res <- gbm.tune$results
res


# load the Log Loss function
LogLossBinary = function(actual, predicted, eps = 1e-15) {  
  predicted = pmin(pmax(predicted, eps), 1-eps)  
  - (sum(actual * log(predicted) + (1 - actual) * log(1 - predicted))) / length(actual)
}



# recode factor levels because the method bernoulli in GBM needs this

s.trainX.GBM=s.trainX
s.testX.GBM=s.testX
levels(s.trainX.GBM$V55.1)<- c("0","1")
levels(s.testX.GBM$V55.1)<- c("0","1")
# turn response variables into characters because the extraction of prediction on the model needs this

s.trainX.GBM$V55.1=as.character(s.trainX.GBM$V55.1)

# fit model


gbmModel = gbm(formula = s.trainX.GBM$V55.1 ~ .,
               distribution = "bernoulli",
               data = s.trainX.GBM,
               n.trees = 3000,
               shrinkage = .01,
               n.minobsinnode = 100,
               interaction.depth=7)



# predictions
gbmTrainPredictions = predict(object = gbmModel,
                              newdata = s.testX.GBM,
                              n.trees = 3000,
                              type = "response")

# rechange levels
levels(s.trainX.GBM$V55.1)<- c("-1","1")
levels(s.testX.GBM$V55.1)<- c("-1","1")
# Recode factors
y_pred_num <- ifelse(gbmTrainPredictions > 0.5, 1, -1)
y_pred <- factor(y_pred_num, levels=c(-1, 1))
y_act <- s.testX.GBM$V55.1
#Confusion Matrix
dim(s.testX.GBM)
#create vector of n "1" elements
GMB.pred=rep("1" ,7441)
#changing the value of the vector when the probability in glm.DF.probs is >0.5
GMB.pred[gbmTrainPredictions <.5]="-1"
# obtaining the confusion matrix
table(GMB.pred ,s.testX.GBM$V55.1 ) 

# Plotting the ROC curve GBM
GBM.results <- confusionMatrix(y_pred,  s.testX.GBM$V55.1)
GBM.accuracy <- GBM.results$overall[1]
GBM.kappa <- GBM.results$overall[2]
GBM.sensitivity <- as.numeric(GBM.results$byClass[1])
GBM.spec <- as.numeric(GBM.results$byClass[2])
GBM.AUC <- trapezoid.auc(GBM.sensitivity, GBM.spec)
GBM.results
GBM.accuracy
GBM.kappa
GBM.sensitivity
GBM.spec
GBM.AUC

table(y_pred_num)


GBM.pred.1 <- predict(gbmModel, s.testX[,2:55], type="response",n.trees = 20)
#Plotting the ROC curve
GBM.ROC <- roc(s.testX[,1], GBM.pred.1,levels = levels(s.testX[,1]))
plot(GBM.ROC, legacy.axes=TRUE, col='black', xlim=c(1,0), ylim=c(0,1)) 
# Finding threshold by post processing
GBM.topleft <- coords(GBM.ROC, x = "best", ret="threshold", best.method="closest.topleft") # closest.topleft, youden
GBM.results.topleft <- factor(ifelse(GBM.pred.1 > GBM.topleft,
                                     "1", "-1"),levels = levels(s.testX[,1]))
# threshold
GBM.topleft

# checking the metrics with the new threshold
final.result <- confusionMatrix(GBM.results.topleft, s.testX[,1])
GBM.accuracy <- final.result$overall[1]
GBM.kappa <- final.result$overall[2]
GBM.sensitivity <- as.numeric(final.result$byClass[1])
GBM.spec <- as.numeric(final.result$byClass[2])
GBM.AUC <- trapezoid.auc(GBM.sensitivity, GBM.spec)
GBM.accuracy
GBM.kappa
GBM.sensitivity
GBM.spec
GBM.AUC













