
# website where the data is being retrieved from https://finance.yahoo.com/sector/technology

library(quantmod)  
library(stringr)    
library(forcats)    
library(lubridate)  
library(plotly)     
library(corrplot)
library(xts)        
library(rvest)      
library(tidyverse)  
   

Sys.Date() # current date
# Retrieve  Financial data of Nvidia (it symbol is NVDA) up to the current date
getSymbols(Symbols="NVDA", src= "yahoo")
NVDA= data.frame(NVDA)
fix(NVDA) # the data goes to 2007-01-03 up to the current date
dim(NVDA)


# checking the highest point of price
getSymbols(Symbols="NVDA", src= "yahoo")
seriesHi(NVDA)
chartSeries(NVDA,TA= NULL, theme="white") # time series of the highest point of price
addMACD() # moving average convergence divergence 
addBBands() # Bollinger bands 
addCCI() # commodity channel index
addADX() # directional movement indicator
addCMF() # chaiken money flow
# getting the closing price and plot it
NVIDIA.closeprice=Cl(NVDA)
plot(NVIDIA.closeprice)
hist(NVDA[,4],main = "NVIDIA Close", breaks=25)
# stocks returns are approximately normally distributed and uncorrelated, therefore, based on the stock`s previous returns`
# it is possible to model the behavior of stock prices within a confidence interval
# once applied the log-transformation it is possible to see that the daily returns are roughly normally distributed
NVDA_log_returns = NVDA %>%
  Ad() %>%
  dailyReturn(type = "log")
names(NVDA_log_returns) <- "NVDA.Log.Returns"
# Plot the log-returns    
NVDA_log_returns %>%    
  ggplot(aes(x = NVDA.Log.Returns)) + 
  geom_histogram(bins = 100) + 
  geom_density() +
  geom_rug(alpha = 0.5) 


# now it is possible to see the distibution of log returns
probs <- c(.005, .025, .25, .5, .75, .975, .995)
distribution_log_returns <- NVDA_log_returns %>% 
  quantile(probs = probs, na.rm = TRUE)
distribution_log_returns

# mean and standard deviation of the daily log returns
mean_log_returns = mean(NVDA_log_returns, na.rm = TRUE)
sd_log_returns = sd(NVDA_log_returns, na.rm = TRUE)
mean_log_returns
sd_log_returns
# remove the log to get the real returns
mean_log_returns %>% exp() # piping the mean of the log returns to exp()
# this means that on average  the mean daily return is  0.000851% more than the price of the previous day


# the random walk process will use the mean and standard deviation to simulate the price
# for 1000 trading days considering that one year has 252 trading days on average.
# it is necessary to specify the number of random walks(number.RW), the mean (meanMU) which is 
# our mean_log_returns from earlier. And finally the standard deviation (sdSigma) which is our sd_log_returns

# initializing the parameters
number.RW = 500
MeanMU= mean_log_returns
sdSigma = sd_log_returns
day = 1:number.RW
price.i = NVDA$NVDA.Adjusted[[nrow(NVDA$NVDA.Adjusted)]]
                             
# Simulation
# this simulation calculates the prices by finding a new price using a random return 
# from the normal distribution with MeanMu and sdSigma then it multiplies it to the previous da price
set.seed(123) 
price  = c(price.i, rep(NA, number.RW))
for(i in 2:number.RW) {
  price[i] = price[i-1] * exp(rnorm(1, MeanMU, sdSigma))
}
price.simulation = cbind(day, price) %>% 
  as_tibble()

# Plotting the price simulation
price.simulation %>%
  ggplot(aes(day, price)) +geom_line() + ggtitle(str_c("NVDA: Simulated Prices for ", number.RW," Trading Days"))

# this simulation is not very trustworthy because confidence intervals are found by simulating
# many iterations of this. Therefore I am going to perform a Monte Carlo Simulation
# The Monte Carlo simulation repeatedly performs randm walk simulations a number of times.
# This simulation is computed for one year of trading (252 days) and the random walk is repeated 300 times

