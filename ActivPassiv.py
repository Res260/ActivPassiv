import logging
import os
from typing import Optional

import requests


class ActivPassiv:
    """
    Use the Passiv (https://passiv.com) API to automatically buy the recommended stocks.
    """

    def __init__(self, api_key: str, base_url: str, log_level: str):
        self.log = logging.getLogger()
        self.setup_logging(log_level)

        self.api_key = api_key
        self.base_url = base_url

    def setup_logging(self, log_level: str):
        """
        :param log_level: Minimum Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_format = logging.Formatter("%(asctime)s - %(levelname)8s - %(name)22s - %(message)s")
        self.log.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setFormatter(log_format)
        self.log.addHandler(handler)
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(log_format)
        self.log.addHandler(file_handler)

    def activ_passiv(self):
        """
        Executes the routine to automatically buy the recommended stocks.
        """

        self.log.info("Starting ActivPassiv")

        self.verify_env_file()
        self.test_api_connectivity()

        logging.info("Exiting")

    def test_api_connectivity(self):
        """
        Test if the API works
        """
        self.log.debug("Testing the API...")
        response = requests.get(f"{self.base_url}/")
        if response.status_code != 200:
            logging.critical(f"API returned an error. Code: {response.status_code}. Data: {response.text}")
            exit(1)
        self.log.debug(f"API Works! {response.text}")

    def verify_env_file(self):
        """
        Check if the env file is okay and contain the correct data. Exit the program if not.
        """

        if not os.path.exists(".env"):
            logging.critical(".env file not found. Make sure to copy ")
            exit(1)
        if not self.api_key:
            logging.critical(
                "Passiv API key not found. Make sure to have a .env file in the working directory and that it "
                "contains passiv_api_key=<apikey> .")
            exit(1)
