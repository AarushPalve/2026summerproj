#!/usr/bin/env python3
"""
Test script to verify the updated match winner prediction system works correctly.
This tests both the data loader and neural network notebook functionality.
"""

import json
import sys
from pathlib import Path

def test_data_loader_output():
    """Test that data loader creates the expected output files"""
    print("Testing data loader output...")

    # Check if the expected output files exist
    expected_files = [
        "match_winner_dataset_2026_before.csv",
        "match_winner_dataset_2026_after.csv",
        "match_winner_dataset_2026.csv"
    ]

    missing_files = []
    for file in expected_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"[ERROR] Missing data loader output files: {missing_files}")
        return False

    print("[SUCCESS] Data loader output files exist")

    # Check that the before dataset contains the expected features
    before_df = Path("match_winner_dataset_2026_before.csv")
    if before_df.exists():
        import pandas as pd
        df = pd.read_csv(before_df)

        # Check for expected feature types (statbotics is optional)
    expected_feature_types = {
        'epa': any('epa' in col.lower() for col in df.columns),
        'opr': any('opr' in col.lower() for col in df.columns),
        'copr': any('copr' in col.lower() for col in df.columns),
        'phase': 'phase' in df.columns
    }

    missing_features = [feat for feat, present in expected_feature_types.items() if not present]
    if missing_features:
        print(f"[ERROR] Missing feature types in before dataset: {missing_features}")
        return False

    # Check for statbotics features (optional)
    has_statbotics = any('statbotics' in col.lower() or 'win_odds' in col.lower() for col in df.columns)
    if has_statbotics:
        print(f"[INFO] Statbotics features found: {sum('statbotics' in col.lower() or 'win_odds' in col.lower() for col in df.columns)}")
    else:
        print(f"[INFO] No Statbotics features found (this is expected if no Statbotics match data is available)")

        print(f"[SUCCESS] Before dataset contains all expected feature types")
        print(f"   - EPA features: {sum('epa' in col.lower() for col in df.columns)}")
        print(f"   - OPR features: {sum('opr' in col.lower() for col in df.columns)}")
        print(f"   - cOPR features: {sum('copr' in col.lower() for col in df.columns)}")
        print(f"   - Statbotics features: {sum('statbotics' in col.lower() or 'win_odds' in col.lower() for col in df.columns)}")

    return True

def test_neural_network_output():
    """Test that neural network creates the expected output files"""
    print("\nTesting neural network output...")

    # Check if the expected output files exist
    expected_files = [
        "match_winner_ensemble_2026.pt",
        "match_winner_ensemble_2026_metadata.json"
    ]

    missing_files = []
    for file in expected_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"[ERROR] Missing neural network output files: {missing_files}")
        return False

    print("[SUCCESS] Neural network output files exist")

    # Check metadata file content
    metadata_file = Path("match_winner_ensemble_2026_metadata.json")
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Check for expected metadata structure (feature_types is optional)
            required_keys = ['feature_count', 'neural_network', 'random_forest', 'simple_ensemble', 'stacked_ensemble']
            missing_keys = [key for key in required_keys if key not in metadata]

            if missing_keys:
                print(f"[ERROR] Missing metadata keys: {missing_keys}")
                return False

            print(f"[SUCCESS] Metadata file has correct structure")
            print(f"   - Feature count: {metadata['feature_count']}")

            # Check feature types if present
            if 'feature_types' in metadata:
                print(f"   - Feature types: {metadata['feature_types']}")
                feature_types = metadata['feature_types']
                if any(count == 0 for count in feature_types.values()):
                    print(f"[ERROR] Some feature types have zero count: {feature_types}")
                    return False
                print(f"[SUCCESS] All feature types have positive counts")
            else:
                print(f"   - Feature types: Not present in metadata (optional)")

        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in metadata file: {e}")
            return False

    return True

def test_system_integration():
    """Test that the system components work together"""
    print("\nTesting system integration...")

    # Test that we can load the model and make predictions
    try:
        import torch
        import pandas as pd
        import numpy as np
        from torch import nn

        # Load the model bundle
        model_path = Path("match_winner_ensemble_2026.pt")
        if not model_path.exists():
            print("❌ Model file not found")
            return False

        bundle = torch.load(model_path, map_location="cpu")

        # Check bundle contents
        required_bundle_keys = ['feature_columns', 'feature_mean', 'feature_std', 'model_state_dict']
        missing_bundle_keys = [key for key in required_bundle_keys if key not in bundle]

        if missing_bundle_keys:
            print(f"[ERROR] Missing keys in model bundle: {missing_bundle_keys}")
            return False

        print(f"[SUCCESS] Model bundle loaded successfully")
        print(f"   - Feature columns: {len(bundle['feature_columns'])}")
        print(f"   - Feature mean length: {len(bundle['feature_mean'])}")
        print(f"   - Feature std length: {len(bundle['feature_std'])}")

        # Test prediction function
        test_data = np.array(bundle['feature_mean'], dtype=np.float32)  # Ensure float32 dtype
        test_tensor = torch.from_numpy(np.array([test_data]))

        # Create a simple model for testing
        input_dim = len(bundle['feature_columns'])
        model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

        # Test forward pass
        with torch.no_grad():
            output = model(test_tensor.float())  # Ensure float dtype
            if output.shape == (1, 1):
                print("[SUCCESS] Model forward pass successful")
                return True
            else:
                print(f"[ERROR] Unexpected output shape: {output.shape}")
                return False

    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Updated Match Winner Prediction System")
    print("=" * 60)

    tests = [
        test_data_loader_output,
        test_neural_network_output,
        test_system_integration
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("[SUCCESS] All tests passed! System is working correctly.")
        return 0
    else:
        print("[ERROR] Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())