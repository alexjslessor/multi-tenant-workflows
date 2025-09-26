
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
            "datefmt": "%H:%M",
        },
        "access": {
            "format": '%(asctime)s - %(levelname)s - %(message)s',
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
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
        # Your app-specific logger
        "auth": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}