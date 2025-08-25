#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALYTIC FREQUENCE APPS: Django App Configuration
Configures the advanced frequency analysis Django app
"""

from django.apps import AppConfig


class AnalyticFrequenceConfig(AppConfig):
    """Configuration for the analytic_frequence Django app"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "analytic_frequence"
    verbose_name = "Advanced Frequency Analysis"

    def ready(self):
        """Initialize app components when Django starts"""
        # Import signals if any
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass

        # Initialize logging
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"🎯 {self.verbose_name} app initialized successfully")

        # Validate app features
        try:
            from . import FEATURES

            enabled_features = [name for name, enabled in FEATURES.items() if enabled]
            logger.info(f"📊 Enabled features: {', '.join(enabled_features)}")
        except ImportError:
            logger.debug("No features configuration found")

        # Check for required dependencies
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required dependencies are available"""
        import logging

        logger = logging.getLogger(__name__)

        dependencies = {
            "rest_framework": "Django REST Framework",
            "django.contrib.contenttypes": "Django Content Types",
            "django.contrib.auth": "Django Authentication",
        }

        missing_deps = []
        for dep_module, dep_name in dependencies.items():
            try:
                __import__(dep_module)
                logger.debug(f"✅ {dep_name} available")
            except ImportError:
                missing_deps.append(dep_name)
                logger.warning(f"❌ {dep_name} not available")

        if missing_deps:
            logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
        else:
            logger.info("✅ All required dependencies are available")
