
# coding: utf-8

# # Breaks_AllTrade_MarkitCTD

# ## Inputs:
# - All Trade file
# - Markit Lgim NY CTD Rates for Swaps ( Markit Val :Interest and Zero Coupons Swaps,InfSwaps,GBP Swaptions)
# - Exchange Rates from Quasar LE04

# ## Outputs:
# ##### A swaps and a swaptions dataframes with :
#  - Absolute Tolerance exception column
#  - Relative Tolerance exception column
#  - Exception Column when Relative and Absolute are both broken
#  - % of notional column

# ##### Please note:
# - removes non shared trades
# - duplicates in All trade are selected based on fund (if fund matches in Markit)
# - removes All trade file  sedols with no valuation
# - It uses markits PresentValue which is in GBP and converts the all trade counterparty MTM to GBP

# ## Code

# In[1]:

# load libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import re
import datetime
from QuantLib import *


# In[2]:

# inputs path
path_inputs="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Input All Trade/"


# ##### Retrieve COB date datetime method (only takes into account weekends)

# In[3]:

# retrieve today`s date to output the files with the correct name
#yesterday = datetime.date.today() - timedelta(days=1)
# the variable yesterday needs to be manually created if yesterday was a holiday example: yesterday=datetime.date(2019, 4, 13)


# In[4]:

# exclude weekends (holidays will have to be manually accounted for)
#if datetime.date.weekday(yesterday) not in range (0,5):
    #yesterday=datetime.date.today() - timedelta(days=3)


# In[5]:

# store the date into a string
#lastBusDay=yesterday.strftime("%d.%m.%Y")


# ##### Retrieve COB date QuantLib method (takes into account all uk calendar holidays)

# In[6]:

# load UK calendar
uk_calendar=UnitedKingdom()


# In[7]:

today = datetime.date.today()


# In[8]:

dayQ=today.day
monthQ=today.month
yearQ=today.year


# In[9]:

QBDate=Date(dayQ,monthQ,yearQ)


# In[10]:

for i in range(1,30):
    uk_busdays = uk_calendar.businessDaysBetween(QBDate-i,QBDate)
    if uk_busdays == 1:
        lastBusDay_original=QBDate-i
        break


# In[11]:

day=lastBusDay_original.dayOfMonth()
month=lastBusDay_original.month()
year=lastBusDay_original.year()


# In[12]:

lastBusDay_original=datetime.datetime(year,month,day)


# In[13]:

# store the date into a string
lastBusDay=lastBusDay_original.strftime("%d.%m.%Y")


# In[14]:

lastBusDay


# ## If the date needs to be input manually use the lastBusDay assignment below

# In[15]:

#lastBusDay="mm.dd.yy"


# ##### Automatic RegEx Method (Markit CTD and LE04 are still from input folder)

# In[16]:

# import All Trade file automatically with regex
lastBusDayALLTRADE=lastBusDay_original.strftime("%d-%b-%y") # format date in appropiate way 25-Mar-19
ALLTRADEPATH="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Reconciliation Reports/"
pattern_AllTrade  = r"Tri-Optima_AllTrades_Pricing_"+lastBusDayALLTRADE+".xlsx"
AllTrade_df=pd.read_excel(ALLTRADEPATH+pattern_AllTrade,sheetname="Tri-Optima_AllTrades_Pricing")


# In[17]:

# import LE04 file from input folder
pattern_LE04  = r"LE04.*"
for i in os.listdir(path_inputs):
    if re.search(pattern_LE04 ,i):
        with open(path_inputs+i, encoding='utf8') as LE04_txt: #open the txt file
            LE04_txt1=LE04_txt.read().replace('\n', '')
        break


# In[18]:

# import markit ctd from imput folder


# In[19]:

pattern_CTD  = r".*LGIM_NY_Rates_CTD.*" # patterns for the LE04
for i in os.listdir(path_inputs):   # Regex method
    if re.search(pattern_CTD,i):
        CTD_Swap_df=pd.read_excel(path_inputs+i,sheetname="Swap")
        CTD_InfSwap_df=pd.read_excel(path_inputs+i,sheetname="InfSwap")
        CTD_Swaption_df=pd.read_excel(path_inputs+i,sheetname="Swaption")
        break


# ### USE THIS IF THERE ARE ISSUES WITH AUTOMATIC METHOD (change cell type from Markdown to Code)

