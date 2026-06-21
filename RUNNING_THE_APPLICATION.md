# FRC Strategic Dashboard - Complete Running Guide

This comprehensive guide provides step-by-step instructions for setting up and running the FRC Strategic Dashboard application, including both the data processing components and the Flutter mobile application.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Data Processing Pipeline](#data-processing-pipeline)
5. [Machine Learning Models](#machine-learning-models)
6. [ONNX Inference Pipeline](#onnx-inference-pipeline)
7. [Flutter Mobile Application](#flutter-mobile-application)
8. [Running Tests](#running-tests)
9. [Troubleshooting](#troubleshooting)
10. [Data File Reference](#data-file-reference)

## 🏆 System Overview

The FRC Strategic Dashboard is a comprehensive system for real-time match analysis and predictive analytics in FIRST Robotics Competition. The system consists of:

- **Data Processing Pipeline**: Handles CSV data import, feature engineering, and dataset generation
- **Machine Learning Models**: Neural network and ensemble models for match outcome prediction
- **ONNX Inference Pipeline**: Cross-platform model deployment for efficient predictions
- **Flutter Mobile App**: User interface for viewing predictions and team analytics

## ⚙️ Prerequisites

### Software Requirements

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version` or `python3 --version`

2. **Flutter SDK** (for mobile app)
   - Download: https://flutter.dev/docs/get-started/install
   - Verify: `flutter --version`
   - Required version: >=3.0.0

3. **Git**
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

4. **Required Python Packages**
   ```
   pandas
   numpy
   scikit-learn
   torch
   onnx
   onnxruntime
   ```

5. **Development Environment** (Recommended)
   - VS Code with Python and Flutter extensions
   - OR PyCharm for Python development
   - OR Android Studio for Flutter development

### Hardware Requirements

- **Minimum**: 4GB RAM, 2 CPU cores, 2GB free disk space
- **Recommended**: 8GB RAM, 4 CPU cores, 10GB free disk space
- **For Flutter Development**: Android/iOS device or emulator

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-repo/frc-strategic-dashboard.git
cd frc-strategic-dashboard
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:python -m venv venv

source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Install required packages
pip install pandas numpy scikit-learn torch onnx onnxruntime

# Optional: Install development dependencies
pip install jupyter notebook matplotlib seaborn
```

### 4. Set Up Flutter Environment (Optional)

```bash
# Navigate to flutter_app directory
cd flutter_app

# Get Flutter dependencies
flutter pub get

# Verify Flutter setup
flutter doctor
```

## 📊 Data Processing Pipeline

The data processing pipeline handles raw FRC data and prepares it for machine learning models.

### Data Directory Structure

```
data/
├── raw/                  # Original CSV datasets
├── processed/            # Processed and cleaned data
├── models/               # Trained ML models
└── onnx/                 # ONNX format models for deployment
```

### Processing Steps

#### 1. Process EPA Data

```bash
# Navigate to project root
cd /path/to/frc-strategic-dashboard

# Run EPA data processing
python src/data_processing/build_year_match_EPA_loader.py
```

**What it does:**
- Loads raw match data from CSV files
- Calculates Expected Points Added (EPA) for each team
- Uses exponential smoothing with learning rate α = 0.10
- Saves processed data to `data/processed/`

#### 2. Process OPR Data

```bash
# Run OPR data processing
python src/data_processing/build_year_match_OPR_loader.py
```

**What it does:**
- Calculates Offensive Power Rating (OPR) for teams
- Uses simplified delta update approach
- Generates historical performance tracking

#### 3. Train Match Winner Prediction Model

```bash
# Train the neural network model
python src/data_processing/build_year_match_winner_nn.py
```

**What it does:**
- Loads processed match data
- Creates 293-dimensional feature vectors
- Trains a 3-layer neural network (293 → 128 → 64 → 1)
- Saves trained model to `data/models/`
- Generates normalization parameters

## 🤖 Machine Learning Models

### Model Architecture

```
Input: 293 features (145 red alliance + 145 blue alliance + 3 context)
├── Linear(293 → 128) + ReLU + Dropout(0.25)
├── Linear(128 → 64) + ReLU + Dropout(0.15)
└── Linear(64 → 1) → Sigmoid → Probability
```

### Feature Vector Breakdown

- **Red Alliance**: 145 features (indices 0-144)
  - Mean features: 72 (indices 0-71)
  - Std features: 73 (indices 72-144)

- **Blue Alliance**: 145 features (indices 145-289)
  - Mean features: 72 (indices 145-216)
  - Std features: 73 (indices 217-289)

- **Context Features**: 3 features (indices 290-292)
  - Index 290: Qualification match flag
  - Index 291: Semifinal match flag
  - Index 292: Final match flag

### Model Files

- `data/models/match_winner_all_features_2026.pt` - Main PyTorch model
- `data/models/match_winner_ensemble_2026.pt` - Ensemble model
- `data/models/normalization_params.json` - Normalization parameters

## ⚡ ONNX Inference Pipeline

The ONNX pipeline enables cross-platform model deployment.

### Convert PyTorch Model to ONNX

```bash
# Navigate to src/ml_models directory
cd src/ml_models

# Run conversion script
python -c "
from onnx_inference_pipeline import convert_pytorch_to_onnx
import torch

# Load model
model_dict = torch.load('../../data/models/match_winner_all_features_2026.pt', map_location='cpu')

# Convert to ONNX
convert_pytorch_to_onnx(
    '../../data/models/match_winner_all_features_2026.pt',
    '../../data/onnx/match_winner_dnn_2026.onnx',
    model_dict['feature_mean'],
    model_dict['feature_std']
)
"
```

### Run ONNX Inference

```python
from src.ml_models.onnx_inference_pipeline import ONNXInferencePipeline
import json

# Load normalization parameters
with open('data/models/normalization_params.json', 'r') as f:
    norm_params = json.load(f)

# Initialize pipeline
pipeline = ONNXInferencePipeline(
    onnx_model_path='data/onnx/match_winner_dnn_2026.onnx',
    feature_mean=norm_params['feature_mean'],
    feature_std=norm_params['feature_std']
)

# Make prediction
result = pipeline.predict_from_components(
    red_mean_features=[45.0]*72,   # Red alliance mean features
    red_std_features=[1.0]*73,    # Red alliance std features
    blue_mean_features=[44.0]*72,  # Blue alliance mean features
    blue_std_features=[1.1]*73,   # Blue alliance std features
    is_qm=True                   # Qualification match flag
)

print(f"Red Win Probability: {result['ensemble_prob']:.2%}")
print(f"Blue Win Probability: {result['blue_win_prob']:.2%}")
```

### ONNX Pipeline Files

- `src/ml_models/onnx_inference_pipeline.py` - Main pipeline
- `src/ml_models/input_packaging_utils.py` - Input data handling
- `src/ml_models/runtime_normalization.py` - Feature normalization
- `src/ml_models/ensemble_blending.py` - Model ensemble

## 📱 Flutter Mobile Application

The Flutter app provides a user interface for viewing predictions and team analytics.

### Running the Flutter App

#### 1. Navigate to Flutter App Directory

```bash
cd flutter_app
```

#### 2. Get Dependencies

```bash
flutter pub get
```

#### 3. Run on Emulator or Device

```bash
# List available devices
flutter devices

# Run on connected device
flutter run

# Run on specific device
flutter run -d <device_id>

# Run on Android emulator
flutter emulators --launch <emulator_name>
flutter run

# Run on iOS simulator
flutter run -d iPhone
```

#### 4. Build APK (Android)

```bash
# Build debug APK
flutter build apk

# Build release APK
flutter build apk --release

# Find APK location
# build/app/outputs/flutter-apk/app-release.apk
```

#### 5. Build iOS App

```bash
# Build iOS app (requires macOS and Xcode)
flutter build ios

# Open in Xcode
open ios/Runner.xcworkspace
```

### Flutter App Structure

```
flutter_app/
├── lib/
│   ├── main.dart                  # Application entry point
│   ├── app.dart                    # Main app widget with providers
│   ├── theme/                     # Theme management
│   │   ├── color_themes.dart       # 5 dark theme definitions
│   │   ├── theme_manager.dart       # Theme switching logic
│   │   └── theme_data.dart          # Custom theme extensions
│   ├── screens/                   # App screens
│   │   ├── home_screen.dart        # Main screen with theme showcase
│   │   └── settings_screen.dart     # Theme selection screen
│   ├── widgets/                   # Reusable widgets
│   │   ├── themed_button.dart      # Custom button widgets
│   │   ├── themed_card.dart        # Custom card widgets
│   │   └── themed_text.dart        # Typography components
│   └── utils/                     # Utilities
│       └── constants.dart          # App constants
├── pubspec.yaml                  # Flutter dependencies
└── README.md                     # Flutter app documentation
```

### Flutter App Features

- **5 Dark Themes**: Midnight Ocean, Deep Forest, Royal Velvet, Mystic Purple, Carbon Fiber
- **Theme Switching**: Cycle through themes or select from settings
- **Theme Persistence**: Selected theme saved across app restarts
- **Custom Widgets**: Themed buttons, cards, and text components

## 🧪 Running Tests

### Python Tests

```bash
# Run ONNX pipeline tests
python tests/test_onnx_pipeline.py

# Run delta updater tests
python tests/test_delta_updater.py

# Run complete system tests
python tests/test_updated_system.py
```

### Flutter Tests

```bash
# Navigate to flutter_app directory
cd flutter_app

# Run Flutter tests
flutter test

# Run specific test file
flutter test test/theme_test.dart
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Python Environment Issues

**Issue**: `ModuleNotFoundError` for required packages

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install missing packages
pip install -r requirements.txt  # If file exists
# OR
pip install pandas numpy scikit-learn torch onnx onnxruntime
```

#### Flutter Setup Issues

**Issue**: `flutter doctor` shows missing dependencies

**Solution**: Follow Flutter's platform-specific setup guides:
- Android: Install Android Studio and set up SDK
- iOS: Install Xcode and set up command line tools
- Windows: Enable Hyper-V for emulator

#### ONNX Conversion Errors

**Issue**: Errors during PyTorch to ONNX conversion

**Solution**:
```bash
# Ensure you have the correct PyTorch version
pip install torch==2.0.1

# Verify model file exists
ls -la data/models/match_winner_all_features_2026.pt

# Check model structure
import torch
model = torch.load('data/models/match_winner_all_features_2026.pt', map_location='cpu')
print(model.keys())
```

#### Database Connection Issues

**Issue**: SQLite database connection failures

**Solution**:
```bash
# Ensure data directory exists and is writable
mkdir -p data
chmod 755 data

# Check database file permissions
chmod 644 data/*.db  # If database file exists
```

## 📂 Data File Reference

### Raw Data Files

- `data/raw/frc_matches_2026.csv` - Main match dataset
- `data/raw/frc_matches_2026_opr.csv` - OPR calculations
- `data/raw/statbotics_team_year_2026.csv` - Team statistics

### Processed Data Files

- `data/processed/match_winner_dataset_2026_before.csv` - Pre-match features
- `data/processed/match_winner_dataset_2026_after.csv` - Post-match features
- `data/processed/match_winner_dataset_2026.csv` - Combined dataset

### Model Files

- `data/models/match_winner_all_features_2026.pt` - Neural network model (PyTorch)
- `data/models/match_winner_ensemble_2026.pt` - Ensemble model (PyTorch)
- `data/models/normalization_params.json` - Normalization parameters (JSON)
- `data/onnx/match_winner_dnn_2026.onnx` - ONNX deployment model

### Metadata Files

- `data/models/*.metadata.json` - Model training metadata
- `docs/*.md` - Comprehensive documentation

## 📊 Performance Metrics

### Model Performance

| Model Type         | Test Accuracy | Test AUC  | Test Log Loss |
|--------------------|---------------|-----------|---------------|
| Neural Network     | 0.7655        | 0.8492    | 0.5103        |
| Random Forest      | 0.7572        | 0.8372    | 0.4986        |
| Simple Ensemble    | 0.7671        | 0.8489    | 0.4818        |
| Stacked Ensemble   | 0.7674        | 0.8479    | 0.4974        |

### System Performance

- **Data Processing**: ~10,000 matches/second
- **Model Training**: ~5 minutes for full dataset
- **Inference Speed**: <1ms per prediction
- **Memory Usage**: ~50MB total footprint
- **ONNX Model Size**: 8.6 KB
- **Total Deployment Footprint**: ~24 KB

## 🎓 Key Algorithms

### 1. EPA (Expected Points Added) Calculation

```
Δ_Alliance = Score_Actual - Σ EPA_i,before
EPA_i,after = EPA_i,before + α * (Δ_Alliance / N_teams)
```

Where:
- α = 0.10 (learning rate)
- N_teams = 3 (standard FRC alliance size)

### 2. OPR (Offensive Power Rating) Calculation

Simplified delta update approach with exponential smoothing for real-time performance.

### 3. Ensemble Blending

```
P(Red_Win) = (σ(Logit_DNN) + P_RF(Red_Win)) / 2
```

Combines neural network and random forest probabilities for improved accuracy.

## 🔄 Development Workflow

### Data Update Process

1. **Fetch New Data**: Download latest match results from FRC API
2. **Process Data**: Run data processing scripts
3. **Update Models**: Retrain models with new data (optional)
4. **Export ONNX**: Convert updated models to ONNX format
5. **Update App**: Deploy new models to Flutter app

### Adding New Features

1. **Feature Engineering**: Add to data processing scripts
2. **Model Training**: Update notebooks with new features
3. **ONNX Conversion**: Export updated model format
4. **App Integration**: Update Flutter UI and services

## 📚 Additional Resources

- **FRC Official Documentation**: https://docs.firstinspires.org/
- **Statbotics API Documentation**: https://api.statbotics.io/
- **ONNX Runtime Documentation**: https://onnxruntime.ai/
- **Flutter Documentation**: https://flutter.dev/docs
- **PyTorch Documentation**: https://pytorch.org/docs/stable/

## 🎯 Quick Start Checklist

- [ ] Clone repository
- [ ] Set up Python virtual environment
- [ ] Install Python dependencies
- [ ] Set up Flutter environment (if using mobile app)
- [ ] Process EPA data
- [ ] Process OPR data
- [ ] Train match winner model
- [ ] Convert model to ONNX format
- [ ] Run tests to verify setup
- [ ] Launch Flutter app (optional)

## 📞 Support

For issues, questions, or suggestions:

1. Check the documentation in the `docs/` directory
2. Review existing GitHub issues
3. Open a new GitHub issue with detailed information

## 🏁 Conclusion

This guide provides comprehensive instructions for setting up and running the FRC Strategic Dashboard application. The system integrates data processing, machine learning, and mobile application components to provide real-time match analysis and predictive analytics for FRC competitions.

**Last Updated**: 2026-06-17
**Maintainer**: Aarush P
**License**: MIT
