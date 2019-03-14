
# coding: utf-8

# # Tolerance Breaks Exceptions Oberon-Markit

# ## Inputs :
#   - VLN file (trades with Oberon valuations)
#   - Markit Lgim NY CTD Rates for Swaps ( Markit Val :Interest and Zero Coupons,InfSwaps,GBP Swaptions)
#   - POS file (for the reference rate to exclude OIS)
#   - Daily Discount Factors
#   - Oberon 40207 Premium and Cancellation report

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

pd.options.mode.chained_assignment = None # disabling chained assignment warnings


# In[3]:

# retrieve today`s date to output the files with the correct name
yesterday = dt.date.today() - timedelta(days=1)
# the variable yesterday needs to be manually created if yesterday was a holiday example: yesterday=datetime.date(2019, 4, 13)


# In[4]:

# exclude weekends (holidays will have to be manually accounted for)
if dt.date.weekday(yesterday) not in range (0,5):
    yesterday=dt.date.today() - timedelta(days=3)


# In[5]:

# store the date into a string
lastBusDay=yesterday.strftime("%d.%m.%Y")


# ##### Load input files

# In[6]:

# inputs path
path_inputs="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Input Oberon/"


# ##### Automatic RegEx Method

# In[7]:

os.listdir(path_inputs)


# In[8]:

pattern_Payments  = r"Book.*\.xls" # patterns for the Input Files


# In[9]:

pattern_POS  = r"\d*POS\.csv" 


# In[10]:

pattern_VLN  = r"COB\s\d{8}\.xls" 


# In[11]:

pattern_DFS  = r"DFS\s\d{8}\.xls" 


# In[12]:

pattern_CTD  = r"LGIM_NY_Rates_CTD.*\.xls" 


# In[13]:

#re.search(pattern_CTD,'LGIM_NY_Rates_CTD.07Feb19.xls')


# In[14]:

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
    elif re.search(pattern_CTD,i):
        Markit_Swap=pd.read_excel(path_inputs+i, sheetname="Swap")#Swap
        Markit_InfSwap=pd.read_excel(path_inputs+i, sheetname="InfSwap")#InfSwap
    else:    # Manual method
        VLN_filename=input("Please insert the VLN file name:")
        Markit_filename=input("Please insert the Markit file name :")
        POS_filename=input("Please insert the POS file name :")
        Oberon40207_filename=input("Please insert the Oberon40207 Report file name :")
        DFS_filename=input("Please insert the Daily DFS file name :")
        complete_path_VLN=path_inputs+VLN_filename+".xls"
        complete_path_Markit=path_inputs+Markit_filename+".xls"
        complete_path_POS=path_inputs+POS_filename+".csv"
        complete_path_Oberon40207=path_inputs+Oberon40207_filename+".xls"
        complete_path_DFS=path_inputs+DFS_filename+".xls"
        VLN_df=pd.read_excel(complete_path_VLN,sheetname="Sheet1")
        Markit_Swap=pd.read_excel(complete_path_Markit, sheetname="Swap")
        Markit_InfSwap=pd.read_excel(complete_path_Markit, sheetname="InfSwap")
        Markit_Swaptions=pd.read_excel(complete_path_Markit, sheetname="Swaption")
        POS_df=pd.read_csv(complete_path_POS,dtype=object)
        Oberon40207=pd.read_excel(complete_path_Oberon40207, sheetname="Sheet1")
        DFS_GBPSONIA=pd.read_excel(complete_path_DFS, sheetname="GBP SONIA",header=None)
        DFS_EUREONIA=pd.read_excel(complete_path_DFS, sheetname="EUR EONIA",header=None)
        DFS_USDOISNY=pd.read_excel(complete_path_DFS, sheetname="USD OIS NY",header=None)
        break
   
        


# ##### Manual Input Method

# In[15]:

# input file name for VLN file
#VLN_filename=input("Please insert the VLN file name:")


# In[16]:

# input file name for Markit
#Markit_filename=input("Please insert the Markit file name :")


# In[17]:

# input file name for POS ,sheetname="Sheet1"
#POS_filename=input("Please insert the POS file name :")


# In[18]:

# input file name for Oberon40207 Report ,sheetname="Sheet1"
#Oberon40207_filename=input("Please insert the Oberon40207 Report file name :")


