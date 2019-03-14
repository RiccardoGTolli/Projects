
library(reshape2)
library(ggplot2)
library(recommenderlab)
library(data.table)
library(dplyr)
library(proxy)
library(recosystem)
library(RColorBrewer)
library(plyr)
library(grid)
library(fpc)
library(cluster)

# loading the data from movies.csv and ratings.csv 
# (make sure the data files are in the R working folder)
rat.dat = read.csv("ratings.csv", header = TRUE) # can take a few minutes
mov.dat = read.csv("movies.csv",stringsAsFactors=FALSE)


# Reduce observations in terms of users. 
summary(rat.dat$userId)
# There are 270,896 users , each users has several movies watched therefore 260.242.89 rows
# which makes calculations extremely long. I will only use the last 1000 users 
# (I don't use the first 1000 because the last are the most recent data)
rat.dat.sub=filter(rat.dat,rat.dat$userId >= 269897)
summary(rat.dat.sub$userId)
dim(rat.dat.sub)
# With 1000 users (max-min) we end up with 96176 ratings observations

head(mov.dat)
dim(mov.dat)
summary(rat.dat.sub)
head(rat.dat.sub)
dim(rat.dat.sub)






# Recommender systems
# Content-based filtering on genres

# ratings are on a scale of 1 to 5 stars with 0.5 stars increments
# in order to simplify I will turn this 5 stars rating into a like/dislike system
# 1= like and -1= dislike
# this process takes takes a few minutes
likes <- rat.dat.sub
for (i in 1:nrow(likes)){
  if (likes[i,3] > 3){
    likes[i,3] = 1
  }
  else{
    likes[i,3] =  -1
  }
}

dim(likes)

# using dcast function to make likes into a wide format
likes.wide = dcast(likes, movieId~userId, value.var = "rating", na.rm=FALSE)
# changing the NA values to zero. This is because not every movie had been 
# liked or disliked 
for (i in 1:ncol(likes.wide)){
  likes.wide[which(is.na(likes.wide[,i]) == TRUE),i] = 0
}
likes.wide = likes.wide[,-1] #remove movieIds col.

dim(likes.wide)
# now likes.wide is a dataframe where the columns are unique users ids and the rows are movies ids
# this is the first matrix we need
# next I ll find the second matrix needed











# first removing all movies that have "(no genres listed as genre)"
mov.dat.2=filter(mov.dat,mov.dat$genres != "(no genres listed)")

# Getting a matrix with movie genres as columns and movies as rows
# in the mov.dat there are vertical lines (pipes) that separate genres
# for a given movie.
genreM=as.data.frame(mov.dat.2$genres, stringsAsFactors=FALSE)
genreMatrix= as.data.frame(tstrsplit(genreM[,1], '[|]', type.convert=TRUE), stringsAsFactors=FALSE, header=FALSE)
colnames(genreMatrix)= c(1:7)
# obtaining all the genres
list.genres=unique(genreMatrix$"1")
list.genres

# creating a matrix with all the genres as columns and all the movies as rows
dim(mov.dat.2)
# creating the skeleton of the matrix, rows and column names
genreMovieMatrix = matrix(0,43088,19) #43087 movies, 19 genres, need one extra row for the loop below
colnames(genreMovieMatrix) <- list.genres
# giving the first row the name of the genres in order to use the function "which" for the loop below that fills the cells
genreMovieMatrix[1,] = list.genres 
# filling the matrix with the movie genres (takes around 20 seconds)
for (n in 1:nrow(genreMatrix)) {
  for (i in 1:ncol(genreMatrix)) {
    colg = which(genreMovieMatrix[1,] == genreMatrix[n,i])
    genreMovieMatrix[n+1,colg] <- 1
  }
}
# make it a dataframe
genreMovieMatrix1 = as.data.frame(genreMovieMatrix[-1,], stringsAsFactors=FALSE)
# change all the columns to integers
for (i in 1:ncol(genreMovieMatrix1)) {
  genreMovieMatrix1[,i] = as.integer(genreMovieMatrix1[,i])
} 

dim(genreMovieMatrix1) 

# this matrix has columns as genres and rows as unique movies
# this is the second matrix needed










#This is to find a user matrix

#  need to remove the movies that havent been liked or disliked  from the genreMovieMatrix1
mIDnumber = length(unique(mov.dat.2$movieId)) 
mIDnumber # this is the number of all the unique movies (except the ones without a genre assigned)
rmIDnumber = length(unique(rat.dat.sub$movieId)) 
rmIDnumber # this is the number of all the unique movies present in the 
           # rating dataset (there are a lot less because I have reduced the dataset to a fraction of itself earlier)

