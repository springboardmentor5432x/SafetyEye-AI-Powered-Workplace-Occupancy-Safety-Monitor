# Milestone 1 Report 


## Title

SafetyEye: Environment Setup, Dataset Exploration, and YOLOv8 Dataset Preparation


## 1. Objective

Milestone 1 focused on building a reliable starting point for the project. The work in this phase was about getting the environment ready, understanding the construction-safety dataset, and converting the data into a clean YOLOv8 training format that could support the later model and dashboard stages.

This milestone covered the Week 1 and Week 2 tasks:

- environment setup and tool installation
- dataset download and inspection
- train, validation, and test split preparation
- creation of the dataset configuration file
- a small training smoke test to verify the setup

## 2. Project Setup

The SafetyEye project was organized under the main project folder:

```text
SafetyEye/
├── dataset/
├── scripts/
├── models/
├── notebooks/
```

This structure made it easier to separate dataset files, code scripts, model assets, and experiment notes.

A Python virtual environment was created for package isolation, and the required libraries for computer vision and model training were installed. The main dependencies used in the project include:

- ultralytics
- torch
- opencv-python
- numpy
- pandas
- matplotlib
- scikit-learn

The YOLOv8 installation was verified through the Ultralytics package and by running a training smoke test with a YOLOv8 model.

## 3. Dataset Exploration

The project uses the Construction Site Safety Image Dataset. After downloading and extracting the dataset, the images and labels were placed inside the `dataset/` folder and inspected to confirm that the annotation files were present.

The dataset configuration file was created at:

- `dataset/data.yaml`

The dataset includes 10 classes:

1. Hardhat
2. Mask
3. NO-Hardhat
4. NO-Mask
5. NO-Safety Vest
6. Person
7. Safety Cone
8. Safety Vest
9. machinery
10. vehicle

This class list allowed the project to support both object detection and explicit safety violation detection.

## 4. Dataset Preparation for YOLOv8

The dataset was organized into the standard YOLOv8 directory structure:

```text
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
└── data.yaml
```

The dataset was split using the required proportions:

- 70% training
- 20% validation
- 10% testing

Final split counts in the current project are:

- Train: 1960 images and 1960 label files
- Validation: 560 images and 560 label files
- Test: 281 images and 281 label files

These matching counts confirm that each image has a corresponding annotation file.

## 5. Scripts Developed in This Milestone

To support environment and dataset verification, the following scripts were created:

### 5.1 `scripts/verify_data.py`

This script loads a random image and its corresponding YOLO label file, converts the normalized coordinates into pixel coordinates, and draws the bounding boxes using OpenCV. It was used to visually confirm that:

- images load correctly
- label files exist
- class IDs map to the expected class names
- the annotations are aligned correctly on the images

### 5.2 `scripts/split_data.py`

This script performs the dataset split by:

- reading images from the source dataset
- shuffling them
- dividing them into train, validation, and test groups
- copying both images and label files into the correct folders

### 5.3 `scripts/test_train.py`

This script runs a one-epoch YOLOv8 training job using `dataset/data.yaml` to verify that the dataset structure is valid and that the training pipeline can start without path or formatting errors.

## 6. Dataset Configuration

The `data.yaml` file defines:

- the dataset root path
- train, validation, and test image folders
- number of classes
- class names

This file is essential because YOLOv8 uses it to locate the dataset and map label IDs to class names during training and validation.

## 7. Key Outcomes of Milestone 1

By the end of this milestone, the following outcomes were achieved:

- the development environment was created successfully
- the SafetyEye project folder structure was organized
- the required libraries were installed
- the construction safety dataset was downloaded and placed in the project
- the dataset was converted into YOLOv8-compatible folder structure
- the image and label counts were verified for all splits
- sample annotated images were inspected through OpenCV
- a YOLO training smoke test was prepared to validate the dataset setup

## 8. Challenges Faced

Some practical challenges in this stage included:

- ensuring that every image had a corresponding `.txt` label file
- correctly formatting the dataset into YOLOv8 folder structure
- verifying that the class names and IDs matched the dataset annotations
- working with absolute paths in scripts during early setup

These issues were resolved through dataset inspection scripts and repeated folder verification.

## 9. Conclusion

Milestone 1 gave SafetyEye a workable foundation. By the end of this phase, the environment was ready, the dataset had been reorganized into YOLOv8 structure, and the supporting checks confirmed that training could begin on a clean data pipeline. That preparation made the next stage, model training and evaluation, much more straightforward.