# In[19]:

# input file name for Discount Factors
#DFS_filename=input("Please insert the Daily DFS file name :")


# In[20]:

# Complete paths of the input files
#complete_path_VLN=path_inputs+VLN_filename+".xls"
#complete_path_Markit=path_inputs+Markit_filename+".xls"
#complete_path_POS=path_inputs+POS_filename+".csv"
#complete_path_Oberon40207=path_inputs+Oberon40207_filename+".xls"
#complete_path_DFS=path_inputs+DFS_filename+".xls"


# In[21]:

# Load VLN
#VLN_df=pd.read_excel(complete_path_VLN,sheetname="Sheet1")


# In[22]:

# Load Markit
#Swap
#Markit_Swap=pd.read_excel(complete_path_Markit, sheetname="Swap")
#InfSwap
#Markit_InfSwap=pd.read_excel(complete_path_Markit, sheetname="InfSwap")
#Swaptions
#Markit_Swaptions=pd.read_excel(complete_path_Markit, sheetname="Swaption")


# In[23]:

# Load POS
#POS_df=pd.read_csv(complete_path_POS,dtype=object)


# In[24]:

# Load Oberon40207 Report
#Oberon40207=pd.read_excel(complete_path_Oberon40207, sheetname="Sheet1")


# In[25]:

# Load discount factors
#DFS_GBPSONIA=pd.read_excel(complete_path_DFS, sheetname="GBP SONIA",header=None)
#DFS_EUREONIA=pd.read_excel(complete_path_DFS, sheetname="EUR EONIA",header=None)
#DFS_USDOISNY=pd.read_excel(complete_path_DFS, sheetname="USD OIS NY",header=None)


# #### Data Cleanup

# ##### VLN POS Cleanup

# In[26]:

# VLN File remove non needed columns
VLN_df1=VLN_df.drop(["Oberon ID","Value 1bp(Inflation)","Value 1bp(Interest)","Exch.Principals","Receive Currency","Receive Discount Curve","Receive Estimation Curve","Receive Valuation","Receive Last Rollover Discount Factor","Receive PV of Current Principal","Receive Valuation inc Principal Exch","Receive Valuation inc Principal Exch in Val Ccy","Pay Currency","Pay Discount Curve","Pay Estimation Curve","Pay Valuation","Pay Current Principal","Pay Last Rollover Discount Factor","Pay PV of Current Principal","Pay Valuation inc Principal Exch","Pay Valuation inc Principal Exch in Val Ccy"],axis=1)


# In[27]:

# POS File remove non needed columns
POS_df1=POS_df.filter(['Ticket','Receive Reference Rate','Pay Reference Rate'], axis=1)


# In[28]:

#POS_df2.groupby('Pay Reference Rate').count()


# In[29]:

# Create a list of sedols where Receive Reference Rate or Pay Reference Rate are GBP SONIA OIS
POS_df2_R = POS_df1[POS_df1['Receive Reference Rate'] == 'GBP SONIA OIS']
POS_df2_P = POS_df1[POS_df1['Pay Reference Rate'] == 'GBP SONIA OIS']
POS_df2_R = POS_df2_R.reset_index(drop=True) # reset index
POS_df2_P = POS_df2_P.reset_index(drop=True) # reset index
POS_df2_P_R = POS_df2_P.append(POS_df2_R) # top merge the two dataframes


# In[30]:

# remove tickets in VLN that are contained in POS_df2_P_R
VLN_df2 = VLN_df1[~VLN_df1['Ticket'].isin(POS_df2_P_R["Ticket"])]
VLN_df2 = VLN_df2.reset_index(drop=True) # reset index


# In[31]:

# remove all rows with currencies that arent GBP EUR USD CAD and AUD (technically by selecting only the rows with those currencies in column Valuation Currency)
VLN_df2 = VLN_df2[VLN_df2['Valuation Currency'].isin(["GBP", "EUR","USD","CAD","AUD"])]


# In[32]:

VLN_df2["Valuation Currency"].unique()


# ##### Markit Cleanup

# In[33]:

