# FRC Strategic Dashboard - Complete System

## 🏆 Project Overview

This is a comprehensive FRC (FIRST Robotics Competition) Strategic Dashboard application that provides real-time match analysis, predictive analytics, and strategic insights for competitive robotics teams. The system integrates data processing, machine learning models, and a Flutter-based mobile interface.

## 🎯 Key Features

- **Real-time Data Processing**: Efficient parsing and storage of FRC match data
- **Predictive Analytics**: Machine learning models for match outcome prediction
- **Performance Metrics**: EPA, OPR, and cOPR calculations with historical tracking
- **ONNX Inference Pipeline**: Cross-platform model deployment for mobile devices
- **30-Second Hotspot Sync**: Rapid data synchronization for competition environments
- **Comprehensive Visualization**: Flutter-based dashboard with strategic insights

## 📁 Project Structure

```
FRC-Strategic-Dashboard/
├── data/
│   ├── raw/                  # Original CSV datasets
│   ├── processed/            # Processed and cleaned data
│   ├── models/               # Trained ML models and metadata
│   └── onnx/                 # ONNX format models for deployment
│
├── docs/                    # Documentation and specifications
│   ├── 01_system_architecture.md
│   ├── 02_data_importer_spec.md
│   ├── 03_delta_updater_spec.md
│   ├── 04_ml_inference_pipeline.md
│   ├── 05_monte_carlo_predictor.md
│   ├── csv_file_catalog.md
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── ONNX_INFERENCE_PIPELINE_README.md
│   ├── ONNX_PIPELINE_SUMMARY.md
│   └── SYSTEM_SUMMARY.md
│
├── notebooks/               # Jupyter notebooks for analysis
│   ├── data_loader.ipynb
│   ├── year_match_EPA_loader.ipynb
│   ├── year_match_OPR_loader.ipynb
│   ├── year_match_winner_nn.ipynb
│   └── match_loader.ipynb
│
├── src/
│   ├── data_processing/     # Data loading and preprocessing
│   │   ├── build_year_match_EPA_loader.py
│   │   ├── build_year_match_OPR_loader.py
│   │   └── build_year_match_winner_nn.py
│   │
│   ├── ml_models/           # Machine learning components
│   │   ├── onnx_inference_pipeline.py
│   │   ├── input_packaging_utils.py
│   │   ├── runtime_normalization.py
│   │   └── ensemble_blending.py
│   │
│   └── utils/               # Utility scripts
│       ├── delta_updater_agent.py
│       ├── demo_onnx_pipeline.py
│       └── test_*.py scripts
│
├── tests/                   # Test suite
│   ├── test_delta_updater.py
│   ├── test_onnx_pipeline.py
│   └── test_updated_system.py
│
├── flutter_app/             # Flutter mobile application
│   ├── lib/                 # Flutter source code
│   ├── pubspec.yaml         # Flutter dependencies
│   └── README.md            # Flutter app documentation
│
├── frc_app/                 # Alternative FRC application
│   └── lib/                 # FRC app source code
│
├── .gitignore              # Git ignore patterns
├── LICENSE                  # Project license
└── README.md                # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Flutter SDK (for mobile app)
- Required Python packages (see below)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/frc-strategic-dashboard.git
cd frc-strategic-dashboard

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install pandas numpy scikit-learn torch onnx onnxruntime

# For Flutter app (optional)
cd flutter_app
flutter pub get
```

## 🔧 System Components

### 1. Data Processing Pipeline

The data processing pipeline handles:

- **Raw Data Import**: CSV files from FRC API and Statbotics
- **Feature Engineering**: EPA, OPR, cOPR calculations
- **Data Cleaning**: Handling missing values and inconsistencies
- **Dataset Generation**: Creating training and prediction datasets

**Key Files:**
- `src/data_processing/build_year_match_EPA_loader.py`
- `src/data_processing/build_year_match_OPR_loader.py`
- `src/data_processing/build_year_match_winner_nn.py`

### 2. Machine Learning Models

The system includes multiple predictive models:

- **Neural Network**: PyTorch-based DNN with 293 features
- **Random Forest**: Scikit-learn ensemble classifier
- **ONNX Models**: Cross-platform deployment format

**Model Architecture:**
```
Input: 293 features (145 red alliance + 145 blue alliance + 3 context)
├── Linear(293 → 128) + ReLU + Dropout(0.25)
├── Linear(128 → 64) + ReLU + Dropout(0.15)
└── Linear(64 → 1) → Sigmoid → Probability
```

**Key Files:**
- `src/ml_models/onnx_inference_pipeline.py`
- `src/ml_models/input_packaging_utils.py`
- `src/ml_models/runtime_normalization.py`
- `src/ml_models/ensemble_blending.py`

### 3. ONNX Inference Pipeline

The ONNX pipeline provides:

- **Cross-platform compatibility**: Works on mobile, web, and desktop
- **Memory efficiency**: Models loaded once and cached
- **Runtime normalization**: Consistent feature scaling
- **Ensemble blending**: Combines DNN and Random Forest predictions

**Performance:**
- Model size: ~8.6 KB
- Inference time: <1ms per prediction
- Memory footprint: ~24 KB total

### 4. Flutter Mobile Application

