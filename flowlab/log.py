from pathlib import Path
from datetime import time as dt

from flowlab import settings


# {project_root}/logs/ 不存在的話自動建立, mode=777-<umask>
LOGGING_DIR = Path(__file__).resolve().parent.parent / 'logs/'
LOGGING_DIR.mkdir(mode=777, exist_ok=True)

# https://docs.djangoproject.com/zh-hans/3.2/topics/logging/#configuring-logging
LOGGING = {
    'version': 1,
    # 和 Django 的預設 logging config 合併, 而非覆蓋
    # Django Default dictCongit:
    # https://github.com/django/django/blob/main/django/utils/log.py
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # https://docs.python.org/zh-tw/3/library/logging.html#logrecord-attributes
            'format': '[{asctime}] [{levelname}] ({name}:{lineno:d}) {message}',
            'style': '{',
            # https://docs.python.org/zh-tw/3/library/time.html#time.strftime
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{asctime} {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO' if settings.DEBUG else 'WARNING',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'web': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_DIR / 'web.log',
            'maxBytes': 1 * (10 ** 9),  # 文件大小
            'backupCount': 5,  # 備份份數
        },
        'error': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGGING_DIR / 'error.log',
            'maxBytes': 1 * (10 ** 9),  # 文件大小
            'backupCount': 99,  # 備份份數
            'delay': True,
        },
        'access': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'formatter': 'simple',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGGING_DIR / 'access.log',
            'atTime': dt.min,
            'when': 'd',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'web', 'error'],
            'propagate': False,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'access'],
            'propagate': False,
            'level': 'INFO',
        },
        'flowlab': {
            'handlers': ['console', 'web', 'error'],
            'propagate': False,
            'level': 'INFO',
        },
    },
}
