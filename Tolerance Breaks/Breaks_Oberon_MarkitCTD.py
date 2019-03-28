
# coding: utf-8

# # Tolerance Breaks Exceptions Oberon-Markit

# ## Inputs :
#   - VLN file (trades with Oberon valuations)
#   - Markit Lgim NY CTD Rates for Swaps ( Markit Val :Interest and Zero Coupons,InfSwaps,GBP Swaptions)
#   - POS file (for the reference rate to exclude OIS)
#   - Daily Discount Factors
#   - Oberon 40207 Premium and Cancellation report
#   - Swaptions Oberon report (SWN file)
#   - LE04 Report from Quasar

# ## Outputs:
# ##### Single dataframe with :
#  - Absolute Tolerance exception column
#  - Relative Tolerance exception column
#  - Exception Column when Relative and Absolute are both broken
#  - % of notional column

# ##### Please note:
# 
#   
#   - Assumes they re all csa Clean (for the payment discounting)
#   - Removes unshared trades between Markit and Oberon
#   - Removes the trades in VLN and SWN that arent GBP,EUR,USD,CAD or AUD because the value in Oberon is wrong
#   - It uses PresentValue from Markit which is in GBP and converts the Oberon Value in GBP with LE04
#   - Takes into account payments for Swaps and Swaptions

# ## Code

# In[1]:

# inputs path
path_inputs="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Input Oberon/"


# In[2]:

# load libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import os
import re
from QuantLib import *


# In[3]:

pd.options.mode.chained_assignment = None # disabling chained assignment warnings


# ##### Retrieve COB date datetime method (only takes into account weekends)

# In[4]:

# retrieve today`s date to output the files with the correct name
#yesterday = dt.date.today() - timedelta(days=1)
# the variable yesterday needs to be manually created if yesterday was a holiday example: yesterday=datetime.date(2019, 4, 13)


# In[5]:

# exclude weekends (holidays will have to be manually accounted for)
#if dt.date.weekday(yesterday) not in range (0,5):
   # yesterday=dt.date.today() - timedelta(days=3)


# In[6]:

# store the date into a string
#lastBusDay=yesterday.strftime("%d.%m.%Y")


# ##### Retrieve COB date QuantLib method (takes into account all uk calendar holidays)

# In[7]:

# load UK calendar
uk_calendar=UnitedKingdom()


# In[8]:

today = dt.date.today()


# In[9]:

dayQ=today.day
monthQ=today.month
yearQ=today.year


# In[10]:

QBDate=Date(dayQ,monthQ,yearQ)


# In[11]:

for i in range(1,30):
    uk_busdays = uk_calendar.businessDaysBetween(QBDate-i,QBDate)
    if uk_busdays == 1:
        lastBusDay_original=QBDate-i
        break


# In[12]:

day=lastBusDay_original.dayOfMonth()
month=lastBusDay_original.month()
year=lastBusDay_original.year()


# In[13]:

lastBusDay_original=dt.datetime(year,month,day)


# In[14]:

# store the date into a string
lastBusDay=lastBusDay_original.strftime("%d.%m.%Y")


# In[15]:

lastBusDay


# ## If the date needs to be input manually use the lastBusDay assignment below

# In[16]:

#lastBusDay="mm.dd.yy"


# ##### Automatic RegEx Method (Markit CTD and LE04 are still from input folder)

# In[17]:

# import POS file automatically with regex
lastBusDayPOS=lastBusDay_original.strftime("%Y%m%d") # format date in appropiate way
POSPATH="S:/Other/Datafeeds/Oberon1/" 
pattern_POS  = lastBusDayPOS+r"\d*POS\.csv" 
for i in os.listdir(POSPATH):  # Regex method
    if re.search(pattern_POS,i):
        POS_df=pd.read_csv(POSPATH+i,dtype=object)
        break


# In[18]:

# import Book1 (Oberon payments) from input folder
pattern_Payments  = r"Book.*\.xls"
for i in os.listdir(path_inputs):
    if re.search(pattern_Payments,i):
        Oberon40207=pd.read_excel(path_inputs+i, sheetname="Sheet1")
        break


# In[19]:

# import VLN file automatically with regex
lastBusDayVLN=lastBusDay_original.strftime("%d%m%Y") # format date in appropiate way
VLNPATH="S:/Shared/Operations/Derivatives/Daily MTM File/"
pattern_VLN  = "COB "+lastBusDayVLN
for i in os.listdir(VLNPATH):
    if re.search(pattern_VLN,i):
        VLN_df=pd.read_excel(VLNPATH+i,sheetname="Sheet1")
        break


# In[20]:

# import DFS automatically with regex
DFSfolder1=lastBusDay_original.strftime("%Y/")
DFSfolder2=lastBusDay_original.strftime("%b %Y/")
DFSPATH="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Life Funds/Discount Factors/"+DFSfolder1+DFSfolder2
lastBusDayDFS=lastBusDay_original.strftime("%d%m%Y")
pattern_DFS = "DFS "+lastBusDayDFS+".xls"
for i in os.listdir(DFSPATH):
    if re.search(pattern_DFS,i):
        DFS_GBPSONIA=pd.read_excel(DFSPATH+i, sheetname="GBP SONIA",header=None)
        DFS_EUREONIA=pd.read_excel(DFSPATH+i, sheetname="EUR EONIA",header=None)
        DFS_USDOISNY=pd.read_excel(DFSPATH+i, sheetname="USD OIS NY",header=None)
        break


