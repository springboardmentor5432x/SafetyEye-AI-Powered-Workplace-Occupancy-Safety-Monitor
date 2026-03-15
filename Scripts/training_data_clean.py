import pandas as pd 
import shutil 
import os 
from pathlib import Path


df = pd.read_parquet('../Output/intermediate_data/clean_annotated_1.parquet')

source_img = Path('../Datasets/css-data/cleaned_train/train/images')
source_label = Path('../Datasets/css-data/cleaned_train/train/labels')


keep_img = set(df['filenames'])
keep_label = set(df['label_names'])



def clean_folder (folder , allow):
    count = 0 

    for file in folder.glob('*'):
        if file.name not in allow:
            os.remove(file)
            count+=1

    return count


deleted_imgs = clean_folder(source_img, keep_img)
deleted_lbls = clean_folder(source_label, keep_label)


print(f"Cleanup complete!")
print(f"Removed {deleted_imgs} unannotated images.")
print(f"Removed {deleted_lbls} unannotated labels.")