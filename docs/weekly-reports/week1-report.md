# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Weekly Progress Report (Week 1)

**Intern:** Mohammed Ateeq Ur Rahman  
**Program:** Infosys Virtual Internship  
**Project:** SafetyEye – AI Powered Workplace Occupancy & Safety Monitor  
**Framework:** YOLOv8 (Ultralytics)  
**Hardware Used:** NVIDIA GTX 1650 Ti GPU (4GB)  
**Software:** Python, PyTorch, Ultralytics YOLOv8, OpenCV, VS Code  


# Week 1 – Environment Setup and Dataset Exploration

## Objective

The objective of Week 1 was to set up the development environment, understand the dataset structure, and perform initial dataset verification to ensure that the training process could run smoothly.


## Environment Setup

The following tools and libraries were installed and configured:

- Python  
- Virtual Environment (`venv`)  
- PyTorch  
- Ultralytics YOLOv8  
- OpenCV  
- NumPy  
- Matplotlib  
- VS Code  

A **virtual environment** was created to maintain project dependencies separately.

## GitHub Repository Setup

The project repository was cloned from GitHub. A new branch was created to maintain personal development work without modifying the main branch.

### Repository Structure
dataset/
images/
labels/
scripts/
docs/
notebooks/

This structure helps maintain *clean organization and easier collaboration*.


## Dataset Exploration

The dataset used for the project is the *Construction Site Safety Dataset* obtained from *Roboflow*.

### Dataset Details

- *Total images:* 2801  
- *Annotation format:* YOLOv8  
- *Classes:* 10  

### Classes in the Dataset

- Person  
- Helmet  
- Safety Vest  
- Head  
- Machinery  
- Safety Cone  
- Gloves  
- Boots  
- Face Mask  
- Tools  

## Dataset Verification

Custom scripts were created to verify the dataset quality.

The script checked for:

- Missing label files  
- Empty label files  
- Incorrect label formats  

### Results of Dataset Verification

| Split      | Images | Labels | Missing Labels | Empty Labels |
| Train      | 1960   | 1960   | 0              | 15           |
| Validation | 560    | 560    | 0              | 7            |
| Test       | 281    | 281    | 0              | 2            |

The dataset was successfully verified and is *ready for training*.

## Image Visualization

*OpenCV* was used to display sample images from the dataset to ensure that:

- Images were readable  
- Labels corresponded correctly with objects  

This step ensured that *bounding boxes were properly aligned with the annotated objects*.


# Conclusion

During Week 1, the development environment was successfully set up and the project repository was cloned and organized into a structured format.

The *Construction Site Safety dataset* was explored and verified using scripts to ensure correct annotations and dataset quality. Dataset images were visualized using OpenCV to confirm that bounding boxes were correctly aligned with objects.

By the end of the week, the *dataset and environment were fully prepared for model training*.

# Key Points / Results

- Total dataset images: *2801*
- Total classes identified: *10*
- Dataset verified for missing and incorrect labels
- Development environment successfully configured