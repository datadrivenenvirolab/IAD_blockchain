import pandas as pd
import os

"""
This is a ad hoc overview join script. 
After scraped the overview page. we will add two more columns based on 'baseline' and 'progress' page. 
"""

out_path = r"C:\Users\wangx\Documents\GitHub\Data-Driven\contextualize-actors\output\actors\EU Covenant"

ov_path = r"C:/Users/wangx/Documents/GitHub/Data-Driven/contextualize-actors/scraper/src/actors/eu_covenant\data/02.26.21overview.csv"
pg_path = os.path.join(out_path,"02.23.21progress.csv")
base_path = os.path.join(out_path,"02.19.21baseline.csv")


overview = pd.read_csv(ov_path)
progress = pd.read_csv(pg_path)
baseline = pd.read_csv(base_path)

overview.drop(columns = ['Unnamed: 0'], inplace = True)
print("shape before drop na: ",overview.shape)
overview.dropna(subset = ['name'],inplace=True)
print("shape after drop na: ",overview.shape)

new_merge = overview.merge(baseline,on=['name', 'country'], how='left')

new_merge['ACTION'] = new_merge['emissions_factor'].apply(lambda x: 0 if pd.isnull(x) else 1)

progress['MONITOR'] = 1
new_merge = new_merge.merge(progress, on=['name', 'country'], how='left')  # Not sure what this merge is for
#
new_merge['MONITOR'] = new_merge['MONITOR'].apply(lambda x: 0 if pd.isnull(x) else 1)

overview['ACTION'] = new_merge['ACTION']
overview['MONITOR'] = new_merge['MONITOR']
overview.to_csv(r'C:\Users\wangx\Documents\GitHub\Data-Driven\contextualize-actors\output\actors\EU Covenant\02.26.21overview.csv', encoding="utf-8")
print(1)