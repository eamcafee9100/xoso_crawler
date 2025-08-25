import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from results.services.EnhancedMLModelTrainer import EnhancedMLModelTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_all_models():
    """Retrain all models with current scikit-learn version"""
    try:
        logger.info("Starting model retraining with current scikit-learn version...")
        
        trainer = EnhancedMLModelTrainer()
        success = trainer.train_all_models(force_retrain=True)
        
        if success:
            logger.info("✅ All models retrained successfully!")
            return True
        else:
            logger.error("❌ Model retraining failed")
            return False
            
    except Exception as e:
        logger.error(f"Error during retraining: {e}")
        return False

if __name__ == "__main__":
    retrain_all_models()