"""
Django Management Command for Enhanced Prediction System
Setup and management command for production deployment
"""

import logging
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Setup and manage Enhanced Prediction System"

    def add_arguments(self, parser):
        parser.add_argument(
            "--action",
            type=str,
            choices=["setup", "initialize", "status", "reset", "backup", "validate"],
            default="setup",
            help="Action to perform",
        )

        parser.add_argument(
            "--force", action="store_true", help="Force action without confirmation"
        )

        parser.add_argument("--verbose", action="store_true", help="Verbose output")

    def handle(self, *args, **options):
        action = options["action"]
        force = options["force"]
        verbose = options["verbose"]

        if verbose:
            logging.basicConfig(level=logging.INFO)

        self.stdout.write(
            self.style.SUCCESS(
                f"Enhanced Prediction System Management - Action: {action}"
            )
        )

        try:
            if action == "setup":
                self.setup_system(force)
            elif action == "initialize":
                self.initialize_system(force)
            elif action == "status":
                self.show_status()
            elif action == "reset":
                self.reset_system(force)
            elif action == "backup":
                self.backup_system()
            elif action == "validate":
                self.validate_system()

        except Exception as e:
            raise CommandError(f"Command failed: {e}")

    def setup_system(self, force=False):
        """Setup the enhanced prediction system"""

        self.stdout.write("Setting up Enhanced Prediction System...")

        # Check Django models
        try:
            from results.models import (
                KetQuaXoSo,
                ModelTrainingHistory,
                PredictionPerformanceMetrics,
            )

            self.stdout.write(
                self.style.SUCCESS("✓ Django models imported successfully")
            )
        except ImportError as e:
            raise CommandError(f"Failed to import Django models: {e}")

        # Check data availability
        total_records = KetQuaXoSo.objects.count()
        self.stdout.write(f"Total lottery records: {total_records}")

        if total_records < 100:
            if not force:
                raise CommandError(
                    f"Insufficient data ({total_records} records). "
                    f"Need at least 100 records. Use --force to proceed anyway."
                )
            else:
                self.stdout.write(self.style.WARNING("⚠ Proceeding with limited data"))

        # Create required directories
        directories = ["ml_validation", "templates", "static/enhanced_system"]

        for directory in directories:
            dir_path = os.path.join(settings.BASE_DIR, directory)
            os.makedirs(dir_path, exist_ok=True)
            self.stdout.write(f"✓ Created directory: {directory}")

        # Check validation modules
        validation_modules = [
            "backtesting",
            "statistical_tests",
            "confidence_intervals",
            "adaptive_weights",
            "performance_monitor",
        ]

        missing_modules = []
        for module in validation_modules:
            try:
                __import__(f"ml_validation.{module}")
                self.stdout.write(f"✓ Validation module: {module}")
            except ImportError:
                missing_modules.append(module)
                self.stdout.write(self.style.WARNING(f"⚠ Missing module: {module}"))

        if missing_modules and not force:
            raise CommandError(
                f"Missing validation modules: {missing_modules}. "
                f"Use --force to proceed anyway."
            )

        self.stdout.write(self.style.SUCCESS("System setup completed!"))

    def initialize_system(self, force=False):
        """Initialize the enhanced prediction system with real data"""

        self.stdout.write("Initializing Enhanced Prediction System...")

        try:
            import os
            import sys

            # Add project root to Python path
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from results.django_enhanced_system import (
                DjangoEnhancedPredictionSystem,
                ProductionConfig,
            )

            # Import enhanced_views with fallback
            try:
                from results.enhanced_views import reset_enhanced_system
            except ImportError:

                def reset_enhanced_system():
                    self.stdout.write("Reset function not available, skipping...")

            # Reset any existing system
            reset_enhanced_system()

            # Create new system instance
            config = ProductionConfig()
            system = DjangoEnhancedPredictionSystem(config)

            self.stdout.write("Initializing with real data...")
            system.initialize_with_real_data()

            # Get system health
            health_data = system._assess_system_health()

            self.stdout.write(f"System Health Score: {health_data['score']}/100")
            self.stdout.write(f"System Status: {health_data['status']}")

            if health_data["issues"]:
                self.stdout.write(self.style.WARNING("Issues found:"))
                for issue in health_data["issues"]:
                    self.stdout.write(f"  - {issue}")

            # Cleanup
            system.cleanup()

            self.stdout.write(self.style.SUCCESS("System initialization completed!"))

        except Exception as e:
            raise CommandError(f"Initialization failed: {e}")

    def show_status(self):
        """Show system status"""

        self.stdout.write("Enhanced Prediction System Status:")
        self.stdout.write("=" * 50)

        # Check Django models
        try:
            from results.models import (
                KetQuaXoSo,
                ModelTrainingHistory,
                PredictionPerformanceMetrics,
            )

            # Data statistics
            total_records = KetQuaXoSo.objects.count()
            recent_records = KetQuaXoSo.objects.filter(
                ngay__gte=datetime.now().date() - timedelta(days=30)
            ).count()

            self.stdout.write(f"Total lottery records: {total_records}")
            self.stdout.write(f"Recent records (30 days): {recent_records}")

            # Performance records
            total_predictions = PredictionPerformanceMetrics.objects.count()
            recent_predictions = PredictionPerformanceMetrics.objects.filter(
                prediction_date__gte=datetime.now().date() - timedelta(days=7)
            ).count()

            self.stdout.write(f"Total predictions made: {total_predictions}")
            self.stdout.write(f"Recent predictions (7 days): {recent_predictions}")

            # Model training records
            active_models = ModelTrainingHistory.objects.filter(is_active=True).count()
            total_models = ModelTrainingHistory.objects.count()

            self.stdout.write(f"Active models: {active_models}")
            self.stdout.write(f"Total models trained: {total_models}")

            # Recent performance
            if total_predictions > 0:
                recent_performance = PredictionPerformanceMetrics.objects.filter(
                    accuracy__gt=0
                ).order_by("-prediction_date")[:10]

                if recent_performance:
                    avg_accuracy = sum(p.accuracy for p in recent_performance) / len(
                        recent_performance
                    )
                    avg_hit_rate = sum(p.hit_rate for p in recent_performance) / len(
                        recent_performance
                    )

                    self.stdout.write(f"Recent average accuracy: {avg_accuracy:.3f}")
                    self.stdout.write(f"Recent average hit rate: {avg_hit_rate:.3f}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error retrieving status: {e}"))

        # System health check
        try:
            from results.django_enhanced_system import (
                DjangoEnhancedPredictionSystem,
                ProductionConfig,
            )

            config = ProductionConfig()
            system = DjangoEnhancedPredictionSystem(config)
            system.initialize_with_real_data()

            health_data = system._assess_system_health()

            self.stdout.write("\nSystem Health:")
            self.stdout.write(f'Score: {health_data["score"]}/100')
            self.stdout.write(f'Status: {health_data["status"]}')

            if health_data["issues"]:
                self.stdout.write("Issues:")
                for issue in health_data["issues"]:
                    self.stdout.write(f"  - {issue}")

            system.cleanup()

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Health check failed: {e}"))

    def reset_system(self, force=False):
        """Reset the enhanced prediction system"""

        if not force:
            confirm = input("This will reset all system data. Continue? (y/N): ")
            if confirm.lower() != "y":
                self.stdout.write("Reset cancelled.")
                return

        self.stdout.write("Resetting Enhanced Prediction System...")

        try:
            from results.enhanced_views import reset_enhanced_system
            from results.models import (
                ModelTrainingHistory,
                PredictionPerformanceMetrics,
            )

            # Reset system instance
            reset_enhanced_system()

            # Optional: Clear prediction records
            with transaction.atomic():
                deleted_predictions = (
                    PredictionPerformanceMetrics.objects.all().delete()
                )
                deleted_models = ModelTrainingHistory.objects.all().delete()

                self.stdout.write(
                    f"Deleted {deleted_predictions[0]} prediction records"
                )
                self.stdout.write(f"Deleted {deleted_models[0]} model training records")

            self.stdout.write(self.style.SUCCESS("System reset completed!"))

        except Exception as e:
            raise CommandError(f"Reset failed: {e}")

    def backup_system(self):
        """Backup system data"""

        self.stdout.write("Creating system backup...")

        try:
            import json

            from results.models import (
                ModelTrainingHistory,
                PredictionPerformanceMetrics,
            )

            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "predictions": [],
                "models": [],
            }

            # Backup predictions
            for prediction in PredictionPerformanceMetrics.objects.all():
                backup_data["predictions"].append(
                    {
                        "id": prediction.id,
                        "prediction_date": prediction.prediction_date.isoformat(),
                        "predicted_numbers": prediction.predicted_numbers,
                        "actual_numbers": prediction.actual_numbers,
                        "accuracy": prediction.accuracy,
                        "hit_rate": prediction.hit_rate,
                    }
                )

            # Backup models
            for model in ModelTrainingHistory.objects.all():
                backup_data["models"].append(
                    {
                        "id": model.id,
                        "model_id": model.model_id,
                        "model_type": model.model_type,
                        "version": model.version,
                        "training_date": model.training_date.isoformat(),
                        "is_active": model.is_active,
                    }
                )

            # Save backup
            backup_filename = f'enhanced_system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(backup_filename, "w") as f:
                json.dump(backup_data, f, indent=2)

            self.stdout.write(self.style.SUCCESS(f"Backup saved to: {backup_filename}"))

        except Exception as e:
            raise CommandError(f"Backup failed: {e}")

    def validate_system(self):
        """Validate system integrity"""

        self.stdout.write("Validating Enhanced Prediction System...")

        validation_results = []

        # Check Django setup
        try:
            import django

            validation_results.append(
                ("Django Setup", True, f"Django {django.get_version()}")
            )
        except Exception as e:
            validation_results.append(("Django Setup", False, str(e)))

        # Check models
        try:
            from results.models import (
                KetQuaXoSo,
                ModelTrainingHistory,
                PredictionPerformanceMetrics,
            )

            # Test model access
            KetQuaXoSo.objects.count()
            validation_results.append(("Django Models", True, "All models accessible"))
        except Exception as e:
            validation_results.append(("Django Models", False, str(e)))

        # Check validation modules
        validation_modules = [
            "backtesting",
            "statistical_tests",
            "confidence_intervals",
            "adaptive_weights",
            "performance_monitor",
        ]

        for module in validation_modules:
            try:
                __import__(f"ml_validation.{module}")
                validation_results.append((f"Module {module}", True, "Available"))
            except ImportError:
                validation_results.append((f"Module {module}", False, "Missing"))

        # Check system initialization
        try:
            import os
            import sys

            # Add project root to Python path
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from results.django_enhanced_system import (
                DjangoEnhancedPredictionSystem,
                ProductionConfig,
            )

            config = ProductionConfig()
            system = DjangoEnhancedPredictionSystem(config)
            system.initialize_with_real_data()

            health_data = system._assess_system_health()
            system.cleanup()

            validation_results.append(
                (
                    "System Health",
                    True,
                    f'{health_data["status"]} ({health_data["score"]}/100)',
                )
            )

        except Exception as e:
            validation_results.append(("System Health", False, str(e)))

        # Display results
        self.stdout.write("\nValidation Results:")
        self.stdout.write("=" * 50)

        for component, status, details in validation_results:
            status_symbol = "✓" if status else "✗"
            status_color = self.style.SUCCESS if status else self.style.ERROR

            self.stdout.write(f"{status_symbol} {component}: {status_color(details)}")

        # Summary
        passed = sum(1 for _, status, _ in validation_results if status)
        total = len(validation_results)

        self.stdout.write(f"\nValidation Summary: {passed}/{total} checks passed")

        if passed == total:
            self.stdout.write(self.style.SUCCESS("✓ All validations passed!"))
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠ {total - passed} validation(s) failed")
            )