# need to remove all the moviesIds (rows) in the mov.dat.2 that arent present
# in the rat.dat.sub . 
mov.dat.ld =mov.dat.2[-which((mIDnumber %in% rmIDnumber) == FALSE),]
rownames(mov.dat.ld) = NULL
#delete rows of unliked/undisliked movies from genreMovieMatrix2
genreMovieMatrix2 = genreMovieMatrix1[-which((mIDnumber %in% rmIDnumber) == FALSE),]
rownames(genreMovieMatrix2) <- NULL

# Here we want to find the user matrix. Which is found with
# the dot product of genreMovieMatrix2 and the likes.wide matrix
# this matrix shows if a user should watch a movie genre or not.
# columns are a userId rows are the genre, 1 is favorable toward that genre, 0 is unfavorable

dim(likes.wide) #columns are users ids and the rows are movies ids
dim (genreMovieMatrix2) # columns as genres and rows as movies ids

UserMatrix = matrix(0,19,1000)
for (i in 1:ncol(likes.wide)){
  for (n in 1:ncol(genreMovieMatrix2)){
    UserMatrix[n,i] = sum((genreMovieMatrix2[,n]) * (likes.wide[,i]))
  }
}


# Simplify the aggregate user likes and dislikes by making them binary
for (i in 1:nrow(UserMatrix)){
  for (n in 1:ncol(UserMatrix)){
    if (UserMatrix[i,n]<0){
      UserMatrix[i,n]=0
    }
    else{
      UserMatrix[i,n] =1
    }
  }
}



# UserMatrix. columns are a userID rows are genres
# if the value in a cell is positive it means that that user is more 
# inclined to watch that genre. If the value is negative, not inclined.
# this comes from the users ratings on various movies that they have already watched




# Measuring users similarity using Jaccard distance

# combining the genreMovieMatrix2 with UserMatrix then
# Jaccard distance between UserMatrix and the movies selected 
# (will only use selected movies because  using all the movies here gives me the error: "Error: cannot allocate vector of size 6.9 Gb"
# not ideal but I will simply remove most of the movies for this final step)
set.seed(123)
sample.genreMovieMatrix3= sample.int(n = nrow(genreMovieMatrix2), size = floor(.10*nrow(genreMovieMatrix2)), replace = F)
genreMovieMatrix3= genreMovieMatrix2[sample.genreMovieMatrix3, ]

# vector of liked/disliked genres for a specific user (first in this case)
UserMatrix2 =UserMatrix[,1] # changing this number will give prediction for different users
UserMatrix2
#combine genreMovieMatrix3 (movieIds by genres) with the vector above
sm = rbind.data.frame(UserMatrix2, genreMovieMatrix3)
#turn to integer
sm = data.frame(lapply(sm,function(x){as.integer(x)})) 
#Jaccard distance from vector to movies data in movie.dat.2
smr = dist(sm, method = "Jaccard")
smr = as.data.frame(as.matrix(smr[1:4308]))
#minimum distance between rows
minrows = which(smr == min(smr))
# These are the recommended movies for each user ( there aren't too many movies
# per recommendation simply because the movies list genreMovieMatrix2 had to
# be reduced artificially due to the vector too big error above).
mov.dat.2[minrows,]

# This method favors movies that have fewer genres attached to them, because
# it is easier to find similarity between users. To solve this we can apply a function to the values
# of genreMovieMatrix3 which is dividing each value by the square root of  the movie's
# total number of assigned genres.

# this changes the values in the genreMovieMatrix3 but I am not going forward with this method
# as it would require changing the Jaccard process above
for (i in 1:nrow(genreMovieMatrix3)){
  sqrtsum=sqrt(sum(genreMovieMatrix3[i,]))
  for (n in 1:ncol(genreMovieMatrix3)){
    if (genreMovieMatrix3[i,n]==1){   # this if-statement is superflous, but it optimized the computation
      genreMovieMatrix3[i,n]=genreMovieMatrix3[i,n]/sqrtsum
    }
  }
}



# Collaborative Filtering 
# clustering users on the basis of their behavior history and seek to recommend
# a movie that a similar user watched and liked

# first of all a rating matrix is needed
# cols are movieId and rows are userId
ratlab = dcast(rat.dat.sub, userId~movieId, value.var = "rating", na.rm=FALSE)
#remove userIds
ratlab = as.matrix(ratlab[,-1]) 
dim(ratlab)

# recommenderlab has pre-made functions and suggestions and will use one of them (Method: UBCFSimilarity Calculation Method: Cosine SimilarityNearest Neighbors: 30)

#Convert ratlab into a recommenderlab sparse matrix
ratlab = as(ratlab, "realRatingMatrix")
#Normalize data
nratlab = normalize(ratlab)


#using a recommenderlab standard procedure called UBFC 
ubfc = Recommender(nratlab, method = "UBCF", param=list(method="Cosine",nn=30))
#second row (user) as example for top 10 recommendations
ubfcpred = predict(ubfc, nratlab[2], n=10) # changing nratlab index number will change the user
ubfcpredlist = as(ubfcpred, "list")

