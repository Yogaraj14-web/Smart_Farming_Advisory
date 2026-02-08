# model/predictor.py
"""
ML Inference Module for Fertilizer Recommendation.

Loads pre-trained model and provides prediction with human-readable explanations.
Designed to be reusable by backend APIs.
"""
import os
import pickle
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "fertilizer_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")
METADATA_PATH = os.path.join(BASE_DIR, "model_metadata.json")



# =============================================================================
# FEATURE DESCRIPTIONS
# =============================================================================

FEATURE_INFO = {
    "nitrogen": {
        "name": "Nitrogen",
        "unit": "kg/ha",
        "description": "Essential for vegetative growth and leaf development",
        "low_threshold": 50,
        "optimal_threshold": 100
    },
    "phosphorus": {
        "name": "Phosphorus",
        "unit": "kg/ha",
        "description": "Critical for root development and energy transfer",
        "low_threshold": 20,
        "optimal_threshold": 50
    },
    "potassium": {
        "name": "Potassium",
        "unit": "kg/ha",
        "description": "Important for drought resistance and disease tolerance",
        "low_threshold": 80,
        "optimal_threshold": 150
    },
    "leaf_color": {
        "name": "Leaf Color",
        "description": "Visual indicator of plant nutrient status",
        "mapping": {
            0: "Yellow (severe nitrogen deficiency)",
            1: "Pale Green (moderate deficiency)",
            2: "Light Green (slight deficiency)",
            3: "Medium Green (healthy)",
            4: "Dark Green (good)",
            5: "Dark Green with Spots (possible toxicity)"
        }
    },
    "weather": {
        "name": "Weather",
        "description": "Current environmental conditions affecting nutrient uptake",
        "mapping": {
            0: "Dry and Hot",
            1: "Dry and Cool",
            2: "Humid and Hot",
            3: "Humid and Cool",
            4: "Normal Conditions"
        }
    }
}

# Fertilizer reference information
FERTILIZER_INFO = {
    "urea": {
        "name": "Urea (46-0-0)",
        "type": "Nitrogen fertilizer",
        "use_case": "Rapid nitrogen supplementation for vegetative growth"
    },
    "dap": {
        "name": "DAP (18-46-0)",
        "type": "Phosphorus fertilizer",
        "use_case": "Root development and early growth stage"
    },
    "potash": {
        "name": "Potash (0-0-60)",
        "type": "Potassium fertilizer",
        "use_case": "Drought resistance and stem strength"
    },
    "npk_10_10_10": {
        "name": "NPK 10-10-10",
        "type": "Balanced fertilizer",
        "use_case": "General purpose nutrition and maintenance"
    },
    "npk_20_20_20": {
        "name": "NPK 20-20-20",
        "type": "High-analysis balanced fertilizer",
        "use_case": "Moderate deficiencies across all nutrients"
    },
    "organic_compost": {
        "name": "Organic Compost",
        "type": "Soil amendment",
        "use_case": "Long-term soil health and structure"
    },
    "zinc_sulfate": {
        "name": "Zinc Sulfate",
        "type": "Micronutrient fertilizer",
        "use_case": "Zinc deficiency correction"
    },
    "iron_sulfate": {
        "name": "Iron Sulfate",
        "type": "Micronutrient fertilizer",
        "use_case": "Iron deficiency (chlorosis) treatment"
    }
}


# =============================================================================
# MODEL LOADING
# =============================================================================