# pattern_AllTrade  = r"Tri-Optima_AllTrades_Pricing.*" # patterns for the AllTrade
# pattern_LE04  = r"LE04.*" # patterns for the CTD
# pattern_CTD  = r".*LGIM_NY_Rates_CTD.*" # patterns for the LE04
# 
# #retrieve Input Files with Regex or Manual input
# for i in os.listdir(path_inputs):   # Regex method
#     if re.search(pattern_AllTrade,i):
#         AllTrade_df=pd.read_excel(path_inputs+i,sheetname="Tri-Optima_AllTrades_Pricing")
#     elif re.search(pattern_CTD,i):
#         CTD_Swap_df=pd.read_excel(path_inputs+i,sheetname="Swap")
#         CTD_InfSwap_df=pd.read_excel(path_inputs+i,sheetname="InfSwap")
#         CTD_Swaption_df=pd.read_excel(path_inputs+i,sheetname="Swaption")
#     elif re.search(pattern_LE04,i):
#         with open(path_inputs+i, encoding='utf8') as LE04_txt: #open the txt file
#             LE04_txt1=LE04_txt.read().replace('\n', '') # read the txt file and substitute the newline symbols with nothing
#     else:                     # Manual method
#         AllTrade_filename=input("Please insert the AllTrade file name:")
#         CTD_filename=input("Please insert the CTD file name:")
#         LE04_filename=input("Please insert the LE04 file name:")
#         complete_path_AllTrade=path_inputs+AllTrade_filename+".xlsx"
#         complete_path_CTD=path_inputs+CTD_filename+".xls"
#         complete_path_LE04=path_inputs+LE04_filename+".TXT"
#         AllTrade_df=pd.read_excel(complete_path_AllTrade,sheetname="Tri-Optima_AllTrades_Pricing")
#         CTD_Swap_df=pd.read_excel(complete_path_CTD,sheetname="Swap")
#         CTD_InfSwap_df=pd.read_excel(complete_path_CTD,sheetname="InfSwap")
#         CTD_Swaption_df=pd.read_excel(complete_path_CTD,sheetname="Swaption")
#         with open(complete_path_LE04, encoding='utf8') as LE04_txt:
#             LE04_txt1=LE04_txt.read().replace('\n', '')
#         break
#  
#         
#         
#         
#    

# ### Data Cleanup

# ##### CTD

# In[20]:

# rename column labels with the actual column names
CTD_Swaption_df.columns = CTD_Swaption_df.iloc[2] #give header row 2 names
CTD_Swaption_df=CTD_Swaption_df.reset_index(drop=True) # resetting index

CTD_InfSwap_df.columns = CTD_InfSwap_df.iloc[2] #give header row 2 names
CTD_InfSwap_df=CTD_InfSwap_df.reset_index(drop=True) # resetting index

CTD_Swap_df.columns = CTD_Swap_df.iloc[2] #give header row 2 names
CTD_Swap_df=CTD_Swap_df.reset_index(drop=True) # resetting index


# In[21]:

# remove markits header
CTD_Swaption_df= CTD_Swaption_df.drop([0,1,2])# remove the first three rows
CTD_InfSwap_df= CTD_InfSwap_df.drop([0,1,2])# remove the first three rows
CTD_Swap_df= CTD_Swap_df.drop([0,1,2])# remove the first three rows
CTD_Swap_df=CTD_Swap_df.reset_index(drop=True) # resetting index
CTD_InfSwap_df=CTD_InfSwap_df.reset_index(drop=True) #resetting index
CTD_Swaption_df=CTD_Swaption_df.reset_index(drop=True) #resetting index


# In[22]:

# remove non needed columns
CTD_Swaption_df=CTD_Swaption_df[['TradeId', 'Book',"LocalCcy", 'PresentValue',"SwaptionVega"]]
CTD_InfSwap_df=CTD_InfSwap_df[['TradeId', 'Book', 'LegId',"LocalCcy","PresentValue","NetPV01"]]
CTD_Swap_df=CTD_Swap_df[['TradeId', 'Book', 'LegId',"LocalCcy","PresentValue","NetPV01"]]


# In[23]:

# top merge Swaps and InfSwaps in a single dataframe
CTD_AllSwaps=CTD_InfSwap_df.append(CTD_Swap_df)
#resetting row index
CTD_AllSwaps=CTD_AllSwaps.reset_index(drop=True)


# In[24]:

