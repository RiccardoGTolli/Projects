library(caret)
# Read CSV (obtained from python) into R
DF <- read.csv(file="DF.csv", header=TRUE, sep=",")

#Variable encoding = blue team :0 , red team :1, no one: 3

# Split the  dataset into train and test (75% train and 25% test) 
# setting the seed for reproducibility 
set.seed(123)
sample0 <- sample.int(n = nrow(DF), size = floor(.75*nrow(DF)), replace = F)
train<- DF[sample0, ]
test<- DF[-sample0, ]
attach(DF)



# Logistic regression predicting the winner using First Blood as predictor
glm.train=glm(Winner~First.Blood ,data=train ,family=binomial)
summary (glm.train)
# get probabilities for every game
glm.train.probs=predict (glm.train ,newdata= test,type = "response")
# Recode factors
y_pred_num <- ifelse(glm.train.probs > 0.5, 1, 0)
y_pred <- factor(y_pred_num, levels=c(0, 1))
y_act <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred == y_act) #59%
#Confusion Matrix
dim(test)
#create vector of 12574 zero elements
glm.pred=rep("1" ,12574)
#changing the value of the vector when the probability in glm.DF.probs is >0.5
glm.pred[glm.train.probs <.5]=" 0"
# obtaining the confusion matrix
attach(test)
# table(glm.pred ,Winner ) # which is 59% as seen above
# append new column to test with the probabilities so that test can be taken to python, be split
# into correctly predicted and incorrectly. Then do descriptive statistics from there.
test["probabilities"]=glm.pred






# Doing same process with different predictors
# this model uses all the first objectives in the game to understand their impact
glm.train.1=glm(Winner~First.Blood+First.Tower+First.Inibitor+First.Baron+First.Dragon+First.Rift.Herald,data=train ,family=binomial)
summary (glm.train.1)
# get probabilities for every game
glm.train.1.probs=predict (glm.train.1 ,newdata= test,type = "response")
# Recode factors
y_pred_num1 <- ifelse(glm.train.1.probs > 0.5, 1, 0)
y_pred1 <- factor(y_pred_num1, levels=c(0, 1))
y_act1 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred1 == y_act1) #75%
#Confusion Matrix
dim(test)
#create vector of 12574 zero elements
glm.pred1=rep("1" ,12574)
#changing the value of the vector when the probability in glm.DF.probs1 is >0.5
glm.pred1[glm.train.1.probs <.5]=" 0"
# obtaining the confusion matrix
attach(test)
table(glm.pred1 ,Winner ) # which is 75% as seen above

# low coefficent and low z value on Firs.Rift.Herald, First.Baron is not looking too good,
# with an acceptable z value but lower than other predictors , it also has a relatively low impact
# doing this again without these two predictors. In general no predictor has a very high coefficent

glm.train.1=glm(Winner~First.Blood+First.Tower+First.Inibitor+First.Dragon,data=train ,family=binomial)
summary (glm.train.1)
# get probabilities for every game
glm.train.1.probs=predict (glm.train.1 ,newdata= test,type = "response")
# Recode factors
y_pred_num1 <- ifelse(glm.train.1.probs > 0.5, 1, 0)
y_pred1 <- factor(y_pred_num1, levels=c(0, 1))
y_act1 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred1 == y_act1) #75%
# accuracy still 75% , let's try to include First.Baron and remove  only Firs.Rift.Herald because it
# had unacceptable z score
glm.train.1=glm(Winner~First.Blood+First.Tower+First.Inibitor+First.Baron+First.Dragon,data=train ,family=binomial)
summary (glm.train.1)
# get probabilities for every game
glm.train.1.probs=predict (glm.train.1 ,newdata= test,type = "response")
# Recode factors
y_pred_num1 <- ifelse(glm.train.1.probs > 0.5, 1, 0)
y_pred1 <- factor(y_pred_num1, levels=c(0, 1))
y_act1 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred1 == y_act1) #75%
# 75% is the maximum possible with this set of predictors
#Confusion Matrix
dim(test)
#create vector of 12574 zero elements
glm.pred1=rep("1" ,12574)
#changing the value of the vector when the probability in glm.DF.probs1 is >0.5
glm.pred1[glm.train.1.probs <.5]=" 0"
# obtaining the confusion matrix
attach(test)
table(glm.pred1 ,Winner ) # which is 75% as seen above
# append probabilities to the test sample
test["probabilities1"]=glm.pred1







