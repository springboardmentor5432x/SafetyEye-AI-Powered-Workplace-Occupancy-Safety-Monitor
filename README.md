# 🛡️ SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

SafetyEye is a cutting-edge, AI-driven workplace monitoring system designed to enhance safety compliance in construction sites and industrial environments. Utilizing **YOLOv8** and **OpenCV**, this real-time solution detects personnel and verifies the usage of Personal Protective Equipment (PPE) like hardhats, masks, and safety vests.

---

## 🌟 Key Features

### 🖥️ Interactive Dashboard
A premium, dark-themed **Streamlit** dashboard featuring a futuristic UI with neon-glow aesthetics. The dashboard provides a high-level overview of system status, active alerts, and real-time metrics.

### 🎥 Real-Time Monitoring
- **Webcam Integration**: Live feed processing for immediate safety verification.
- **Video Testing**: Support for pre-recorded video analysis to evaluate workplace behavior.
- **PPE Detection**: Specialized detection for Hardhats, Safety Vests, and Masks.

### 📊 Advanced Analytics
- **Violations Over Time**: Track safety trends using interactive line charts.
- **Violation Distribution**: Visualize the prevalence of different safety breaches via pie charts.
- **Compliance Tracking**: Monitor overall safety percentages with doughnut charts and AI-driven insights.

### 📋 Comprehensive Logging
- **Detailed History**: Every violation is logged with a timestamp, source, and confidence score.
- **Smart Filtering**: Filter logs by date, violation type, or system source.
- **Export Ready**: Download logs as **CSV** files for external reporting and audits.

---

## 🛠️ Technology Stack

- **Core Engine**: Python 3.x
- **Deep Learning**: YOLOv8 (Ultralytics)
- **Computer Vision**: OpenCV
- **Interface**: Streamlit
- **Data Visualization**: Plotly, Pandas
- **Machine Learning**: PyTorch

---

## 📂 Project Structure

```text
SafetyEye/
├── dataset/             # Images, labels, and test videos
├── docs/                # Milestone reports and documentation (PDFs)
├── models/              # Pre-trained YOLOv8 weights (.pt files)
├── notebooks/           # Experimental and training notebooks
├── scripts/
│   ├── app.py           # Main entry point (Streamlit Dashboard)
│   └── pages/           # Modular page logic
│       ├── analytics.py # Analytics visualizations
│       └── logs.py      # Incident logging system
└── requirements.txt     # Project dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.8+ installed. It is recommended to use a virtual environment.

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/springboardmentor5432x/SafetyEye-AI-Powered-Workplace-Occupancy-Safety-Monitor.git
cd SafetyEye-AI-Powered-Workplace-Occupancy-Safety-Monitor
pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit dashboard:
```bash
streamlit run scripts/app.py
```

---

## 📈 Milestone Progress

- **Milestone 1**: Data Preparation & Environment Setup.
- **Milestone 2**: Model Training & Initial Evaluation.
- **Milestone 3**: Core Logic Development & Alert System.
- **Milestone 4**: Dashboard UI, Analytics, and System Integration.

---

## 👤 Author
**Mohammed Ateeq Ur Rahman**  
*Intern, Infosys Virtual Internship*  

---

## 📜 License
This project is for educational purposes as part of the Infosys Virtual Internship program.