# remove all rows with LegId non-NaN
CTD_AllSwaps =CTD_AllSwaps[pd.isnull(CTD_AllSwaps['LegId'])]
#resetting index
CTD_AllSwaps=CTD_AllSwaps.reset_index(drop=True)


# In[25]:

# remove legId column
CTD_AllSwaps=CTD_AllSwaps.drop(["LegId"],axis=1)


# ##### All Trade

# In[26]:

AllTrade_df=AllTrade_df[['BOOK', 'CPTY NAME', 'SEDOL',"ASSET CLASS","NOTIONAL","MTM DATE","GBP CPTY MTM","MTM CCY"]]


# In[27]:

# delete rows from CTD_AllSwaps whose Id do not appear in AllTrade_df
CTD_AllSwaps1=CTD_AllSwaps[CTD_AllSwaps["TradeId"].isin(AllTrade_df["SEDOL"])]
CTD_AllSwaps1=CTD_AllSwaps1.reset_index(drop=True) # reset index
# delete rows from AllTrade_df whose Id do not appear in CTD_AllSwaps (viceversa of above cell)
AllTrade_df1=AllTrade_df[AllTrade_df["SEDOL"].isin(CTD_AllSwaps["TradeId"])]
AllTrade_df1=AllTrade_df1.reset_index(drop=True) # reset index


# In[28]:

#check for duplicates in All Trade and CTD all swaps
duplicated_AllTrade_df1 = AllTrade_df1.duplicated(subset="SEDOL", keep="first")
any(x == True for x in duplicated_AllTrade_df1) # check if there is a True in the list


# In[29]:

duplicated_CTD_AllSwaps1 = CTD_AllSwaps1.duplicated(subset="TradeId", keep="first")
any(x == True for x in duplicated_CTD_AllSwaps1) # check if there is a True in the list


# In[30]:

#get indices of duplicate id rows in the All Trade and convert to a list
duplicated_AllTrade_df1 = AllTrade_df1.duplicated(subset="SEDOL", keep="first") # using boolean masking
duplicated_AllTrade_df1= np.where(duplicated_AllTrade_df1 ==True)
#convert the tuple of indeces to a list
duplicated_AllTrade_df1=list(duplicated_AllTrade_df1)
# Create list with the indeces of the duplicate ids rows
duplicated_AllTrade_df1_list=[]
for n in duplicated_AllTrade_df1:
    duplicated_AllTrade_df1_list.extend(n)


# In[31]:

CTD_AllSwaps1["Book"]=CTD_AllSwaps1["Book"].astype(int) # convert book column to integer in AllSwaps


# In[32]:

AllTrade_df1["BOOK"]=AllTrade_df1["BOOK"].astype(int) # convert book column to integer in AllTrade


# In[33]:

# get trade Ids from All trade which are duplicates
duplicate_TradeIds_AllTrade=[] # this is now a list of trades that are duplicates
for i in duplicated_AllTrade_df1_list:
    duplicate_TradeIds_AllTrade.append(AllTrade_df1.iloc[i,2])


# In[34]:

indicestoremove=[]
for index, row in AllTrade_df1.iterrows():
    if (AllTrade_df1.iloc[index,2]) in (duplicate_TradeIds_AllTrade):#diverso dal book dello stesso sedol in markit, toglilo
        if AllTrade_df1.iloc[index,0]!=CTD_AllSwaps1.iloc[CTD_AllSwaps1[CTD_AllSwaps1['TradeId']==AllTrade_df1.iloc[index,2]].index.item(),1]:
            xxx=CTD_AllSwaps1.iloc[CTD_AllSwaps1[CTD_AllSwaps1['TradeId']==AllTrade_df1.iloc[index,2]].index.item(),0]
            # rimuovi la row dall all trade con l index a cui ti trovi
            # create list of indices to remove because they are both duplicates and have different book than CTD
            indicestoremove.append(index)


# In[35]:

#remove indices
# the new AllTrade_df2 will not have the duplicated sedols with book that is different from the ctd file
# only the (previously) duplicated sedols with same book as markit will be left
AllTrade_df1=AllTrade_df1.drop(AllTrade_df1.index[indicestoremove])


# In[36]:

AllTrade_df2=AllTrade_df1.reset_index(drop=True)


# In[37]:

