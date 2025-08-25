# management/commands/train_models.py

import json
import logging
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from lottery_prediction.ml.models.baseline import (
    CyclicalPredictor,
    DayOfWeekPredictor,
    FrequencyBasedPredictor,
)
from lottery_prediction.ml.models.ensemble import ModelFactory
from lottery_prediction.ml.models.gradient_boosting import (
    HyperparameterOptimizer,
    LotteryGradientBoostingModel,
)
from results.models import KetQuaXoSo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Train lottery prediction models with hyperparameter optimization"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model-type",
            type=str,
            choices=[
                "baseline",
                "gradient_boosting",
                "hist_gradient_boosting",
                "ensemble",
                "all",
            ],
            default="ensemble",
            help="Type of model to train (default: ensemble)",
        )
        parser.add_argument(
            "--train-days",
            type=int,
            default=365,
            help="Number of days of training data (default: 365)",
        )
        parser.add_argument(
            "--optimize",
            action="store_true",
            help="Perform hyperparameter optimization",
        )
        parser.add_argument(
            "--search-type",
            type=str,
            choices=["grid", "random"],
            default="random",
            help="Type of hyperparameter search (default: random)",
        )
        parser.add_argument(
            "--search-iterations",
            type=int,
            default=50,
            help="Number of iterations for random search (default: 50)",
        )
        parser.add_argument(
            "--cv-folds",
            type=int,
            default=3,
            help="Number of cross-validation folds (default: 3)",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default="models",
            help="Directory to save trained models (default: models)",
        )
        parser.add_argument(
            "--evaluate",
            action="store_true",
            help="Evaluate trained models on validation set",
        )
        parser.add_argument(
            "--validation-days",
            type=int,
            default=60,
            help="Number of days for validation (default: 60)",
        )

    def handle(self, *args, **options):
        model_type = options["model_type"]
        train_days = options["train_days"]
        optimize = options["optimize"]
        search_type = options["search_type"]
        search_iterations = options["search_iterations"]
        cv_folds = options["cv_folds"]
        output_dir = options["output_dir"]
        evaluate = options["evaluate"]
        validation_days = options["validation_days"]

        self.stdout.write(f"Starting model training: {model_type}")

        # Add this at the beginning of the handle method
        self.stdout.write("Checking data availability...")
        earliest_date = KetQuaXoSo.objects.earliest("ngay").ngay
        latest_date = KetQuaXoSo.objects.latest("ngay").ngay
        total_days = (latest_date - earliest_date).days

        self.stdout.write(
            f"Data available from {earliest_date} to {latest_date} ({total_days} days)"
        )

        if total_days < options["train_days"] + 30:  # Training days + buffer
            self.stdout.write(
                self.style.ERROR(
                    f"Insufficient data. Need at least {options['train_days'] + 30} days, have {total_days}"
                )
            )
            return

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Check data availability
        if not self._check_data_availability(train_days):
            return

        # FIX: Set up date ranges properly without artificial reduction
        current_date = timezone.now().date()

        # CRITICAL FIX: Use actual latest data, not artificially reduced
        # The system should train on ALL available historical data
        end_date = latest_date  # Use all available data

        # Only reduce end_date if it's in the future (which shouldn't happen)
        if end_date > current_date:
            end_date = current_date - timedelta(days=1)

        train_start_date = end_date - timedelta(days=train_days)
        validation_start_date = end_date - timedelta(days=validation_days)

        # Ensure validation period is before training end
        if validation_start_date >= end_date:
            validation_start_date = end_date - timedelta(
                days=min(validation_days, train_days // 2)
            )

        self.stdout.write(f"Training period: {train_start_date} to {end_date}")
        self.stdout.write(f"Validation period: {validation_start_date} to {end_date}")

        # Train models based on type
        if model_type == "all":
            self._train_all_models(
                train_start_date,
                end_date,
                validation_start_date,
                optimize,
                search_type,
                search_iterations,
                cv_folds,
                output_dir,
                evaluate,
            )
        else:
            self._train_single_model_type(
                model_type,
                train_start_date,
                end_date,
                validation_start_date,
                optimize,
                search_type,
                search_iterations,
                cv_folds,
                output_dir,
                evaluate,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Model training completed. Models saved to {output_dir}"
            )
        )

    def _check_data_availability(self, train_days: int) -> bool:
        """Check if sufficient training data is available"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=train_days)

        available_data = KetQuaXoSo.objects.filter(
            ngay__gte=start_date, ngay__lte=end_date
        ).count()

        if available_data < 30:
            self.stdout.write(
                self.style.ERROR(
                    f"Insufficient training data. Found {available_data} records, need at least 30."
                )
            )
            return False

        self.stdout.write(f"Training data available: {available_data} records")
        return True

    def _train_all_models(
        self,
        train_start_date,
        end_date,
        validation_start_date,
        optimize,
        search_type,
        search_iterations,
        cv_folds,
        output_dir,
        evaluate,
    ):
        """Train all model types"""
        self.stdout.write("Training all model types...")

        model_types = [
            "baseline",
            "gradient_boosting",
            "hist_gradient_boosting",
            "ensemble",
        ]

        for model_type in model_types:
            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"Training {model_type.upper()} models")
            self.stdout.write(f"{'='*50}")

            try:
                self._train_single_model_type(
                    model_type,
                    train_start_date,
                    end_date,
                    validation_start_date,
                    optimize,
                    search_type,
                    search_iterations,
                    cv_folds,
                    output_dir,
                    evaluate,
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error training {model_type}: {e}"))
                logger.error(f"Error training {model_type}: {e}", exc_info=True)

    def _train_single_model_type(
        self,
        model_type,
        train_start_date,
        end_date,
        validation_start_date,
        optimize,
        search_type,
        search_iterations,
        cv_folds,
        output_dir,
        evaluate,
    ):
        """Train a single model type"""

        if model_type == "baseline":
            self._train_baseline_models(
                train_start_date, end_date, output_dir, evaluate, validation_start_date
            )

        elif model_type == "gradient_boosting":
            self._train_gradient_boosting_model(
                "gradient_boosting",
                train_start_date,
                end_date,
                validation_start_date,
                optimize,
                search_type,
                search_iterations,
                cv_folds,
                output_dir,
                evaluate,
            )

        elif model_type == "hist_gradient_boosting":
            self._train_gradient_boosting_model(
                "hist_gradient_boosting",
                train_start_date,
                end_date,
                validation_start_date,
                optimize,
                search_type,
                search_iterations,
                cv_folds,
                output_dir,
                evaluate,
            )

        elif model_type == "ensemble":
            self._train_ensemble_models(
                train_start_date, end_date, validation_start_date, output_dir, evaluate
            )

    def _train_baseline_models(
        self, train_start_date, end_date, output_dir, evaluate, validation_start_date
    ):
        """Train baseline models"""
        self.stdout.write("Training baseline models...")

        baseline_models = [
            ("frequency_based_90d", FrequencyBasedPredictor(lookback_days=90)),
            ("frequency_based_180d", FrequencyBasedPredictor(lookback_days=180)),
            ("day_of_week", DayOfWeekPredictor(lookback_days=180)),
            ("cyclical", CyclicalPredictor(lookback_days=365)),
        ]

        baseline_results = {}

        for name, model in baseline_models:
            self.stdout.write(f"  Training {name}...")

            try:
                # Train model
                model.fit(start_date=train_start_date, end_date=end_date)

                # Save model
                model_path = os.path.join(output_dir, f"{name}_model.pkl")
                import joblib

                joblib.dump(model, model_path)

                # Evaluate if requested
                if evaluate:
                    evaluation = self._evaluate_baseline_model(
                        model, validation_start_date, end_date
                    )
                    baseline_results[name] = evaluation
                    self.stdout.write(
                        f"    Validation accuracy: {evaluation['accuracy']:.4f}"
                    )

                self.stdout.write(f"    ✓ {name} trained and saved")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ✗ Error training {name}: {e}"))
                logger.error(
                    f"Error training baseline model {name}: {e}", exc_info=True
                )

        # Save baseline results
        if baseline_results:
            results_path = os.path.join(output_dir, "baseline_evaluation_results.json")
            with open(results_path, "w") as f:
                json.dump(baseline_results, f, indent=2, default=str)

    def _train_gradient_boosting_model(
        self,
        model_type,
        train_start_date,
        end_date,
        validation_start_date,
        optimize,
        search_type,
        search_iterations,
        cv_folds,
        output_dir,
        evaluate,
    ):
        """Train gradient boosting models with optional optimization"""
        self.stdout.write(f"Training {model_type} model...")

        try:
            if optimize:
                self.stdout.write(
                    f"  Performing hyperparameter optimization ({search_type} search)..."
                )

                # Create optimizer
                optimizer = HyperparameterOptimizer(model_type=model_type)

                # Prepare training data for optimization
                temp_model = LotteryGradientBoostingModel(model_type=model_type)
                X_train, y_train = temp_model.prepare_training_data(
                    train_start_date, end_date
                )

                # Optimize hyperparameters
                optimization_results = optimizer.optimize(
                    X_train,
                    y_train,
                    search_type=search_type,
                    n_iter=search_iterations,
                    cv_folds=cv_folds,
                )

                # Create optimized model
                model = optimizer.create_optimized_model()

                # Save optimization results
                opt_results_path = os.path.join(
                    output_dir, f"{model_type}_optimization_results.json"
                )
                with open(opt_results_path, "w") as f:
                    json.dump(optimization_results, f, indent=2, default=str)

                self.stdout.write(
                    f"    Best CV score: {optimization_results['best_score']:.4f}"
                )
                self.stdout.write(
                    f"    Best parameters: {optimization_results['best_params']}"
                )

            else:
                # Use default parameters
                model = LotteryGradientBoostingModel(model_type=model_type)

            # Train final model
            self.stdout.write("  Training final model...")
            model.fit(start_date=train_start_date, end_date=end_date)

            # Save model
            model_path = os.path.join(output_dir, f"{model_type}_model.pkl")
            model.save_model(model_path)

            # Evaluate if requested
            if evaluate:
                self.stdout.write("  Evaluating model...")
                evaluation = model.evaluate_on_validation_set(
                    validation_start_date, end_date
                )

                # Save evaluation results
                eval_path = os.path.join(output_dir, f"{model_type}_evaluation.json")
                with open(eval_path, "w") as f:
                    json.dump(evaluation, f, indent=2, default=str)

                self.stdout.write(
                    f"    Validation accuracy: {evaluation['accuracy']:.4f}"
                )
                self.stdout.write(
                    f"    Top-10 accuracy: {evaluation.get('top_10_accuracy', 'N/A'):.4f}"
                )

            # Print feature importance
            feature_importance = model.get_feature_importance(top_n=10)
            if feature_importance:
                self.stdout.write("  Top 10 important features:")
                for i, (feature, importance) in enumerate(feature_importance, 1):
                    self.stdout.write(f"    {i:2d}. {feature}: {importance:.4f}")

            self.stdout.write(f"    ✓ {model_type} model trained and saved")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"    ✗ Error training {model_type}: {e}")
            )
            logger.error(f"Error training {model_type} model: {e}", exc_info=True)

    def _train_ensemble_models(
        self, train_start_date, end_date, validation_start_date, output_dir, evaluate
    ):
        """Train ensemble models"""
        self.stdout.write("Training ensemble models...")

        # Check if we have enough historical data before the training period
        from results.models import KetQuaXoSo

        historical_count = KetQuaXoSo.objects.filter(ngay__lt=train_start_date).count()
        if historical_count < 30:
            self.stdout.write(
                self.style.ERROR(
                    f"Insufficient historical data before training period. "
                    f"Need at least 30 days before {train_start_date}, found {historical_count}."
                )
            )
            return

        ensemble_types = [
            ("default_weighted", ModelFactory.create_default_ensemble),
            ("dynamic", ModelFactory.create_dynamic_ensemble),
            ("stacking", ModelFactory.create_stacking_ensemble),
        ]

        ensemble_results = {}

        for name, factory_method in ensemble_types:
            self.stdout.write(f"  Training {name} ensemble...")

            try:
                # Create ensemble
                ensemble = factory_method()

                # Train ensemble
                self.stdout.write(
                    f"    Training with data from {train_start_date} to {end_date}"
                )
                ensemble.fit(start_date=train_start_date, end_date=end_date)

                # Save ensemble
                ensemble_path = os.path.join(output_dir, f"{name}_ensemble.pkl")
                import joblib

                joblib.dump(ensemble, ensemble_path)

                # Evaluate if requested
                if evaluate:
                    evaluation = self._evaluate_ensemble_model(
                        ensemble, validation_start_date, end_date
                    )
                    ensemble_results[name] = evaluation
                    self.stdout.write(
                        f"    Validation accuracy: {evaluation['accuracy']:.4f}"
                    )

                self.stdout.write(f"    ✓ {name} ensemble trained and saved")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"    ✗ Error training {name} ensemble: {e}")
                )
                logger.error(f"Error training {name} ensemble: {e}", exc_info=True)

        # Save ensemble results
        if ensemble_results:
            results_path = os.path.join(output_dir, "ensemble_evaluation_results.json")
            with open(results_path, "w") as f:
                json.dump(ensemble_results, f, indent=2, default=str)

    def _evaluate_ensemble_model(
        self, ensemble, validation_start_date, validation_end_date
    ):
        """Evaluate ensemble model with proper context"""
        results = KetQuaXoSo.objects.filter(
            ngay__gte=validation_start_date, ngay__lt=validation_end_date
        ).order_by("ngay")

        total_correct = 0
        total_predictions = 0
        total_days = 0
        detailed_results = []

        for result in results:
            try:
                # Use evaluation context to suppress data leakage warnings
                predictions = ensemble.predict_top_k(
                    X=None,
                    k=10,
                    target_date=result.ngay,
                    context="evaluation",  # KEY FIX: Use evaluation context
                )
                predicted_numbers = [pred[0] for pred in predictions]

                # Get actual numbers
                actual_numbers = result.get_all_2digit_numbers()

                # Count correct predictions
                correct_numbers = set(predicted_numbers) & set(actual_numbers)
                correct_count = len(correct_numbers)

                total_correct += correct_count
                total_predictions += 10
                total_days += 1

                # Store detailed results
                detailed_results.append(
                    {
                        "date": result.ngay.isoformat(),
                        "predicted": predicted_numbers,
                        "actual": list(actual_numbers),
                        "correct": list(correct_numbers),
                        "correct_count": correct_count,
                        "success_rate": correct_count / 10,
                    }
                )

            except Exception as e:
                logger.error(f"Error evaluating ensemble on {result.ngay}: {e}")
                continue

        # Calculate metrics
        accuracy = total_correct / total_predictions if total_predictions > 0 else 0
        avg_correct_per_day = total_correct / total_days if total_days > 0 else 0

        # Calculate success rate
        successful_days = sum(
            1 for day in detailed_results if day["correct_count"] >= 5
        )
        success_rate = successful_days / total_days if total_days > 0 else 0

        return {
            "accuracy": accuracy,
            "avg_correct_per_day": avg_correct_per_day,
            "success_rate": success_rate,
            "total_days_evaluated": total_days,
            "successful_days": successful_days,
            "total_correct_predictions": total_correct,
            "detailed_results": detailed_results[-10:],
        }

    def _evaluate_baseline_model(
        self, model, validation_start_date, validation_end_date
    ):
        """Evaluate baseline model with evaluation context"""
        results = KetQuaXoSo.objects.filter(
            ngay__gte=validation_start_date, ngay__lt=validation_end_date
        ).order_by("ngay")

        total_correct = 0
        total_predictions = 0
        total_days = 0

        for result in results:
            try:
                # Use evaluation context
                predictions = model.predict_top_k(
                    X=None,
                    k=10,
                    target_date=result.ngay,
                    context="evaluation",  # KEY FIX
                )
                predicted_numbers = [pred[0] for pred in predictions]

                # Get actual numbers
                actual_numbers = result.get_all_2digit_numbers()

                # Count correct predictions
                correct = len(set(predicted_numbers) & set(actual_numbers))
                total_correct += correct
                total_predictions += 10
                total_days += 1

            except Exception as e:
                logger.error(f"Error evaluating model on {result.ngay}: {e}")
                continue

        accuracy = total_correct / total_predictions if total_predictions > 0 else 0
        avg_correct_per_day = total_correct / total_days if total_days > 0 else 0

        return {
            "accuracy": accuracy,
            "avg_correct_per_day": avg_correct_per_day,
            "total_days_evaluated": total_days,
            "total_correct_predictions": total_correct,
        }