#remove non needed columns Swaps (this is using the PVLocal, not the Present value, because Oberon trades are in local currency)
Markit_Swap_1=Markit_Swap.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 4', 'Unnamed: 6', 'Unnamed: 7',"Unnamed: 8","Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12","Unnamed: 13","Unnamed: 14","Unnamed: 15","Unnamed: 16","Unnamed: 17","Unnamed: 19"], axis=1)
#remove non needed columns InfSwaps(this is using the PVLocal, not the Present value, because Oberon trades are in local currency)
Markit_InfSwap_1=Markit_InfSwap.drop(['Unnamed: 1','Unnamed: 2','Unnamed: 4','Unnamed: 6', 'Unnamed: 7',"Unnamed: 8","Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12","Unnamed: 13","Unnamed: 14","Unnamed: 15","Unnamed: 16","Unnamed: 17","Unnamed: 18","Unnamed: 19","Unnamed: 21"], axis=1)


# In[34]:

#make the third row the header
Markit_InfSwap_1.columns = Markit_InfSwap_1.iloc[2] #give header the third row names
Markit_Swap_1.columns = Markit_Swap_1.iloc[2] #give header the third row names
Markit_InfSwap_1=Markit_InfSwap_1.reset_index(drop=True) # resetting index
Markit_Swap_1=Markit_Swap_1.reset_index(drop=True) #resetting index


# In[35]:

# remove the first three rows
Markit_Swap_1= Markit_Swap_1.drop([0,1,2])
Markit_InfSwap_1= Markit_InfSwap_1.drop([0,1,2])
Markit_InfSwap_1=Markit_InfSwap_1.reset_index(drop=True) # resetting index
Markit_Swap_1=Markit_Swap_1.reset_index(drop=True) #resetting index


# In[36]:

# top merge Swaps and InfSwaps in a single dataframe
Markit_df1=Markit_Swap_1.append(Markit_InfSwap_1)
#resetting row index
Markit_df1=Markit_df1.reset_index(drop=True)


# In[37]:

# changing PVLocal to Present Value because code was already written with that name
Markit_df1=Markit_df1.rename(index=str, columns={"PVLocal": "PresentValue"})


# In[38]:

# resetting column order
#columnsTitles = ['Trade Valuations','Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3','Unnamed: 4','Unnamed: 5','Unnamed: 6','Unnamed: 7','Unnamed: 8','Unnamed: 9','Unnamed: 10','Unnamed: 11','Unnamed: 12','Unnamed: 13','Unnamed: 14','Unnamed: 15','Unnamed: 16','Unnamed: 17','Unnamed: 18','Unnamed: 19','Unnamed: 20','Unnamed: 21']
#Markit_df2=Markit_df1.reindex(columns=columnsTitles)


# In[39]:

# remove all rows with LegId non-NaN
Markit_df2 = Markit_df1[pd.isnull(Markit_df1['LegId'])]
#resetting index
Markit_df2=Markit_df2.reset_index(drop=True)


# In[40]:

# delete rows from the Markit dataframe whose Id do not match any id in the VLN file
Markit_df3=Markit_df2[Markit_df2["TradeId"].isin(VLN_df2["Ticket"])]
Markit_df3=Markit_df3.reset_index(drop=True) # reset index


# In[41]:

# delete rows from the VLN file whose Id do not match any id in the Markit file
VLN_df2=VLN_df2[VLN_df2["Ticket"].isin(Markit_df3["TradeId"])]
VLN_df2=VLN_df2.reset_index(drop=True) # reset index


# In[42]:

VLN_df2["Valuation Currency"].unique()


# In[43]:

# remove legId column
Markit_df3=Markit_df3.drop(["LegId"],axis=1)


# In[44]:

#Check for duplicates in Markit file
duplicated_Markit_df3 = Markit_df3.duplicated(subset="TradeId", keep="first")
any(x == True for x in duplicated_Markit_df3) # check if there is a True in the list


# In[45]:

#Check for duplicates in VLN file
duplicated_VLN_df2=VLN_df2.duplicated(subset="Ticket", keep="first")
any(x == True for x in duplicated_VLN_df2) # check if there is a True in the list


# In[46]:

#get indices of duplicate id rows in the Markit File
#duplicated_Markit_df5_1 = Markit_df5.duplicated(subset="TradeId", keep=False)
#Markit5_duplicated_indeces= np.where(duplicated_Markit_df5_1 ==True)


