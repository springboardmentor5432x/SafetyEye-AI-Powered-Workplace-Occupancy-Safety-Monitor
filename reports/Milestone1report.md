# 🧾 Milestone 1 Report
## Project Title: Safety Eye Pro – AI-Based PPE Detection System

---

## 1. Introduction
Workplace safety is a critical concern in industries such as construction, manufacturing, and mining. Workers are required to wear Personal Protective Equipment (PPE) such as helmets, safety vests, and masks. However, manual monitoring is inefficient and prone to human error.

This project aims to automate PPE detection using Artificial Intelligence and Computer Vision techniques.

---

## 2. Problem Statement
Manual supervision of PPE compliance:
- Is time-consuming
- Not scalable
- Prone to negligence

There is a need for an automated system that can:
- Detect PPE usage in real-time
- Identify violations
- Improve workplace safety

---

## 3. Objectives
- Develop an AI-based PPE detection system
- Identify whether workers are wearing helmets, vests, and masks
- Detect violations (No Helmet, No Mask, etc.)
- Prepare dataset and environment for model training

---

## 4. Literature Overview
Existing systems:
- Use CCTV monitoring
- Require human supervision
- Lack real-time alerting

AI-based detection improves:
- Accuracy
- Automation
- Real-time decision-making

---

## 5. Tools & Technologies Selected
- Python → Core programming
- YOLOv8 → Object detection model
- OpenCV → Image processing
- Streamlit → UI framework

---

## 6. Dataset Collection
- PPE dataset collected from online sources
- Classes included:
  - Helmet
  - No Helmet
  - Vest
  - No Vest
  - Mask
  - No Mask
  - Person

---

## 7. Data Preprocessing
- Images resized
- Annotations verified
- Label format converted to YOLO format

---

## 8. Outcome
- Dataset prepared successfully
- Environment configured
- Ready for training phase

---

## 9. Challenges Faced
- Dataset imbalance
- Incorrect labeling

---

## 10. Conclusion
Milestone 1 successfully established the foundation for building the PPE detection system.