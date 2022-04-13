
# coding: utf-8

# In[11]:


import requests
import pandas as pd


# # Scrape Secondnature.org University Data
# #### Step 1: The table on http://reporting.secondnature.org/
# Secondnature maintains an API that returns a JSON version of the data table used below. 

# In[18]:


raw_data = requests.get('http://reporting.secondnature.org/api/v1/pubinst/?format=json')
data = raw_data.json()


# In[31]:


# delete and rename some soon-to-be columns. 
# get values stored in lists as well. 

for n,row in enumerate(data):
    del row['fte']
    del row['ipedsfte']
    del row['ghg_reports']
    
    try:
        row['net_emissions'] = row['net_emis'][0]
    except:
        row['net_emissions'] = None
    del row['net_emis']
    
    try:
        row['neutral_dates'] = row['neutral_dates_pub'][0]
    except:
        row['neutral_dates'] = None
    del row['neutral_dates_pub']
    
    try:
        row['sq_ft'] = row['sq_ft_pub'][0]
    except:
        row['sq_ft'] = None
    del row['sq_ft_pub']
    
    data[n] = row


# In[89]:


data = pd.DataFrame(data)
data.info()


# In[ ]:


# write interim file. 
data.to_csv('secondnature_universities.csv')


# In[88]:


from tqdm import tqdm
emission_stats = []
targets = []
percent_reductions = []

for uid in tqdm(list(data['id'])):
    university = requests.get('http://reporting.secondnature.org/api/v1/detail/{}'.format(uid)).json()
    
    university_emission_stats = university['stats']['statslist']
    for i in university_emission_stats:
        i['id'] = uid
    
    # add university id to targets dictionary so it can be matched
    university_targets = university['stats']['targetlist']
    for i in university_targets:
        i['id'] = uid
        del i['cap_id']
        del i['targetsource'] # a single number. Not sure what it means. 
        
    university_percent_reductions = university['stats']['percent_reductions']
    university_percent_reductions['id'] = uid
    
    emission_stats += university_emission_stats
    targets += university_targets
    percent_reductions.append(university_percent_reductions)


# In[106]:


# makes the column names more readable. 
def fix_column_names(x):
    x = x.replace('ge', 'total_emissions')
    x = x.replace('fte', 'per_student')
    x = x.replace('sq', 'per_1000_sq_ft')
    x = x.replace('ts12', 'total_scope_1_and_2')
    x = x.replace('ts1', 'total_scope_1')
    x = x.replace('ts2', 'total_scope_2')
    x = x.replace('ts3', 'total_scope_3')
    return x


# In[126]:


emission_stats_df = pd.DataFrame(emission_stats)
emission_stats_df.columns = map(fix_column_names, emission_stats_df.columns)
emission_stats_df.info()
emission_stats_df.to_csv('secondnature_emission_stats.csv', index=False)


# In[127]:


targets_df = pd.DataFrame(targets)
targets_df = targets_df.rename(columns={'reduction': 'percent_reduction', 'targetyear': 'target_year'})
targets_df.info()
targets_df.to_csv('secondnature_targets.csv', index=False)


# In[128]:


percent_reductions_df = pd.DataFrame(percent_reductions)
percent_reductions_df.columns = map(fix_column_names, percent_reductions_df.columns)
percent_reductions_df.columns = map(lambda x: x if x == 'id' else x + '_%_change', percent_reductions_df.columns)
percent_reductions_df.info()
percent_reductions_df.to_csv('secondnature_percent_reductions.csv', index=False)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




