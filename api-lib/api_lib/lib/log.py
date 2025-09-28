

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s]-[%(levelname)s]-[%(name)s]-[%(funcName)s]-%(message)s",
            "datefmt": "%H:%M",
        },
        "access": {
            "format": '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            "datefmt": "%H:%M",
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "access": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console",
        ]
    },
    "loggers": {
        "uvicorn": {
            "handlers": [
                "default",
                'console',
            ],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": [
                "default",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": [
                "access",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "tasks": {
            "handlers": [
                "default",
                'console',
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "metadata": {
            "handlers": [
                "default",
                'console',
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "rabbit": {
            "handlers": [
                "default",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}