# delete rows from CTD_AllSwaps whose Id do not appear in AllTrade_df
CTD_AllSwaps1=CTD_AllSwaps1[CTD_AllSwaps1["TradeId"].isin(AllTrade_df2["SEDOL"])]
CTD_AllSwaps1=CTD_AllSwaps1.reset_index(drop=True) # reset index
# delete rows from AllTrade_df whose Id do not appear in CTD_AllSwaps (viceversa of above cell)
AllTrade_df2=AllTrade_df2[AllTrade_df2["SEDOL"].isin(CTD_AllSwaps1["TradeId"])]
AllTrade_df2=AllTrade_df2.reset_index(drop=True) # reset index


# In[38]:

# remove trades from all trade file that have missing val
AllTrade_df2 = AllTrade_df2[pd.notnull(AllTrade_df2["GBP CPTY MTM"])]


# In[39]:

# delete rows from CTD_AllSwaps whose Id do not appear in AllTrade_df
CTD_AllSwaps1=CTD_AllSwaps1[CTD_AllSwaps1["TradeId"].isin(AllTrade_df2["SEDOL"])]
CTD_AllSwaps1=CTD_AllSwaps1.reset_index(drop=True) # reset index
# delete rows from AllTrade_df whose Id do not appear in CTD_AllSwaps (viceversa of above cell)
AllTrade_df2=AllTrade_df2[AllTrade_df2["SEDOL"].isin(CTD_AllSwaps1["TradeId"])]
AllTrade_df2=AllTrade_df2.reset_index(drop=True) # reset index


# In[40]:

#check for duplicates in AllTrade_df2
duplicated_AllTrade_df2 = AllTrade_df2.duplicated(subset="SEDOL", keep="first")
any(x == True for x in duplicated_AllTrade_df2) # check if there is a True in the list


# ##### Quasar LE04

# In[41]:

LE04_words=LE04_txt1.split() # split the string file into a list of words


# In[42]:

Currency=[]
Currency_Value=[]
for i in range(len(LE04_words)):
    if LE04_words[i] =="US"and LE04_words[i-1]=="1" :
        Currency.append("US DOLLAR")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="JAPANESE":
        Currency.append("JAPANESE YEN")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="AUSTRALIAN":
        Currency.append("AUSTRALIAN DOLLAR")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="CANADIAN":
        Currency.append("CANADIAN DOLLAR")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="NORWEGIAN":
        Currency.append("NORWEGIAN KRONER")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="SWISS":
        Currency.append("SWISS FRANC")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="STH":
        Currency.append("SOUTH AFRICAN RAND")
        Currency_Value.append(LE04_words[i+3])
    elif LE04_words[i] =="ZEALAND":
        Currency.append("NEW ZEALAND DOLLAR")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="SWEDISH":
        Currency.append("SWEDISH KRONER")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="SINGAPORE":
        Currency.append("SINGAPORE DOLLAR")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="KOREA":
        Currency.append("KOREA (SOUTH) WON")
        Currency_Value.append(LE04_words[i+3])
    elif LE04_words[i] =="INDIAN":
        Currency.append("INDIAN RUPEE")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="TAIWANESE":
        Currency.append("TAIWANESE DOLLAR")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="CHINESE":
        Currency.append("CHINESE YUAN")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="ARGENTINE":
        Currency.append("ARGENTINE PESO")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="BRAZILIAN":
        Currency.append("BRAZILIAN REAL")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="MEXICAN":
        Currency.append("MEXICAN PESO")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="Russian":
        Currency.append("Russian Rouble (new)")
        Currency_Value.append(LE04_words[i+3])
    elif LE04_words[i] =="EURO":
        Currency.append("EURO")
        Currency_Value.append(LE04_words[i+1])
    elif LE04_words[i] =="Arab":
        Currency.append("Arab Emirates Dirham")
        Currency_Value.append(LE04_words[i+3])
    elif LE04_words[i] =="ICELAND":
        Currency.append("ICELAND KRONA")
        Currency_Value.append(LE04_words[i+2])
    elif LE04_words[i] =="HONG":
        Currency.append("HONG KONG DOLLAR")
        Currency_Value.append(LE04_words[i+3])


# In[43]:

# create dataframe with currency name and value
Currency_df=pd.DataFrame(Currency, columns=['Currency'])
Currency_df[1]=Currency_Value
Currency_df.columns=["Currency","Exchange_Rate"]


# ##### Swaptions Cleanup and Analysis

# In[44]:

