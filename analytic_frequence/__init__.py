#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALYTIC FREQUENCE APP: Advanced Frequency Analysis
Django app for quantum-inspired lottery frequency analysis with AI integration
"""

default_app_config = "analytic_frequence.apps.AnalyticFrequenceConfig"

__version__ = "1.0.0"
__author__ = "Enhanced Frequency Analysis System"
__email__ = "analytics@xoso.local"

# App metadata
APP_NAME = "analytic_frequence"
APP_VERBOSE_NAME = "Advanced Frequency Analysis"
APP_DESCRIPTION = "Quantum-inspired lottery frequency analysis with AI integration"

# Feature flags
FEATURES = {
    "quantum_processing": True,
    "neural_recognition": True,
    "quantum_optimization": True,
    "meta_learning": True,
    "advanced_analysis": True,
    "prediction_validation": True,
    "visualization": True,
    "system_health": True,
}

# Version info
VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "release": "stable",
    "build": "20250811",
}


def get_version():
    """Get formatted version string"""
    return f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"


def get_full_version():
    """Get full version string with build info"""
    base_version = get_version()
    if VERSION_INFO["release"] != "stable":
        base_version += f"-{VERSION_INFO['release']}"
    return f"{base_version}+{VERSION_INFO['build']}"


# Export key components
__all__ = [
    "APP_NAME",
    "APP_VERBOSE_NAME",
    "APP_DESCRIPTION",
    "FEATURES",
    "VERSION_INFO",
    "get_version",
    "get_full_version",
]
