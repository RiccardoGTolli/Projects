
# coding: utf-8

# # State Street
# 

# ## Inputs & Outputs
# 

# 
# ### Inputs:
# 
# •	
# 
# •	
# 
# •	
# 
# •	
# 
# •	NY_SameDay_Global email from around 22:00 yesterday for the Equity TRS
# 
# •	Markit Pricing email from a member of the Chicago team from yesterday
# 
# 
# 
# 
# ### Outputs:
# 
# •	“COB dd.mm.yyyy Sent” file (Swaps and Swaptions)OBERON RELIANT
# 
# •	“COB dd.mm.yyyy TRS” file (Equity TRSs) 
# 
# •	“DDMMYYY” file (CDS)
# 
# •   “COB dd.mm.yyyy Option” file (Equity Options)
# 
# •	The two emails to the relevant people
# 
# 

# ## Code

# In[1]:

#load libraries
import pandas as pd
from datetime import datetime, timedelta
import datetime
import os
import re


# #### Load inputs

# ##### Load SameDay Global with RegEx in path_inputs and load Markit Pricing from original folder

# In[2]:

# inputs path
path_inputs="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Riccardo Tolli/BAU Automation/State Street/Inputs/"


# In[3]:

os.listdir(path_inputs) # list files in the input folder


# In[4]:

pattern_MG  = r"LGIM_NY_SameDay_Global.*\.xls" # pattern for Markit SameDay Global


# In[5]:

# retrieve Markit Same day Global file from input folder using Regex names
for i in os.listdir(path_inputs): 
    if re.search(pattern_MG,i):
        EqOpt_df=pd.read_excel(path_inputs+i, sheetname="StructProd")
        EqTRS_df=pd.read_excel(path_inputs+i, sheetname="EqTRS")


# In[6]:

EqOpt_df


# In[7]:

# retrieve today`s date to get the correct MarkitPricing file
yesterday = datetime.date.today() - timedelta(days=1)
# the variable yesterday needs to be manually created if yesterday was a holiday example: yesterday=datetime.date(2019, 4, 13)


# In[8]:

# exclude weekends (holidays will have to be manually accounted for)
if datetime.date.weekday(yesterday) not in range (0,5):
    yesterday=datetime.date.today() - timedelta(days=3)


# In[9]:

# store the date into a string
lastBusDay=yesterday.strftime("%d%m%Y")


# In[10]:

#concatenate the two strings (path of MarkitPricing and correct name with date)
CDS_lastBusDay="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Markit/MarkitSent/"+"MarkitPricing"+lastBusDay+".xls"


# In[11]:

#CDS_lastBusDay


# In[12]:

#import CDS file
CDS_df=pd.read_excel(CDS_lastBusDay)


# ##### Load data by inputting name with files being in path_inputs

# In[13]:

# input file name for EqTRS & EqOpt
#Markit_EqTRS_EqOpt_filename=input("Please insert the Markit filename for EqOpt and EqTRS:")


# In[14]:

# input file name for CDS
#Markit_Pricing_filename=input("Please insert the Markit filename for CDS:")


# In[15]:

# Complete paths of the input files
#complete_path_EqTRS_EqOpt=path_inputs+Markit_EqTRS_EqOpt_filename+".xls"
#complete_path_CDS=path_inputs+Markit_Pricing_filename+".xls"


# In[16]:

#Equity TRS
#EqTRS_df=pd.read_excel(complete_path_EqTRS_EqOpt, sheetname="EqTRS")


# In[17]:

# Equity Options
#EqOpt_df=pd.read_excel(complete_path_EqTRS_EqOpt, sheetname="StructProd")


# In[18]:

#CDS
#CDS_df=pd.read_excel(complete_path_CDS)


# ##### Swaps and Swaptions

# ###### Equity TRS

# In[19]:

# visualize
#EqTRS_df


# In[20]:

# select all rows in fund 8454
EqTRS_df1=EqTRS_df.set_index('Unnamed: 1', append=True, drop=False).xs('8454', level=1)


# In[21]:

# visualize
#EqTRS_df1


# In[22]:

#resetting row index
EqTRS_df1=EqTRS_df1.reset_index(drop=True)
# remove the last three rows and reset the row index
EqTRS_df2= EqTRS_df1.drop([3,4,5])


# In[23]:

EqTRS_df1


# In[ ]:

# visualize
#EqTRS_df2


# In[ ]:

# Create a dataframe with the original header
Eq_TRS_Markit_Header=EqTRS_df[:3]


# In[ ]:

# Visualize
#Eq_TRS_Markit_Header


# In[ ]:

# add back the full Markit Header to df2
EqTRS_Final=Eq_TRS_Markit_Header.append(EqTRS_df2)# merge the two dataframes


# In[ ]:

# Visualize
#EqTRS_Final


# ##### Equity Options

# In[ ]:

#Visualize
#EqOpt_df


# In[ ]:

# select rows with sedols 595602 and 595603 
EqOpt_df1=EqOpt_df.loc[EqOpt_df["Trade Valuations"].isin(["595602","595603"])]


# In[ ]:

# visualize
#EqOpt_df1


# In[ ]:

#reset index
EqOpt_df1=EqOpt_df1.reset_index(drop=True)


# In[ ]:

# Create a dataframe with the original header
Eq_Opt_Markit_Header=EqOpt_df[:3]


# In[ ]:

#Visualize
#Eq_Opt_Markit_Header


# In[ ]:

# add back the full Markit Header to df2
EqOpt_Final=Eq_Opt_Markit_Header.append(EqOpt_df1)# merge the two dataframes


# In[ ]:

#visualize 
#EqOpt_Final


# ##### CDS

# In[ ]:

#visualize
#CDS_df


# In[ ]:

# select rows with funds 4722 and 4723
CDS_Final=CDS_df.loc[CDS_df["Fund held on"].isin(["4722","4723"])]


# In[ ]:

#visualize
CDS_Final.head()


# ### Naming the output files

# In[ ]:

# EqTRS file name
file_name_TRS="%s %s %s%s" %("COB",lastBusDay,"TRS",".csv")


# In[ ]:

# EqOpt file name
file_name_EqOpt="%s %s %s%s" %("COB",lastBusDay,"Option",".csv")


# In[ ]:

# Output path
path_Outputs="//Inv/lgim/FO Operations/Derivative Trade Support/Pricing/Riccardo Tolli/BAU Automation/State Street/Outputs/"


# In[ ]:

# CDS file name
lastBusDay1=yesterday.strftime("%d%m%Y") # no need for dots 
file_name_CDS="%s%s" %(lastBusDay1,".csv") # create string with the file name


# In[ ]:

path_Outputs+file_name_TRS


# ### Exporting the Outputs

# In[ ]:

# write to csv EqTRS
EqTRS_Final.to_csv(path_Outputs+file_name_TRS,header=False,index=False)


# In[ ]:

# write to csv EqOpt
EqOpt_Final.to_csv(path_Outputs+file_name_EqOpt,header=False,index=False)


# In[ ]:

# write to csv CDS
CDS_Final.to_csv(path_Outputs+file_name_CDS,header=True,index=False)