# In[21]:

# import LE04 file from input folder
pattern_LE04  = r"LE04.*"
for i in os.listdir(path_inputs):
    if re.search(pattern_LE04 ,i):
        with open(path_inputs+i, encoding='utf8') as LE04_txt: #open the txt file
            LE04_txt1=LE04_txt.read().replace('\n', '')
        break


# In[22]:

# import markit file
pattern_CTD  = r".*LGIM_NY_Rates_CTD.*" # patterns for the LE04
for i in os.listdir(path_inputs):   # Regex method
    if re.search(pattern_CTD,i):
        Markit_Swap=pd.read_excel(path_inputs+i,sheetname="Swap")
        Markit_InfSwap=pd.read_excel(path_inputs+i,sheetname="InfSwap")
        Markit_Swaptions=pd.read_excel(path_inputs+i,sheetname="Swaption")
        break


# In[23]:

# import SWN file automatically with regex
lastBusDaySWN=lastBusDay_original.strftime("%d%m%Y") # format date in appropiate way 
SWNPATH="S:/Shared/Operations/Derivatives/TriResolve/SWN/LIVE/"
pattern_SWN  = lastBusDaySWN+"_SWN.csv"
SWN_file=pd.read_csv(SWNPATH+pattern_SWN)


# ### USE THIS IF THERE ARE ISSUES WITH AUTOMATIC METHOD (change cell type from Markdown to Code)

# pattern_Payments  = r"Book.*\.xls" # patterns for the Input Files
# pattern_POS  = r"\d*POS\.csv" 
# pattern_VLN  = r"COB\s\d{8}\.xls" 
# pattern_DFS  = r"DFS\s\d{8}\.xls" 
# pattern_CTD  = r"LGIM_NY_Rates_CTD.*\.xls" 
# pattern_SWN  = r".*SWN\.csv" 
# pattern_LE04  = r"LE04.*" 
# 
# #retrieve Input Files with Regex or Manual input
# for i in os.listdir(path_inputs):  # Regex method
#     if re.search(pattern_POS,i):
#         POS_df=pd.read_csv(path_inputs+i,dtype=object)
#     elif re.search(pattern_Payments,i):
#         Oberon40207=pd.read_excel(path_inputs+i, sheetname="Sheet1")
#     elif re.search(pattern_VLN,i):
#         VLN_df=pd.read_excel(path_inputs+i,sheetname="Sheet1")
#     elif re.search(pattern_DFS,i):
#         DFS_GBPSONIA=pd.read_excel(path_inputs+i, sheetname="GBP SONIA",header=None)
#         DFS_EUREONIA=pd.read_excel(path_inputs+i, sheetname="EUR EONIA",header=None)
#         DFS_USDOISNY=pd.read_excel(path_inputs+i, sheetname="USD OIS NY",header=None)
#     elif re.search(pattern_CTD,i):
#         Markit_Swap=pd.read_excel(path_inputs+i, sheetname="Swap")#Swap
#         Markit_InfSwap=pd.read_excel(path_inputs+i, sheetname="InfSwap")#InfSwap
#         Markit_Swaptions=pd.read_excel(path_inputs+i,sheetname="Swaption")#Swaptions
#     elif re.search(pattern_SWN,i):
#         SWN_file=pd.read_csv(path_inputs+i)#Swaptions
#     elif re.search(pattern_LE04,i):
#         with open(path_inputs+i, encoding='utf8') as LE04_txt: #open the txt file
#             LE04_txt1=LE04_txt.read().replace('\n', '') # read the txt file and substitute the newline symbols with nothin
#     else:    # Manual method
#         VLN_filename=input("Please insert the VLN file name:")
#         Markit_filename=input("Please insert the Markit file name :")
#         POS_filename=input("Please insert the POS file name :")
#         Oberon40207_filename=input("Please insert the Oberon40207 Report file name :")
#         DFS_filename=input("Please insert the Daily DFS file name :")
#         SWN_filename=input("Please insert the SWN file name")
#         complete_path_VLN=path_inputs+VLN_filename+".xls"
#         complete_path_Markit=path_inputs+Markit_filename+".xls"
#         complete_path_POS=path_inputs+POS_filename+".csv"
#         complete_path_Oberon40207=path_inputs+Oberon40207_filename+".xls"
#         complete_path_DFS=path_inputs+DFS_filename+".xls"
#         complete_path_SWN=path_inputs+SWN_filename+".csv"
#         VLN_df=pd.read_excel(complete_path_VLN,sheetname="Sheet1")
#         Markit_Swap=pd.read_excel(complete_path_Markit, sheetname="Swap")
#         Markit_InfSwap=pd.read_excel(complete_path_Markit, sheetname="InfSwap")
#         Markit_Swaptions=pd.read_excel(complete_path_Markit, sheetname="Swaption")
#         POS_df=pd.read_csv(complete_path_POS,dtype=object)
#         Oberon40207=pd.read_excel(complete_path_Oberon40207, sheetname="Sheet1")
#         SWN_file=pd.read_csv(complete_path_SWN)#Swaptions
#         DFS_GBPSONIA=pd.read_excel(complete_path_DFS, sheetname="GBP SONIA",header=None)
#         DFS_EUREONIA=pd.read_excel(complete_path_DFS, sheetname="EUR EONIA",header=None)
#         DFS_USDOISNY=pd.read_excel(complete_path_DFS, sheetname="USD OIS NY",header=None)
#         break
#    
#         
# 