#print recommendation list
topmoviesubfc = matrix(0,10)
for (i in c(1:10)){
  topmoviesubfc[i] = mov.dat.2[as.integer(ubfcpredlist[[1]][i]),2]
}
topmoviesubfc

# check performance with recommender lab functions
#5-fold cross validation with Given-1 protocol
perf <- evaluationScheme(ratlab, method="cross-validation", k=5, given=1, goodRating=5) 
perf2 <- evaluate(perf, method="UBCF", n=c(1,3,5,10,15,20))
confmatrx <- getConfusionMatrix(perf2)[[1]]
confmatrx
# this assesses performance of the top 1,3,5,10,15,20 recommender




# descriptive statistics

# histogram of how many times different ratings are selected
hist(rat.dat.sub$rating, main="Different Ratings", xlab="Ratings",ylab= "Frequency") # we can see that users don't generally favor half star ratings, full stars are more popular
mean(rat.dat.sub$rating) #3.44 which is 0.94 points away from the median

# histogram of user average scores and their frequency
hist.ratings= rat.dat.sub
hist.ratings=as.data.frame(hist.ratings)
hist.ratings$movieId = NULL
hist.ratings$timestamp = NULL
# dataframe with unique user ids as rows and all their ratings as one column
hist.ratings2 = ddply(hist.ratings, .(userId), summarize,ratings=paste(rating,collapse=",")) 
hist.ratings.vector=hist.ratings2$ratings
# ratings are characters, cannot calculate average from this
#retrieve a vector with all the computed averages
accumulator=vector(mode="numeric", length=0)
for (i in 1:nrow(hist.ratings2)){
  f= hist.ratings.vector[i]
  f=strsplit(f, split = ",")
  f=unlist(f, use.names=FALSE)
  f=as.numeric(f)
  avg=sum(f)/length(f)
  accumulator=append(accumulator, avg, after=length(accumulator))
  
}

# adding accumulator vector as new column in hist.ratings.2
hist.ratings2$avgratings=NA
hist.ratings2$avgratings=accumulator

# remove single ratings column
hist.ratings2$ratings = NULL
hist(hist.ratings2$avgratings,main="Average Ratings", xlab="Avg rating per user",ylab= "Frequency")
# density plot
d = density(hist.ratings2$avgratings)
plot(d, main="Average Ratings per user")
polygon(d, col="black", border="black")


# Movies with highest ratings

rat.dat.sub.high=rat.dat.sub
rat.dat.sub.high$timestamp=NULL
rat.dat.sub.high$userId=NULL
# dataframe with unique movie ids as rows and all their ratings from every user as one column
rat.dat.ratings2 = ddply(rat.dat.sub.high, .(movieId), summarize,ratings=paste(rating,collapse=",")) 
rat.dat.ratings.vector=rat.dat.ratings2$ratings
# ratings are characters, cannot calculate average from this
#retrieve a vector with all the computed averages
accumulator2=vector(mode="numeric", length=0)
for (i in 1:nrow(rat.dat.ratings2)){
  l= rat.dat.ratings.vector[i]
  l=strsplit(l, split = ",")
  l=unlist(l, use.names=FALSE)
  l=as.numeric(l)
  avg=sum(l)/length(l)
  accumulator2=append(accumulator2, avg, after=length(accumulator2))
  
}

head(accumulator2)

# adding accumulator vector as new column in rat.dat.ratings2
rat.dat.ratings2$avgratings=NA
rat.dat.ratings2$avgratings=accumulator2

# remove single ratings column
rat.dat.ratings2$ratings = NULL
hist(rat.dat.ratings2$avgratings)
# density plot
d2 <- density(rat.dat.ratings2$avgratings)
plot(d, main="Average Ratings per movies")
polygon(d, col="black", border="black")


# top movies by average user ratings
topmovies = rat.dat.ratings2[order(-rat.dat.ratings2$avgratings),] 
head(topmovies)
# bottom movies by average user ratings
bottmovies = rat.dat.ratings2[order(rat.dat.ratings2$avgratings),] 
head(bottmovies)
# movieId can be used in the dataframe mov.dat.2 to retrieve movie title
# in actuality there are many more movies with 0.5 and 5 average rating
# they are all sorted in topmovies and bottmovies, I chose to display the 
# top and bottom 6 for convenience purposes.

# to find out which movieId correspond to which movie title (this is because rows and movie id do not always match in movies.dat.2)
# for example movie 3165 "Boiling Point"is actually row 3080, the code below takes care of this
id.movie=3165 # can change this number depending on the movieId
mov.dat.2[mov.dat.2$movieId == id.movie, ] 


# Multiple genres are assigned to movies. Let us count how many times each genre has been counted
# to see what the most and least available genres are there.

