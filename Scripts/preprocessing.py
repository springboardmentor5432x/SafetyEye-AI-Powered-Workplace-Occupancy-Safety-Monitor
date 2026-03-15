import os , glob 
import tqdm 
import numpy as np 
import warnings
import pandas as pd
warnings.filterwarnings('ignore')

data_path  = '../Datasets/css-data'

train_path = os.path.join(data_path ,'train')
valid_path = os.path.join(data_path,'valid')
test_path = os.path.join(data_path,'test')


output_path = '../Output/working'

folder = ['images' , 'labels']

train_dic = dict(train = 0 , valid = 1 , test = 2)
path = [train_path, valid_path , test_path]
class_names = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle']
class_dict = dict(zip(range(len(class_names)),class_names))


train_filenames  = sorted(os.listdir(os.path.join(train_path , folder[0])))
valid_filenames  = sorted(os.listdir(os.path.join(valid_path , folder[0])))
test_filenames  = sorted(os.listdir(os.path.join(test_path , folder[0])))
train_label  = sorted(os.listdir(os.path.join(train_path , folder[1])))
valid_label  = sorted(os.listdir(os.path.join(valid_path , folder[1])))
test_label  = sorted(os.listdir(os.path.join(test_path , folder[1])))


df = pd.DataFrame()
df['filenames'] = train_filenames +valid_filenames+test_filenames
df['label_names'] = train_label+valid_label+test_label

df['train_id'] = [0]*len(train_filenames) + [1]*len(valid_filenames) +[2]*len(test_filenames)


train_keys = list(train_dic.keys())
annotation_files = (data_path + '/' + df.train_id.map(lambda x: train_keys[x]) + '/' + folder[1]
                    + '/' + df.label_names).tolist()

t_id = df.train_id.tolist()
counts = []
invalid_idx = []
is_annotated = []
for idx, annotation_file in tqdm.tqdm(enumerate(annotation_files)):
    annotation = np.loadtxt(annotation_file)
    if len(annotation)==0:
        invalid_idx.append(idx)
        is_annotated.append(-1)
        counts.append([])
        continue
    if len(annotation.shape)==1:
        annotation = annotation.reshape(1, -1)
    counts.append(annotation[:,0].astype(int))
    is_annotated.append(1)
df['is_annotated'] = is_annotated
df['count'] = counts
df_clean = df[df.is_annotated==1].copy() 




df_clean.to_parquet('../Output/intermediate_data/annotated_1.parquet',index=False,engine="pyarrow")
