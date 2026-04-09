# Milestone 2 Report 

## Title

SafetyEye: YOLOv8 Model Training and PPE Detection


## 1. Objective

Milestone 2 was the stage where the project moved from data preparation into actual model building. The aim was to train and compare YOLOv8 detection runs, measure how well the detector handled PPE-related classes, and choose the most dependable result to carry into the live monitoring stage.

This markdown report has been aligned with the original Milestone 2 submission and the matching training artifacts preserved in the repository. Later post-milestone experiments are documented separately in the final report so that the milestone record and the final-project record do not get mixed together.

## 2. Training Preparation

Before model training began, the dataset prepared in Milestone 1 was checked to confirm that it followed the expected YOLOv8 format:

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

The dataset verification confirmed:

- matching image and label files in all splits
- valid YOLO annotation structure
- correct dataset configuration file
- correct class name mapping inside `data.yaml`

Split counts in the current dataset were:

- Train: 1960 images
- Validation: 560 images
- Test: 281 images

## 3. Model Configuration

The strongest stable run completed during the Milestone 2 submission window is preserved under:

- `runs/detect/train4/`

This milestone run used:

- Model: `yolov8s.pt`
- Epochs: 25
- Batch size: 16
- Image size: 640
- Device: CPU
- Optimizer: auto
- Task: object detection

The milestone weights are available at:

- `runs/detect/train4/weights/best.pt`
- `runs/detect/train4/weights/last.pt`

The repository also contains later extended experiments under `runs/detect/train6/` and `runs/detect/train7/`, but those belong to the post-milestone improvement phase and are summarized in the final report rather than treated as the original Milestone 2 submission result.

## 4. Training Process

YOLOv8 was trained on the prepared safety dataset using pretrained weights. Using a pretrained model improved convergence speed and allowed the network to adapt quickly to the PPE detection task.

The model learned to detect the following classes:

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

The training process produced the standard YOLOv8 result files, including:

- `results.csv`
- `results.png`
- `confusion_matrix.png`
- `confusion_matrix_normalized.png`
- `BoxPR_curve.png`
- `BoxP_curve.png`
- `BoxR_curve.png`
- `BoxF1_curve.png`

These plots were used to evaluate how well the model was learning during training and how accurately it performed on validation data.

## 5. Performance Metrics

The final row in `runs/detect/train4/results.csv` shows the following validation-related performance values:

- Precision: 0.87522
- Recall: 0.72093
- mAP@0.5: 0.80358
- mAP@0.5:0.95: 0.54729

These values match the original milestone summary, which reported about 87.5% precision and 80.3% mAP@0.5 for the selected milestone model.

The best values achieved during this milestone run were:

- Best precision: 0.88495 at epoch 24
- Best recall: 0.72093 at epoch 25
- Best mAP@0.5: 0.80358 at epoch 25
- Best mAP@0.5:0.95: 0.54729 at epoch 25

Final loss values at epoch 25 were:

- Train box loss: 0.81396
- Train class loss: 0.5749
- Train DFL loss: 1.07403
- Validation box loss: 0.97958
- Validation class loss: 0.64276
- Validation DFL loss: 1.0734

These results show that the selected milestone model achieved strong precision and solid overall detection quality, making it suitable to carry forward into the real-time monitoring phase.

## 6. Files and Outputs Produced

The main milestone outputs are:

- `runs/detect/train4/weights/best.pt`
- `runs/detect/train4/weights/last.pt`
- validation prediction images
- confusion matrix plots
- precision-recall curves
- training statistics in CSV format

These outputs provide evidence that the model was trained successfully and evaluated using standard object detection metrics.

## 7. Supporting Code

The repository includes scripts that supported Milestone 2:

### 7.1 `scripts/test_train.py`

This script performs a one-epoch training run using YOLOv8 and was useful as a smoke test for:

- checking `data.yaml`
- validating dataset structure
- confirming that Ultralytics training starts correctly

### 7.2 Dataset Validation

The earlier dataset scripts from Milestone 1 were reused to make sure training data quality was acceptable before running longer training sessions.

## 8. Observations

The training process demonstrated that YOLOv8 can effectively learn PPE and safety-related classes from the construction dataset. Precision was high, which indicates that a large portion of predicted detections were correct. Recall was lower than precision, which suggests that while the model was accurate, some objects in the scene may still have been missed.

The `mAP@0.5` result above 0.80 indicates strong detection performance for the milestone scope. The lower `mAP@0.5:0.95` value is expected because it uses stricter overlap thresholds and is generally harder to optimize.

## 9. Challenges Faced

Key challenges in this milestone included:

- training a multi-class detector on a diverse construction-site dataset
- balancing accuracy and training time
- selecting appropriate image size and pretrained weights
- ensuring the validation metrics improved consistently

These challenges were addressed by using pretrained YOLOv8 weights, comparing multiple experiments, and selecting the most accurate stable configuration that could run reliably on the available hardware.

## 10. Conclusion

Milestone 2 produced the first dependable PPE detector for SafetyEye. The submission-era `train4` run offered a strong balance between accuracy and stability, which made it a sensible foundation for the next stage of live detection. Later experiments improved on those numbers, but this milestone established the core model that made the rest of the project possible.
