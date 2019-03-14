
# coding: utf-8

# # Tolerance Breaks Exceptions Oberon-AllTrade

# ## Inputs :
#   - VLN file (trades with Oberon valuations)
#   - POS file (for the reference rate to exclude OIS)
#   - Daily Discount Factors (for discounting payments)
#   - Oberon 40207 Premium and Cancellation report
#   - All Trade file
#   - Exchange Rates from Quasar LE04

# ## Outputs:
# ##### Single dataframe with :
#  - Absolute Tolerance exception column
#  - Relative Tolerance exception column
#  - Exception Column when Relative and Absolute are both broken
#  - % of notional column

# ## Code

# In[1]:

# load libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import os
import re


# In[2]:

# retrieve today`s date to output the files with the correct name
yesterday = dt.date.today() - timedelta(days=1)
# the variable yesterday needs to be manually created if yesterday was a holiday example: yesterday=datetime.date(2019, 4, 13)


# In[3]:

# exclude weekends (holidays will have to be manually accounted for)
if dt.date.weekday(yesterday) not in range (0,5):
    yesterday=dt.date.today() - timedelta(days=3)


# In[4]:

# store the date into a string
lastBusDay=yesterday.strftime("%d.%m.%Y")


# In[5]:

# inputs path
path_inputs="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Input Oberon-AllTrade/"


# ##### Automatic RegEx Method

# In[6]:

os.listdir(path_inputs)


# In[7]:

pattern_Payments  = r"Book.*\.xls" # patterns for the Input Files
pattern_POS  = r"\d*POS\.csv" 
pattern_VLN  = r"COB\s\d{8}\.xls" 
pattern_DFS  = r"DFS\s\d{8}\.xls" 
pattern_AllTrade  = r"Tri-Optima_AllTrades_Pricing.*" 
pattern_LE04  = r"LE04.*" # patterns for the CTD


# In[8]:

#retrieve Input Files with Regex or Manual input
for i in os.listdir(path_inputs):  # Regex method
    if re.search(pattern_POS,i):
        POS_df=pd.read_csv(path_inputs+i,dtype=object)
    elif re.search(pattern_Payments,i):
        Oberon40207=pd.read_excel(path_inputs+i, sheetname="Sheet1")
    elif re.search(pattern_VLN,i):
        VLN_df=pd.read_excel(path_inputs+i,sheetname="Sheet1")
    elif re.search(pattern_DFS,i):
        DFS_GBPSONIA=pd.read_excel(path_inputs+i, sheetname="GBP SONIA",header=None)
        DFS_EUREONIA=pd.read_excel(path_inputs+i, sheetname="EUR EONIA",header=None)
        DFS_USDOISNY=pd.read_excel(path_inputs+i, sheetname="USD OIS NY",header=None)
    elif re.search(pattern_AllTrade,i):
        AllTrade_df=pd.read_excel(path_inputs+i,sheetname="Tri-Optima_AllTrades_Pricing")
    elif re.search(pattern_LE04,i):
        with open(path_inputs+i, encoding='utf8') as LE04_txt: #open the txt file
            LE04_txt1=LE04_txt.read().replace('\n', '') # read the txt file and substitute the newline symbols with nothin
        
    else:    # Manual method
        VLN_filename=input("Please insert the VLN file name:")
        AllTrade_filename=input("Please insert the AllTrade file name:")
        POS_filename=input("Please insert the POS file name :")
        Oberon40207_filename=input("Please insert the Oberon40207 Report file name :")
        DFS_filename=input("Please insert the Daily DFS file name :")
        LE04_filename=input("Please insert the LE04 file name:")
        complete_path_VLN=path_inputs+VLN_filename+".xls"
        complete_path_POS=path_inputs+POS_filename+".csv"
        complete_path_Oberon40207=path_inputs+Oberon40207_filename+".xls"
        complete_path_DFS=path_inputs+DFS_filename+".xls"
        complete_path_AllTrade=path_inputs+AllTrade_filename+".xlsx"
        complete_path_LE04=path_inputs+LE04_filename+".TXT"
        VLN_df=pd.read_excel(complete_path_VLN,sheetname="Sheet1")
        AllTrade_df=pd.read_excel(complete_path_AllTrade,sheetname="Tri-Optima_AllTrades_Pricing")
        POS_df=pd.read_csv(complete_path_POS,dtype=object)
        Oberon40207=pd.read_excel(complete_path_Oberon40207, sheetname="Sheet1")
        DFS_GBPSONIA=pd.read_excel(complete_path_DFS, sheetname="GBP SONIA",header=None)
        DFS_EUREONIA=pd.read_excel(complete_path_DFS, sheetname="EUR EONIA",header=None)
        DFS_USDOISNY=pd.read_excel(complete_path_DFS, sheetname="USD OIS NY",header=None)
        with open(complete_path_LE04, encoding='utf8') as LE04_txt:
            LE04_txt1=LE04_txt.read().replace('\n', '')
        break
   