# ##### Manual Input Method

# In[24]:

# input file name for VLN file
#VLN_filename=input("Please insert the VLN file name:")


# In[25]:

# input file name for Markit
#Markit_filename=input("Please insert the Markit file name :")


# In[26]:

# input file name for POS ,sheetname="Sheet1"
#POS_filename=input("Please insert the POS file name :")


# In[27]:

# input file name for Oberon40207 Report ,sheetname="Sheet1"
#Oberon40207_filename=input("Please insert the Oberon40207 Report file name :")


# In[28]:

# input file name for Discount Factors
#DFS_filename=input("Please insert the Daily DFS file name :")


# In[29]:

# Complete paths of the input files
#complete_path_VLN=path_inputs+VLN_filename+".xls"
#complete_path_Markit=path_inputs+Markit_filename+".xls"
#complete_path_POS=path_inputs+POS_filename+".csv"
#complete_path_Oberon40207=path_inputs+Oberon40207_filename+".xls"
#complete_path_DFS=path_inputs+DFS_filename+".xls"


# In[30]:

# Load VLN
#VLN_df=pd.read_excel(complete_path_VLN,sheetname="Sheet1")


# In[31]:

# Load Markit
#Swap
#Markit_Swap=pd.read_excel(complete_path_Markit, sheetname="Swap")
#InfSwap
#Markit_InfSwap=pd.read_excel(complete_path_Markit, sheetname="InfSwap")
#Swaptions
#Markit_Swaptions=pd.read_excel(complete_path_Markit, sheetname="Swaption")


# In[32]:

# Load POS
#POS_df=pd.read_csv(complete_path_POS,dtype=object)


# In[33]:

# Load Oberon40207 Report
#Oberon40207=pd.read_excel(complete_path_Oberon40207, sheetname="Sheet1")


# In[34]:

# Load discount factors
#DFS_GBPSONIA=pd.read_excel(complete_path_DFS, sheetname="GBP SONIA",header=None)
#DFS_EUREONIA=pd.read_excel(complete_path_DFS, sheetname="EUR EONIA",header=None)
#DFS_USDOISNY=pd.read_excel(complete_path_DFS, sheetname="USD OIS NY",header=None)


# #### Data Cleanup

# ##### VLN, POS and SWN Cleanup

# In[35]:

# VLN File remove non needed columns
VLN_df1=VLN_df.drop(["Oberon ID","Value 1bp(Inflation)","Value 1bp(Interest)","Exch.Principals","Receive Currency","Receive Discount Curve","Receive Estimation Curve","Receive Valuation","Receive Last Rollover Discount Factor","Receive PV of Current Principal","Receive Valuation inc Principal Exch","Receive Valuation inc Principal Exch in Val Ccy","Pay Currency","Pay Discount Curve","Pay Estimation Curve","Pay Valuation","Pay Current Principal","Pay Last Rollover Discount Factor","Pay PV of Current Principal","Pay Valuation inc Principal Exch","Pay Valuation inc Principal Exch in Val Ccy"],axis=1)


# In[36]:

# POS File remove non needed columns
POS_df1=POS_df.filter(['Ticket','Receive Reference Rate','Pay Reference Rate'], axis=1)


# In[37]:

#POS_df2.groupby('Pay Reference Rate').count()


# In[38]:

# Create a list of sedols where Receive Reference Rate or Pay Reference Rate are GBP SONIA OIS
POS_df2_R = POS_df1[POS_df1['Receive Reference Rate'] == 'GBP SONIA OIS']
POS_df2_P = POS_df1[POS_df1['Pay Reference Rate'] == 'GBP SONIA OIS']
POS_df2_R = POS_df2_R.reset_index(drop=True) # reset index
POS_df2_P = POS_df2_P.reset_index(drop=True) # reset index
POS_df2_P_R = POS_df2_P.append(POS_df2_R) # top merge the two dataframes


# In[39]:

# remove tickets in VLN that are contained in POS_df2_P_R
VLN_df2 = VLN_df1[~VLN_df1['Ticket'].isin(POS_df2_P_R["Ticket"])]
VLN_df2 = VLN_df2.reset_index(drop=True) # reset index


# In[40]:

# remove all rows with currencies that arent GBP EUR USD CAD and AUD (technically by selecting only the rows with those currencies in column Valuation Currency)
VLN_df2 = VLN_df2[VLN_df2['Valuation Currency'].isin(["GBP", "EUR","USD","CAD","AUD"])]


# In[41]:

VLN_df2["Valuation Currency"].unique()


# In[42]:

SWN_file.head()


# In[43]:

SWN_file=SWN_file[["Swap Type","Ticket","Book","Valuation","Valuation Currency","Valuation Date"]]


# In[44]:

# remove all rows with currencies that arent GBP EUR USD CAD and AUD (technically by selecting only the rows with those currencies in column Valuation Currency)
SWN_file = SWN_file[SWN_file['Valuation Currency'].isin(["GBP", "EUR","USD","CAD","AUD"])]


# ##### Markit Cleanup

# In[45]:

#remove non needed columns Swaps (this is using the PVLocal, not the Present value, because Oberon trades are in local currency)
Markit_Swap_1=Markit_Swap.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 4', 'Unnamed: 5', 'Unnamed: 7',"Unnamed: 8","Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12","Unnamed: 13","Unnamed: 14","Unnamed: 15","Unnamed: 16","Unnamed: 17","Unnamed: 19"], axis=1)
#remove non needed columns InfSwaps(this is using the PVLocal, not the Present value, because Oberon trades are in local currency)
Markit_InfSwap_1=Markit_InfSwap.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 4','Unnamed: 5', 'Unnamed: 7',"Unnamed: 8","Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12","Unnamed: 13","Unnamed: 14","Unnamed: 15","Unnamed: 16","Unnamed: 17","Unnamed: 18","Unnamed: 19","Unnamed: 21"], axis=1)
# Markit_Swaptionsremove non needed columns Swaptions(this is using the PVLocal, not the Present value, because Oberon trades are in local currency)
Markit_Swaptions=Markit_Swaptions[['Trade Valuations', 'Unnamed: 2',"Unnamed: 3", 'Unnamed: 5',"Unnamed: 14"]]


# In[46]:

#make the third row the header
Markit_InfSwap_1.columns = Markit_InfSwap_1.iloc[2] #give header the third row names
Markit_Swap_1.columns = Markit_Swap_1.iloc[2] #give header the third row names
Markit_Swaptions.columns = Markit_Swaptions.iloc[2]
Markit_InfSwap_1=Markit_InfSwap_1.reset_index(drop=True) # resetting index
Markit_Swap_1=Markit_Swap_1.reset_index(drop=True) #resetting index
Markit_Swaptions=Markit_Swaptions.reset_index(drop=True) #resetting index


# In[47]:

# remove the first three rows
Markit_Swap_1= Markit_Swap_1.drop([0,1,2])
Markit_InfSwap_1= Markit_InfSwap_1.drop([0,1,2])
Markit_Swaptions= Markit_Swaptions.drop([0,1,2])
Markit_InfSwap_1=Markit_InfSwap_1.reset_index(drop=True) # resetting index
Markit_Swap_1=Markit_Swap_1.reset_index(drop=True) #resetting index
Markit_Swaptions=Markit_Swaptions.reset_index(drop=True) #resetting index


# In[48]:

# top merge Swaps and InfSwaps  in a single dataframe
Markit_df1=Markit_Swap_1.append(Markit_InfSwap_1)
#resetting row index
Markit_df1=Markit_df1.reset_index(drop=True)


# In[49]:

# resetting column order
#columnsTitles = ['Trade Valuations','Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3','Unnamed: 4','Unnamed: 5','Unnamed: 6','Unnamed: 7','Unnamed: 8','Unnamed: 9','Unnamed: 10','Unnamed: 11','Unnamed: 12','Unnamed: 13','Unnamed: 14','Unnamed: 15','Unnamed: 16','Unnamed: 17','Unnamed: 18','Unnamed: 19','Unnamed: 20','Unnamed: 21']
#Markit_df2=Markit_df1.reindex(columns=columnsTitles)


# In[50]:

# remove all rows with LegId non-NaN
Markit_df2 = Markit_df1[pd.isnull(Markit_df1['LegId'])]
#resetting index
Markit_df2=Markit_df2.reset_index(drop=True)


# In[51]:

# delete rows from the Markit dataframe whose Id do not match any id in the VLN file
Markit_df3=Markit_df2[Markit_df2["TradeId"].isin(VLN_df2["Ticket"])]
Markit_df3=Markit_df3.reset_index(drop=True) # reset index


# In[52]:

# delete rows from the VLN file whose Id do not match any id in the Markit file
VLN_df2=VLN_df2[VLN_df2["Ticket"].isin(Markit_df3["TradeId"])]
VLN_df2=VLN_df2.reset_index(drop=True) # reset index


# In[53]:

# Swaptions 
#convert sedol columns to string (convert to int first to remove the .0 at the end)
Markit_Swaptions["TradeId"]=Markit_Swaptions["TradeId"].astype(int)
Markit_Swaptions["TradeId"]=Markit_Swaptions["TradeId"].astype(str)
SWN_file["Ticket"]=SWN_file["Ticket"].astype(int)
SWN_file["Ticket"]=SWN_file["Ticket"].astype(str)
SWN_file["Book"]=SWN_file["Book"].astype(int) # same for book
SWN_file["Book"]=SWN_file["Book"].astype(str)


# In[54]:

# delete rows from the Markit_Swaptions dataframe whose Id do not match any id in the SWN_file
Markit_Swaptions=Markit_Swaptions[Markit_Swaptions["TradeId"].isin(SWN_file["Ticket"])]
Markit_Swaptions=Markit_Swaptions.reset_index(drop=True) # reset index
# delete rows from the VLN file whose Id do not match any id in the Markit file
SWN_file=SWN_file[SWN_file["Ticket"].isin(Markit_Swaptions["TradeId"])]
SWN_file=SWN_file.reset_index(drop=True) # reset index


# In[55]:

# remove legId column for swaps
Markit_df3=Markit_df3.drop(["LegId"],axis=1)


# In[56]:

#Check for duplicates in Markit file
duplicated_Markit_df3 = Markit_df3.duplicated(subset="TradeId", keep="first")
any(x == True for x in duplicated_Markit_df3) # check if there is a True in the list


# In[57]:

#Check for duplicates in VLN file
duplicated_VLN_df2=VLN_df2.duplicated(subset="Ticket", keep="first")
any(x == True for x in duplicated_VLN_df2) # check if there is a True in the list


# In[58]:

#get indices of duplicate id rows in the Markit File
#duplicated_Markit_df5_1 = Markit_df5.duplicated(subset="TradeId", keep=False)
#Markit5_duplicated_indeces= np.where(duplicated_Markit_df5_1 ==True)