# Initialising the Parameters
number.SP     = 252 # Number of stock price Simulations
number.MC     = 300  # Number of monte carlo Simulations   
MeanMU    = mean_log_returns
sdSigma = sd_log_returns
day = 1:number.SP
price.i = NVDA$NVDA.Adjusted[[nrow(NVDA$NVDA.Adjusted)]]
# Price simulation
set.seed(123)
MC.matrix = matrix(nrow = number.SP, ncol = number.MC )
for (j in 1:number.MC ) {
  MC.matrix[[1, j]] = price.i
  for(i in 2:number.SP) {
    MC.matrix[[i, j]] = MC.matrix[[i - 1, j]] * exp(rnorm(1, MeanMU, sdSigma))
  }
}

MC.matrix

# Create tidy dataframe
price.simulation = cbind(day, MC.matrix) %>%
  as_tibble() 
xy = str_c("Sim.", seq(1, number.MC ))
xy = c("Day", xy)
names(price.simulation) = xy
price.simulation = price.simulation %>%
  gather(key = "Simulation", value = "Stock.Price", -(Day))
# Plot simulation
price.simulation %>%
  ggplot(aes(x = Day, y = Stock.Price, Group = Simulation)) + 
  geom_line(alpha = 0.1) +
  ggtitle(str_c("NVDA: ", number.MC, 
                " Monte Carlo Simulations for Prices Over ", number.SP, 
                " Trading Days"))

# the quantile function will give us the confidence intervals for the stock price

sp.end= price.simulation %>% 
  filter(Day == max(Day))
probs = c(.005, .025, .25, .5, .75, .975, .995)
dist.sp.end = quantile(sp.end$Stock.Price, probs = probs)
dist.sp.end %>% round(2)



# in order to see if this simulation is realistic it is necessary to calculate the compound annual growth rate (CARG)

#parameters
number.sp.hist = nrow(NVDA) / 252
NVDA.start= NVDA$NVDA.Adjusted[[1]]
NVDA.end = NVDA$NVDA.Adjusted[[nrow(NVDA)]]
sumber.SP.sim  = number.SP/ 252
start.sim = NVDA.end
end.sim = dist.sp.end[[4]]
# CAGR 
CARG.H= (NVDA.end / NVDA.start) ^ (1 / number.sp.hist) - 1
CARG.sim = (NVDA.end / NVDA.start) ^ (1 / sumber.SP.sim ) - 1
CARG.H # historical CARG
CARG.sim # simulated CARG
# there is a substantial difference between the historical CARG and simulated Carg of 11%
# this may be due to the fact that this company`s stocks have been rising consistently

# With this simulation it is possible to compare stocks using the mean and the standard deviation of the log returns.
# the mean stands for the average growth and the standard deviation stands for the volatility


# Bring this task to a Standard & Poor`s 500 Analysis 

# retriving list of S&P500 stocks
# webscraping s&p500 list from Wikipedia
sp.500 =read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies") %>% #getting the html data
  html_node("table.wikitable") %>%  # parsing to dataframe
  html_table() %>% 
  select(`Ticker symbol`, Security, `GICS Sector`, `GICS Sub Industry`) %>%
  as_tibble()
# Clean the columns
names(sp.500) = sp.500 %>% 
  names() %>% 
  str_to_lower() %>% 
  make.names()

sp.500 %>% 
names() # columns of the tibble sp.500
        #1 is the stock ticker 2 is the the company name 3 is the GICS classification of the sector and 4 is GICS classification of the subsector

# finding how many unique values are for each column
sp.500 %>% 
  lapply(function(x) x %>% unique() %>% length()) %>%
  unlist() # show result
# there are 505 companies with respective 505 tickers, 11 main industries and 123 sub industries
# find out the distribution of companies by sector
sp.500 %>% # Summarise data by frequency
  group_by(gics.sector) %>%
  summarise(count = n()) %>%
  # plotting
  ggplot(aes(x = gics.sector %>% fct_reorder(count),
             y = count
  )) + 
  geom_bar(stat = "identity") +
  geom_text(aes(label = count), size = 3, nudge_y = 4, nudge_x = .1) + 
  scale_y_continuous(limits = c(0,100)) +
  ggtitle(label = "Sector Frequency of SP500 Stocks") +
  xlab(label = "GICS Sector") +
  theme(plot.title = element_text(size = 16)) + 
  coord_flip() 

