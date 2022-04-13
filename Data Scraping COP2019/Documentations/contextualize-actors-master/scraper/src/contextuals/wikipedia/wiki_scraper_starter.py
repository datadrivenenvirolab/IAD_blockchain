import pandas as pd
import wikipedia


input_data_path = r"C:\Users\wangx\Downloads\RTZ_tobescrapedupdated.csv"
output_data_path = r"C:\Users\wangx\Downloads\RTZ_wiki_scraped.csv"

input_data = pd.read_csv(input_data_path, encoding= 'unicode_escape')

result_list = []
i = 0
for row in input_data.iterrows():
    try:
        wiki_result = wikipedia.get_data(row[1]['name'], row[1]['iso'], row[1]['entity_type'], EN=True)
        # print(1)

    except Exception as e:
        wiki_result = {}
        print(e, "error at get lat long for ", row[1]['name'], row[1]['iso'])
    i +=1
    if i%20 ==0:
        print("finished {} rows".format(i))

    result_list.append(wiki_result)
wiki_result_df = pd.DataFrame(result_list)

# Merge into one df
merged_df = input_data.merge(wiki_result_df,left_index = True, right_index = True)
merged_df.to_csv(output_data_path)
print("Finding missing lat long from wiki finished")


