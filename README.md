# SafetyEye – AI-Powered Workplace Occupancy & Safety Monitor

## Week 1 – Data Preparation & Environment Setup

### Completed Tasks
- Created structured project folders
- Defined PPE violation rules
- Prepared YOLOv8 configuration template
- Set up development environment

---

## Folder Structure

src/
  ├── data_prep/
  ├── model/
  ├── detection/
  └── dashboard/

notebooks/
configs/
requirements.txt
---

## Safety Violation Rules

1. Person without helmet → Helmet Violation
2. Person without safety vest → Vest Violation
3. Person without helmet and vest → Critical Violation
4. All PPE present → Compliant

These rules will be implemented in the violation detection engine in Week 3.