# convert sedol columns to string
CTD_Swaption_df["TradeId"]=CTD_Swaption_df["TradeId"].astype(str)
AllTrade_df["SEDOL"]=AllTrade_df["SEDOL"].astype(str)


# In[45]:

# delete rows from CTD_Swaption_df whose Id do not appear in AllTrade_df
CTD_Swaption_df1=CTD_Swaption_df[CTD_Swaption_df["TradeId"].isin(AllTrade_df["SEDOL"])]
CTD_Swaption_df1=CTD_Swaption_df1.reset_index(drop=True) # reset index


# In[46]:

# delete rows from CTD_Swaption_df whose Id do not appear in AllTrade_df
AllTrade_Swaptions=AllTrade_df[AllTrade_df["SEDOL"].isin(CTD_Swaption_df1["TradeId"])]
AllTrade_Swaptions=AllTrade_Swaptions.reset_index(drop=True) # reset index


# In[47]:

# convert fund column to int
AllTrade_Swaptions["BOOK"]=AllTrade_Swaptions["BOOK"].astype(int) # convert the book columns to int
CTD_Swaption_df1["Book"]=CTD_Swaption_df1["Book"].astype(int) # convert the book columns to int


# In[48]:

#check for duplicates in all ctd swaption
duplicated_CTD_Swaption_df1 = CTD_Swaption_df1.duplicated(subset="TradeId", keep="first")
any(x == True for x in duplicated_CTD_Swaption_df1) # check if there is a True in the list


# In[49]:

#check for duplicates in  all trade swaption
duplicated_AllTrade_Swaptions = AllTrade_Swaptions.duplicated(subset="SEDOL", keep="first")
any(x == True for x in duplicated_AllTrade_Swaptions) # check if there is a True in the list


# In[50]:

#get indices of duplicate id rows in the All Trade swaptions and convert to a list
duplicated_AllTrade_Swaptions_df1 = AllTrade_Swaptions.duplicated(subset="SEDOL", keep="first") # using boolean masking
duplicated_AllTrade_Swaptions_df1= np.where(duplicated_AllTrade_Swaptions_df1 ==True)
#convert the tuple of indeces to a list
duplicated_AllTrade_Swaptions_df1=list(duplicated_AllTrade_Swaptions_df1)
# Create list with the indeces of the duplicate ids rows
duplicated_AllTrade_Swaptions_df1_list=[]
for n in duplicated_AllTrade_Swaptions_df1:
    duplicated_AllTrade_Swaptions_df1_list.extend(n) 


# In[51]:

# get trade Ids from All trades which are duplicates
duplicate_TradeIds_AllTrade_Swaptions=[] # this is now a list of trades that are duplicates
for i in duplicated_AllTrade_Swaptions_df1_list:
    duplicate_TradeIds_AllTrade_Swaptions.append(AllTrade_Swaptions.iloc[i,2])


# In[52]:

indicestoremoveswaptions=[]
for index, row in AllTrade_Swaptions.iterrows():
    if (AllTrade_Swaptions.iloc[index,2]) in (duplicate_TradeIds_AllTrade_Swaptions):#diverso dal book dello stesso sedol in markit, toglilo
        if AllTrade_Swaptions.iloc[index,0]!=CTD_Swaption_df1.iloc[CTD_Swaption_df1[CTD_Swaption_df1['TradeId']==AllTrade_Swaptions.iloc[index,2]].index.item(),1]:
            xxx=CTD_Swaption_df1.iloc[CTD_Swaption_df1[CTD_Swaption_df1['TradeId']==AllTrade_Swaptions.iloc[index,2]].index.item(),0]
            # rimuovi la row dall all trade con l index a cui ti trovi
            # create list of indices to remove because they are both duplicates and have different book than CTD
            indicestoremoveswaptions.append(index)


# In[53]:

#remove indices
# the new AllTrade_df2 will not have the duplicated sedols with book that is different from the ctd file
# only the (previously) duplicated sedols with same book as markit will be left
AllTrade_Swaptions=AllTrade_Swaptions.drop(AllTrade_Swaptions.index[indicestoremoveswaptions])


# In[54]:

AllTrade_Swaptions=AllTrade_Swaptions.reset_index(drop=True)


# In[55]:

# remove trades from all trade swaption file that have missing 
#AllTrade_Swaptions= AllTrade_Swaptions[AllTrade_Swaptions["GBP CPTY MTM"] != 0]
AllTrade_Swaptions = AllTrade_Swaptions[pd.notnull(AllTrade_Swaptions["GBP CPTY MTM"])]
AllTrade_Swaptions=AllTrade_Swaptions.reset_index(drop=True)