# #### Data Cleanup

# ##### VLN POS Cleanup

# In[9]:

# VLN File remove non needed columns
VLN_df1=VLN_df[["Swap Type","Ticket","Book","Valuation","Valuation Currency","Valuation Date","Receive Current Principal","Value 1bp(Inflation)","Value 1bp(Interest)"]]


# In[10]:

# POS File remove non needed columns
POS_df1=POS_df.filter(['Ticket','Receive Reference Rate','Pay Reference Rate'], axis=1)


# In[11]:

#POS_df2.groupby('Pay Reference Rate').count()


# In[12]:

# Create a list of sedols where Receive Reference Rate or Pay Reference Rate are GBP SONIA OIS
POS_df2_R = POS_df1[POS_df1['Receive Reference Rate'] == 'GBP SONIA OIS']
POS_df2_P = POS_df1[POS_df1['Pay Reference Rate'] == 'GBP SONIA OIS']
POS_df2_R = POS_df2_R.reset_index(drop=True) # reset index
POS_df2_P = POS_df2_P.reset_index(drop=True) # reset index
POS_df2_P_R = POS_df2_P.append(POS_df2_R) # top merge the two dataframes


# In[13]:

# remove tickets in VLN that are contained in POS_df2_P_R
VLN_df2 = VLN_df1[~VLN_df1['Ticket'].isin(POS_df2_P_R["Ticket"])]
VLN_df2 = VLN_df2.reset_index(drop=True) # reset index


# In[14]:

# remove all the trades that are present in the VLN but they are priced in markit only therefore the value in Oberon is wrong
# remove all rows with currencies that arent GBP EUR USD CAD and AUD (technically by selecting only the rows with those currencies in column Valuation Currency)
VLN_df2 = VLN_df2[VLN_df2['Valuation Currency'].isin(["GBP", "EUR","USD","CAD","AUD"])]


# In[15]:

# delete rows from AllTrade_df whose Id do not appear in VLN
AllTrade_df=AllTrade_df[AllTrade_df["SEDOL"].isin(VLN_df2["Ticket"])]
AllTrade_df=AllTrade_df.reset_index(drop=True) # reset index
# delete rows from VLN whose Id do not appear in AllTrade_df
VLN_df2=VLN_df2[VLN_df2["Ticket"].isin(AllTrade_df["SEDOL"])]
VLN_df2=VLN_df2.reset_index(drop=True) # reset index


# ##### All Trade Cleanup

# In[16]:

AllTrade_df=AllTrade_df[['BOOK', 'CPTY NAME', 'SEDOL',"ASSET CLASS","NOTIONAL","MTM DATE","GBP CPTY MTM","MTM CCY"]]


# In[17]:

#check for duplicates in All Trade
duplicated_AllTrade_df1 = AllTrade_df.duplicated(subset="SEDOL", keep="first")
any(x == True for x in duplicated_AllTrade_df1) # check if there is a True in the list


# In[18]:

#check for duplicates in  VLN_df2
duplicated_VLN_df2 = VLN_df2.duplicated(subset="Ticket", keep="first")
any(x == True for x in duplicated_VLN_df2) # check if there is a True in the list


# In[19]:

# delete rows from AllTrade_df whose Id do not appear in VLN
AllTrade_df=AllTrade_df[AllTrade_df["SEDOL"].isin(VLN_df2["Ticket"])]
AllTrade_df=AllTrade_df.reset_index(drop=True) # reset index
# delete rows from VLN whose Id do not appear in AllTrade_df
VLN_df2=VLN_df2[VLN_df2["Ticket"].isin(AllTrade_df["SEDOL"])]
VLN_df2=VLN_df2.reset_index(drop=True) # reset index


# In[20]:

#get indices of duplicate id rows in the All Trade and convert to a list
duplicated_AllTrade_df1 = AllTrade_df.duplicated(subset="SEDOL", keep="first") # using boolean masking
duplicated_AllTrade_df1= np.where(duplicated_AllTrade_df1 ==True)
#convert the tuple of indeces to a list
duplicated_AllTrade_df1=list(duplicated_AllTrade_df1)
# Create list with the indeces of the duplicate ids rows
duplicated_AllTrade_df1_list=[]
for n in duplicated_AllTrade_df1:
    duplicated_AllTrade_df1_list.extend(n)


# In[21]:

AllTrade_df["BOOK"]=AllTrade_df["BOOK"].astype(int) # convert to int just to remove decimal zero
AllTrade_df["BOOK"]=AllTrade_df["BOOK"].astype(str)# convert book column to string in AllTrade


# In[22]:

VLN_df2["Book"]=VLN_df2["Book"].astype(str) # convert book column to string in VLN_df2


# In[23]:

# get trade Ids from All trade which are duplicates
duplicate_TradeIds_AllTrade=[] # this is now a list of trades that are duplicates
for i in duplicated_AllTrade_df1_list:
    duplicate_TradeIds_AllTrade.append(AllTrade_df.iloc[i,2])


# In[24]:

indicestoremove=[]
for index, row in AllTrade_df.iterrows():
    if (AllTrade_df.iloc[index,2]) in (duplicate_TradeIds_AllTrade):#diverso dal book dello stesso sedol in markit, toglilo
        if AllTrade_df.iloc[index,0]!=VLN_df2.iloc[VLN_df2[VLN_df2['Ticket']==AllTrade_df.iloc[index,2]].index.item(),1]:
            xxx=VLN_df2.iloc[VLN_df2[VLN_df2['Ticket']==AllTrade_df.iloc[index,2]].index.item(),0]
            # rimuovi la row dall all trade con l index a cui ti trovi
            # create list of indices to remove because they are both duplicates and have different book than CTD
            indicestoremove.append(index)


# In[25]:

#remove indices
AllTrade_df=AllTrade_df.drop(AllTrade_df.index[indicestoremove])
AllTrade_df=AllTrade_df.reset_index(drop=True)


# In[26]:

# delete rows from AllTrade_df whose Id do not appear in VLN
AllTrade_df=AllTrade_df[AllTrade_df["SEDOL"].isin(VLN_df2["Ticket"])]
AllTrade_df=AllTrade_df.reset_index(drop=True) # reset index
# delete rows from VLN whose Id do not appear in AllTrade_df
VLN_df2=VLN_df2[VLN_df2["Ticket"].isin(AllTrade_df["SEDOL"])]
VLN_df2=VLN_df2.reset_index(drop=True) # reset index


# In[27]:

# remove trades from all trade file that have missing val
AllTrade_df = AllTrade_df[pd.notnull(AllTrade_df["GBP CPTY MTM"])]


# In[28]:

# remove trades from vln file that have missing val
VLN_df2 = VLN_df2[pd.notnull(VLN_df2["Valuation"])]


# In[29]:

# delete rows from AllTrade_df whose Id do not appear in VLN
AllTrade_df=AllTrade_df[AllTrade_df["SEDOL"].isin(VLN_df2["Ticket"])]
AllTrade_df=AllTrade_df.reset_index(drop=True) # reset index
# delete rows from VLN whose Id do not appear in AllTrade_df
VLN_df2=VLN_df2[VLN_df2["Ticket"].isin(AllTrade_df["SEDOL"])]
VLN_df2=VLN_df2.reset_index(drop=True) # reset index



# ##### Quasar LE04

# In[30]:

LE04_words=LE04_txt1.split() # split the string file into a list of words


# In[31]:

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


# In[32]:

# create dataframe with currency name and value
Currency_df=pd.DataFrame(Currency, columns=['Currency'])
Currency_df[1]=Currency_Value
Currency_df.columns=["Currency","Exchange_Rate"]


# ##### Oberon 40207 Cleanup

# In[33]:

# remove all rows where 2nd column is NaN of Oberon report
Oberon40207_df1=Oberon40207.dropna(subset=["Unnamed: 1"])
Oberon40207_df1 = Oberon40207_df1.reset_index(drop=True) # reset index


# In[34]:

# remove all unneded columns
Oberon40207_df2 = Oberon40207_df1.filter(["Unnamed: 1","Unnamed: 2","Unnamed: 15","Unnamed: 16"], axis=1)


# In[35]:

# put the dates next to the trades (the oberon report can have any number of dates and trades)
Oberon40207_df3 = Oberon40207_df2
accumulator=1
for index, row in Oberon40207_df3.iterrows():
    if Oberon40207_df3.iloc[index,0]=='Payment Date :':
        while Oberon40207_df3.iloc[index+accumulator,0]!='Payment Date :' :
            Oberon40207_df3.iloc[index+accumulator,1]=Oberon40207_df3.iloc[index,1]
            accumulator = accumulator+ 1
            if index+accumulator>=len(Oberon40207_df3):
                break
        else:
            accumulator=1
            
            
            
            #if index == len(Oberon40207_df3)-2:
               # break

#Oberon40207_df3.iloc[-1,1]=Oberon40207_df3.iloc[-2,1]



# In[36]:

# remove rows where Unnamed 1 is Payment Date
Oberon40207_df4 = Oberon40207_df3[Oberon40207_df3['Unnamed: 1'] != 'Payment Date :']
Oberon40207_df4 = Oberon40207_df4.reset_index(drop=True) # reset index


# In[37]:

# make the first row the header
Oberon40207_df4.columns = Oberon40207_df4.iloc[0] #give header the first row names
Oberon40207_df4=Oberon40207_df4.drop([0]) # drop the frist row
Oberon40207_df4=Oberon40207_df4.reset_index(drop=True) # resetting index


# ##### Discount Factors for payments

# In[38]:

# remove all columns from dfs dataframes after the second
DFS_USDOISNY1=DFS_USDOISNY[DFS_USDOISNY.columns[0:2]] 
DFS_GBPSONIA1=DFS_GBPSONIA[DFS_GBPSONIA.columns[0:2]] 
DFS_EUREONIA1=DFS_EUREONIA[DFS_EUREONIA.columns[0:2]] 


# In[39]:

# renaming the dfs dataframe`s columns
DFS_USDOISNY1.columns = ['Date', 'DFS']
DFS_GBPSONIA1.columns = ['Date', 'DFS']
DFS_EUREONIA1.columns = ['Date', 'DFS']


# In[40]:

pd.options.mode.chained_assignment = None # disabling chained assignment warnings
# add the first row as today s date and dfs = 1 because USD and EUR start from tomorrow
DFS_USDOISNY1.loc[-1] = [DFS_USDOISNY1.iloc[0,0]-timedelta(days=1) ,float(1)]  # adding a row with the correct data
DFS_USDOISNY1 = DFS_USDOISNY1.reset_index(drop=True) # reset index
DFS_EUREONIA1.loc[-1] = [DFS_EUREONIA1.iloc[0,0]-timedelta(days=1) ,float(1)]  
DFS_EUREONIA1 = DFS_EUREONIA1.reset_index(drop=True) 


# In[41]:

Oberon40207_df4['C/Pty Trade ID']=pd.to_datetime(Oberon40207_df4['C/Pty Trade ID'])


# In[42]:

# change column 1 timestamp format in the Oberon40207_df5.
Oberon40207_df4['C/Pty Trade ID'] = Oberon40207_df4['C/Pty Trade ID'].dt.strftime('%Y-%m-%d')


# In[43]:

# create DFS column in Oberon40207_df4
Oberon40207_df5=Oberon40207_df4
Oberon40207_df5['DFS']="NaN" # create column


# In[44]:

# based on the currency and date put the appropiate discount factor next to ticket 
# DFS_GBPSONIA DFS_EUREONIA DFS_USDOISNY
for index, row in Oberon40207_df5.iterrows():
    if Oberon40207_df5.iloc[index,3]=='USD':
        Oberon40207_df5.iloc[index,4]= DFS_USDOISNY1.iloc[DFS_USDOISNY1[DFS_USDOISNY1['Date']==Oberon40207_df5.iloc[index,1]].index.item() ,1] # the code in the row index retrieves the index of DFS where the date corresponds to the date of the trade in the Oberon40207 dataframe    
    elif Oberon40207_df5.iloc[index,3]=='GBP':
        Oberon40207_df5.iloc[index,4]= DFS_GBPSONIA1.iloc[DFS_GBPSONIA1[DFS_GBPSONIA1['Date']==Oberon40207_df5.iloc[index,1]].index.item(),1]
    elif Oberon40207_df5.iloc[index,3]=='EUR':
        Oberon40207_df5.iloc[index,4]= DFS_EUREONIA1.iloc[DFS_EUREONIA1[DFS_EUREONIA1['Date']==Oberon40207_df5.iloc[index,1]].index.item() ,1] 
        