# In[59]:

# convert the tuple of indeces to a list
#Markit5_duplicated_indeces_list=list(Markit5_duplicated_indeces)


# In[60]:

# Create list with the indeces of the duplicate ids rows
#Markit5_duplicated_indeces_list1=[]
#for n in Markit5_duplicated_indeces:
   # Markit5_duplicated_indeces_list1.extend(n)


# In[61]:

# retrieve the rows for the duplicated Ids at indeces 127:160, 417:428,433:435,869:902,1863:1874,1914:1916
#Markit_df5_duplicated_rows=Markit_df5[Markit_df5.index.isin(Markit5_duplicated_indeces_list1)]


# In[62]:

# sort this dataframe by trade id in order to check wether the rows are the same
#Markit_df5_duplicated_rows=Markit_df5_duplicated_rows.sort_values(by=['TradeId'])


# In[63]:

# remove duplicate rows in the Markit file by only leaving the first observation
#Markit_df6=Markit_df5
#for index, row in Markit_df5.iterrows():
    #if duplicated_Markit_df5[index]==True:
       # Markit_df6= Markit_df6.drop([index]) 


# In[64]:

# REMINDER :Active dataframes : VLN_df2,Markit_df3
#VLN_df2.head()
#Markit_df3.head()


# ##### Create VLN-Markit merged dataframe for Swaps

# In[65]:

VLN_Markit= VLN_df2.rename(index=str, columns={"Ticket":"TradeId"})#rename VLN Ticket to TradeId in order to use the merge function


# In[66]:

# Merge so that VLN dataframe has markits valuation
Final_df=pd.merge(VLN_Markit, Markit_df3, on="TradeId")


# In[67]:

# rename Markit and VLN valuation columns
Final_df= Final_df.rename(index=str, columns={"PresentValue":"MarkitValuation","Valuation":"OberonValuation"})


# In[68]:

# Remove trades where the valuation is NA in either Markit or VLN
#Final_df2=Final_df1.dropna(subset=["OberonValuation"])
#Final_df2=Final_df1.dropna(subset=["MarkitValuation"])
#Final_df1=Final_df.dropna() # drop the rows where at least one element is NA
#Final_df1=Final_df1.reset_index(drop=True) # reset index


# In[69]:

#Final_df7.Markit_Oberon_Diff.value_counts() # count unique values in column
Final_df.MarkitValuation.isnull().values.any() # check if any value in column is NaN


# In[70]:

Final_df.OberonValuation.isnull().values.any() # check if any value in column is NaN


# In[71]:

# remove rows where there is no oberon or markit val
Final_df=Final_df.dropna(subset=['OberonValuation',"MarkitValuation"])
Final_df = Final_df.reset_index(drop=True) # reset index


# ##### Create SWN-Markit merged dataframe for Swaptions

# In[72]:

SWN_file= SWN_file.rename(index=str, columns={"Ticket":"TradeId"})#rename SWN_file Ticket to TradeId in order to use the merge function


# In[73]:

# Merge so that SWN dataframe has markits valuation
Final_SWN=pd.merge(SWN_file, Markit_Swaptions, on="TradeId")


# In[74]:

Final_SWN.head()


# In[75]:

# choose the needed columns
Final_SWN=Final_SWN[["Swap Type","TradeId","Book_x","Valuation","Valuation Currency","Valuation Date","PresentValue","SwaptionVega"]]


# In[76]:

#rename columns
Final_SWN=Final_SWN.rename(index=str, columns={"Book_x":"Book","Valuation":"Oberon_Valuation","PresentValue":"Markit_Valuation"})


# ##### Oberon 40207 Cleanup

# In[77]:

# remove all rows where 2nd column is NaN of Oberon report
Oberon40207_df1=Oberon40207.dropna(subset=["Unnamed: 1"])
Oberon40207_df1 = Oberon40207_df1.reset_index(drop=True) # reset index


# In[78]:

# remove all unneded columns
Oberon40207_df2 = Oberon40207_df1.filter(["Unnamed: 1","Unnamed: 2","Unnamed: 15","Unnamed: 16"], axis=1)


# In[79]:

# pd.set_option('display.max_rows', 500) change max rows displayed


# In[80]:

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



# In[81]:

# remove rows where Unnamed 1 is Payment Date
Oberon40207_df4 = Oberon40207_df3[Oberon40207_df3['Unnamed: 1'] != 'Payment Date :']
Oberon40207_df4 = Oberon40207_df4.reset_index(drop=True) # reset index


# In[82]:

# make the first row the header
Oberon40207_df4.columns = Oberon40207_df4.iloc[0] #give header the first row names
Oberon40207_df4=Oberon40207_df4.drop([0]) # drop the frist row
Oberon40207_df4=Oberon40207_df4.reset_index(drop=True) # resetting index


# ##### Discount Factors for payments

# In[83]:

# remove all columns from dfs dataframes after the second
DFS_USDOISNY1=DFS_USDOISNY[DFS_USDOISNY.columns[0:2]] 
DFS_GBPSONIA1=DFS_GBPSONIA[DFS_GBPSONIA.columns[0:2]] 
DFS_EUREONIA1=DFS_EUREONIA[DFS_EUREONIA.columns[0:2]] 


# In[84]:

# renaming the dfs dataframe`s columns
DFS_USDOISNY1.columns = ['Date', 'DFS']
DFS_GBPSONIA1.columns = ['Date', 'DFS']
DFS_EUREONIA1.columns = ['Date', 'DFS']


