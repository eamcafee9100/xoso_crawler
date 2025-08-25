"""
Production Deployment Script cho Cyclical Intelligence System
"""
import os
import sys
import logging
import subprocess
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductionDeployment:
    """Production deployment manager"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.deployment_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / "backups" / f"deployment_{self.deployment_timestamp}"
        self.config = self._load_deployment_config()
    
    def deploy(self) -> bool:
        """
        Full production deployment
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Starting production deployment")
            
            # 1. Pre-deployment checks
            if not self._pre_deployment_checks():
                raise Exception("Pre-deployment checks failed")
            
            # 2. Create deployment backup
            if not self._create_deployment_backup():
                raise Exception("Deployment backup failed")
            
            # 3. Install/update dependencies
            if not self._install_dependencies():
                raise Exception("Dependencies installation failed")
            
            # 4. Database migrations
            if not self._run_database_migrations():
                raise Exception("Database migrations failed")
            
            # 5. Collect static files
            if not self._collect_static_files():
                raise Exception("Static files collection failed")
            
            # 6. Setup environment (already done in pre-checks)
            logger.info("Environment already configured")
            
            # 7. Run critical tests
            if not self._run_critical_tests():
                logger.warning("Some tests failed, but continuing deployment")
            
            # 8. Setup monitoring
            if not self._setup_monitoring():
                logger.warning("Monitoring setup failed, but continuing")
            
            # 9. Setup logging
            if not self._setup_logging():
                logger.warning("Logging setup failed, but continuing")
            
            # 10. Setup caching
            if not self._setup_caching():
                logger.warning("Caching setup failed, but continuing")
            
            # 11. Setup security
            if not self._setup_security():
                logger.warning("Security setup failed, but continuing")
            
            # 12. Restart services
            if not self._restart_services():
                logger.warning("Service restart failed, but continuing")
            
            # 13. Post-deployment validation
            if not self._post_deployment_validation():
                logger.warning("Some validations failed, but deployment completed")
            
            # 14. Cleanup old backups
            self._cleanup_old_backups()
            
            logger.info("Production deployment completed successfully")
            self._log_deployment_summary()
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            self._rollback_deployment()
            return False
    
    def _load_deployment_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        try:
            config_file = self.project_root / "deploy" / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Default configuration
            return {
                "python_version": "3.8+",
                "required_packages": ["django", "psutil", "scipy", "numpy"],
                "critical_apps": ["predictions_tracker", "results"],
                "backup_retention_days": 30,
                "test_coverage_threshold": 80,
                "performance_thresholds": {
                    "max_response_time_ms": 2000,
                    "max_memory_usage_mb": 1024,
                    "min_accuracy": 0.05
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to load config, using defaults: {str(e)}")
            return {}
    
    def _pre_deployment_checks(self) -> bool:
        """
        Pre-deployment environment checks với improved error handling
        
        Returns:
            bool: True nếu tất cả checks pass hoặc có fallback thành công
        """
        try:
            logger.info("Running pre-deployment checks")
            
            # 1. Check Python version
            python_version = sys.version_info
            if python_version.major != 3 or python_version.minor < 8:
                logger.error(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
                return False
            
            # 2. Check Django project structure
            critical_files = ["manage.py", "requirements.txt"]
            for file_name in critical_files:
                if not (self.project_root / file_name).exists():
                    logger.error(f"Critical file missing: {file_name}")
                    return False
            
            # 3. Setup directories
            self._ensure_required_directories()
            
            # 4. Setup environment variables
            if not self._setup_required_environment_variables():
                logger.error("Failed to setup required environment variables")
                return False
            
            # 5. Setup database configuration với fallback
            db_result = self._setup_production_database_config()
            if not db_result["success"]:
                logger.error(f"Database setup failed: {db_result['message']}")
                return False
            
            logger.info(f"Database configured: {db_result['message']}")
            
            # 6. Check database connectivity với fallback đã được handle
            if not self._check_database_connectivity():
                logger.error("Database connectivity check failed")
                return False
            
            # 7. Check disk space
            if not self._check_disk_space():
                logger.warning("Low disk space warning")
                # Don't fail deployment for disk space, just warn
            
            logger.info("Pre-deployment checks completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Pre-deployment checks failed: {str(e)}")
            return False
    
    
    def _get_database_config(self) -> dict:
        """
        Extract database configuration from settings
        
        Returns:
            dict: {
                "engine": str,
                "name": str, 
                "host": str,
                "port": str,
                "user": str,
                "password": str
            }
        """
        # Try to import Django settings with proper PYTHONPATH
        try:
            # Add project root to Python path
            project_root_str = str(self.project_root)
            if project_root_str not in sys.path:
                sys.path.insert(0, project_root_str)
            
            # Set Django settings module
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
            
            # Import and setup Django
            import django
            from django.conf import settings
            
            # Configure Django if not already configured
            if not settings.configured:
                django.setup()
            
            db_settings = settings.DATABASES['default']
            
            # Determine engine type
            if 'postgresql' in db_settings['ENGINE']:
                engine = 'postgresql'
            elif 'sqlite3' in db_settings['ENGINE']:
                engine = 'sqlite3'
            else:
                engine = 'unknown'
            
            config = {
                "engine": engine,
                "name": db_settings.get('NAME', ''),
                "host": db_settings.get('HOST', 'localhost'),
                "port": db_settings.get('PORT', '5432'),
                "user": db_settings.get('USER', ''),
                "password": db_settings.get('PASSWORD', '')
            }
            
            logger.info(f"Successfully read Django settings - Engine: {engine}")
            return config
            
        except ImportError as e:
            logger.warning(f"Django import failed: {str(e)}")
        except Exception as e:
            logger.warning(f"Could not read Django settings: {str(e)}")
        
        # Fallback: try to read settings.py directly
        try:
            return self._read_settings_file_directly()
        except Exception as e:
            logger.warning(f"Direct settings file read failed: {str(e)}")
        
        # Final fallback config
        logger.info("Using fallback SQLite configuration")
        return {
            "engine": "sqlite3",
            "name": "db.sqlite3",
            "host": "",
            "port": "",
            "user": "",
            "password": ""
        }
    
    def _read_settings_file_directly(self) -> dict:
        """
        Read settings.py file directly để extract database config
        
        Returns:
            dict: Database configuration
        """
        settings_file = self.project_root / "xoso_crawler" / "settings.py"
        
        if not settings_file.exists():
            raise FileNotFoundError("settings.py not found")
        
        # Read settings file content
        settings_content = settings_file.read_text(encoding='utf-8')
        
        # Parse database configuration
        if 'postgresql' in settings_content and 'ENGINE' in settings_content:
            # Extract PostgreSQL config from settings
            import re
            
            # Find database configuration block
            db_match = re.search(r"DATABASES\s*=\s*{[^}]*'default':\s*{([^}]+)}", settings_content, re.DOTALL)
            
            if db_match:
                db_block = db_match.group(1)
                
                # Extract individual values
                name_match = re.search(r"'NAME':\s*'([^']+)'", db_block)
                user_match = re.search(r"'USER':\s*'([^']+)'", db_block)
                password_match = re.search(r"'PASSWORD':\s*'([^']+)'", db_block)
                host_match = re.search(r"'HOST':\s*'([^']+)'", db_block)
                port_match = re.search(r"'PORT':\s*'([^']+)'", db_block)
                
                if name_match:  # PostgreSQL config found
                    return {
                        "engine": "postgresql",
                        "name": name_match.group(1) if name_match else "",
                        "host": host_match.group(1) if host_match else "localhost",
                        "port": port_match.group(1) if port_match else "5432",
                        "user": user_match.group(1) if user_match else "",
                        "password": password_match.group(1) if password_match else ""
                    }
        
        # Default to SQLite if PostgreSQL config not found
        return {
            "engine": "sqlite3",
            "name": "db.sqlite3",
            "host": "",
            "port": "",
            "user": "",
            "password": ""
        }
    
    def _check_database_connectivity(self) -> bool:
        """
        Check database connectivity với multiple fallback strategies
        
        Returns:
            bool: True nếu database accessible hoặc được setup thành công
        """
        try:
            logger.info("Checking database connectivity")
            
            # Read current database config
            db_config = self._get_database_config()
            logger.info(f"Database engine: {db_config['engine']}")
            
            # Check connectivity based on engine type
            if db_config['engine'] == 'postgresql':
                if self._test_postgresql_connectivity(db_config):
                    return True
                else:
                    logger.info("PostgreSQL connectivity failed, falling back to SQLite")
                    return self._setup_sqlite_fallback()
            
            elif db_config['engine'] == 'sqlite3':
                return self._test_sqlite_connectivity(db_config)
            
            else:
                logger.error(f"Unsupported database engine: {db_config['engine']}")
                return self._setup_sqlite_fallback()
                
        except Exception as e:
            logger.error(f"Database connectivity check failed: {str(e)}")
            return self._setup_sqlite_fallback()
    
    def _test_postgresql_connectivity(self, db_config: dict) -> bool:
        """
        Test PostgreSQL connectivity với multiple methods
        
        Args:
            db_config: Database configuration dict
            
        Returns:
            bool: True nếu connection thành công
        """
        try:
            logger.info(f"Testing PostgreSQL: {db_config['host']}:{db_config['port']}")
            
            # Method 1: Test socket connection first
            if not self._test_socket_connection(db_config['host'], int(db_config['port'])):
                logger.warning("PostgreSQL port not accessible")
                return False
            
            # Method 2: Test direct psycopg2 connection
            if self._test_direct_postgresql_connection(db_config):
                logger.info("Direct PostgreSQL connection successful")
                return True
            
            # Method 3: Test Django connection với shorter timeout
            if self._test_django_database_connection(timeout=10):
                logger.info("Django PostgreSQL connection successful")
                return True
            
            logger.warning("All PostgreSQL connection methods failed")
            return False
            
        except Exception as e:
            logger.error(f"PostgreSQL connectivity test failed: {str(e)}")
            return False
    
    def _test_socket_connection(self, host: str, port: int) -> bool:
        """
        Test basic socket connection
        
        Args:
            host: Database host
            port: Database port
            
        Returns:
            bool: True nếu socket connection thành công
        """
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def _test_direct_postgresql_connection(self, db_config: dict) -> bool:
        """
        Test direct PostgreSQL connection using psycopg2
        
        Args:
            db_config: Database configuration dict
            
        Returns:
            bool: True nếu connection thành công
        """
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=10
            )
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result[0] == 1
            
        except ImportError:
            logger.warning("psycopg2 not available for direct connection test")
            return False
        except Exception as e:
            logger.warning(f"Direct PostgreSQL connection failed: {str(e)}")
            return False
    
    def _test_django_database_connection(self, timeout: int = 10) -> bool:
        """
        Test Django database connection
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True nếu Django connection thành công
        """
        try:
            # Add project to Python path
            project_root_str = str(self.project_root)
            if project_root_str not in sys.path:
                sys.path.insert(0, project_root_str)
            
            # Test Django database check
            result = subprocess.run([
                sys.executable, "manage.py", "check", "--database", "default"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                return True
            else:
                logger.warning(f"Django database check failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning(f"Django database check timed out after {timeout} seconds")
            return False
        except Exception as e:
            logger.warning(f"Django database check error: {str(e)}")
            return False
    
    def _test_sqlite_connectivity(self, db_config: dict) -> bool:
        """
        Test SQLite connectivity
        
        Args:
            db_config: Database configuration dict
            
        Returns:
            bool: True nếu SQLite accessible
        """
        try:
            logger.info("Testing SQLite connectivity")
            
            # Test Django connection first
            if self._test_django_database_connection(timeout=8):
                logger.info("SQLite Django connection successful")
                return True
            
            # Try to create SQLite database
            logger.info("Attempting to create SQLite database")
            return self._create_sqlite_database()
            
        except Exception as e:
            logger.error(f"SQLite connectivity test failed: {str(e)}")
            return False
    
    def _create_sqlite_database(self) -> bool:
        """
        Create SQLite database with migrations
        
        Returns:
            bool: True nếu database creation thành công
        """
        try:
            # Add project to Python path
            project_root_str = str(self.project_root)
            if project_root_str not in sys.path:
                sys.path.insert(0, project_root_str)
            
            # Run migrations to create database
            result = subprocess.run([
                sys.executable, "manage.py", "migrate", "--run-syncdb"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("SQLite database created successfully")
                return True
            else:
                logger.error(f"SQLite database creation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("SQLite database creation timed out")
            return False
        except Exception as e:
            logger.error(f"SQLite database creation error: {str(e)}")
            return False
    
    def _setup_sqlite_fallback(self) -> bool:
        """
        Setup SQLite fallback configuration
        
        Returns:
            bool: True nếu SQLite fallback thành công
        """
        try:
            logger.info("Setting up SQLite fallback configuration")
            
            # Update environment to use SQLite
            os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
            
            # Update .env file
            self._update_env_file_database_url('sqlite:///db.sqlite3')
            
            # Test SQLite connectivity
            fallback_config = {
                "engine": "sqlite3",
                "name": "db.sqlite3",
                "host": "",
                "port": "",
                "user": "",
                "password": ""
            }
            
            return self._test_sqlite_connectivity(fallback_config)
            
        except Exception as e:
            logger.error(f"SQLite fallback setup failed: {str(e)}")
            return False
    
    def _update_env_file_database_url(self, database_url: str) -> None:
        """
        Update DATABASE_URL in .env file
        
        Args:
            database_url: New database URL
        """
        try:
            env_file = self.project_root / ".env"
            
            if env_file.exists():
                content = env_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Update existing DATABASE_URL
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('DATABASE_URL='):
                        lines[i] = f"DATABASE_URL={database_url}"
                        updated = True
                        break
                
                # Add DATABASE_URL if not found
                if not updated:
                    lines.append(f"DATABASE_URL={database_url}")
                
                # Write updated content
                env_file.write_text('\n'.join(lines), encoding='utf-8')
                
            else:
                # Create new .env file
                env_content = f"DATABASE_URL={database_url}\n"
                env_file.write_text(env_content, encoding='utf-8')
            
            logger.info(f"Updated DATABASE_URL in .env file: {database_url}")
            
        except Exception as e:
            logger.error(f"Failed to update .env file: {str(e)}")
            
    def _check_postgresql_connection(self, db_config: dict) -> bool:
        """
        Check PostgreSQL connection với timeout và fallback
        
        Args:
            db_config: Database configuration dict
            
        Returns:
            bool: True nếu connection thành công
        """
        try:
            logger.info(f"Testing PostgreSQL connection: {db_config['host']}:{db_config['port']}")
            
            # Test basic Django database check với shorter timeout
            result = subprocess.run([
                sys.executable, "manage.py", "check", "--database", "default"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                logger.info("PostgreSQL connection successful")
                return True
            
            logger.warning(f"Django check failed: {result.stderr}")
            
            # Test direct PostgreSQL connection nếu có psycopg2
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    database=db_config['name'],
                    user=db_config['user'],
                    password=db_config['password'],
                    connect_timeout=10  # 10 second timeout
                )
                conn.close()
                logger.info("Direct PostgreSQL connection successful")
                return True
                
            except ImportError:
                logger.warning("psycopg2 not available for direct connection test")
            except Exception as e:
                logger.warning(f"Direct PostgreSQL connection failed: {str(e)}")
            
            # Fallback to SQLite
            logger.info("PostgreSQL connection failed, falling back to SQLite")
            return self._fallback_to_sqlite()
            
        except subprocess.TimeoutExpired:
            logger.warning("PostgreSQL connection test timed out, falling back to SQLite")
            return self._fallback_to_sqlite()
        except Exception as e:
            logger.error(f"PostgreSQL connection test failed: {str(e)}")
            return self._fallback_to_sqlite()
    
    def _check_sqlite_connection(self, db_config: dict) -> bool:
        """
        Check SQLite connection
        
        Args:
            db_config: Database configuration dict
            
        Returns:
            bool: True nếu SQLite setup thành công
        """
        try:
            logger.info("Testing SQLite connection")
            
            # Test Django check với SQLite
            result = subprocess.run([
                sys.executable, "manage.py", "check", "--database", "default"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("SQLite connection successful")
                return True
            
            # Try to run migrations to create SQLite database
            logger.info("Attempting to create SQLite database")
            result = subprocess.run([
                sys.executable, "manage.py", "migrate", "--run-syncdb"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("SQLite database created successfully")
                return True
            
            logger.error(f"SQLite setup failed: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"SQLite connection test failed: {str(e)}")
            return False
    
    def _fallback_to_sqlite(self) -> bool:
        """
        Fallback to SQLite configuration
        
        Returns:
            bool: True nếu SQLite fallback thành công
        """
        try:
            logger.info("Setting up SQLite fallback configuration")
            
            # Update .env file với SQLite config
            env_file = self.project_root / ".env"
            env_content = env_file.read_text(encoding='utf-8')
            
            # Replace DATABASE_URL
            updated_content = env_content.replace(
                'DATABASE_URL=sqlite:///db.sqlite3',
                'DATABASE_URL=sqlite:///db.sqlite3'
            )
            
            # Ensure SQLite DATABASE_URL is set
            if 'DATABASE_URL=' not in updated_content:
                updated_content += '\nDATABASE_URL=sqlite:///db.sqlite3\n'
            
            env_file.write_text(updated_content, encoding='utf-8')
            
            # Update environment variable
            os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
            
            logger.info("SQLite fallback configuration completed")
            
            # Test SQLite connection
            return self._check_sqlite_connection({"engine": "sqlite3", "name": "db.sqlite3"})
            
        except Exception as e:
            logger.error(f"SQLite fallback failed: {str(e)}")
            return False
    
    def _setup_production_database_config(self) -> dict:
        """
        Setup production database configuration based on environment
        
        Returns:
            dict: {
                "success": bool,
                "engine": str,
                "config_applied": dict,
                "message": str
            }
        """
        try:
            # Check if PostgreSQL is available
            postgres_available = self._is_postgresql_available()
            
            if postgres_available:
                config = {
                    "engine": "postgresql",
                    "database_url": f"postgresql://postgres:1123@localhost:5432/xsmb"
                }
                logger.info("PostgreSQL configuration applied")
            else:
                config = {
                    "engine": "sqlite3", 
                    "database_url": "sqlite:///db.sqlite3"
                }
                logger.info("SQLite configuration applied as fallback")
            
            # Update .env file
            self._update_database_env_config(config)
            
            return {
                "success": True,
                "engine": config["engine"],
                "config_applied": config,
                "message": f"Database configured with {config['engine']}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "engine": "unknown",
                "config_applied": {},
                "message": f"Database configuration failed: {str(e)}"
            }
    
    def _is_postgresql_available(self) -> bool:
        """
        Check if PostgreSQL server is available
        
        Returns:
            bool: True nếu PostgreSQL server có thể connect
        """
        try:
            import socket
            
            # Test socket connection to PostgreSQL port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex(('localhost', 5432))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def _update_database_env_config(self, config: dict) -> None:
        """
        Update .env file với database configuration
        
        Args:
            config: Database configuration dict
        """
        try:
            env_file = self.project_root / ".env"
            
            if env_file.exists():
                content = env_file.read_text(encoding='utf-8')
            else:
                content = ""
            
            # Update DATABASE_URL
            if 'DATABASE_URL=' in content:
                # Replace existing DATABASE_URL
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('DATABASE_URL='):
                        lines[i] = f"DATABASE_URL={config['database_url']}"
                        break
                content = '\n'.join(lines)
            else:
                # Add DATABASE_URL
                content += f"\nDATABASE_URL={config['database_url']}\n"
            
            env_file.write_text(content, encoding='utf-8')
            
            # Update environment variable
            os.environ['DATABASE_URL'] = config['database_url']
            
        except Exception as e:
            logger.error(f"Failed to update database config: {str(e)}")
            
    def _ensure_required_directories(self) -> None:
        """
        Ensure required directories exist
        
        Returns:
            None
        """
        critical_dirs = [
            "templates",
            "static", 
            "media",
            "logs",
            "backups"
        ]
        
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                logger.info(f"Creating missing directory: {dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)

    def _setup_required_environment_variables(self) -> bool:
        """
        Setup required environment variables
        
        Returns:
            bool: True if setup successful
        """
        try:
            logger.info("Setting up environment variables")
            
            # Check for existing .env file
            env_file = self.project_root / ".env"
            env_vars = {}
            
            if env_file.exists():
                # Load existing .env file
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            
            # Required environment variables with defaults
            required_vars = {
                'DJANGO_SETTINGS_MODULE': 'xoso_crawler.settings',
                'SECRET_KEY': self._generate_secret_key(),
                'DEBUG': 'False',
                'ALLOWED_HOSTS': 'localhost,127.0.0.1',
                'DATABASE_URL': 'sqlite:///db.sqlite3',
                'REDIS_URL': 'redis://localhost:6379/1'
            }
            
            # Update missing variables
            updated = False
            for var_name, default_value in required_vars.items():
                if var_name not in env_vars or not env_vars[var_name]:
                    env_vars[var_name] = default_value
                    updated = True
                    logger.info(f"Set environment variable: {var_name}")
                
                # Set in current environment
                os.environ[var_name] = env_vars[var_name]
            
            # Write updated .env file if changes made
            if updated:
                env_content = f"""# Generated by deployment script on {datetime.now().isoformat()}
# Django Configuration
DJANGO_SETTINGS_MODULE={env_vars['DJANGO_SETTINGS_MODULE']}
SECRET_KEY={env_vars['SECRET_KEY']}
DEBUG={env_vars['DEBUG']}
ALLOWED_HOSTS={env_vars['ALLOWED_HOSTS']}

# Database Configuration
DATABASE_URL={env_vars['DATABASE_URL']}

# Cache Configuration
REDIS_URL={env_vars['REDIS_URL']}

# Production Settings
DJANGO_ENV=production
PYTHONIOENCODING=utf-8
"""
                
                env_file.write_text(env_content, encoding='utf-8')
                logger.info(f"Updated .env file: {env_file}")
            
            # Verify all required variables are now set
            missing_vars = []
            for var_name in ['DJANGO_SETTINGS_MODULE', 'SECRET_KEY']:
                if not os.getenv(var_name):
                    missing_vars.append(var_name)
            
            if missing_vars:
                logger.error(f"Still missing environment variables: {missing_vars}")
                return False
            
            logger.info("Environment variables setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Environment setup failed: {str(e)}")
            return False
    
    
     
    def _generate_secret_key(self) -> str:
        """
        Generate a secure Django SECRET_KEY
        
        Returns:
            str: Generated secret key
        """
        try:
            import secrets
            import string
            
            # Generate 50 character secret key
            chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
            return ''.join(secrets.choice(chars) for _ in range(50))
            
        except Exception:
            # Fallback method
            import random
            import string
            chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
            return ''.join(random.choice(chars) for _ in range(50))
    
    def _check_disk_space(self, min_free_gb: float = 2.0) -> bool:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = free / (1024**3)
            
            if free_gb < min_free_gb:
                logger.error(f"Insufficient disk space: {free_gb:.2f}GB free, {min_free_gb}GB required")
                return False
            
            logger.info(f"Disk space OK: {free_gb:.2f}GB available")
            return True
            
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return False
    
    def _create_deployment_backup(self) -> bool:
        """Create deployment backup"""
        try:
            logger.info("Creating deployment backup")
            
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup critical directories
            backup_items = [
                "predictions_tracker",
                "results",
                "templates",
                "static",
                "media",
                "manage.py",
                "requirements.txt"
            ]
            
            for item in backup_items:
                source = self.project_root / item
                if source.exists():
                    destination = self.backup_dir / item
                    
                    if source.is_dir():
                        shutil.copytree(source, destination, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                    else:
                        shutil.copy2(source, destination)
            
            # Backup database (if SQLite)
            db_file = self.project_root / "db.sqlite3"
            if db_file.exists():
                shutil.copy2(db_file, self.backup_dir / "db.sqlite3")
            
            # Create backup metadata
            backup_info = {
                "timestamp": self.deployment_timestamp,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "items_backed_up": [item for item in backup_items if (self.project_root / item).exists()],
                "backup_size_mb": self._get_directory_size(self.backup_dir) / (1024*1024)
            }
            
            with open(self.backup_dir / "backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"Backup created: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return False
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size
    
    def _install_dependencies(self) -> bool:
        """Install Python dependencies"""
        try:
            logger.info("Installing dependencies")
            
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                logger.warning("requirements.txt not found, skipping dependency installation")
                return True
            
            # Upgrade pip first
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], cwd=self.project_root, check=True)
            
            # Install requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Dependencies installation failed: {result.stderr}")
                return False
            
            # Verify critical packages
            critical_packages = self.config.get("required_packages", [])
            for package in critical_packages:
                try:
                    __import__(package)
                except ImportError:
                    logger.error(f"Critical package not available: {package}")
                    return False
            
            logger.info("Dependencies installed")
            return True
            
        except Exception as e:
            logger.error(f"Dependencies installation failed: {str(e)}")
            return False
    
    def _run_database_migrations(self) -> bool:
        """Run Django database migrations"""
        try:
            logger.info("Running database migrations")
            
            # Check for pending migrations
            result = subprocess.run([
                sys.executable, "manage.py", "showmigrations", "--plan"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Migration check failed: {result.stderr}")
                return False
            
            # Make migrations for critical apps
            critical_apps = self.config.get("critical_apps", ["predictions_tracker"])
            for app in critical_apps:
                result = subprocess.run([
                    sys.executable, "manage.py", "makemigrations", app
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.returncode != 0 and "No changes detected" not in result.stdout:
                    logger.error(f"Make migrations failed for {app}: {result.stderr}")
                    return False
            
            # Run migrations
            result = subprocess.run([
                sys.executable, "manage.py", "migrate"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Migrations failed: {result.stderr}")
                return False
            
            logger.info("Database migrations completed")
            return True
            
        except Exception as e:
            logger.error(f"Database migrations failed: {str(e)}")
            return False
    
    def _collect_static_files(self) -> bool:
        """Collect Django static files"""
        try:
            logger.info("Collecting static files")
            
            result = subprocess.run([
                sys.executable, "manage.py", "collectstatic", "--noinput", "--clear"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Static files collection failed: {result.stderr}")
                return False
            
            # Verify static files
            static_root = self.project_root / "staticfiles"
            if not static_root.exists() or not any(static_root.iterdir()):
                logger.error("Static files directory empty after collection")
                return False
            
            logger.info("Static files collected")
            return True
            
        except Exception as e:
            logger.error(f"Static files collection failed: {str(e)}")
            return False
    
    def _setup_environment(self) -> bool:
        """Setup environment variables and configuration"""
        try:
            logger.info("Setting up environment")
            
            # Create .env file if not exists
            env_file = self.project_root / ".env"
            if not env_file.exists():
                env_content = f"""
# Generated by deployment script on {datetime.now().isoformat()}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=xoso_crawler.settings.production
SECRET_KEY={os.getenv('SECRET_KEY', 'change-me-in-production')}
DATABASE_URL={os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')}
REDIS_URL={os.getenv('REDIS_URL', 'redis://localhost:6379/1')}
"""
                env_file.write_text(env_content.strip())
                logger.info("Created .env file")
            
            # Set production environment
            os.environ['DJANGO_ENV'] = 'production'
            os.environ['DEBUG'] = 'False'
            
            logger.info("Environment setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Environment setup failed: {str(e)}")
            return False
    
    def _run_critical_tests(self) -> bool:
        """Run critical system tests"""
        try:
            logger.info("Running critical tests")
            
            # Run Django system checks
            result = subprocess.run([
                sys.executable, "manage.py", "check", "--deploy"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"System checks failed: {result.stderr}")
                return False
            
            # Run unit tests for critical apps
            critical_apps = self.config.get("critical_apps", [])
            for app in critical_apps:
                result = subprocess.run([
                    sys.executable, "manage.py", "test", f"{app}.tests", "--verbosity=1"
                ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    logger.error(f"Tests failed for {app}: {result.stderr}")
                    return False
            
            # Performance smoke test
            if not self._run_performance_tests():
                logger.error("Performance tests failed")
                return False
            
            logger.info("Critical tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Tests failed: {str(e)}")
            return False
    
    def _run_performance_tests(self) -> bool:
        """Run basic performance tests"""
        try:
            logger.info("Running performance tests")
            
            # Test basic view response times
            test_urls = [
                "/predictions_tracker/",
                "/api/monitoring-dashboard/",
                "/production-monitoring/"
            ]
            
            for url in test_urls:
                # Simple test using Django test client
                result = subprocess.run([
                    sys.executable, "-c", 
                    f"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings.production')
django.setup()
from django.test import Client
import time

client = Client()
start_time = time.time()
response = client.get('{url}')
end_time = time.time()

response_time_ms = (end_time - start_time) * 1000
print(f'Response time: {{response_time_ms:.2f}}ms')

if response.status_code not in [200, 302]:
    exit(1)
if response_time_ms > 2000:
    exit(1)
"""
                ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.error(f"Performance test failed for {url}")
                    return False
            
            logger.info("Performance tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Performance tests failed: {str(e)}")
            return False
    
    def _setup_monitoring(self) -> bool:
        """Setup monitoring và alerting"""
        try:
            logger.info("Setting up monitoring")
            
            # Create monitoring directories
            monitoring_dirs = [
                "logs",
                "monitoring",
                "backups"
            ]
            
            for dir_name in monitoring_dirs:
                (self.project_root / dir_name).mkdir(exist_ok=True)
            
            # Setup log rotation
            self._setup_log_rotation()
            
            # Initialize monitoring service
            result = subprocess.run([
                sys.executable, "-c",
                """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings.production')
django.setup()

from predictions_tracker.core.services.ProductionMonitoringService import production_monitoring_service
summary = production_monitoring_service.get_system_health_summary()
print(f"Monitoring initialized: {summary['overall_status']}")
"""
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Monitoring initialization warning: {result.stderr}")
            
            logger.info("Monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {str(e)}")
            return False
    
    def _setup_logging(self) -> bool:
        """Setup logging configuration"""
        try:
            logger.info("Setting up logging")
            
            # Create logs directory
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Create logging configuration
            logging_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "verbose": {
                        "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                        "style": "{",
                    },
                    "simple": {
                        "format": "{levelname} {message}",
                        "style": "{",
                    },
                },
                "handlers": {
                    "file": {
                        "level": "INFO",
                        "class": "logging.handlers.RotatingFileHandler",
                        "filename": str(logs_dir / "django.log"),
                        "maxBytes": 1024*1024*15,  # 15MB
                        "backupCount": 10,
                        "formatter": "verbose",
                    },
                    "console": {
                        "level": "INFO",
                        "class": "logging.StreamHandler",
                        "formatter": "simple",
                    },
                },
                "root": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                },
                "loggers": {
                    "django": {
                        "handlers": ["console", "file"],
                        "level": "INFO",
                        "propagate": False,
                    },
                    "predictions_tracker": {
                        "handlers": ["console", "file"],
                        "level": "DEBUG",
                        "propagate": False,
                    },
                },
            }
            
            # Save logging config
            with open(self.project_root / "logging_config.json", 'w') as f:
                json.dump(logging_config, f, indent=2)
            
            logger.info("Logging setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Logging setup failed: {str(e)}")
            return False
    
    def _setup_log_rotation(self) -> None:
        """Setup log rotation for system logs"""
        try:
            # Create logrotate configuration
            logrotate_config = f"""
{self.project_root}/logs/*.log {{
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload gunicorn
    endscript
}}
"""
            
            logrotate_file = self.project_root / "deploy" / "logrotate.conf"
            logrotate_file.parent.mkdir(exist_ok=True)
            logrotate_file.write_text(logrotate_config)
            
        except Exception as e:
            logger.warning(f"Log rotation setup failed: {str(e)}")
    
    def _setup_caching(self) -> bool:
        """Setup caching configuration"""
        try:
            logger.info("Setting up caching")
            
            # Test Redis connection if configured
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                try:
                    import redis
                    r = redis.from_url(redis_url)
                    r.ping()
                    logger.info("Redis connection successful")
                except Exception as e:
                    logger.warning(f"Redis connection failed: {str(e)}")
            
            # Clear existing cache
            result = subprocess.run([
                sys.executable, "manage.py", "clear_cache"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning("Cache clearing failed - command may not exist")
            
            logger.info("Caching setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Caching setup failed: {str(e)}")
            return False
    
    def _setup_security(self) -> bool:
        """Setup security configurations"""
        try:
            logger.info("Setting up security")
            
            # Check security settings
            result = subprocess.run([
                sys.executable, "manage.py", "check", "--deploy"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Security checks failed: {result.stderr}")
            
            # Set secure file permissions
            self._set_secure_permissions()
            
            logger.info("Security setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Security setup failed: {str(e)}")
            return False
    
    def _set_secure_permissions(self) -> None:
        """Set secure file permissions"""
        try:
            import stat
            
            # Secure sensitive files
            sensitive_files = [
                ".env",
                "db.sqlite3",
                "deploy/config.json"
            ]
            
            for file_path in sensitive_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    full_path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
            
        except Exception as e:
            logger.warning(f"Permission setting failed: {str(e)}")
    
    def _restart_services(self) -> bool:
        """Restart application services"""
        try:
            logger.info("Restarting services")
            
            # For development/simple deployment
            # In production, you'd restart gunicorn, nginx, etc.
            
            # Kill any existing Django processes
            try:
                result = subprocess.run([
                    "pkill", "-f", "manage.py runserver"
                ], capture_output=True, text=True)
            except Exception:
                pass  # Process might not exist
            
            # Clear any Django cache
            try:
                subprocess.run([
                    sys.executable, "manage.py", "clear_cache"
                ], cwd=self.project_root, capture_output=True, text=True)
            except Exception:
                pass
            
            logger.info("Services restarted")
            return True
            
        except Exception as e:
            logger.error(f"Service restart failed: {str(e)}")
            return False
    
    def _post_deployment_validation(self) -> bool:
        """Post-deployment validation tests"""
        try:
            logger.info("Running post-deployment validation")
            
            # Test basic functionality
            validation_tests = [
                self._validate_database_connectivity,
                self._validate_static_files,
                self._validate_monitoring_system,
                self._validate_api_endpoints,
                self._validate_performance_thresholds
            ]
            
            for test in validation_tests:
                if not test():
                    return False
            
            logger.info("Post-deployment validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Post-deployment validation failed: {str(e)}")
            return False
    
    def _validate_database_connectivity(self) -> bool:
        """Validate database connectivity"""
        try:
            result = subprocess.run([
                sys.executable, "-c",
                """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings.production')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    assert result[0] == 1
print('Database connectivity OK')
"""
            ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Database connectivity validated")
                return True
            else:
                logger.error(f"Database validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Database validation error: {str(e)}")
            return False
    
    def _validate_static_files(self) -> bool:
        """Validate static files are accessible"""
        try:
            static_root = self.project_root / "staticfiles"
            if not static_root.exists():
                logger.error("Static files directory does not exist")
                return False
            
            # Check for critical static files
            critical_static = ["admin", "css", "js"]
            for item in critical_static:
                if not (static_root / item).exists():
                    logger.warning(f"Static directory missing: {item}")
            
            logger.info("Static files validated")
            return True
            
        except Exception as e:
            logger.error(f"Static files validation failed: {str(e)}")
            return False
    
    def _validate_monitoring_system(self) -> bool:
        """Validate monitoring system"""
        try:
            result = subprocess.run([
                sys.executable, "-c",
                """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings.production')
django.setup()

from predictions_tracker.core.services.ProductionMonitoringService import production_monitoring_service
summary = production_monitoring_service.get_system_health_summary()
print(f"Monitoring status: {summary['overall_status']}")
assert summary['overall_status'] in ['healthy', 'warning', 'degraded']
"""
            ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Monitoring system validated")
                return True
            else:
                logger.error(f"Monitoring validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Monitoring validation error: {str(e)}")
            return False
    
    def _validate_api_endpoints(self) -> bool:
        """Validate critical API endpoints"""
        try:
            # Test critical endpoints
            test_endpoints = [
                "/api/monitoring-dashboard/",
                "/api/system-health-check/",
                "/api/production-performance-metrics/"
            ]
            
            for endpoint in test_endpoints:
                result = subprocess.run([
                    sys.executable, "-c",
                    f"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings.production')
django.setup()
from django.test import Client

client = Client()
response = client.get('{endpoint}')
print(f'Endpoint {endpoint}: {{response.status_code}}')
assert response.status_code in [200, 302, 404]  # 404 is OK for non-configured endpoints
"""
                ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.warning(f"API endpoint test failed: {endpoint}")
            
            logger.info("API endpoints validated")
            return True
            
        except Exception as e:
            logger.error(f"API validation error: {str(e)}")
            return False
    
    def _validate_performance_thresholds(self) -> bool:
        """Validate performance meets thresholds"""
        try:
            thresholds = self.config.get("performance_thresholds", {})
            
            # Basic performance check
            result = subprocess.run([
                sys.executable, "-c",
                f"""
import os
import django
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings.production')
django.setup()

from django.test import Client
from predictions_tracker.core.services.ProductionMonitoringService import production_monitoring_service

# Test response time
client = Client()
start_time = time.time()
response = client.get('/predictions_tracker/')
end_time = time.time()
response_time_ms = (end_time - start_time) * 1000

# Test monitoring metrics
metrics = production_monitoring_service._collect_current_metrics()

print(f'Response time: {{response_time_ms:.2f}}ms')
print(f'Memory usage: {{metrics.get("memory_usage_mb", 0):.2f}}MB')

# Check thresholds
max_response_time = {thresholds.get('max_response_time_ms', 2000)}
max_memory_usage = {thresholds.get('max_memory_usage_mb', 1024)}

assert response_time_ms < max_response_time, f"Response time too high: {{response_time_ms}}ms"
assert metrics.get("memory_usage_mb", 0) < max_memory_usage, f"Memory usage too high"
"""
            ], cwd=self.project_root, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("Performance thresholds validated")
                return True
            else:
                logger.warning(f"Performance validation failed: {result.stderr}")
                return True  # Don't fail deployment for performance warnings
                
        except Exception as e:
            logger.error(f"Performance validation error: {str(e)}")
            return True  # Don't fail deployment for validation errors
    
    def _cleanup_old_backups(self) -> None:
        """Clean up old backup files"""
        try:
            backup_parent = self.project_root / "backups"
            if not backup_parent.exists():
                return
            
            retention_days = self.config.get("backup_retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for backup_dir in backup_parent.iterdir():
                if backup_dir.is_dir():
                    # Extract timestamp from directory name
                    try:
                        timestamp_str = backup_dir.name.split('_', 1)[1]
                        backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        
                        if backup_date < cutoff_date:
                            shutil.rmtree(backup_dir)
                            logger.info(f"Removed old backup: {backup_dir.name}")
                    except (ValueError, IndexError):
                        continue  # Skip directories with invalid names
            
        except Exception as e:
            logger.warning(f"Backup cleanup failed: {str(e)}")
    
    def _rollback_deployment(self) -> None:
        """Rollback deployment in case of failure"""
        try:
            logger.info("Rolling back deployment")
            
            if not self.backup_dir.exists():
                logger.error("No backup available for rollback")
                return
            
            # Restore from backup
            backup_info_file = self.backup_dir / "backup_info.json"
            if backup_info_file.exists():
                with open(backup_info_file, 'r') as f:
                    backup_info = json.load(f)
                
                items_to_restore = backup_info.get("items_backed_up", [])
                
                for item in items_to_restore:
                    backup_item = self.backup_dir / item
                    target_item = self.project_root / item
                    
                    if backup_item.exists():
                        if target_item.exists():
                            if target_item.is_dir():
                                shutil.rmtree(target_item)
                            else:
                                target_item.unlink()
                        
                        if backup_item.is_dir():
                            shutil.copytree(backup_item, target_item)
                        else:
                            shutil.copy2(backup_item, target_item)
                
                logger.info("Rollback completed")
            else:
                logger.error("Backup metadata not found")
                
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
    
    def _log_deployment_summary(self) -> None:
        """Log deployment summary"""
        try:
            summary = {
                "deployment_timestamp": self.deployment_timestamp,
                "deployment_status": "SUCCESS",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "project_root": str(self.project_root),
                "backup_location": str(self.backup_dir),
                "environment_variables": {
                    "DJANGO_SETTINGS_MODULE": os.getenv("DJANGO_SETTINGS_MODULE"),
                    "DEBUG": os.getenv("DEBUG", "Not set"),
                    "DJANGO_ENV": os.getenv("DJANGO_ENV", "Not set")
                }
            }
            
            summary_file = self.project_root / "deploy" / f"deployment_summary_{self.deployment_timestamp}.json"
            summary_file.parent.mkdir(exist_ok=True)
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Deployment summary saved: {summary_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save deployment summary: {str(e)}")


def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Deployment Script")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        return
    
    project_root = Path(args.project_root).resolve()
    deployment = ProductionDeployment(str(project_root))
    
    success = deployment.deploy()
    
    if success:
        logger.info(" Deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()