#create dataframe with genres as columns and count of genres as rows
genre.count= genreMovieMatrix2[c(1),]
row.names(genre.count)="Count"

# Now need to retrieve the count for every genre
#v ector with all the genre counts in order
accumulator3=vector(mode="numeric", length=0)
for (i in 1:ncol(genreMovieMatrix2)){
  x=sum(genreMovieMatrix2[,i])
  accumulator3=append(accumulator3, x, after=length(accumulator3))
} # this dataframe has rows as movieIds and columns as genres. The cells have a 1 if the movie is assigned that genre or zero if not
accumulator3
genre.count[1,] = accumulator3
genre.count2=t(genre.count )
genre.count2
genre.count2=as.data.frame(genre.count2)
genre.count3=genre.count2[order(-genre.count2$Count),drop=FALSE,]
genre.count3 # ordered dataframe of genres and their total count
# bar chart of the genre counts
rownames.genre.count.3=rownames(genre.count3)
barplot(as.matrix(genre.count3), beside=TRUE,names.arg=c(1:19),horiz=TRUE,main="Distribution of Movie Genres",xlab="Count",ylab="Genres")



# Find the individual genre rankings
# Merge the 2 dataframes (mov.dat and rat.dat) into one using inner join on column movieId. This dataframe contains all the ratings for all the movies(this can take up to 3-5 minutes)
# do not want to sample it or some movies will not be seen
joined.mov.rat. = merge(mov.dat, rat.dat, all = "movieId", all.x = FALSE, all.y = FALSE)
# removing unnecessary columns
joined.mov.rat.$userId=NULL
joined.mov.rat.$timestamp=NULL
# aggregate the dataframe so that rows are single movies and the column rating is the average of all the ratings from all the users (not all movies have ratings)
require(plyr)
agg.movie.ratings1=ddply(joined.mov.rat.,.(movieId,genres),summarise,rating = mean(rating))
# need to know the average rating for each individual genre, not for combinations of it
# first need vector of all separate genres = (list.genres was used earlier)

# this for loop adds the avg rating in agg.movie.ratings1 for each genre to the vector in order (the order of the vector list.genres)
accumulator4=vector(mode="numeric", length=0)
inter.loop.accumulator=vector(mode="numeric", length=0)
for (i in 1:19){
  single.genre=list.genres[i]
  for (n in 1:nrow(agg.movie.ratings1)){
    if (grepl(single.genre, agg.movie.ratings1$genres[n])){ # this checks if a single genre is found in the string of all the ratings attached to a movie
      inter.loop.accumulator=append(inter.loop.accumulator,agg.movie.ratings1$rating[n],after=length(inter.loop.accumulator))
    }
  }
  avg1=mean(inter.loop.accumulator)
  accumulator4=append(accumulator4, avg1, after=length(accumulator4))
  inter.loop.accumulator=vector(mode="numeric", length=0)
  print(accumulator4)
}

accumulator4

# dataframe with single movie genre and its average rating across all users
single.genre.avg.rating=data.frame("Genre"=list.genres,"avgratings"=accumulator4 )



# ordered list of individual genres by average user ratings
single.genre.avg.rating.ordered=single.genre.avg.rating[order(-single.genre.avg.rating$avgratings),drop=FALSE,]
single.genre.avg.rating.ordered

# bar chart 
# change the name of the rows and drop the first column for the barplot function
row.names(single.genre.avg.rating.ordered) =single.genre.avg.rating.ordered$Genre
single.genre.avg.rating.ordered$Genre=NULL
barplot(as.matrix(single.genre.avg.rating.ordered), beside=TRUE,names.arg=c(1:19),horiz=TRUE,main="Movie genre average ratings",xlab="Count",ylab="Genres")






# K-means Clustering for movies with similar ratings
# sampling the rating dataset
set.seed(17)  
data = rat.dat[sample(1:nrow(rat.dat), 10000,replace=FALSE),]
agg = aggregate.data.frame(data$rating, by=list(data$movieId), FUN=mean, data = data) # dataframe with col= average ratings and rows= unique movie IDs
summary(agg)
#finding the centers  
kmc.data = kmeans(agg$x, centers=5)
kmc.data$centers # this are the centers of the 5 clusters
#visualizing the clustering  
plotcluster(agg, kmc.data$cluster)
clusplot(agg, kmc.data$cluster, color=TRUE, shade=TRUE, labels=2, lines=0)
  

# K-means Clustering for genres with similar ratings
set.seed(100)
kmc.data1 = kmeans(single.genre.avg.rating$avgrating, centers=5)
#finding the centers 
kmc.data1$centers
#visualizing the clustering  
clusplot(single.genre.avg.rating, kmc.data1$cluster, color=TRUE, shade=TRUE, labels=2, lines=0)




