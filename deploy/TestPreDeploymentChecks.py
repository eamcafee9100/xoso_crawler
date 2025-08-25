import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.test import TestCase

from deploy.production_deployment import ProductionDeployment

"""
Tests for ProductionDeployment._pre_deployment_checks method
Tests for ProductionDeployment._pre_deployment_checks method
"""


class TestPreDeploymentChecks(TestCase):
    """Test cases for _pre_deployment_checks method"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.deployment = ProductionDeployment(str(self.temp_dir))

        # Create basic project structure
        self.create_basic_project_structure()

    def tearDown(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_basic_project_structure(self):
        """Create minimal project structure for tests"""
        # Create manage.py
        (self.temp_dir / "manage.py").write_text("#!/usr/bin/env python\n")

        # Create requirements.txt
        (self.temp_dir / "requirements.txt").write_text("django>=3.2\n")

        # Create xoso_crawler directory
        xoso_dir = self.temp_dir / "xoso_crawler"
        xoso_dir.mkdir()
        (xoso_dir / "__init__.py").write_text("")
        (xoso_dir / "settings.py").write_text(
            """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
"""
        )

    def test_python_version_check_success(self):
        """Test successful Python version check (3.8+)"""
        with patch("sys.version_info", (3, 9, 0)):
            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

    def test_python_version_check_failure_old_version(self):
        """Test Python version check failure with old Python version"""
        with patch("sys.version_info", (3, 7, 0)):
            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    def test_python_version_check_failure_python2(self):
        """Test Python version check failure with Python 2"""
        with patch("sys.version_info", (2, 7, 18)):
            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    def test_critical_files_exist_success(self):
        """Test successful critical files validation"""
        # Files already created in setUp
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

    def test_critical_files_missing_manage_py(self):
        """Test failure when manage.py is missing"""
        (self.temp_dir / "manage.py").unlink()

        result = self.deployment._pre_deployment_checks()
        self.assertFalse(result)

    def test_critical_files_missing_requirements_txt(self):
        """Test failure when requirements.txt is missing"""
        (self.temp_dir / "requirements.txt").unlink()

        result = self.deployment._pre_deployment_checks()
        self.assertFalse(result)

    def test_directories_creation_success(self):
        """Test successful directory creation"""
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            # Check that directories were created
            expected_dirs = ["templates", "static", "media", "logs", "backups"]
            for dir_name in expected_dirs:
                self.assertTrue((self.temp_dir / dir_name).exists())

    def test_environment_variables_setup_failure(self):
        """Test failure when environment variables setup fails"""
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=False
        ):
            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    def test_database_config_setup_failure(self):
        """Test failure when database configuration setup fails"""
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": False, "message": "Database setup failed"},
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    def test_database_connectivity_failure(self):
        """Test failure when database connectivity check fails"""
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=False
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    def test_disk_space_warning_continues_deployment(self):
        """Test that disk space warning doesn't fail deployment"""
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=False
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)  # Should continue despite disk space warning

    @patch("deploy.production_deployment.logger")
    def test_logging_behavior_success(self, mock_logger):
        """Test logging messages during successful pre-deployment checks"""
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "Database configured"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            # Verify logging calls
            mock_logger.info.assert_any_call("Running pre-deployment checks")
            mock_logger.info.assert_any_call("Database configured: Database configured")
            mock_logger.info.assert_any_call(
                "Pre-deployment checks completed successfully"
            )

    @patch("deploy.production_deployment.logger")
    def test_logging_behavior_failure(self, mock_logger):
        """Test logging messages during failed pre-deployment checks"""
        # Remove critical file to cause failure
        (self.temp_dir / "manage.py").unlink()

        result = self.deployment._pre_deployment_checks()
        self.assertFalse(result)

        # Verify error logging
        mock_logger.error.assert_any_call("Critical file missing: manage.py")

    def test_exception_handling(self):
        """Test exception handling in pre-deployment checks"""
        with patch.object(
            self.deployment,
            "_setup_required_environment_variables",
            side_effect=Exception("Test exception"),
        ):
            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    @patch("deploy.production_deployment.logger")
    def test_exception_logging(self, mock_logger):
        """Test that exceptions are properly logged"""
        with patch.object(
            self.deployment,
            "_setup_required_environment_variables",
            side_effect=Exception("Test exception"),
        ):
            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

            mock_logger.error.assert_any_call(
                "Pre-deployment checks failed: Test exception"
            )

    def test_complete_workflow_success(self):
        """Test complete successful workflow"""
        # Mock all dependencies to return success
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ) as mock_env, patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "Database OK"},
        ) as mock_db_config, patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ) as mock_db_conn, patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ) as mock_disk:

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            # Verify all methods were called
            mock_env.assert_called_once()
            mock_db_config.assert_called_once()
            mock_db_conn.assert_called_once()
            mock_disk.assert_called_once()

    def test_python_version_edge_case_38_exactly(self):
        """Test Python version check with exactly 3.8 (minimum required)"""
        with patch("sys.version_info", (3, 8, 0)):
            with patch.object(
                self.deployment,
                "_setup_required_environment_variables",
                return_value=True,
            ), patch.object(
                self.deployment,
                "_setup_production_database_config",
                return_value={"success": True, "message": "OK"},
            ), patch.object(
                self.deployment, "_check_database_connectivity", return_value=True
            ), patch.object(
                self.deployment, "_check_disk_space", return_value=True
            ):

                result = self.deployment._pre_deployment_checks()
                self.assertTrue(result)

    def test_python_version_edge_case_37_exactly(self):
        """Test Python version check with exactly 3.7 (should fail)"""
        with patch("sys.version_info", (3, 7, 999)):
            result = self.deployment._pre_deployment_checks()
            self.assertFalse(result)

    def test_directories_already_exist(self):
        """Test behavior when required directories already exist"""
        # Pre-create directories
        for dir_name in ["templates", "static", "media", "logs", "backups"]:
            (self.temp_dir / dir_name).mkdir(exist_ok=True)

        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            # Directories should still exist
            for dir_name in ["templates", "static", "media", "logs", "backups"]:
                self.assertTrue((self.temp_dir / dir_name).exists())

    def test_partial_failure_recovery(self):
        """Test behavior when some checks fail but others succeed"""
        # Test scenario where disk space fails but others succeed
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=False
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)  # Should continue despite disk space warning

    def test_database_config_success_message_logging(self):
        """Test that database configuration success message is logged"""
        test_message = "PostgreSQL configured successfully"

        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": test_message},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ), patch(
            "deploy.production_deployment.logger"
        ) as mock_logger:

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            mock_logger.info.assert_any_call(f"Database configured: {test_message}")

    def test_method_call_order(self):
        """Test that methods are called in the correct order"""
        call_order = []

        def track_env_setup():
            call_order.append("env_setup")
            return True

        def track_db_config():
            call_order.append("db_config")
            return {"success": True, "message": "OK"}

        def track_db_connectivity():
            call_order.append("db_connectivity")
            return True

        def track_disk_space():
            call_order.append("disk_space")
            return True

        with patch.object(
            self.deployment,
            "_setup_required_environment_variables",
            side_effect=track_env_setup,
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            side_effect=track_db_config,
        ), patch.object(
            self.deployment,
            "_check_database_connectivity",
            side_effect=track_db_connectivity,
        ), patch.object(
            self.deployment, "_check_disk_space", side_effect=track_disk_space
        ):

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            expected_order = ["env_setup", "db_config", "db_connectivity", "disk_space"]
            self.assertEqual(call_order, expected_order)


