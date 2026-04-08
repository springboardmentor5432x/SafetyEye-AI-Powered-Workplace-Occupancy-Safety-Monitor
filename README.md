# SafetyEye – AI Powered Workplace Safety Monitor

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/YOLOv8-Latest-brightgreen" alt="YOLOv8">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</div>

## 📋 Overview

SafetyEye is an AI-powered computer vision system designed to monitor workplace safety and compliance in real-time. Built on YOLOv8, it detects personal protective equipment (PPE) and identifies safety violations on construction sites and other hazardous environments.

### Key Features
- 🎯 **Real-time Detection**: Live video stream processing for instant safety alerts
- 🦺 **PPE Detection**: Identifies hard hats, masks, safety vests, and more
- ⚠️ **Safety Alerts**: Automated notification system for compliance violations
- 📊 **Occupancy Monitoring**: Track real-time occupancy levels
- 🎬 **Multiple Input Modes**: Webcam, video files, or image directories
- 📈 **Performance Metrics**: Detailed detection accuracy and performance analysis

## 🎓 Dataset Information

### Classes Detected (10)
- Hardhat ✓
- Mask ✓
- Safety Vest ✓
- NO-Hardhat ✗
- NO-Mask ✗
- NO-Safety Vest ✗
- Person
- Safety Cone
- Machinery
- Vehicle

### Dataset Source
This project uses the **Construction Site Safety** dataset sourced from Roboflow Universe.
- **License**: CC BY 4.0
- **Size**: 2605 training images, validation and test splits included

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- CUDA 11.8+ (for GPU support, optional but recommended)
- pip or conda

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/safetyeye_AI.git
cd safetyeye_AI
```

2. **Create a virtual environment**
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download model weights**
Download the pre-trained weights and place them in the project root:
```bash
# Download best.pt from your storage/cloud service
# Models available:
# - best.pt (standard model)
# - best_epoch100.pt (epoch 100)
# - best_img800.pt (800px input)
# - best_largemodel.pt (large model variant)
```

5. **Setup dataset** (optional for training)
```bash
# Download dataset from Roboflow and extract to:
mkdir -p dataset/
# Place images and labels in dataset/images/ and dataset/labels/
```

## 📖 Usage

### 1. Real-time Webcam Detection
```bash
python webcam_detect.py
```

### 2. Detect from Video File
```bash
python detect.py --source video.mp4 --model best.pt
```

### 3. Detect from Images Directory
```bash
python Realtime_pipeline.py
```

### 4. Train Custom Model
```bash
python train.py --epochs 100 --imgsz 800 --batch 16
```

### 5. Test on GPU
```bash
python gpu_test.py
```

### 6. Label Validation
```bash
python check_labels.py
python scan_labels.py
```

## 📁 Project Structure

```
safetyeye_AI/
├── best.pt                    # Pre-trained model weights
├── best_epoch100.pt          # Alternative model
├── best_img800.pt            # Alternative model
├── best_largemodel.pt        # Alternative model
├── detect.py                 # Main detection script
├── webcam_detect.py          # Real-time webcam detection
├── Realtime_pipeline.py      # Real-time pipeline
├── train.py                  # Training script
├── gpu_test.py               # GPU benchmark
├── test_images.py            # Image testing utility
├── check_labels.py           # Dataset label validation
├── scan_labels.py            # Scan and analyze labels
├── requirements.txt          # Python dependencies
├── dataset/                  # Local dataset folder
│   ├── data.yaml            # Dataset configuration
│   ├── images/              # Training/validation/test images
│   └── labels/              # YOLO format annotations
├── datasets/                # Alternative datasets location
├── models/                  # Additional model definitions
├── notebooks/               # Jupyter notebooks (analysis)
├── runs/                    # Training outputs & results
├── scripts/                 # Utility scripts
└── README.md               # This file
```

## 🛠️ Dependencies

Key dependencies include:
- **ultralytics>=8.4.14** - YOLOv8 framework
- **torch>=2.10.0** - Deep learning framework
- **opencv-python>=4.13.0** - Computer vision
- **pandas>=3.0.0** - Data manipulation
- **matplotlib>=3.10.0** - Visualization

See [requirements.txt](requirements.txt) for complete list.

## 📊 Model Performance

Models are evaluated on the test set:
- **Standard Model (best.pt)**: Balanced performance
- **Epoch 100 (best_epoch100.pt)**: Extended training
- **Large Image Size (best_img800.pt)**: 800px input resolution
- **Large Model (best_largemodel.pt)**: Larger architecture variant

Detailed metrics available in `runs/detect/` directory.

## 🔍 Key Scripts

### detect.py
Main detection script for images, videos, and streams.
```bash
python detect.py --source 0 --model best.pt --conf 0.5
```

### train.py
Train or fine-tune the model on custom dataset.
```bash
python train.py --data dataset/data.yaml --epochs 100 --imgsz 640
```

### webcam_detect.py
Live detection with real-time display and alerts.
```bash
python webcam_detect.py --model best.pt --conf 0.5
```

### Realtime_pipeline.py
Advanced real-time processing pipeline.

## ⚙️ Configuration

Edit `map.yaml` or pass arguments to scripts for configuration:
- `--conf`: Confidence threshold (0-1)
- `--iou`: IoU threshold for NMS (0-1)
- `--imgsz`: Input image size (default: 640)
- `--device`: GPU device ID or 'cpu'

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add your feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The dataset is licensed under **CC BY 4.0**.

## 📧 Contact & Support

For issues, questions, or suggestions, please open an [GitHub Issue](https://github.com/yourusername/safetyeye_AI/issues).

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/yolov8)
- [Roboflow](https://roboflow.com) - Dataset source
- Construction site safety community

## 📚 References

- [YOLOv8 Documentation](https://docs.ultralytics.com)
- [PyTorch Documentation](https://pytorch.org/docs)
- [OpenCV Documentation](https://docs.opencv.org)

---

⭐ **If this project helped you, please consider giving it a star!**
- YOLOv8 by Ultralytics
