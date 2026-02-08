# model/train_model.py
"""
Fertilizer Recommendation Model Training Script.

This script trains a Random Forest classifier to recommend optimal fertilizer
based on soil nutrients, leaf color, and weather conditions.

================================================================================
WHY TRAINING IS OFFLINE
================================================================================
1. Model training requires significant computational resources (CPU/GPU)
2. Training on every API request would be extremely slow and expensive
3. Pre-trained models can be served instantly for predictions
4. Allows A/B testing multiple model versions independently
5. Enables model versioning and rollback capabilities
6. Separates data science workflow from production serving

In production:
- Train offline (this script) → Save model → Serve predictions via API
- Re-train periodically when new labeled data is available
- Deploy new model versions without downtime

================================================================================
WHY RANDOM FOREST WAS CHOSEN
================================================================================
1. Classification Task: Fertilizer recommendation is a multi-class
   classification problem (discrete fertilizer types)

2. Mixed Feature Types: Works well with numerical (N, P, K values) and
   categorical (leaf color) features without extensive preprocessing

3. Handles Non-Linearity: Soil nutrient relationships are often non-linear;
   Random Forest captures complex interactions automatically

4. Robust to Overfitting: Random Forest's ensemble approach reduces variance
   compared to single Decision Trees

5. Feature Importance: Built-in feature importance rankings help understand
   which soil factors matter most for recommendations

6. No Scaling Required: Unlike SVM or Neural Networks, Random Forest is
   invariant to feature scaling

7. Works with Small Data: Performs well even with limited training data
   compared to deep learning approaches

Alternative models considered:
- Decision Tree: More prone to overfitting, less robust
- SVM: Requires scaling, less interpretable
- Neural Network: Overkill for this problem size, harder to interpret
- XGBoost: Also excellent, but Random Forest is simpler and sufficient
================================================================================
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
import pickle
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================

# Output paths for trained model and metadata
MODEL_OUTPUT_PATH = "model/fertilizer_model.pkl"
ENCODER_OUTPUT_PATH = "model/label_encoder.pkl"
METADATA_OUTPUT_PATH = "model/model_metadata.json"

# Random Forest hyperparameters
# These are common defaults that work well for many classification tasks
N_ESTIMATORS = 100          # Number of trees in the forest
MAX_DEPTH = 10              # Maximum depth of each tree
RANDOM_STATE = 42           # For reproducible results
TEST_SIZE = 0.2             # 20% of data for testing

# Fertilizer classes (target labels)
FERTILIZER_CLASSES = [
    "urea",
    "dap",
    "potash",
    "npk_10_10_10",
    "npk_20_20_20",
    "organic_compost",
    "zinc_sulfate",
    "iron_sulfate"
]


# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_synthetic_data(n_samples: int = 10000) -> pd.DataFrame:
    """
    Generate synthetic dataset for fertilizer recommendation.
    
    In real-world scenarios, this data would come from:
    - Historical soil test results paired with expert recommendations
    - Agricultural extension service databases
    - Research publications on crop nutrition
    
    Args:
        n_samples: Number of synthetic samples to generate
        
    Returns:
        DataFrame with features and target labels
    """
    print(f"Generating {n_samples} synthetic data samples...")
    
    np.random.seed(RANDOM_STATE)
    
    # Generate features based on realistic agricultural ranges
    
    # Soil nutrient levels (kg/ha)
    # Nitrogen: 20-200 kg/ha
    nitrogen = np.random.uniform(20, 200, n_samples)
    
    # Phosphorus: 5-100 kg/ha
    phosphorus = np.random.uniform(5, 100, n_samples)
    
    # Potassium: 20-300 kg/ha
    potassium = np.random.uniform(20, 300, n_samples)
    
    # Leaf color (categorical encoded as 0-5)
    # 0: yellow, 1: pale_green, 2: light_green, 3: medium_green,
    # 4: dark_green, 5: dark_with_spots
    leaf_color = np.random.randint(0, 6, n_samples)
    
    # Weather conditions (categorical encoded as 0-4)
    # 0: dry_hot, 1: dry_cool, 2: humid_hot, 3: humid_cool, 4: normal
    weather = np.random.randint(0, 5, n_samples)
    
    # Generate target labels based on rule-based logic
    # This simulates how an agricultural expert would recommend fertilizer
    
    recommendations = []
    
    for i in range(n_samples):
        n, p, k = nitrogen[i], phosphorus[i], potassium[i]
        color = leaf_color[i]
        w = weather[i]
        
        # Rule-based fertilizer recommendation logic
        # In real training data, these would come from expert annotations
        
        if n < 50 and p < 20 and k < 50:
            # Severe deficiency across all nutrients
            recommendations.append("urea")
        elif n < 70 and p < 30:
            # Nitrogen and phosphorus deficiency
            recommendations.append("dap")
        elif k < 60:
            # Potassium deficiency
            recommendations.append("potash")
        elif color <= 1:
            # Yellow/pale leaves suggest nitrogen deficiency
            if w == 0 or w == 2:  # Hot weather
                recommendations.append("urea")
            else:
                recommendations.append("organic_compost")
        elif color >= 4:
            # Dark green with spots could indicate nutrient toxicity
            recommendations.append("npk_10_10_10")
        elif p < 40 and k < 100:
            # Moderate deficiencies
            recommendations.append("npk_20_20_20")
        elif w == 0:  # Dry hot
            recommendations.append("zinc_sulfate")
        elif w == 3:  # Humid cool
            recommendations.append("iron_sulfate")
        else:
            # Balanced recommendation
            recommendations.append("npk_10_10_10")
    
    # Create DataFrame
    df = pd.DataFrame({
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium,
        "leaf_color": leaf_color,
        "weather": weather,
        "fertilizer_recommendation": recommendations
    })
    
    print(f"Generated dataset shape: {df.shape}")
    print(f"Class distribution:\n{df['fertilizer_recommendation'].value_counts()}")
    
    return df


# =============================================================================
# MODEL TRAINING
# =============================================================================

def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray
) -> tuple[RandomForestClassifier, dict]:
    """
    Train Random Forest classifier and return trained model with metrics.
    
    Args:
        X_train: Training features: Training labels

        y_train        X_test: Test features
        y_test: Test labels
        
    Returns:
        Tuple of (trained_model, evaluation_metrics)
    """
    print("\n" + "="*60)
    print("TRAINING RANDOM FOREST CLASSIFIER")
    print("="*60)
    
    # Initialize Random Forest classifier
    # Why these parameters:
    # - n_estimators=100: Good balance of accuracy vs training time
    # - max_depth=10: Prevents overfitting, keeps trees interpretable
    # - random_state=42: Ens reproducibility
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Use all CPU cores for faster training
        class_weight="balanced"  # Handle imbalanced classes
    )
    
    print(f"Model: RandomForestClassifier")
    print(f"  - n_estimators: {N_ESTIMATORS}")
    print(f"  - max_depth: {MAX_DEPTH}")
    print(f"  - class_weight: balanced")
    print(f"\nTraining on {len(X_train)} samples...")
    
    # Train the model
    model.fit(X_train, y_train)
    print("Training complete!")
    
    # Make predictions on test set
    y_pred = model.predict(X_test)
    
    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Per-class metrics
    class_report = classification_report(
        y_test, y_pred,
        output_dict=True,
        zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Feature importances
    feature_names = ["nitrogen", "phosphorus", "potassium", "leaf_color", "weather"]
    importances = model.feature_importances_
    feature_importance = dict(zip(feature_names, importances.tolist()))
    
    # Compile metrics
    metrics = {
        "accuracy": float(accuracy),
        "classification_report": class_report,
        "confusion_matrix": cm.tolist(),
        "feature_importance": feature_importance
    }
    
    return model, metrics


# =============================================================================
# MODEL SAVING
# =============================================================================

def save_model(
    model: RandomForestClassifier,
    label_encoder: LabelEncoder,
    metadata: dict
) -> None:
    """
    Save trained model, label encoder, and metadata to disk.
    
    Saves three files:
    1. fertilizer_model.pkl - Trained Random Forest model
    2. label_encoder.pkl - Label encoder for target classes
    3. model_metadata.json - Training metadata and metrics
    
    Args:
        model: Trained Random Forest classifier
        label_encoder: Fitted label encoder for target classes
        metadata: Training metadata and evaluation metrics
    """
    print("\n" + "="*60)
    print("SAVING MODEL")
    print("="*60)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    
    # Save model
    with open(MODEL_OUTPUT_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"✓ Model saved: {MODEL_OUTPUT_PATH}")
    
    # Save label encoder
    with open(ENCODER_OUTPUT_PATH, "wb") as f:
        pickle.dump(label_encoder, f)
    print(f"✓ Label encoder saved: {ENCODER_OUTPUT_PATH}")
    
    # Save metadata
    with open(METADATA_OUTPUT_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {METADATA_OUTPUT_PATH}")


# =============================================================================
# MAIN TRAINING PIPELINE
# =============================================================================

def main():
    """
    Main training pipeline.
    
    Execution flow:
    1. Generate synthetic training data
    2. Encode categorical features
    3. Split data into train/test sets
    4. Train Random Forest model
    5. Evaluate model performance
    6. Save model and artifacts
    7. Print training summary
    """
    print("\n" + "="*60)
    print("FERTILIZER RECOMMENDATION MODEL TRAINING")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Generate synthetic data
    df = generate_synthetic_data(n_samples=10000)
    
    # Step 2: Prepare features and target
    feature_columns = ["nitrogen", "phosphorus", "potassium", "leaf_color", "weather"]
    X = df[feature_columns].values
    y_raw = df["fertilizer_recommendation"].values
    
    # Step 3: Encode target labels
    # Convert string labels to integers for sklearn
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    print(f"\nTarget classes: {list(label_encoder.classes_)}")
    
    # Step 4: Split data into train/test sets
    # Stratify ensures each class is proportionally represented in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    print(f"\nData split:")
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    
    # Step 5: Train model
    model, metrics = train_model(
        X_train, y_train,
        X_test, y_test
    )
    
    # Step 6: Print evaluation results
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    
    print("\nFeature Importances:")
    for feature, importance in sorted(
        metrics['feature_importance'].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"  - {feature}: {importance:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(
        y_test,
        model.predict(X_test),
        target_names=label_encoder.classes_,
        zero_division=0
    ))
    
    # Step 7: Save model and artifacts
    metadata = {
        "model_type": "RandomForestClassifier",
        "training_date": datetime.now().isoformat(),
        "n_estimators": N_ESTIMATORS,
        "max_depth": MAX_DEPTH,
        "n_samples_train": len(X_train),
        "n_samples_test": len(X_test),
        "target_classes": list(label_encoder.classes_),
        "feature_names": feature_columns,
        "metrics": metrics
    }
    
    save_model(model, label_encoder, metadata)
    
    # Step 8: Print summary
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"Model saved to: {MODEL_OUTPUT_PATH}")
    print(f"Ready for deployment in production API!")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return model, label_encoder


if __name__ == "__main__":
    main()