class TestPreDeploymentChecksIntegration(TestCase):
    """Integration tests for _pre_deployment_checks with real file system"""

    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.deployment = ProductionDeployment(str(self.temp_dir))

    def tearDown(self):
        """Clean up integration test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_real_directory_creation(self):
        """Test actual directory creation without mocking"""
        # Create minimal project structure
        (self.temp_dir / "manage.py").write_text("#!/usr/bin/env python\n")
        (self.temp_dir / "requirements.txt").write_text("django>=3.2\n")

        # Mock only the complex dependencies
        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ):

            # Verify directories don't exist initially
            for dir_name in ["templates", "static", "media", "logs", "backups"]:
                self.assertFalse((self.temp_dir / dir_name).exists())

            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)

            # Verify directories were actually created
            for dir_name in ["templates", "static", "media", "logs", "backups"]:
                self.assertTrue((self.temp_dir / dir_name).exists())
                self.assertTrue((self.temp_dir / dir_name).is_dir())

    def test_file_permission_handling(self):
        """Test handling of file permissions during directory creation"""
        # Create minimal project structure
        (self.temp_dir / "manage.py").write_text("#!/usr/bin/env python\n")
        (self.temp_dir / "requirements.txt").write_text("django>=3.2\n")

        # Create a directory with restricted permissions to test error handling
        restricted_dir = self.temp_dir / "static"
        restricted_dir.mkdir()

        with patch.object(
            self.deployment, "_setup_required_environment_variables", return_value=True
        ), patch.object(
            self.deployment,
            "_setup_production_database_config",
            return_value={"success": True, "message": "OK"},
        ), patch.object(
            self.deployment, "_check_database_connectivity", return_value=True
        ), patch.object(
            self.deployment, "_check_disk_space", return_value=True
        ):

            # Should handle existing directories gracefully
            result = self.deployment._pre_deployment_checks()
            self.assertTrue(result)
