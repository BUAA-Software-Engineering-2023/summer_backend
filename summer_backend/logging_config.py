def get_logging_config(base_log_dir):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                          '[%(levelname)s] - %(message)s'
            },
            'simple': {
                'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'debug': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'info': {
                'level': 'INFO',
                'filters': ['require_debug_false'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': base_log_dir / "info.log",
                'maxBytes': 1024 * 1024 * 500,
                'backupCount': 3,
                'formatter': 'standard',
                'encoding': 'utf-8',
            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': base_log_dir / "error.log",
                'maxBytes': 1024 * 1024 * 5,
                'backupCount': 5,
                'formatter': 'standard',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'mail_admins', 'file', 'error'],
                'level': 'INFO',
                'propagate': False
            },
            'django.server': {
                'handlers': ['django.server', 'file', 'error'],
                'level': 'INFO',
                'propagate': False
            },
        },
        'root': {
            'handlers': ['debug', 'info', 'file', 'error'],
            'level': 'DEBUG'
        }
    }

    return LOGGING