# In[85]:

# add the first row as today s date and dfs = 1 because USD and EUR start from tomorrow
DFS_USDOISNY1.loc[-1] = [DFS_USDOISNY1.iloc[0,0]-timedelta(days=1) ,float(1)]  # adding a row with the correct data
DFS_USDOISNY1 = DFS_USDOISNY1.reset_index(drop=True) # reset index
DFS_EUREONIA1.loc[-1] = [DFS_EUREONIA1.iloc[0,0]-timedelta(days=1) ,float(1)]  
DFS_EUREONIA1 = DFS_EUREONIA1.reset_index(drop=True) 


# In[86]:

Oberon40207_df4['C/Pty Trade ID']=pd.to_datetime(Oberon40207_df4['C/Pty Trade ID'])


# In[87]:

# change column 1 timestamp format in the Oberon40207_df5.
Oberon40207_df4['C/Pty Trade ID'] = Oberon40207_df4['C/Pty Trade ID'].dt.strftime('%Y-%m-%d')


# In[88]:

# create DFS column in Oberon40207_df4
Oberon40207_df5=Oberon40207_df4
Oberon40207_df5['DFS']="NaN" # create column


# In[89]:

# based on the currency and date put the appropiate discount factor next to ticket 
# DFS_GBPSONIA DFS_EUREONIA DFS_USDOISNY
for index, row in Oberon40207_df5.iterrows():
    if Oberon40207_df5.iloc[index,3]=='USD':
        Oberon40207_df5.iloc[index,4]= DFS_USDOISNY1.iloc[DFS_USDOISNY1[DFS_USDOISNY1['Date']==Oberon40207_df5.iloc[index,1]].index.item() ,1] # the code in the row index retrieves the index of DFS where the date corresponds to the date of the trade in the Oberon40207 dataframe    
    elif Oberon40207_df5.iloc[index,3]=='GBP':
        Oberon40207_df5.iloc[index,4]= DFS_GBPSONIA1.iloc[DFS_GBPSONIA1[DFS_GBPSONIA1['Date']==Oberon40207_df5.iloc[index,1]].index.item(),1]
    elif Oberon40207_df5.iloc[index,3]=='EUR':
        Oberon40207_df5.iloc[index,4]= DFS_EUREONIA1.iloc[DFS_EUREONIA1[DFS_EUREONIA1['Date']==Oberon40207_df5.iloc[index,1]].index.item() ,1] 
        


# In[90]:

# remove rows of Oberon40207_df5 where DFS is NaN (that means it is a weird currency and it is not priced in Oberon)
Oberon40207_df5 = Oberon40207_df5[Oberon40207_df5.DFS != "NaN"]
Oberon40207_df5 = Oberon40207_df5.reset_index(drop=True) # reset index


# In[91]:

# create discounted amount column
Oberon40207_df5['Discounted_Amount']="NaN" # create column


# In[92]:

# Fill in Discounted Amount column
Oberon40207_df5['Discounted_Amount'] = Oberon40207_df5['Amount'] * Oberon40207_df5['DFS']


# ### Add back the payment in the VLN and SWN

# In[93]:

Oberon40207_df_SWN=Oberon40207_df5.copy() # create a copy of the dataframe to use for Swaptions 
Oberon40207_df6=Oberon40207_df5.copy()  # create a copy of the dataframe to use for Swaps 


# In[94]:

# remove rows(trades) in Oberon40207_df6 that do not appear in Final_df # empty dataframe means no payment for swaps
Oberon40207_df6 = Oberon40207_df6[Oberon40207_df6['Ticket'].isin(Final_df["TradeId"])]
Oberon40207_df6 = Oberon40207_df6.reset_index(drop=True) # reset index


# In[95]:

# remove rows(trades) in Oberon40207_df5 that do not appear in Final_df # empty dataframe means no payment for swaptions
Oberon40207_df_SWN = Oberon40207_df_SWN[Oberon40207_df_SWN['Ticket'].isin(Final_SWN["TradeId"])]
Oberon40207_df_SWN = Oberon40207_df_SWN.reset_index(drop=True) # reset index


# In[96]:

# Fix the OberonValuation in Final_df by subtracting or adding the Discounted_Amount
Final_df1=Final_df
for index, row in Oberon40207_df6.iterrows():
    if Oberon40207_df6.iloc[index,5]>0:# if the Amount is positive then subtract the abs of Amount from the valuation in the larger dataset
        Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3]=(Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3])-abs(Oberon40207_df6.iloc[index,5]) 
    elif Oberon40207_df6.iloc[index,5]<0:# if the Amount is negative then add the abs of Amount to the valuation in the larger dataset
        Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3]=(Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3])+abs(Oberon40207_df6.iloc[index,5]) 


# In[97]:

# Fix the OberonValuation in Final_SWN by subtracting or adding the Discounted_Amount
for index, row in Oberon40207_df_SWN.iterrows():
    if Oberon40207_df_SWN.iloc[index,5]>0:# if the Amount is positive then subtract the abs of Amount from the valuation in the larger dataset
        Final_SWN.iloc[ Final_SWN[Final_SWN['TradeId']==Oberon40207_df_SWN.iloc[index,0]].index.item(),3]=(Final_SWN.iloc[ Final_SWN[Final_SWN['TradeId']==Oberon40207_df_SWN.iloc[index,0]].index.item(),3])-abs(Oberon40207_df_SWN.iloc[index,5]) 
    elif Oberon40207_df_SWN.iloc[index,5]<0:# if the Amount is negative then add the abs of Amount to the valuation in the larger dataset
        Final_SWN.iloc[ Final_SWN[Final_SWN['TradeId']==Oberon40207_df_SWN.iloc[index,0]].index.item(),3]=(Final_SWN.iloc[ Final_SWN[Final_SWN['TradeId']==Oberon40207_df_SWN.iloc[index,0]].index.item(),3])+abs(Oberon40207_df_SWN.iloc[index,5]) 