# In[47]:

# convert the tuple of indeces to a list
#Markit5_duplicated_indeces_list=list(Markit5_duplicated_indeces)


# In[48]:

# Create list with the indeces of the duplicate ids rows
#Markit5_duplicated_indeces_list1=[]
#for n in Markit5_duplicated_indeces:
   # Markit5_duplicated_indeces_list1.extend(n)


# In[49]:

# retrieve the rows for the duplicated Ids at indeces 127:160, 417:428,433:435,869:902,1863:1874,1914:1916
#Markit_df5_duplicated_rows=Markit_df5[Markit_df5.index.isin(Markit5_duplicated_indeces_list1)]


# In[50]:

# sort this dataframe by trade id in order to check wether the rows are the same
#Markit_df5_duplicated_rows=Markit_df5_duplicated_rows.sort_values(by=['TradeId'])


# In[51]:

# remove duplicate rows in the Markit file by only leaving the first observation
#Markit_df6=Markit_df5
#for index, row in Markit_df5.iterrows():
    #if duplicated_Markit_df5[index]==True:
       # Markit_df6= Markit_df6.drop([index]) 


# In[52]:

# REMINDER :Active dataframes : VLN_df2,Markit_df3
#VLN_df2.head()
#Markit_df3.head()


# ##### Create VLN Markit merged dataframe

# In[53]:

VLN_Markit= VLN_df2.rename(index=str, columns={"Ticket":"TradeId"})#rename VLN Ticket to TradeId in order to use the merge function


# In[54]:

# Merge so that VLN dataframe has markits valuation
Final_df=pd.merge(VLN_Markit, Markit_df3, on="TradeId")


# In[55]:

# rename Markit and VLN valuation columns
Final_df= Final_df.rename(index=str, columns={"PresentValue":"MarkitValuation","Valuation":"OberonValuation"})


# In[56]:

# Remove trades where the valuation is NA in either Markit or VLN
#Final_df2=Final_df1.dropna(subset=["OberonValuation"])
#Final_df2=Final_df1.dropna(subset=["MarkitValuation"])
#Final_df1=Final_df.dropna() # drop the rows where at least one element is NA
#Final_df1=Final_df1.reset_index(drop=True) # reset index


# In[57]:

#Final_df7.Markit_Oberon_Diff.value_counts() # count unique values in column
Final_df.MarkitValuation.isnull().values.any() # check if any value in column is NaN


# In[58]:

Final_df.OberonValuation.isnull().values.any() # check if any value in column is NaN


# In[59]:

# remove rows where there is no oberon or markit val
Final_df=Final_df.dropna(subset=['OberonValuation',"MarkitValuation"])
Final_df = Final_df.reset_index(drop=True) # reset index


# ##### Oberon 40207 Cleanup

# In[60]:

# remove all rows where 2nd column is NaN of Oberon report
Oberon40207_df1=Oberon40207.dropna(subset=["Unnamed: 1"])
Oberon40207_df1 = Oberon40207_df1.reset_index(drop=True) # reset index


# In[61]:

# remove all unneded columns
Oberon40207_df2 = Oberon40207_df1.filter(["Unnamed: 1","Unnamed: 2","Unnamed: 15","Unnamed: 16"], axis=1)


# In[62]:

# pd.set_option('display.max_rows', 500) change max rows displayed


# In[63]:

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



# In[64]:

# remove rows where Unnamed 1 is Payment Date
Oberon40207_df4 = Oberon40207_df3[Oberon40207_df3['Unnamed: 1'] != 'Payment Date :']
Oberon40207_df4 = Oberon40207_df4.reset_index(drop=True) # reset index


# In[65]:

# make the first row the header
Oberon40207_df4.columns = Oberon40207_df4.iloc[0] #give header the first row names
Oberon40207_df4=Oberon40207_df4.drop([0]) # drop the frist row
Oberon40207_df4=Oberon40207_df4.reset_index(drop=True) # resetting index


# ##### Discount Factors for payments

# In[66]:

# remove all columns from dfs dataframes after the second
DFS_USDOISNY1=DFS_USDOISNY[DFS_USDOISNY.columns[0:2]] 
DFS_GBPSONIA1=DFS_GBPSONIA[DFS_GBPSONIA.columns[0:2]] 
DFS_EUREONIA1=DFS_EUREONIA[DFS_EUREONIA.columns[0:2]] 


