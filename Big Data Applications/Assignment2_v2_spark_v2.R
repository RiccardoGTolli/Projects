# sparKR code

# logging on the dsm10 with ssh gtoll001@dsm10.doc.gold.ac.uk
# navigating to my folder with the data inside (precedently copied with a scp command)
# write sparkR , double tap TAB , write sparkR-21 to open sparkR for 
# apache spark 2.1.0


#start parallel process with half the number of cores
library(caret)
library(parallel)
cl=makeCluster((detectCores()*0.5))

# converting my R dataframe "DF" into sparkR dataframe 
DF <- read.csv(file="DF.csv", header=TRUE, sep=",")
DF.spark <-as.DataFrame(DF)

head(DF.spark)


# Split the  dataset into train and test 
trainTest <-randomSplit(DF.spark,c(0.7,0.3), 123)
train = trainTest[[1]]
test = trainTest[[2]]

# checking if sparkR is correctly detecting the train and test sets
head(select(train, train$First_Blood))

# Logistic regression predicting the winner using First Blood as predictor
spark.glm.train <- spark.logit(train, Winner ~ First_Blood, maxIter = 10, regParam = 0.3, elasticNetParam = 0.8)


# Model summary
summary(spark.glm.train)

# Prediction
glm.train.probs <- predict(spark.glm.train, test)
head(glm.train.probs)



# Logistic regression predicting the winner using all the first objectives in the game (beside Rift Herald that had low magnitude z value)
spark.glm.train1 <- spark.logit(train, Winner ~ First_Blood+First_Tower+First_Inibitor+First_Baron+First_Dragon, maxIter = 10, regParam = 0.3, elasticNetParam = 0.8)

# Model summary
summary(spark.glm.train1)

# Prediction
glm.train1.probs <- predict(spark.glm.train1, test)
head(glm.train1.probs)






# Logistic regression predicting the winner using total number of objectives for both teams
spark.glm.train2 <- spark.logit(train, Winner~Team_1_Tower_Kills+Team_1_Inhibitor_Kills+Team_1_Baron_Kills+Team_1_Rift_Herald_Kills+Team_2_Tower_Kills+Team_2_Inhibitor_Kills+Team_2_Baron_Kills+Team_2_Rift_Herald_Kills, maxIter = 10, regParam = 0.3, elasticNetParam = 0.8)

# Model summary
summary(spark.glm.train2)

# Prediction
glm.train2.probs <- predict(spark.glm.train2, test)
head(glm.train2.probs)





# Logistic regression predicting the winner using both the first objectives and the total objectives for both teams (not using the predictors that have given
# too low of a z value in past logistic regressions)
spark.glm.train3 <- spark.logit(train, Winner~Team_1_Tower_Kills+Team_1_Inhibitor_Kills+Team_1_Baron_Kills+Team_1_Rift_Herald_Kills+Team_2_Tower_Kills+Team_2_Inhibitor_Kills+Team_2_Baron_Kills+Team_2_Rift_Herald_Kills, maxIter = 10, regParam = 0.3, elasticNetParam = 0.8)

# Model summary
summary(spark.glm.train3)

# Prediction
glm.train3.probs <- predict(spark.glm.train3, test)
head(glm.train3.probs)




# Logistic regression predicting the winner using only the total barons
spark.glm.train4 <- spark.logit(train, Winner~Team_1_Baron_Kills+Team_2_Baron_Kills , maxIter = 10, regParam = 0.3, elasticNetParam = 0.8)

# Model summary
summary(spark.glm.train4)

# Prediction
glm.train4.probs <- predict(spark.glm.train4, test)
head(glm.train4.probs)



# Random forest for the importance of variables
spark.rand.for <- spark.randomForest(train, Winner ~ Team_1_Tower_Kills+Team_1_Dragon_Kills+Team_1_Inhibitor_Kills+Team_1_Baron_Kills+Team_1_Rift_Herald_Kills+Team_2_Tower_Kills+Team_2_Inhibitor_Kills+Team_2_Baron_Kills+Team_2_Rift_Herald_Kills+Team_2_Dragon.Kills, "classification", numTrees = 500)
summary(spark.rand.for)
pred.rf <- predict(spark.rand.for, test)
head(pred.rf)



