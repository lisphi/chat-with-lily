import os
import commentjson
import sys

from .log import logger

def load_config(arg_type: str):
    config_path = os.environ.get("LILY_CONFIG_PATH", "./settings.jsonc")
    logger.info(f"Loading configuration from: {config_path}") 

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            s_config: dict = commentjson.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)  # Exit if config file is not found
    except Exception as e:
        logger.error(f"Error loading configuration file {config_path}: {e}")
        sys.exit(1)

    if arg_type == "make_dataset":
        config = {**s_config["make_dataset_args"], **s_config["common_args"]}
    
    return config