# this next logistic regression takes the total number of objectives for both teams
glm.train.2=glm(Winner~Team.1.Tower.Kills+Team.1.Inhibitor.Kills+Team.1.Baron.Kills+Team.1.Dragon.Kills+Team.1.Rift.Herald.Kills+Team.2.Tower.Kills+Team.2.Inhibitor.Kills+Team.2.Baron.Kills+Team.2.Dragon.Kills+Team.2.Rift.Herald.Kills+First.Blood+First.Tower+First.Inibitor+First.Baron+First.Dragon+First.Rift.Herald,data=train ,family=binomial)
summary(glm.train.2)
# get probabilities for every game
glm.train.2.probs=predict (glm.train.2 ,newdata= test,type = "response")
# Recode factors
y_pred_num2 <- ifelse(glm.train.2.probs > 0.5, 1, 0)
y_pred2 <- factor(y_pred_num1, levels=c(0, 1))
y_act2 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred2 == y_act2) #almost 97%
# accuracy extremely good but let us remove Team.1.Dragon.Kills and Team.2.Dragon.Kills because z value is unacceptable
glm.train.2=glm(Winner~Team.1.Tower.Kills+Team.1.Inhibitor.Kills+Team.1.Baron.Kills+Team.1.Rift.Herald.Kills+Team.2.Tower.Kills+Team.2.Inhibitor.Kills+Team.2.Baron.Kills+Team.2.Rift.Herald.Kills,data=train ,family=binomial)
summary(glm.train.2)
# get probabilities for every game
glm.train.2.probs=predict (glm.train.2 ,newdata= test,type = "response")
# Recode factors
y_pred_num2 <- ifelse(glm.train.2.probs > 0.5, 1, 0)
y_pred2 <- factor(y_pred_num1, levels=c(0, 1))
y_act2 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred2 == y_act2) #almost 97% , the model did not improve
#Confusion Matrix
dim(test)
#create vector of 12574 zero elements
glm.pred2=rep("1" ,12574)
#changing the value of the vector when the probability in glm.DF.probs2 is >0.5
glm.pred2[glm.train.2.probs <.5]=" 0"
# obtaining the confusion matrix
attach(test)
table(glm.pred2 ,Winner ) # which is almost 97% as seen above
# append probabilities to the test sample
test["probabilities2"]=glm.pred2






# Let's try a logistic regression with both the first objectives and the total objectives for both teams (not using the predictors that have given
# too low of a z value in past logistic regressions)
glm.train.3=glm(Winner~Team.1.Tower.Kills+Team.1.Inhibitor.Kills+Team.1.Baron.Kills+Team.1.Rift.Herald.Kills+Team.2.Tower.Kills+Team.2.Inhibitor.Kills+Team.2.Baron.Kills+Team.2.Rift.Herald.Kills,data=train ,family=binomial)
summary(glm.train.3)
# get probabilities for every game
glm.train.3.probs=predict (glm.train.3 ,newdata= test,type = "response")
# Recode factors
y_pred_num3 <- ifelse(glm.train.3.probs > 0.5, 1, 0)
y_pred3 <- factor(y_pred_num3, levels=c(0, 1))
y_act3 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred3 == y_act3) #almost 97% , the model did not improve significantly but only by 0.0000795 %
#Confusion Matrix
dim(test)
#create vector of 12574 zero elements
glm.pred3=rep("1" ,12574)
#changing the value of the vector when the probability in glm.DF.probs3 is >0.5
glm.pred3[glm.train.3.probs <.5]=" 0"
# obtaining the confusion matrix
attach(test)
table(glm.pred3 ,Winner ) # which is almost 97% as seen above
# append probabilities to the test sample
test["probabilities3"]=glm.pred3