The Flutter app provides:

- **Real-time match analysis**: Live predictions during competitions
- **Team performance tracking**: Historical EPA/OPR trends
- **Strategic insights**: Probability-based recommendations
- **Offline capabilities**: Data caching for competition environments

**Key Features:**
- 30-second hotspot sync for rapid data updates
- Interactive visualizations
- Team comparison tools
- Match outcome predictions

## 📊 Data Files

### Raw Data
- `data/raw/frc_matches_2026.csv` - Main match dataset
- `data/raw/frc_matches_2026_opr.csv` - OPR calculations
- `data/raw/statbotics_team_year_2026.csv` - Team statistics

### Processed Data
- `data/processed/match_winner_dataset_2026_before.csv` - Pre-match features
- `data/processed/match_winner_dataset_2026_after.csv` - Post-match features
- `data/processed/match_winner_dataset_2026.csv` - Combined dataset

### Models
- `data/models/match_winner_nn_2026.pt` - Neural network model
- `data/models/match_winner_ensemble_2026.pt` - Ensemble model
- `data/onnx/match_winner_dnn_2026.onnx` - ONNX deployment model

## 🔬 Usage Examples

### Data Processing

```bash
# Process EPA data
python src/data_processing/build_year_match_EPA_loader.py

# Process OPR data  
python src/data_processing/build_year_match_OPR_loader.py

# Train match winner prediction model
python src/data_processing/build_year_match_winner_nn.py
```

### ONNX Inference

```python
from src.ml_models.onnx_inference_pipeline import ONNXInferencePipeline

# Initialize pipeline
pipeline = ONNXInferencePipeline(
    onnx_model_path='data/onnx/match_winner_dnn_2026.onnx',
    feature_mean=feature_mean,  # Load from normalization_params.json
    feature_std=feature_std      # Load from normalization_params.json
)

# Make prediction
result = pipeline.predict_from_components(
    red_mean_features=[45.0]*72,   # Red alliance mean features
    red_std_features=[1.0]*73,    # Red alliance std features
    blue_mean_features=[44.0]*72, # Blue alliance mean features
    blue_std_features=[1.1]*73,   # Blue alliance std features
    is_qm=True                   # Qualification match flag
)

print(f"Red Win Probability: {result['ensemble_prob']:.2%}")
print(f"Blue Win Probability: {result['blue_win_prob']:.2%}")
```

### Running Tests

```bash
# Test ONNX pipeline
python tests/test_onnx_pipeline.py

# Test delta updater
python tests/test_delta_updater.py

# Test complete system
python tests/test_updated_system.py
```

## 📈 Performance Metrics

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

## 📱 Flutter App Features

### Main Screens

- **Home Screen**: Overview of current event and predictions
- **Team Analysis**: Detailed team performance metrics
- **Match Predictor**: Real-time win probability calculator
- **Settings**: Configuration and data sync options

### Key Components

- **Hotspot Sync Service**: 30-second data synchronization
- **Database Service**: SQLite storage with efficient queries
- **ML Integration**: ONNX model inference on-device
- **Theme System**: Light/dark mode support

## 🔧 Development Workflow

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

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **System Architecture**: `docs/01_system_architecture.md`
- **Data Importer Spec**: `docs/02_data_importer_spec.md`
- **Delta Updater**: `docs/03delta_updater_spec.md`
- **ML Pipeline**: `docs/04_ml_inference_pipeline.md`
- **Monte Carlo Predictor**: `docs/05_monte_carlo_predictor.md`
- **Implementation Summary**: `docs/IMPLEMENTATION_COMPLETE.md`

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Write tests for new functionality
5. Submit a pull request

### Code Style

- Python: PEP 8 style guide
- Flutter: Effective Dart guidelines
- Documentation: Clear, comprehensive comments

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

- **Real-time API Integration**: Direct FRC API connectivity
- **Advanced Visualizations**: Interactive charts and graphs
- **Team Scouting Integration**: Combine with scouting data
- **Monte Carlo Simulation**: Probabilistic outcome modeling
- **Cloud Sync**: Cross-device data synchronization
- **Offline Mode**: Enhanced caching capabilities
- **Performance Optimization**: Further reduce inference time
- **Model Explainability**: Feature importance visualization

## 📞 Support

For issues, questions, or suggestions:

- Open a GitHub issue
- Check the documentation
- Review existing discussions

## 🏁 Quick Start

```bash
# Clone and set up
git clone https://github.com/your-repo/frc-strategic-dashboard.git
cd frc-strategic-dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Process data and train models
python src/data_processing/build_year_match_EPA_loader.py
python src/data_processing/build_year_match_winner_nn.py

# Run tests
python tests/test_onnx_pipeline.py

# Launch Flutter app (in separate terminal)
cd flutter_app
flutter run
```

## 🎓 Learning Resources

- [FRC Official Documentation](https://docs.firstinspires.org/)
- [Statbotics API Documentation](https://api.statbotics.io/)
- [ONNX Runtime Documentation](https://onnxruntime.ai/)
- [Flutter Documentation](https://flutter.dev/docs)

---

**Project Status**: Active Development
**Last Updated**: 2026-06-17
**Maintainer**: Aarush P
**License**: MIT