# knowing which company is in which industry is useful in diversification strategies
# where risk is limited by investing stocks that are not much return correlated, which means
# that the success of some company is not tied to the success of another company

# Creating a function that takes a ticker ,a return format and various getSymbols() arguments
# and returns the prices of a stock as a tibble
sp.retriever = function(ticker, format = "tibble", ...) {
  # retrieve stocks prices
  sp.xts = getSymbols(Symbols = ticker, auto.assign = FALSE, ...) # auto.assign is false so a global variable is not created
  # column names
  names(sp.xts) = c("Open", "High", "Low", "Close", "Volume", "Adjusted")
  # Return in xts format if tibble is not specified ( this is needed for the last step later, the nested dataframe)
  if (format == "tibble") {
    SP = sp.xts %>%
      as_tibble() %>%
      rownames_to_column(var = "Date") %>%
      mutate(Date = ymd(Date))
  } else {
    SP = sp.xts
  }
  SP
}

# calling the above function to get the stock prices on NVIDIA as a test
sp.retriever ("NVDA",format="tibble")


#creating a function that takes a stock prices in xts or tibble, a return format and 
# other periodReturns() arguments; it will return the log returns in tibble or xts

lr.retriever = function(x, format = "tibble", period = 'daily', ...) {
  
  if (!is.xts(x)) { # Convert tibble to xts
    x <- xts(x[,-1], order.by = x$Date)
  }
  # retrieve the log returns
  lg.return.xts = periodReturn(x = x$Adjusted, type = 'log', period = period, ...)
  # column name
  names(lg.return.xts) ="Log.Returns"
  # Return in xts format if tibble is not specified, needed for later
  if (format == "tibble") {
    lg.return = lg.return.xts %>%
      as_tibble() %>%
      rownames_to_column(var = "Date") %>%
      mutate(Date = ymd(Date))
  } else {
    lg.return = lg.return.xts
  }
  lg.return
}

# testing lr.retriever function

"NVDA" %>% 
  sp.retriever(format = "tibble") %>% 
  lr.retriever(format = "tibble") 


# Building a nested data frame where some cells contain another dataframe

# using map() to use the functions created earlier to the nested list-columns in order to
# loop the entire dataframe

# Some companies either create a http 400 error when attempting to retrieve the data
# or have missing values. I am simply removing them because having missing values will
# decrease the quality of the analysis of the next steps. I am not sure if this is constant
# or it will be different depending on the time of retrieval
sp.500.1=sp.500[!sp.500$ticker.symbol=="BRK.B",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="BF.B",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="APTV",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="BKNG",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="BHF",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="DXC",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="JEF",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="DGX",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="UA",]
sp.500.1=sp.500.1[!sp.500.1$ticker.symbol=="PPL",]

sp.500.1 = sp.500.1 %>%
  mutate(
    SP = map(ticker.symbol, 
                       function(.x) sp.retriever(.x, 
                                                     format = "tibble")
                                                
                                                    
    ),
    lg.return  = map(SP, 
                       function(.x) lr.retriever(.x, format = "tibble")),
    mean.log.returns = map_dbl(lg.return, ~ mean(.$Log.Returns)),
    sd.log.returns   = map_dbl(lg.return, ~ sd(.$Log.Returns)),
    n.trade.days = map_dbl(SP, nrow)
  )  

sp.500.1 # now this dataframe has the columns SP (stock prices) and lg.return (log returns)
           # which are tibbles, therefore a dataframe within a cell of a larger dataframe
sp.500.1$SP[[1]] # accessing the first tibble. This is the stock price for the first company, with all its columns and observations


# Plotting the results
# the goal is to compare risk and reward for the s&P500 stocks
# reward is intended as the mean of the log returns, in other words how much it grows
# while risk is intended as the standard deviation of the log returns (the volatility)

# creating a scatter plot with the volatility on the x-axis and the reward on the y-axis, while
# the number of trade days is given by the size and color
# N.B. this plot can be zoomed in and out and panned, which is an excellent feature to check out 
# each stock individually