class FertilizerPredictor:
    """
    Fertilizer recommendation inference class.
    
    Loads pre-trained model and provides reusable prediction methods.
    Designed to be called from backend APIs.
    
    Usage:
        predictor = FertilizerPredictor()
        result = predictor.predict(
            nitrogen=45.0,
            phosphorus=25.0,
            potassium=80.0,
            leaf_color=1,
            weather=0
        )
    """
    
    def __init__(self):
        """Load model, label encoder, and metadata on initialization."""
        self.model = None
        self.label_encoder = None
        self.metadata = None
        self._load_artifacts()
    
    def _load_artifacts(self) -> None:
        """
        Load model, label encoder, and metadata from pickle files.
        
        Raises:
            FileNotFoundError: If model files don't exist
            ValueError: If model files are corrupted
        """
        # Check all required files exist
        missing_files = []
        for path in [MODEL_PATH, ENCODER_PATH, METADATA_PATH]:
            if not os.path.exists(path):
                missing_files.append(path)
        
        if missing_files:
            raise FileNotFoundError(
                f"Missing model files: {', '.join(missing_files)}. "
                "Run 'python model/train_model.py' first."
            )
        
        # Load model
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        
        # Load label encoder
        with open(ENCODER_PATH, "rb") as f:
            self.label_encoder = pickle.load(f)
        
        # Load metadata
        with open(METADATA_PATH, "r") as f:
            self.metadata = json.load(f)
        
        # Extract feature names and importance from metadata
        self.feature_names = self.metadata.get("feature_names", [])
        self.feature_importance = self.metadata.get("metrics", {}).get(
            "feature_importance", {}
        )
        
        # Sort features by importance
        self.sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
    
    def _get_input_summary(self, **kwargs) -> Dict[str, Any]:
        """Create summary of input parameters."""
        return {
            "nitrogen_kg_ha": kwargs.get("nitrogen"),
            "phosphorus_kg_ha": kwargs.get("phosphorus"),
            "potassium_kg_ha": kwargs.get("potassium"),
            "leaf_color_code": kwargs.get("leaf_color"),
            "weather_code": kwargs.get("weather")
        }
    
    def _get_nutrient_status(self, nutrient: str, value: float) -> str:
        """Determine nutrient status level."""
        info = FEATURE_INFO.get(nutrient, {})
        low = info.get("low_threshold", 0)
        optimal = info.get("optimal_threshold", 100)
        
        if value < low:
            return "low"
        elif value < optimal:
            return "medium"
        else:
            return "good"
    
    def _generate_explanation(
        self,
        recommendation: str,
        feature_values: Dict[str, float],
        confidence: float
    ) -> str:
        """
        Generate human-readable explanation for the recommendation.
        
        Args:
            recommendation: Predicted fertilizer class
            feature_values: Dictionary of input feature values
            confidence: Confidence score
            
        Returns:
            Human-readable explanation string
        """
        lines = []
        lines.append("=" * 50)
        lines.append("FERTILIZER RECOMMENDATION ANALYSIS")
        lines.append("=" * 50)
        
        # Top influencing features
        lines.append("\n📊 TOP INFLUENCING FEATURES:")
        for i, (feature, importance) in enumerate(self.sorted_features[:3], 1):
            value = feature_values.get(feature, 0)
            status = self._get_nutrient_status(feature, value)
            lines.append(
                f"  {i}. {FEATURE_INFO[feature]['name']}: "
                f"{value:.1f} ({status}) - importance: {importance:.2%}"
            )
        
        # Nutrient analysis
        lines.append("\n🌱 NUTRIENT ANALYSIS:")
        for nutrient in ["nitrogen", "phosphorus", "potassium"]:
            value = feature_values.get(nutrient, 0)
            status = self._get_nutrient_status(nutrient, value)
            info = FEATURE_INFO[nutrient]
            lines.append(f"  • {info['name']}: {value:.1f} {info['unit']} ({status})")
        
        # Plant condition
        leaf_code = feature_values.get("leaf_color", 0)
        leaf_desc = FEATURE_INFO["leaf_color"]["mapping"].get(leaf_code, "Unknown")
        lines.append(f"\n🌿 PLANT CONDITION: {leaf_desc}")
        
        # Weather
        weather_code = feature_values.get("weather", 0)
        weather_desc = FEATURE_INFO["weather"]["mapping"].get(weather_code, "Unknown")
        lines.append(f"🌤️ WEATHER: {weather_desc}")
        
        # Recommendation
        lines.append("\n" + "=" * 50)
        lines.append("🎯 RECOMMENDATION")
        lines.append("=" * 50)
        
        fert_info = FERTILIZER_INFO.get(recommendation, {})
        lines.append(f"Fertilizer: {fert_info.get('name', recommendation)}")
        lines.append(f"Type: {fert_info.get('type', 'Unknown')}")
        lines.append(f"Use Case: {fert_info.get('use_case', 'N/A')}")
        lines.append(f"\nConfidence: {confidence:.1%}")
        
        return "\n".join(lines)
    
    def predict(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        leaf_color: int,
        weather: int
    ) -> Dict[str, Any]:
        """
        Generate fertilizer recommendation with full analysis.
        
        Args:
            nitrogen: Soil nitrogen level (kg/ha)
            phosphorus: Soil phosphorus level (kg/ha)
            potassium: Soil potassium level (kg/ha)
            leaf_color: Leaf color code (0-5)
            weather: Weather condition code (0-4)
            
        Returns:
            Dictionary containing:
            - recommendation: Predicted fertilizer class
            - confidence: Confidence score (0-1)
            - explanation: Human-readable analysis
            - input_summary: Summary of input values
        """
        # Validate inputs
        if not (0 <= leaf_color <= 5):
            raise ValueError(f"leaf_color must be 0-5, got {leaf_color}")
        if not (0 <= weather <= 4):
            raise ValueError(f"weather must be 0-4, got {weather}")
        if nitrogen < 0 or phosphorus < 0 or potassium < 0:
            raise ValueError("Nutrient values cannot be negative")
        
        # Prepare input features
        X = [[nitrogen, phosphorus, potassium, leaf_color, weather]]
        
        # Get prediction
        pred_encoded = self.model.predict(X)[0]
        recommendation = self.label_encoder.inverse_transform([pred_encoded])[0]
        
        # Get confidence (probability of predicted class)
        proba = self.model.predict_proba(X)[0]
        confidence = proba[pred_encoded]
        
        # Build feature values dict for explanation
        feature_values = {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "leaf_color": leaf_color,
            "weather": weather
        }
        
        # Generate explanation
        explanation = self._generate_explanation(
            recommendation, feature_values, confidence
        )
        
        # Build result
        return {
            "recommendation": recommendation,
            "confidence": round(float(confidence), 4),
            "explanation": explanation,
            "input_summary": self._get_input_summary(
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                leaf_color=leaf_color,
                weather=weather
            )
        }
    
    def get_quick_recommendation(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        leaf_color: int,
        weather: int
    ) -> Dict[str, Any]:
        """
        Get simplified recommendation without full explanation.
        
        Useful for quick API responses.
        """
        X = [[nitrogen, phosphorus, potassium, leaf_color, weather]]
        pred_encoded = self.model.predict(X)[0]
        recommendation = self.label_encoder.inverse_transform([pred_encoded])[0]
        proba = self.model.predict_proba(X)[0]
        confidence = proba[pred_encoded]
        
        return {
            "fertilizer": recommendation,
            "confidence": round(float(confidence), 4)
        }


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def predict_fertilizer(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    leaf_color: int,
    weather: int
) -> Dict[str, Any]:
    """
    Convenience function for single predictions.
    
    Creates a new predictor instance and returns the result.
    For high-frequency calls, create a single FertilizerPredictor instance.
    """
    predictor = FertilizerPredictor()
    return predictor.predict(
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        leaf_color=leaf_color,
        weather=weather
    )


# =============================================================================
# MAIN / TESTING
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("Testing Fertilizer Predictor...")
    print()
    
    # Create predictor
    predictor = FertilizerPredictor()
    
    # Test case
    result = predictor.predict(
        nitrogen=45.0,      # Low nitrogen
        phosphorus=18.0,    # Low phosphorus
        potassium=65.0,      # Medium potassium
        leaf_color=1,        # Pale green leaves
        weather=0            # Dry and hot
    )
    
    print(result["explanation"])
    print()
    print("JSON Output:")
    print(json.dumps(result, indent=2))
