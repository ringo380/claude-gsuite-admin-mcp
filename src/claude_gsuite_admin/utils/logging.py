"""Logging configuration and utilities for Claude GSuite Admin MCP."""

import logging
import os
import sys
from typing import Optional
from pathlib import Path
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'tool_name'):
            log_data['tool_name'] = record.tool_name
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        if hasattr(record, 'error_code'):
            log_data['error_code'] = record.error_code

        # Include exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class AdminMCPLogger:
    """Logger factory for Claude GSuite Admin MCP."""

    _configured = False

    @classmethod
    def configure_logging(
        cls,
        log_level: str = "INFO",
        log_format: str = "structured",
        log_file: Optional[str] = None,
        enable_console: bool = True
    ) -> None:
        """Configure logging for the application."""
        if cls._configured:
            return

        # Get log level
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)

        # Create root logger
        root_logger = logging.getLogger('claude_gsuite_admin')
        root_logger.setLevel(numeric_level)

        # Clear any existing handlers
        root_logger.handlers.clear()

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)

            if log_format == "structured":
                console_handler.setFormatter(StructuredFormatter())
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(formatter)

            root_logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file).parent
            log_path.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)

            if log_format == "structured":
                file_handler.setFormatter(StructuredFormatter())
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)

            root_logger.addHandler(file_handler)

        # Set up third-party loggers
        logging.getLogger('googleapiclient').setLevel(logging.WARNING)
        logging.getLogger('google.auth').setLevel(logging.WARNING)
        logging.getLogger('oauth2client').setLevel(logging.WARNING)
        logging.getLogger('httplib2').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance."""
        if not cls._configured:
            cls.configure_logging()

        return logging.getLogger(f'claude_gsuite_admin.{name}')

    @classmethod
    def configure_from_env(cls) -> None:
        """Configure logging from environment variables."""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_format = os.getenv('LOG_FORMAT', 'structured')
        log_file = os.getenv('LOG_FILE')
        enable_console = os.getenv('LOG_CONSOLE', 'true').lower() == 'true'

        cls.configure_logging(
            log_level=log_level,
            log_format=log_format,
            log_file=log_file,
            enable_console=enable_console
        )


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return AdminMCPLogger.get_logger(name)


def log_tool_execution(tool_name: str, user_id: str, args: dict):
    """Decorator to log tool execution."""
    def decorator(func):
        def wrapper(*args_inner, **kwargs):
            logger = get_logger('tools')
            start_time = datetime.now()

            # Create request ID for tracking
            request_id = f"{tool_name}_{start_time.strftime('%Y%m%d_%H%M%S_%f')}"

            logger.info(
                "Tool execution started",
                extra={
                    'tool_name': tool_name,
                    'user_id': user_id,
                    'request_id': request_id,
                    'args': str(args)[:200]  # Truncate long args
                }
            )

            try:
                result = func(*args_inner, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                logger.info(
                    "Tool execution completed successfully",
                    extra={
                        'tool_name': tool_name,
                        'user_id': user_id,
                        'request_id': request_id,
                        'duration': duration
                    }
                )
                return result

            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.error(
                    f"Tool execution failed: {str(e)}",
                    extra={
                        'tool_name': tool_name,
                        'user_id': user_id,
                        'request_id': request_id,
                        'duration': duration,
                        'error_code': getattr(e, 'error_code', 'UNKNOWN')
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_api_call(service: str, method: str, user_id: str):
    """Decorator to log Google API calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger('api')
            start_time = datetime.now()

            logger.debug(
                f"API call started: {service}.{method}",
                extra={
                    'service': service,
                    'method': method,
                    'user_id': user_id
                }
            )

            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                logger.debug(
                    f"API call completed: {service}.{method}",
                    extra={
                        'service': service,
                        'method': method,
                        'user_id': user_id,
                        'duration': duration
                    }
                )
                return result

            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.warning(
                    f"API call failed: {service}.{method} - {str(e)}",
                    extra={
                        'service': service,
                        'method': method,
                        'user_id': user_id,
                        'duration': duration
                    }
                )
                raise

        return wrapper
    return decorator


# Configure logging when module is imported
AdminMCPLogger.configure_from_env()