# one last logistic regression using only the total barons, since during descriptive statistics this seemed like a very important factor in winning
glm.train.4=glm(Winner~Team.1.Baron.Kills+Team.2.Baron.Kills ,data=train ,family=binomial)
summary(glm.train.4)
# get probabilities for every game
glm.train.4.probs=predict (glm.train.4 ,newdata= test,type = "response")
# Recode factors
y_pred_num4 <- ifelse(glm.train.4.probs > 0.5, 1, 0)
y_pred4 <- factor(y_pred_num4, levels=c(0, 1))
y_act4 <- test$Winner
# Accuracy of train prediction on test 
mean(y_pred4 == y_act4) #72%
#Confusion Matrix
dim(test)
#create vector of 12574 zero elements
glm.pred4=rep("1" ,12574)
#changing the value of the vector when the probability in glm.DF.probs1 is >0.5
glm.pred4[glm.train.4.probs <.5]=" 0"
# obtaining the confusion matrix
attach(test)
table(glm.pred4 ,Winner ) #72%
# append probabilities to the test sample
test["probabilities4"]=glm.pred4







# as 97% accuracy for the model glm.train.3 seems to be unexpectedly high. We are going to perform 10-fold cross validation on the last linear regression
#changing the Winner column to factor
attach(DF)
DF$Winner=factor(DF$Winner)

class(Winner)

ctrl <- trainControl(method = "repeatedcv", number = 10, savePredictions = TRUE)

cross_val<- train(Winner ~ Team.1.Tower.Kills+Team.1.Inhibitor.Kills+Team.1.Baron.Kills+Team.1.Rift.Herald.Kills+Team.2.Tower.Kills+Team.2.Inhibitor.Kills+Team.2.Baron.Kills+Team.2.Rift.Herald.Kills,  data=DF, method="glm", family="binomial",trControl = ctrl, tuneLength = 5)

pred = predict(cross_val, newdata=test)
confusionMatrix(data=pred, test$Winner) # this function needs the library caret

# the model has still the same accuracy , note that by including Dragon the model predicts slighly less well which is exactly what it was 
# noticed during the logistic regression



# Random forest for the importance of variables
str(DF)
dim(DF)
class(DF$Winner)

library(randomForest)
sqrt(10) # initial formula for deciding mtry (number of predictors to consider at each tree splitting step)
set.seed(123) 
rand_for <-randomForest(Winner~Team.1.Tower.Kills+Team.1.Dragon.Kills+Team.1.Inhibitor.Kills+Team.1.Baron.Kills+Team.1.Rift.Herald.Kills+Team.2.Tower.Kills+Team.2.Inhibitor.Kills+Team.2.Baron.Kills+Team.2.Rift.Herald.Kills+Team.2.Dragon.Kills,data=DF, ntree=500,mtry=3) # this function needs the library randomForest
# find optimal mtry
# we need a dataset with only the predictors needed (all the cumulative  predictors which are total dragons,barons,tower kills, rift heralds, inibitors)
rf.DF <- DF[c(3,25:29,50:54)]
mtry <- tuneRF(rf.DF[-1],rf.DF$Winner, ntreeTry=500,stepFactor=1.5,improve=0.01, trace=TRUE, plot=TRUE)
best.m <- mtry[mtry[, 2] == min(mtry[, 2]), 1]
print(mtry)
print(best.m) # result is 2
# redo the random forest with optimal mtry
set.seed(123)
rand_for <-randomForest(Winner~Team.1.Tower.Kills+Team.1.Inhibitor.Kills+Team.1.Baron.Kills+Team.1.Dragon.Kills+Team.1.Rift.Herald.Kills+Team.2.Tower.Kills+Team.2.Inhibitor.Kills+Team.2.Baron.Kills+Team.2.Rift.Herald.Kills+Team.2.Dragon.Kills,data=DF, ntree=500,mtry=2) 
print(rand_for) #2.57& error rate which is almost the same as the logisitc regression error rate, important to notice that including the dragon in the Random Forest increases the accuracy of the model while the same predictor lowers the accuracy of logistic regression even if the gain/loss in prediction is extremely low
importance(rand_for)
varImpPlot(rand_for)

# Calculate Performance with a ROC curve
pred.rf=predict(rand_for,type = "prob")

library(ROCR)
perf.rf = prediction(pred.rf[,2], rf.DF$Winner)

# 1. Area under curve
auc = performance(perf.rf, "auc")
auc

# 2. True Positive and Negative Rate
pred.rf.3 = performance(perf.rf, "tpr","fpr")

# 3. Plot the ROC curve
plot(pred.rf.3,main="ROC Curve for Random Forest",col=2,lwd=2)
abline(a=0,b=1,lwd=2,lty=2,col="gray")

# ROC curve well above the diagonal and the area under the curve is very large and finally the line very closely follows the left margin.

write.csv(test, file = "testprobabilities.csv")