# In[67]:

# renaming the dfs dataframe`s columns
DFS_USDOISNY1.columns = ['Date', 'DFS']
DFS_GBPSONIA1.columns = ['Date', 'DFS']
DFS_EUREONIA1.columns = ['Date', 'DFS']


# In[68]:

# add the first row as today s date and dfs = 1 because USD and EUR start from tomorrow
DFS_USDOISNY1.loc[-1] = [DFS_USDOISNY1.iloc[0,0]-timedelta(days=1) ,float(1)]  # adding a row with the correct data
DFS_USDOISNY1 = DFS_USDOISNY1.reset_index(drop=True) # reset index
DFS_EUREONIA1.loc[-1] = [DFS_EUREONIA1.iloc[0,0]-timedelta(days=1) ,float(1)]  
DFS_EUREONIA1 = DFS_EUREONIA1.reset_index(drop=True) 


# In[69]:

Oberon40207_df4['C/Pty Trade ID']=pd.to_datetime(Oberon40207_df4['C/Pty Trade ID'])


# In[70]:

# change column 1 timestamp format in the Oberon40207_df5.
Oberon40207_df4['C/Pty Trade ID'] = Oberon40207_df4['C/Pty Trade ID'].dt.strftime('%Y-%m-%d')


# In[71]:

# create DFS column in Oberon40207_df4
Oberon40207_df5=Oberon40207_df4
Oberon40207_df5['DFS']="NaN" # create column


# In[72]:

# based on the currency and date put the appropiate discount factor next to ticket 
# DFS_GBPSONIA DFS_EUREONIA DFS_USDOISNY
for index, row in Oberon40207_df5.iterrows():
    if Oberon40207_df5.iloc[index,3]=='USD':
        Oberon40207_df5.iloc[index,4]= DFS_USDOISNY1.iloc[DFS_USDOISNY1[DFS_USDOISNY1['Date']==Oberon40207_df5.iloc[index,1]].index.item() ,1] # the code in the row index retrieves the index of DFS where the date corresponds to the date of the trade in the Oberon40207 dataframe    
    elif Oberon40207_df5.iloc[index,3]=='GBP':
        Oberon40207_df5.iloc[index,4]= DFS_GBPSONIA1.iloc[DFS_GBPSONIA1[DFS_GBPSONIA1['Date']==Oberon40207_df5.iloc[index,1]].index.item(),1]
    elif Oberon40207_df5.iloc[index,3]=='EUR':
        Oberon40207_df5.iloc[index,4]= DFS_EUREONIA1.iloc[DFS_EUREONIA1[DFS_EUREONIA1['Date']==Oberon40207_df5.iloc[index,1]].index.item() ,1] 
        


# In[73]:

# remove rows of Oberon40207_df5 where DFS is NaN (that means it is a weird currency and it is not priced in Oberon)
Oberon40207_df5 = Oberon40207_df5[Oberon40207_df5.DFS != "NaN"]
Oberon40207_df5 = Oberon40207_df5.reset_index(drop=True) # reset index


# In[74]:

# create discounted amount column
Oberon40207_df5['Discounted_Amount']="NaN" # create column


# In[75]:

# Fill in Discounted Amount column
Oberon40207_df5['Discounted_Amount'] = Oberon40207_df5['Amount'] * Oberon40207_df5['DFS']


# In[76]:

# remove rows(trades) in Oberon40207_df5 that do not appear in Final_df
Oberon40207_df6 = Oberon40207_df5[Oberon40207_df5['Ticket'].isin(Final_df["TradeId"])]
Oberon40207_df6 = Oberon40207_df6.reset_index(drop=True) # reset index


# In[77]:

# Fix the OberonValuation in Final_df by subtracting or adding the Discounted_Amount
Final_df1=Final_df
for index, row in Oberon40207_df6.iterrows():
    if Oberon40207_df6.iloc[index,5]>0:# if the Amount is positive then subtract the abs of Amount from the valuation in the larger dataset
        Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3]=(Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3])-abs(Oberon40207_df6.iloc[index,5]) 
    elif Oberon40207_df6.iloc[index,5]<0:# if the Amount is negative then add the abs of Amount to the valuation in the larger dataset
        Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3]=(Final_df1.iloc[ Final_df1[Final_df1['TradeId']==Oberon40207_df6.iloc[index,0]].index.item(),3])+abs(Oberon40207_df6.iloc[index,5]) 