plot_ly(data   = sp.500.1,
        type   = "scatter",
        mode   = "markers",
        x      = ~ sd.log.returns,
        y      = ~ mean.log.returns,
        color  = ~ n.trade.days,
        colors = "Blues",
        size   = ~ n.trade.days,
        text   = ~ str_c("<em>", security, "</em><br>",
                         "Ticker: ", ticker.symbol, "<br>",
                         "Sector: ", gics.sector, "<br>",
                         "Sub Sector: ", gics.sub.industry, "<br>",
                         "No. of Trading Days: ", n.trade.days),
        marker = list(opacity = 0.8,
                      symbol = 'circle',
                      sizemode = 'diameter',
                      sizeref = 4.0,
                      line = list(width = 2, color = '#FFFFFF'))
) %>%
  layout(title   = 'S&amp;P500 Analysis: Stock Risk vs Reward',
         xaxis   = list(title = 'Risk/Volatility (StDev Log Returns)',
                        gridcolor = 'rgb(255, 255, 255)',
                        zerolinewidth = 1,
                        ticklen = 5,
                        gridwidth = 2),
         yaxis   = list(title = 'Reward/Growth (Mean Log Returns)',
                        gridcolor = 'rgb(255, 255, 255)',
                        zerolinewidth = 1,
                        ticklen = 5,
                        gridwith = 2),
         margin = list(l = 100,
                       t = 100,
                       b = 100),
         font   = list(color = '#FFFFFF'),
         paper_bgcolor = 'rgb(0, 0, 0)',
         plot_bgcolor = 'rgb(0, 0, 0)')


# let us isolate the ones that have a low volatility and a high mean

sp.500.1 %>%
  filter(mean.log.returns >= 0.001,
         sd.log.returns < 0.0315) %>%
  select(ticker.symbol, mean.log.returns:n.trade.days) %>%
  arrange(mean.log.returns %>% desc())

#These are the best stocks according to these statistics, it is a way to screen stocks in terms of their potential,
# let us take amazon as an example
# and plot it
"AMZN" %>%
  getSymbols(auto.assign = FALSE) %>%
  chartSeries(name = "AMZN")
# these are not the only things to take into account, there is qualitative analysis
# analysing dividends among other metrics

# when selecting a portfolio you cannot only select the best performance but also diversify
# the stocks so that a few companies going down will not affect too much the investments.
# In order to do this it is necessary to do a correlation assessment and chose stocks with low correlation

# The only stocks examined will be the ones with 1000 trading days and the top 30 in terms of growth and volatility

howmany = 30
sp.500.1.corr = sp.500.1 %>%
  filter(n.trade.days > 1000) %>%
  filter(sd.log.returns < 0.0315) %>%
  mutate(ranking = mean.log.returns %>% desc() %>% min_rank()) %>% # ranking will be a column used to sort the companies
  filter(ranking <= howmany) %>%
  arrange(ranking) %>%
  select(ticker.symbol, ranking, mean.log.returns, sd.log.returns, lg.return)
sp.500.1.corr


# this will unnest the log returns causing the dataframe to list all companies and all of the observations of the log returns (for all 30 companies)
sp.500.1.corr.unnested = sp.500.1.corr %>%
  select(ticker.symbol, lg.return) %>%
  unnest()
sp.500.1.corr.unnested
# checking for NA values in dataframe
any(is.na(sp.500.1.corr.unnested)) # there are no NA values

# putting the companies as columns, needed to carry out the correlation analysis
sp.500.1.corr.unnested.columns = sp.500.1.corr.unnested %>%
  spread(key = ticker.symbol, value = Log.Returns)%>%
  na.omit() # this is because some stocks do not have data for all of the dates, so that all the rows with NA are discarded
  sp.500.1.corr.unnested.columns

  # creating the final dataframe ready for the correlation plot
  sp.500.1.corr.final <- sp.500.1.corr.unnested.columns %>%
    select(-Date) %>% # remove the date column
    cor() 
  sp.500.1.corr.final[1:7, 1:7] # show first 10 columns and rows
  

# plotting the correlation
  sp.500.1.corr.final %>%
    corrplot(order   = "hclust", # this creates boxes with high correlated groups inside
             addrect = 10)    # numnber of boxes chosen   

# with this plot it is possible to see positive and negative correlation with the dot colors
  # some high correlation groups are inside the boxes
  # many correlated companies have a good reason to be so, for example one is the supplier of another
  















