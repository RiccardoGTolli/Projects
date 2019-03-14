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

# There are warnings saying that the task I am doing is too big  
# e.g.->"18/03/28 19:10:53 WARN scheduler.TaskSetManager: Stage 2 contains a task of very large size (27224 KB). The maximum recommended task size is 100 KB."


# The operation on sparkR 2.1.0 on the cluster are unbelieavly slow, I
# am trying to solve this by running parallel processing with the library
# "parallel"


# If I were to use spark R on apache spark 1.4.0 on the cluster (which seems faster)
# I wouldnt be able to go past  creating  the dataframe as NO machine learning
# algorithms are available on 1.4.0


# Split the  dataset into train and test 
trainTest <-randomSplit(DF.spark,c(0.7,0.3), 123)
train = trainTest[[1]]
test = trainTest[[2]]

# checking if sparkR is correctly detecting the train and test sets
head(select(train, train$First_Blood))

# Logistic regression predicting the winner using First Blood as predictor
spark.glm.train <- spark.logit(train, Winner ~ First_Blood, maxIter = 10, regParam = 0.3, elasticNetParam = 0.8)

# getting warnings of this kind :
#"spark.glm.train <- spark.logit(train, Winner ~ First_Blood, maxIter = 10, regP18/03/28 20:56:51 WARN scheduler.TaskSetManager: Stage 3 contains a task of very large size (27224 KB). The maximum recommended task size is 100 KB.
# 18/03/28 20:57:51 WARN scheduler.TaskSetManager: Stage 5 contains a task of very large size (27224 KB). The maximum recommended task size is 100 KB.
# 18/03/28 20:58:50 WARN scheduler.TaskSetManager: Stage 6 contains a task of very large size (27224 KB). The maximum recommended task size is 100 KB.
# 18/03/28 20:58:50 WARN netlib.BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeSystemBLAS
# 18/03/28 20:58:50 WARN netlib.BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeRefBLAS"


# With this same exact code at the beginning I was able to run it with no netlib.BLAS warnings and the code was running correctly but 
# at some point these errors started popping up and when I do the summary for the models all the coefficients are zero

# I am not sure if this is on my end or cluster's end because I am following the sparkR 2.1.0 documentation very closely


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