# In[78]:

# search for single trades in Final_df
# is_in_Final_df =  Final_df['TradeId']=="9D34LG7" # boolean list
# Final_df[is_in_Final_df] # filter with the boolean list


# ##### Create Tolerance Breaks Exceptions

# In[79]:

# Add 6 columns: Markit_Oberon_Diff , Abs_Tolerance,PV01_Tolerance,PV01_Exceptions,%Notional, Exceptions
#Markit_Oberon_Diff
Final_df2 = Final_df1
Final_df2['Markit_Oberon_Diff'] = abs(abs(Final_df1['MarkitValuation']) - abs(Final_df1['OberonValuation']) )


# In[80]:

# Create column with absolute tolerance exceptions
Final_df2['Abs_Tolerance']="NaN" # create column


# In[81]:

# fill in Abs Tolerance
Final_df3=Final_df2
for index, row in Final_df3.iterrows():
    if Final_df3.iloc[index, 9]<1500000:
        Final_df3.iloc[index, 10]=0
    elif Final_df3.iloc[index, 9]>=1500000 and Final_df3.iloc[index, 9]<3000000:
        Final_df3.iloc[index, 10]=1
    elif Final_df3.iloc[index, 9]>=3000000:
        Final_df3.iloc[index, 10]=2
    


# In[82]:

# create PV01 Tolerance column
Final_df3['PV01_Tolerance']="NaN" # create column


# In[83]:

# fill in Pv01 Tolerance
Final_df4=Final_df3
Final_df4['PV01_Tolerance'] = Final_df3['Markit_Oberon_Diff'] / abs(Final_df3["NetPV01"]) 


# In[84]:

# create PV01 Tolerance exceptions column
Final_df4['PV01_Tolerance_exceptions']="NaN" # create column


# In[85]:

# fill in PV01 Tolerance exceptions
Final_df5=Final_df4
for index, row in Final_df5.iterrows():
    if Final_df5.iloc[index, 11]>5:
        Final_df5.iloc[index, 12]=1
    else:
        Final_df5.iloc[index, 12]=0


# In[86]:

# Create exceptions column
Final_df5['Exceptions']="NaN" # create column


# In[87]:

# fill in Exceptions
Final_df6=Final_df5
for index, row in Final_df6.iterrows():
    if int(Final_df6.iloc[index, 10])>=2 and int(Final_df6.iloc[index, 12])>0:
        Final_df6.iloc[index, 13]=1
    else:
        Final_df6.iloc[index, 13]=0


# In[88]:

# create %Notional column
Final_df6['%Notional']="NaN" # create column


# In[89]:

# remove trades where the principal is zero, it means they re dead
Final_df6= Final_df6[Final_df6["Receive Current Principal"] != 0]


# In[90]:

Final_df6['%Notional'] = Final_df6['Markit_Oberon_Diff'] / Final_df6["Receive Current Principal"]


# In[91]:

Final_df6.head()


# In[92]:

Final_df6.Exceptions.value_counts() # Frequency table of Exceptions


# ##### Export the Output

# In[93]:

file_name="/Breaks Oberon Swaps "+lastBusDay+".csv"


# In[94]:

path_Output="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs"
path_Output_Archive="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Tolerance Breaks Outputs/Archive"


# In[95]:

# write to csv
Final_df6.to_csv(path_Output+file_name,header=True,index=False)# write once in the general folder for messing about
Final_df6.to_csv(path_Output_Archive+file_name,header=True,index=False)# write second time in the Archive


# ##### Please note:
# 
#   
#   - Assumes they re all csa Clean (for the payment discounting)
#   - Does not value Swaptions
#   - Removes unshared trades between Markit and Oberon
#   - Removes the trades in Oberon that arent GBP,EUR,USD,CAD or AUD because the value in Oberon is wrong
#   - It uses PVLocal for Markit val and Oberon Valuation (which are both in the currency of the trade)
