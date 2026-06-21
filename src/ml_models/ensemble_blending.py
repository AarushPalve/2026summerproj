#!/usr/bin/env python3
"""
Ensemble Probability Blending

Implementation of the ensemble blending layer that combines DNN and Random Forest
predictions according to the specification.

Blending formula:
    P(Red_Win) = (σ(Logit_DNN) + P_RF(Red_Win)) / 2

Where:
- σ is the sigmoid function
- Logit_DNN is the raw DNN output
- P_RF(Red_Win) is the Random Forest probability
"""

import numpy as np
from typing import Dict, Tuple, Optional


class EnsembleBlender:
    """
    Ensemble blending for combining DNN and Random Forest predictions.

    The ensemble uses unweighted soft-voting to combine probabilities from
    both models.
    """

    def __init__(self, use_rf: bool = True):
        """
        Initialize the ensemble blender.

        Args:
            use_rf: Whether to use Random Forest in the ensemble
        """
        self.use_rf = use_rf

    def sigmoid(self, x: float) -> float:
        """
        Sigmoid function to convert logits to probabilities using scipy.special.expit.

        Args:
            x: Input logit

        Returns:
            Probability in range [0, 1]
        """
        from scipy.special import expit
        return float(expit(x))

    def blend_probabilities(self, dnn_logit: float,
                           rf_prob: Optional[float] = None) -> Dict[str, float]:
        """
        Blend DNN and Random Forest probabilities.

        Formula: P(Red_Win) = (σ(Logit_DNN) + P_RF(Red_Win)) / 2

        Args:
            dnn_logit: Raw logit output from DNN
            rf_prob: Red win probability from Random Forest (optional)

        Returns:
            Dictionary with blended probabilities and intermediate values
        """
        # Convert DNN logit to probability
        dnn_prob = self.sigmoid(dnn_logit)

        if self.use_rf and rf_prob is not None:
            # Blend with Random Forest
            ensemble_prob = (dnn_prob + rf_prob) / 2.0
        else:
            # Use DNN only
            ensemble_prob = dnn_prob

        return {
            'dnn_logit': float(dnn_logit),
            'dnn_prob': float(dnn_prob),
            'rf_prob': float(rf_prob) if rf_prob is not None else None,
            'ensemble_prob': float(ensemble_prob),
            'blue_win_prob': float(1.0 - ensemble_prob)
        }

    def blend_batch(self, dnn_logits: np.ndarray,
                   rf_probs: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """
        Blend probabilities for a batch of predictions.

        Args:
            dnn_logits: Array of DNN logits (N,)
            rf_probs: Array of RF probabilities (N,) or None

        Returns:
            Dictionary with arrays of blended probabilities
        """
        # Convert DNN logits to probabilities
        dnn_probs = self.sigmoid_batch(dnn_logits)

        if self.use_rf and rf_probs is not None:
            # Blend with Random Forest
            ensemble_probs = (dnn_probs + rf_probs) / 2.0
        else:
            # Use DNN only
            ensemble_probs = dnn_probs

        result = {
            'dnn_logits': dnn_logits.astype(np.float32),
            'dnn_probs': dnn_probs.astype(np.float32),
            'rf_probs': rf_probs.astype(np.float32) if rf_probs is not None else None,
            'ensemble_probs': ensemble_probs.astype(np.float32),
            'blue_win_probs': (1.0 - ensemble_probs).astype(np.float32)
        }

        return result

    def sigmoid_batch(self, logits: np.ndarray) -> np.ndarray:
        """
        Apply sigmoid to a batch of logits using scipy.special.expit.

        Args:
            logits: Array of logit values

        Returns:
            Array of probabilities
        """
        from scipy.special import expit
        return expit(logits).astype(np.float32)

    def set_use_rf(self, use_rf: bool) -> None:
        """
        Enable or disable Random Forest in the ensemble.

        Args:
            use_rf: Whether to use Random Forest
        """
        self.use_rf = use_rf


def calculate_ensemble_uncertainty(dnn_prob: float,
                                  rf_prob: Optional[float] = None) -> float:
    """
    Calculate ensemble uncertainty based on model agreement.

    Args:
        dnn_prob: DNN probability
        rf_prob: Random Forest probability (optional)

    Returns:
        Uncertainty score (0 = perfect agreement, 1 = maximum disagreement)
    """
    if rf_prob is None:
        # If only DNN, uncertainty is based on probability confidence
        # Maximum uncertainty at p=0.5, minimum at p=0 or p=1
        return 2 * abs(dnn_prob - 0.5)
    else:
        # Uncertainty is the absolute difference between models
        return abs(dnn_prob - rf_prob)


def analyze_ensemble_behavior(dnn_logits: np.ndarray,
                             rf_probs: Optional[np.ndarray] = None) -> Dict[str, float]:
    """
    Analyze ensemble behavior across a range of predictions.

    Args:
        dnn_logits: Array of DNN logits
        rf_probs: Array of RF probabilities (optional)

    Returns:
        Dictionary with ensemble statistics
    """
    blender = EnsembleBlender(rf_probs is not None)
    results = blender.blend_batch(dnn_logits, rf_probs)

    stats = {
        'mean_dnn_prob': float(np.mean(results['dnn_probs'])),
        'mean_rf_prob': float(np.mean(results['rf_probs'])) if results['rf_probs'] is not None else None,
        'mean_ensemble_prob': float(np.mean(results['ensemble_probs'])),
        'std_ensemble_prob': float(np.std(results['ensemble_probs'])),
        'min_ensemble_prob': float(np.min(results['ensemble_probs'])),
        'max_ensemble_prob': float(np.max(results['ensemble_probs'])),
        'mean_uncertainty': float(np.mean([
            calculate_ensemble_uncertainty(p, r)
            for p, r in zip(results['dnn_probs'],
                           (results['rf_probs'] if results['rf_probs'] is not None else [None] * len(results['dnn_probs'])))
        ]))
    }

    return stats


def test_ensemble_blending():
    """Test the ensemble blending with various scenarios."""
    blender = EnsembleBlender(use_rf=True)

    print("Ensemble Blending Test")
    print("=" * 60)

    # Test case 1: Both models agree on high probability
    result1 = blender.blend_probabilities(dnn_logit=2.0, rf_prob=0.9)
    print("\nCase 1: Both models agree (high red win probability)")
    print(f"  DNN logit: {result1['dnn_logit']:.4f}")
    print(f"  DNN prob: {result1['dnn_prob']:.4f}")
    print(f"  RF prob: {result1['rf_prob']:.4f}")
    print(f"  Ensemble prob: {result1['ensemble_prob']:.4f}")
    print(f"  Blue win prob: {result1['blue_win_prob']:.4f}")

    # Test case 2: Models disagree
    result2 = blender.blend_probabilities(dnn_logit=1.0, rf_prob=0.3)
    print("\nCase 2: Models disagree")
    print(f"  DNN logit: {result2['dnn_logit']:.4f}")
    print(f"  DNN prob: {result2['dnn_prob']:.4f}")
    print(f"  RF prob: {result2['rf_prob']:.4f}")
    print(f"  Ensemble prob: {result2['ensemble_prob']:.4f}")
    print(f"  Uncertainty: {calculate_ensemble_uncertainty(result2['dnn_prob'], result2['rf_prob']):.4f}")

    # Test case 3: DNN only
    blender_no_rf = EnsembleBlender(use_rf=False)
    result3 = blender_no_rf.blend_probabilities(dnn_logit=0.5)
    print("\nCase 3: DNN only (no Random Forest)")
    print(f"  DNN logit: {result3['dnn_logit']:.4f}")
    print(f"  DNN prob: {result3['dnn_prob']:.4f}")
    print(f"  Ensemble prob: {result3['ensemble_prob']:.4f}")

    # Test batch processing
    print("\nBatch Processing Test")
    dnn_logits = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    rf_probs = np.array([0.1, 0.2, 0.5, 0.8, 0.9])
    batch_results = blender.blend_batch(dnn_logits, rf_probs)

    print(f"  Processed {len(dnn_logits)} samples")
    print(f"  Mean ensemble prob: {batch_results['ensemble_probs'].mean():.4f}")
    print(f"  Ensemble probs: {batch_results['ensemble_probs']}")


if __name__ == '__main__':
    test_ensemble_blending()
