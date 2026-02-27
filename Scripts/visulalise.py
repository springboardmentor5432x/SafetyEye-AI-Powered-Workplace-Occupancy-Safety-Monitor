import pandas as pd 
from collections import Counter
import numpy as np 
import matplotlib.pyplot as plt




df = pd.read_csv("../Output/intermediate_data/annotated.parquet")


counts = df['count'].apply(lambda x: np.fromstring(x.strip("[]"),sep=' ').astype(int) if isinstance(x,str)else x)


count_freq = [dict(Counter(i)) for i in counts]


df['count_freq'] = count_freq


df = df.drop('count', axis =1)

train_count = df[df.train_id==0].count_freq.apply(lambda x :Counter(x)).sum()
valid_count= df[df.train_id==1].count_freq.apply(lambda x :Counter(x)).sum()
test_count= df[df.train_id==2].count_freq.apply(lambda x :Counter(x)).sum()

train_total_time = sum(train_count.values())
valid_total_time = sum(valid_count.values())
test_total_time = sum(test_count.values())

train_count = {key:value/ train_total_time for key , value in train_count.items()}
valid_count = {key:value/valid_total_time for key,value in valid_count.items()}
test_count = {key:value/test_total_time  for key , value in test_count.items() }


print("Train Class Distribution Dict: {}\n\nValid Class Distribution Dict: {}\n\nTest Class Distribution Dict: {}"
     .format(train_count, valid_count, test_count))

df_count = pd.DataFrame({'train':train_count, 'valid': valid_count, 'test': test_count}).sort_index()


df_count.plot(y=['train', 'valid', 'test'], kind='bar', title='Train Valid Split Distribution')
plt.legend(['Train', 'Valid', 'Test'])

plt.show() 