# In[98]:

# search for single trades in Final_df
# is_in_Final_df =  Final_df['TradeId']=="9D34LG7" # boolean list
# Final_df[is_in_Final_df] # filter with the boolean list


# ### Convert Oberon Valuations to GBP (Swaps and Swaptions)

# In[99]:

Final_SWN["Valuation Currency"].unique()


# In[100]:

Final_df1["Valuation Currency"].unique()


# In[101]:

LE04_words=LE04_txt1.split() # split the string file into a list of words


# In[102]:

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


# In[103]:

# create dataframe with currency name and value
Currency_df=pd.DataFrame(Currency, columns=['Currency'])
Currency_df[1]=Currency_Value
Currency_df.columns=["Currency","Exchange_Rate"]


# In[104]:

# create Exchange_Rate column in dataframes
Final_df1['Exchange_Rate']="NaN" # create column
Final_SWN['Exchange_Rate']="NaN" # create column


# In[105]:

# based on the currency put the appropiate exchange rate in the rows for Final_df1
for index, row in Final_df1.iterrows():
    if Final_df1.iloc[index,4]=='USD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="US DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        Final_df1.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif Final_df1.iloc[index,4]=='EUR':
        indextochange_list=list(np.where(Currency_df["Currency"]=="EURO")[0])
        indextochange_int=indextochange_list[0]
        Final_df1.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif Final_df1.iloc[index,4]=='GBP':
        Final_df1.iloc[index,9]= 1
    elif Final_df1.iloc[index,4]=='AUD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="AUSTRALIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        Final_df1.iloc[index,9]= Currency_df.iloc[indextochange_int,1]
    elif Final_df1.iloc[index,4]=='CAD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="CANADIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        Final_df1.iloc[index,9]= Currency_df.iloc[indextochange_int,1]


# In[106]:

# based on the currency put the appropiate exchange rate in the rows for Final_SWN (need to convert index 1 to int
# because the above loop changes it to string)
for index1, row in Final_SWN.iterrows():
    if Final_SWN.iloc[int(index1),4]=='USD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="US DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        Final_SWN.iloc[int(index1),8]= Currency_df.iloc[indextochange_int,1]
    elif Final_SWN.iloc[int(index1),4]=='EUR':
        indextochange_list=list(np.where(Currency_df["Currency"]=="EURO")[0])
        indextochange_int=indextochange_list[0]
        Final_SWN.iloc[int(index1),8]= Currency_df.iloc[indextochange_int,1]
    elif Final_SWN.iloc[int(index1),4]=='GBP':
        Final_SWN.iloc[int(index1),8]= 1
    elif Final_SWN.iloc[int(index1),4]=='AUD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="AUSTRALIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        Final_SWN.iloc[int(index1),8]= Currency_df.iloc[indextochange_int,1]
    elif Final_SWN.iloc[int(index1),4]=='CAD':
        indextochange_list=list(np.where(Currency_df["Currency"]=="CANADIAN DOLLAR")[0])
        indextochange_int=indextochange_list[0]
        Final_SWN.iloc[int(index1),8]= Currency_df.iloc[indextochange_int,1]



# In[107]:

# change Exchange rate columns to float and the valuation columns (swaps and swaptions)
Final_df1["Exchange_Rate"]=Final_df1["Exchange_Rate"].astype(float)
Final_SWN["Exchange_Rate"]=Final_SWN["Exchange_Rate"].astype(float)
Final_df1["OberonValuation"]=Final_df1["OberonValuation"].astype(float)
Final_SWN["Oberon_Valuation"]=Final_SWN["Oberon_Valuation"].astype(float)


# In[108]:

# divide valuation for the exchange rate
Final_df1["Oberon Valuation"]=Final_df1["OberonValuation"]/Final_df1["Exchange_Rate"]
Final_SWN["Oberon Valuation"]=Final_SWN["Oberon_Valuation"]/Final_SWN["Exchange_Rate"]


# In[109]:

Final_df1.head()


# In[110]:

Final_SWN.head()


# In[111]:

Final_df1=Final_df1.drop(["Valuation Currency","Exchange_Rate"],axis=1)
Final_SWN=Final_SWN.drop(["Valuation Currency","Exchange_Rate"],axis=1)


# ##### Create Tolerance Breaks Exceptions

# In[112]:

# Add 6 columns: Markit_Oberon_Diff , Abs_Tolerance,PV01_Tolerance,PV01_Exceptions,%Notional, Exceptions
# Markit_Oberon_Diff
Final_df1['Markit_Oberon_Diff'] = abs(abs(Final_df1['MarkitValuation']) - abs(Final_df1['OberonValuation']) )
Final_SWN['Markit_Oberon_Diff'] = abs(abs(Final_SWN['Markit_Valuation']) - abs(Final_SWN['Oberon_Valuation']) )


# In[113]:

# Create column with absolute tolerance exceptions
Final_df1['Abs_Tolerance']="NaN" # create column
Final_SWN['Abs_Tolerance']="NaN" # create column


# In[114]:

# fill in Abs Tolerance swaps
for index, row in Final_df1.iterrows():
    if Final_df1.iloc[index, 9]<1500000:
        Final_df1.iloc[index, 10]=0
    elif Final_df1.iloc[index, 9]>=1500000 and Final_df1.iloc[index, 9]<3000000:
        Final_df1.iloc[index, 10]=1
    elif Final_df1.iloc[index, 9]>=3000000:
        Final_df1.iloc[index, 10]=2
    


# In[115]:

# fill in Abs Tolerance swaptions (needs to int the index because the loop above changes the data type of index)
for index, row in Final_SWN.iterrows():
    if Final_SWN.iloc[int(index), 8]<1500000:
        Final_SWN.iloc[int(index), 9]=0
    elif Final_SWN.iloc[int(index), 8]>=1500000 and Final_SWN.iloc[int(index), 8]<3000000:
        Final_SWN.iloc[int(index), 9]=1
    elif Final_SWN.iloc[int(index), 8]>=3000000:
        Final_SWN.iloc[int(index), 9]=2


# In[116]:

# create PV01 Tolerance column
Final_df1['PV01_Tolerance']="NaN" # create column
Final_SWN['Vega_Tolerance']="NaN" # create column


# In[117]:

# fill in Pv01 Tolerance
Final_df1['PV01_Tolerance'] = Final_df1['Markit_Oberon_Diff'] / abs(Final_df1["NetPV01"]) 
Final_SWN['Vega_Tolerance'] = Final_SWN['Markit_Oberon_Diff'] / abs(Final_SWN["SwaptionVega"]) 


# In[118]:

# create PV01 and Vega Tolerance exceptions column
Final_df1['PV01_Tolerance_exceptions']="NaN" # create column
Final_SWN['Vega_Tolerance_exceptions']="NaN" # create column


# In[119]:

# fill in PV01 Tolerance exceptions
for index, row in Final_df1.iterrows():
    if Final_df1.iloc[index, 11]>5:
        Final_df1.iloc[index, 12]=1
    else:
        Final_df1.iloc[index, 12]=0


# In[120]:

# fill in Vega Tolerance exceptions
for index, row in Final_SWN.iterrows():
    if Final_SWN.iloc[int(index), 10]>5:
        Final_SWN.iloc[int(index), 11]=1
    else:
        Final_SWN.iloc[int(index), 11]=0


# In[121]:

# Create exceptions column
Final_df1['Exceptions']="NaN" # create column
Final_SWN['Exceptions']="NaN" # create column


# In[122]:

# fill in Exceptions swaps

for index, row in Final_df1.iterrows():
    if int(Final_df1.iloc[int(index), 10])>=2 and int(Final_df1.iloc[int(index), 12])>0:
        Final_df1.iloc[int(index), 13]="CHECK"
    else:
        Final_df1.iloc[int(index), 13]="OK"


# In[123]:

# fill in Exceptions swaptions

for index, row in Final_SWN.iterrows():
    if int(Final_SWN.iloc[int(index), 9])>=2 and int(Final_SWN.iloc[int(index), 11])>0:
        Final_SWN.iloc[int(index), 12]="CHECK"
    else:
        Final_SWN.iloc[int(index), 12]="OK"


# In[124]:

# create %Notional column
Final_df1['%Notional']="NaN" # create column


# In[125]:

# remove trades where the principal is zero, it means they re dead
Final_df1= Final_df1[Final_df1["Receive Current Principal"] != 0]


# In[126]:

Final_df1['%Notional'] = Final_df1['Markit_Oberon_Diff'] / Final_df1["Receive Current Principal"] #fill in %Notional


# In[127]:

Final_df1.head()


# In[128]:

Final_SWN.head()


# In[129]:

# rename columns to make currency clear
Final_df1= Final_df1.rename(index=str, columns={"MarkitValuation":"MarkitValuation(GBP)"})
Final_df1= Final_df1.rename(index=str, columns={"OberonValuation":"OberonValuation(GBP)"})
Final_SWN= Final_SWN.rename(index=str, columns={"Markit_Valuation":"MarkitValuation(GBP)"})
Final_SWN= Final_SWN.rename(index=str, columns={"Oberon_Valuation":"OberonValuation(GBP)"})


# In[130]:

Final_df1.Exceptions.value_counts() # Frequency table of Exceptions


# In[131]:

Final_SWN.Exceptions.value_counts() # Frequency table of Exceptions


# ##### Export the Output

# In[132]:

file_name_Swaps="/Breaks Oberon Swaps "+lastBusDay+".csv"
file_name_Swaptions="/Breaks Oberon Swaps "+lastBusDay+".csv"


# In[133]:

path_Output="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs"
path_Output_Archive="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Archive"


# In[134]:

# write to csv Swaps
Final_df1.to_csv(path_Output+file_name_Swaps,header=True,index=False)# write once in the general folder for messing about
Final_df1.to_csv(path_Output_Archive+file_name_Swaps,header=True,index=False)# write second time in the Archive


# In[135]:

# write to csv Swaptions
Final_SWN.to_csv(path_Output+file_name_Swaptions,header=True,index=False)# write once in the general folder for messing about
Final_SWN.to_csv(path_Output_Archive+file_name_Swaptions,header=True,index=False)# write second time in the Archive