# In[45]:

# remove rows of Oberon40207_df5 where DFS is NaN (that means it is a weird currency and it is not priced in Oberon)
Oberon40207_df5 = Oberon40207_df5[Oberon40207_df5.DFS != "NaN"]
Oberon40207_df5 = Oberon40207_df5.reset_index(drop=True) # reset index


# In[46]:

# create discounted amount column
Oberon40207_df5['Discounted_Amount']="NaN" # create column


# In[47]:

# Fill in Discounted Amount column
Oberon40207_df5['Discounted_Amount'] = Oberon40207_df5['Amount'] * Oberon40207_df5['DFS']


# In[48]:

# remove rows(trades) in Oberon40207_df5 that do not appear in VLN_df2
Oberon40207_df6 = Oberon40207_df5[Oberon40207_df5['Ticket'].isin(VLN_df2["Ticket"])]
Oberon40207_df6 = Oberon40207_df6.reset_index(drop=True) # reset index


# In[49]:

# Fix the VLN_df2 Valuation column by subtracting or adding the Discounted_Amount
for index, row in Oberon40207_df6.iterrows():
    if Oberon40207_df6.iloc[index,5]>0:# if the Amount is positive then subtract the abs of Amount from the valuation in the larger dataset
        VLN_df2.iloc[ VLN_df2[VLN_df2['Ticket']==Oberon40207_df6.iloc[index,0]].index.item(),3]=(VLN_df2.iloc[ VLN_df2[VLN_df2['Ticket']==Oberon40207_df6.iloc[index,0]].index.item(),3])-abs(Oberon40207_df6.iloc[index,5]) 
    elif Oberon40207_df6.iloc[index,5]<0:# if the Amount is negative then add the abs of Amount to the valuation in the larger dataset
        VLN_df2.iloc[ VLN_df2[VLN_df2['Ticket']==Oberon40207_df6.iloc[index,0]].index.item(),3]=(VLN_df2.iloc[ VLN_df2[VLN_df2['Ticket']==Oberon40207_df6.iloc[index,0]].index.item(),3])+abs(Oberon40207_df6.iloc[index,5]) 


# ##### Use exchange rates to the AllTrade

# In[50]:

# create Exchange_Rate column in AllTrade_df2
AllTrade_df['Exchange_Rate']="NaN" # create column


# In[51]:

AllTrade_df2=AllTrade_df


# In[52]:

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


# In[53]:

# create new Valuation column in AllTrade_df2
AllTrade_df2['Valuation_AllTrade']="NaN" # create column


# In[54]:

# change Exchange rate column to float
AllTrade_df2["Exchange_Rate"]=AllTrade_df2["Exchange_Rate"].astype(float)
# multiply valuation for the exchange rate
AllTrade_df2["Valuation_AllTrade"]=AllTrade_df2["GBP CPTY MTM"]/AllTrade_df2["Exchange_Rate"]


# #### Use exhange rate to Oberon

# In[55]:

VLN_df2['Exchange_Rate']="NaN" # create column


# In[56]:

# based on the currency put the appropiate exchange rate in the rows
for index, row in VLN_df2.iterrows():
    if VLN_df2.iloc[index,4]=='USD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="US DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='EUR':
        indextochange_list=list(np.where(Currency_df["Currency"]=="EURO")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='GBP':
        VLN_df2.iloc[index,9]= 1
    elif VLN_df2.iloc[index,4]=='JPY':
        indextochange_list=list(np.where(Currency_df["Currency"]=="JAPANESE YEN")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='AUD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="AUSTRALIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='CAD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="CANADIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='CHF':
        indextochange_list=list(np.where(Currency_df["Currency"]=="SWISS FRANC")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='HKD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="HONG KONG DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='NOK':
        indextochange_list=list(np.where(Currency_df["Currency"]=="NORWEGIAN KRONER")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='SEK':
        indextochange_list=list(np.where(Currency_df["Currency"]=="SWEDISH KRONER")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif VLN_df2.iloc[index,4]=='KRW':
        indextochange_list=list(np.where(Currency_df["Currency"]=="KOREA (SOUTH) WON")[0])
        indextochange_int=indextochange_list[0]
        VLN_df2.iloc[index,9]= Currency_df.iloc[indextochange_int,1]


# In[57]:

# create New Valuation after exchange rates column in VLN_df2
VLN_df2['Valuation_Oberon']="NaN" # create column


# In[58]:

# change Exchange rate column to float
VLN_df2["Exchange_Rate"]=VLN_df2["Exchange_Rate"].astype(float)
# divide valuation for the exchange rate
VLN_df2["Valuation_Oberon"]=VLN_df2["Valuation"]/VLN_df2["Exchange_Rate"]


# In[59]:

VLN_df2.head()


# In[60]:

VLN_df2.Valuation_Oberon.isnull().values.any()


# ## Create Tolerance Breaks Exceptions

# In[61]:

# rename the ticket column to sedol in order to merge
VLN_df2= VLN_df2.rename(index=str, columns={"Ticket":"SEDOL"})
# Merge on SEDOL
Final_df=pd.merge(VLN_df2, AllTrade_df2, on="SEDOL")


# In[62]:

# pick only the needed columns
Final_df=Final_df[["SEDOL","Swap Type","Book","Valuation Date","NOTIONAL","CPTY NAME","Valuation_AllTrade","Valuation_Oberon","Value 1bp(Interest)"]]


# In[63]:

Final_df.head()


# In[64]:

# create the required columns


# In[65]:

# difference in Valuation for Swaps and Swaptions
Final_df['Diff_AllTrade_Oberon'] = abs(abs(Final_df['Valuation_AllTrade']) - abs(Final_df['Valuation_Oberon']) )


# In[66]:

# Create column with absolute tolerance exceptions
Final_df['Abs_Tolerance']="NaN" # create column


# In[67]:

# fill in Abs Tolerance
for index, row in Final_df.iterrows():
    if Final_df.iloc[index, 9]<1500000:
        Final_df.iloc[index, 10]=0
    elif Final_df.iloc[index, 9]>=1500000 and Final_df.iloc[index, 9]<3000000:
        Final_df.iloc[index, 10]=1
    elif Final_df.iloc[index, 9]>=3000000:
        Final_df.iloc[index, 10]=2
    


# In[68]:

Final_df.Diff_AllTrade_Oberon.isnull().values.any()


# In[69]:

# create pv01 tolerance for the swaps
Final_df['PV01_Tolerance']="NaN" # create column


# In[70]:

# fill in Pv01 Tolerance
Final_df['PV01_Tolerance'] = Final_df['Diff_AllTrade_Oberon'] / abs(Final_df["Value 1bp(Interest)"]) 


# In[71]:

# create PV01 exceptions column
Final_df['PV01_Exceptions']="NaN" # create column


# In[72]:

# fill in PV01 Exceptions
for index, row in Final_df.iterrows():
    if Final_df.iloc[index, 11]>5:
        Final_df.iloc[index, 12]=1
    else:
        Final_df.iloc[index, 12]=0


# In[73]:

# add % of notional column
Final_df['%Notional']="NaN" # create column


# In[74]:

# fill in % of notional column
Final_df['%Notional'] = Final_df["Diff_AllTrade_Oberon"] / Final_df["NOTIONAL"]


# In[75]:

# add Exceptions column
Final_df['Exceptions']="NaN" # create column


# In[76]:

# fill in Exceptions
for index, row in Final_df.iterrows():
    if int(Final_df.iloc[index, 10])>=2 and int(Final_df.iloc[index, 12])>0:
        Final_df.iloc[index, 14]=1
    else:
        Final_df.iloc[index, 14]=0


# In[77]:

Final_df.Exceptions.value_counts()


# In[78]:

path_Output="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs"
path_Output_Archive="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Archive"


# In[79]:

# file names
file_name="\Breaks Oberon-AllTrade "+lastBusDay+".csv"


# In[80]:

# write to csv
Final_df.to_csv(path_Output+file_name,header=True,index=False) # write once in the general folder for messing about
Final_df.to_csv(path_Output_Archive+file_name,header=True,index=False) # write once in Archive


# ### Please note 

# - removes the trades in Oberon that arent GBP,EUR,USD,CAD or AUD because the value in Oberon is wrong
# - removes non shared trades
# - duplicates in All trade are selected based on fund (if fund matches in Oberon)
# - removes All trade file sedols with no valuation
# - It uses the Valuation in oberon converted with exhcange rates in GBP, and uses All Trade CPTY MTM converted to GBP with excghange rates
# - removes trades in Oberon or All Trade with valuation missing
