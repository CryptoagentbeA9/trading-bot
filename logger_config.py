"""
Structured Logging Configuration
Provides JSON-formatted logging with rotation and separate log files
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if hasattr(record, 'trade_data'):
            log_data['trade_data'] = record.trade_data

        if hasattr(record, 'api_data'):
            log_data['api_data'] = record.api_data

        if hasattr(record, 'error_data'):
            log_data['error_data'] = record.error_data

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(log_dir: str = 'logs') -> Dict[str, logging.Logger]:
    """
    Setup structured logging with rotation

    Args:
        log_dir: Directory for log files

    Returns:
        Dict of specialized loggers
    """
    Path(log_dir).mkdir(exist_ok=True)

    json_formatter = JSONFormatter()
    text_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    loggers = {}

    # Main application logger
    main_logger = logging.getLogger('trading_bot')
    main_logger.setLevel(logging.DEBUG)
    main_logger.handlers.clear()

    main_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    main_handler.setFormatter(text_formatter)
    main_logger.addHandler(main_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(text_formatter)
    console_handler.setLevel(logging.INFO)
    main_logger.addHandler(console_handler)

    loggers['main'] = main_logger

    # Trade logger (JSON format)
    trade_logger = logging.getLogger('trading_bot.trades')
    trade_logger.setLevel(logging.INFO)
    trade_logger.handlers.clear()
    trade_logger.propagate = False

    trade_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/trades.json',
        maxBytes=10*1024*1024,
        backupCount=10
    )
    trade_handler.setFormatter(json_formatter)
    trade_logger.addHandler(trade_handler)

    loggers['trades'] = trade_logger

    # API logger (JSON format)
    api_logger = logging.getLogger('trading_bot.api')
    api_logger.setLevel(logging.DEBUG)
    api_logger.handlers.clear()
    api_logger.propagate = False

    api_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/api.json',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    api_handler.setFormatter(json_formatter)
    api_logger.addHandler(api_handler)

    loggers['api'] = api_logger

    # Error logger
    error_logger = logging.getLogger('trading_bot.errors')
    error_logger.setLevel(logging.ERROR)
    error_logger.handlers.clear()
    error_logger.propagate = False

    error_handler = logging.handlers.RotatingFileHandler(
        f'{log_dir}/errors.log',
        maxBytes=10*1024*1024,
        backupCount=10
    )
    error_handler.setFormatter(text_formatter)
    error_logger.addHandler(error_handler)

    loggers['errors'] = error_logger

    return loggers


def log_trade(logger: logging.Logger, trade_type: str, symbol: str,
              amount: float, price: float, **kwargs):
    """Log trade execution with structured data"""
    trade_data = {
        'type': trade_type,
        'symbol': symbol,
        'amount': amount,
        'price': price,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }

    extra = {'trade_data': trade_data}
    logger.info(f"{trade_type} {symbol} @ ${price:.4f}", extra=extra)


def log_api_call(logger: logging.Logger, endpoint: str, method: str,
                 response_time: float, status_code: int = None, **kwargs):
    """Log API call with performance metrics"""
    api_data = {
        'endpoint': endpoint,
        'method': method,
        'response_time_ms': response_time * 1000,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }

    extra = {'api_data': api_data}
    logger.debug(f"API {method} {endpoint} - {response_time*1000:.2f}ms", extra=extra)


def log_error(logger: logging.Logger, error_type: str, message: str, **kwargs):
    """Log error with context"""
    error_data = {
        'error_type': error_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }

    extra = {'error_data': error_data}
    logger.error(f"{error_type}: {message}", extra=extra)
