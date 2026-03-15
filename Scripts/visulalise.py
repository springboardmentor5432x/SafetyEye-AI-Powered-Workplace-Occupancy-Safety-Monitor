import pandas as pd 
from collections import Counter
import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image
import  cv2




def yolo_boc(annot , h , w):
       sh = annot.shape
      
       if len(sh) ==1 :
            annot = annot.reshape(1 , -1)
       box_list = []

       for idx in range(len(annot)):
             x , y , be , bh  = annot[idx][1:]
             x1 = int((x - be/2)*w)
             y1 = int((y-bh/2)*h)
             x2 = int(( x+  be/2)*w)
             y2 = int((y + bh/2)*h)
             box_list.append([x1,y1,x2,y2])
       return box_list   

def draw_graph(df):
      
     counts = df['count'].apply(lambda x: np.fromstring(x.strip("[]"),sep=' ').astype(int) if isinstance(x,str)else x)


     count_freq = [dict(Counter(i)) for i in counts]


     df['count_freq'] = count_freq

     df = df.drop('count', axis =1)
     df['count_freq'] = df['count_freq'].apply(lambda d: {str(k): v for k, v in d.items()} if isinstance(d, dict) else d)

     df.to_parquet("../Output/intermediate_data/clean_annotated_1.parquet",index=False,engine="pyarrow" )

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
      
def visualize_samples(df,mode = 'train', n_samples = 12):
    """
    Plots 'n_samples' plots from train/valid/test split
    Input:
    mode: 'str' can take values from 'train'/'valid','test'
    n_samples: 'int'
    """
    # We will visualize only those files which have annotations 
    train_dic = dict(train = 0 , valid = 1 , test = 2)
    folders = ['images' , 'labels']

    data_path  = '../Datasets/css-data'
    class_names = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle']
    class_dict = dict(zip(range(len(class_names)),class_names))
    indices = df[df.train_id==1].sample(n_samples).index
    filenames = (data_path + '/' + df.train_id[indices].apply(lambda x: list(train_dic.keys())[x]) + '/' + folders[0] + '/' + df.filenames[indices]).tolist()
    annotations = (data_path + '/' + df.train_id[indices].apply(lambda x: list(train_dic.keys())[x]) + '/' + folders[1] + '/' + df.label_names[indices]).tolist()
    plt.figure(figsize = (21, 11))
    plt.title('{} Set Samples'.format(mode.upper()))
    for idx in range(len(filenames)):
        image = np.array(Image.open(filenames[idx]))
        height, width, _ = image.shape 
        annotation = np.loadtxt(annotations[idx])
        bbox_list = yolo_boc(annotation, height, width)
        if len(annotation.shape)==1:
            annotation = annotation.reshape(1, -1)
        labels = [class_dict[item] for item in annotation[:,0].astype(int)]
        plt.subplot(3, 4, idx + 1)
        for label, bbox in zip(labels, bbox_list):
            x1, y1, x2, y2 = bbox
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        plt.imshow(image)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
      

     df = pd.read_parquet("../Output/intermediate_data/annotated_1.parquet")
     draw_graph(df)
     visualize_samples(df,mode = 'train', n_samples = 12)