# In[56]:

# delete rows from CTD_Swaption_df whose Id do not appear in AllTrade_df
CTD_Swaption_df1=CTD_Swaption_df1[CTD_Swaption_df1["TradeId"].isin(AllTrade_Swaptions["SEDOL"])]
CTD_Swaption_df1=CTD_Swaption_df1.reset_index(drop=True) # reset index


# In[57]:

# delete rows from CTD_Swaption_df whose Id do not appear in AllTrade_df
AllTrade_Swaptions=AllTrade_Swaptions[AllTrade_Swaptions["SEDOL"].isin(CTD_Swaption_df1["TradeId"])]
AllTrade_Swaptions=AllTrade_Swaptions.reset_index(drop=True) # reset index


# In[58]:

# Change All Trade Valuation based on Exchange Rates
AllTrade_Swaptions["BOOK"]=AllTrade_Swaptions["BOOK"].astype(int)


# In[59]:

# create Exchange_Rate column in AllTrade_Swaptions
AllTrade_Swaptions['Exchange_Rate']="NaN" # create column


# In[60]:

# based on the currency put the appropiate exchange rate in the rows
for index, row in AllTrade_Swaptions.iterrows():
    if AllTrade_Swaptions.iloc[index,7]=='USD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="US DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='EUR':
        indextochange_list=list(np.where(Currency_df["Currency"]=="EURO")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='GBP':
        AllTrade_Swaptions.iloc[index,8]= 1
    elif AllTrade_Swaptions.iloc[index,7]=='JPY':
        indextochange_list=list(np.where(Currency_df["Currency"]=="JAPANESE YEN")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='AUD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="AUSTRALIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='CAD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="CANADIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='CHF':
        indextochange_list=list(np.where(Currency_df["Currency"]=="SWISS FRANC")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='HKD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="HONG KONG DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='NOK':
        indextochange_list=list(np.where(Currency_df["Currency"]=="NORWEGIAN KRONER")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='SEK':
        indextochange_list=list(np.where(Currency_df["Currency"]=="SWEDISH KRONER")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_Swaptions.iloc[index,7]=='KRW':
        indextochange_list=list(np.where(Currency_df["Currency"]=="KOREA (SOUTH) WON")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_Swaptions.iloc[index,8]= Currency_df.iloc[indextochange_int,1]



# In[61]:

# Create column with the correct Valuation in the All trade for SWAPTIONS
AllTrade_Swaptions['Valuation_AllTrade']="NaN" # create column


# In[62]:

# change Exchange rate column to float
AllTrade_Swaptions["Exchange_Rate"]=AllTrade_Swaptions["Exchange_Rate"].astype(float)
# multiply valuation for the exchange rate
AllTrade_Swaptions["Valuation_AllTrade"]=AllTrade_Swaptions["GBP CPTY MTM"]/AllTrade_Swaptions["Exchange_Rate"]


# In[63]:

# Swaptions final dataframe merging ctd to all trade
#rename CTD Trade id column to SEDOL in order to use the merge function
CTD_Swaption_df1= CTD_Swaption_df1.rename(index=str, columns={"TradeId":"SEDOL"})
# Merge on SEDOL
Final_df_Swaptions=pd.merge(CTD_Swaption_df1, AllTrade_Swaptions, on="SEDOL")


# In[64]:

# remove non needed columns
Final_df_Swaptions=Final_df_Swaptions[['SEDOL', 'Book',"LocalCcy","CPTY NAME","ASSET CLASS","MTM DATE","NOTIONAL",'PresentValue',"Valuation_AllTrade","SwaptionVega"]]


# ## Swap Analysis

# In[65]:

# Change All Trade Valuation based on Exchange Rates # CTD_AllSwaps1 AllTrade_df2


# In[66]:

# create Exchange_Rate column in AllTrade_df2
AllTrade_df2['Exchange_Rate']="NaN" # create column


# In[67]:

# based on the currency put the appropiate exchange rate in the rows
for index, row in AllTrade_df2.iterrows():
    if AllTrade_df2.iloc[index,7]=='USD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="US DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='EUR':
        indextochange_list=list(np.where(Currency_df["Currency"]=="EURO")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='GBP':
        AllTrade_df2.iloc[index,8]= 1
    elif AllTrade_df2.iloc[index,7]=='JPY':
        indextochange_list=list(np.where(Currency_df["Currency"]=="JAPANESE YEN")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='AUD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="AUSTRALIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='CAD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="CANADIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='CHF':
        indextochange_list=list(np.where(Currency_df["Currency"]=="SWISS FRANC")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='HKD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="HONG KONG DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='NOK':
        indextochange_list=list(np.where(Currency_df["Currency"]=="NORWEGIAN KRONER")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='SEK':
        indextochange_list=list(np.where(Currency_df["Currency"]=="SWEDISH KRONER")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]
    elif AllTrade_df2.iloc[index,7]=='KRW':
        indextochange_list=list(np.where(Currency_df["Currency"]=="KOREA (SOUTH) WON")[0])
        indextochange_int=indextochange_list[0]
        AllTrade_df2.iloc[index,8]= Currency_df.iloc[indextochange_int,1]


# In[68]:

# create New Valuation after exchange rates column in AllTrade_df2
AllTrade_df2['Valuation_AllTrade']="NaN" # create column


# In[69]:

# change Exchange rate column to float
AllTrade_df2["Exchange_Rate"]=AllTrade_df2["Exchange_Rate"].astype(float)
# divide valuation for the exchange rate
AllTrade_df2["Valuation_AllTrade"]=AllTrade_df2["GBP CPTY MTM"]/AllTrade_df2["Exchange_Rate"]


# In[70]:

# Create a unique dataframe with CTD and ALL Trade for Swaps and Swaptions 
# SWAPS: AllTrade_df2 & CTD_AllSwaps1 -> Final_df_Swap
# SWAPTIONS: AllTrade_Swaptions & CTD_Swaption_df1 -> Final_df_Swaptions


# In[71]:

# Swaps final dataframe merging markit ctd to all trade
#rename CTD Trade id column to SEDOL in order to use the merge function
CTD_AllSwaps1= CTD_AllSwaps1.rename(index=str, columns={"TradeId":"SEDOL"})
# Merge on SEDOL
Final_df_Swap=pd.merge(CTD_AllSwaps1, AllTrade_df2, on="SEDOL")


# In[72]:

# remove non needed columns
Final_df_Swap=Final_df_Swap[['SEDOL', 'Book',"LocalCcy","CPTY NAME","ASSET CLASS","MTM DATE","NOTIONAL",'PresentValue',"Valuation_AllTrade","NetPV01"]]


# ##### Create Tolerance Breaks Exceptions

# In[73]:

# difference in Valuation for Swaps and Swaptions
Final_df_Swaptions['AllTrade_MarkitCTD_Diff'] = abs(abs(Final_df_Swaptions['Valuation_AllTrade']) - abs(Final_df_Swaptions['PresentValue']) )
Final_df_Swap['AllTrade_MarkitCTD_Diff'] = abs(abs(Final_df_Swap['Valuation_AllTrade']) - abs(Final_df_Swap['PresentValue']) )


# In[74]:

# Create column with absolute tolerance exceptions
Final_df_Swaptions['Abs_Tolerance']="NaN" # create column
Final_df_Swap['Abs_Tolerance']="NaN" # create column


# In[75]:

# fill in Abs Tolerance : Swaps
for index, row in Final_df_Swap.iterrows():
    if Final_df_Swap.iloc[index, 10]<1500000:
        Final_df_Swap.iloc[index, 11]=0
    elif Final_df_Swap.iloc[index, 10]>=1500000 and Final_df_Swap.iloc[index, 10]<3000000:
        Final_df_Swap.iloc[index, 11]=1
    elif Final_df_Swap.iloc[index, 10]>=3000000:
        Final_df_Swap.iloc[index, 11]=2
    


# In[76]:

# fill in Abs Tolerance : Swaptions
for index, row in Final_df_Swaptions.iterrows():
    if Final_df_Swaptions.iloc[index, 10]<1500000:
        Final_df_Swaptions.iloc[index, 11]=0
    elif Final_df_Swaptions.iloc[index, 10]>=1500000 and Final_df_Swaptions.iloc[index, 10]<3000000:
        Final_df_Swaptions.iloc[index, 11]=1
    elif Final_df_Swaptions.iloc[index, 10]>=3000000:
        Final_df_Swaptions.iloc[index, 11]=2
    


# In[77]:

#PV01 tolerance for Swaps and VegaTolerance for Swaptions


# In[78]:

# create pv01 tolerance for the swaps
Final_df_Swap['PV01_Tolerance']="NaN" # create column


# In[79]:

# fill in Pv01 Tolerance
Final_df_Swap['PV01_Tolerance'] = Final_df_Swap['AllTrade_MarkitCTD_Diff'] / abs(Final_df_Swap["NetPV01"]) 


# In[80]:

# create PV01 exceptions column
Final_df_Swap['PV01_Exceptions']="NaN" # create column


# In[81]:

# fill in PV01 Exceptions
for index, row in Final_df_Swap.iterrows():
    if Final_df_Swap.iloc[index, 12]>5:
        Final_df_Swap.iloc[index, 13]=1
    else:
        Final_df_Swap.iloc[index, 13]=0


# In[82]:

# add % of notional column
Final_df_Swap['%Notional']="NaN" # create column


# In[83]:

# fill in % of notional column
Final_df_Swap['%Notional'] = Final_df_Swap["AllTrade_MarkitCTD_Diff"] / Final_df_Swap["NOTIONAL"]


# In[84]:

# add Exceptions column
Final_df_Swap['Exceptions']="NaN" # create column


# In[85]:

# fill in Exceptions
for index, row in Final_df_Swap.iterrows():
    if int(Final_df_Swap.iloc[index, 11])>=2 and int(Final_df_Swap.iloc[index, 13])>0:
        Final_df_Swap.iloc[index, 15]="CHECK"
    else:
        Final_df_Swap.iloc[index, 15]="OK"


# In[86]:

Final_df_Swap.Exceptions.value_counts()


# In[87]:

# add Vega exception column for Swaptions
Final_df_Swaptions['Vega_Exceptions']="NaN" # create column


# In[88]:

# fill in Vega_Exceptions column
for index, row in Final_df_Swaptions.iterrows():
    if Final_df_Swaptions.iloc[index, 10]>(3*Final_df_Swaptions.iloc[index, 9]):
        Final_df_Swaptions.iloc[index, 12]=1
    else:
        Final_df_Swaptions.iloc[index, 12]=0


# In[89]:

# add  exception column for Swaptions
Final_df_Swaptions['Exceptions']="NaN" # create column


# In[90]:

# fill in Exceptions for Swaptions
for index, row in Final_df_Swaptions.iterrows():
    if int(Final_df_Swaptions.iloc[index, 11])>=2 and int(Final_df_Swaptions.iloc[index, 12])>0:
        Final_df_Swaptions.iloc[index, 13]="CHECK"
    else:
        Final_df_Swaptions.iloc[index, 13]="OK"


# ## Export the outputs

# In[91]:

# renaming valuation columns to make the currency clear
Final_df_Swaptions= Final_df_Swaptions.rename(index=str, columns={"Valuation_AllTrade":"Valuation_AllTrade(GBP)"})
Final_df_Swap= Final_df_Swap.rename(index=str, columns={"Valuation_AllTrade":"Valuation_AllTrade(GBP)"})
Final_df_Swaptions= Final_df_Swaptions.rename(index=str, columns={"PresentValue":"PresentValue(GBP)"})
Final_df_Swap= Final_df_Swap.rename(index=str, columns={"PresentValue":"PresentValue(GBP)"})


# In[92]:

Final_df_Swaptions.head()


# In[93]:

Final_df_Swap.head()


# In[94]:

# file names
file_nameSwaps="\Breaks All Trade Swaps "+lastBusDay+".csv"
file_nameSwaptions="\Breaks All Trade Swaptions "+lastBusDay+".csv"


# In[95]:

Final_df_Swap.Exceptions.value_counts() # Frequency table of Exceptions


# In[96]:

Final_df_Swaptions.Exceptions.value_counts() # Frequency table of Exceptions


# In[97]:

path_Output="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs"
path_Output_Archive="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Archive"


# In[98]:

# write to csv
Final_df_Swap.to_csv(path_Output+file_nameSwaps,header=True,index=False) # write once in the general folder for messing about
Final_df_Swaptions.to_csv(path_Output+file_nameSwaptions,header=True,index=False) # write once in the general folder for messing about
Final_df_Swap.to_csv(path_Output_Archive+file_nameSwaps,header=True,index=False) # write second time in the Archive
Final_df_Swaptions.to_csv(path_Output_Archive+file_nameSwaptions,header=True,index=False) # write second time in the Archive

