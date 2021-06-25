import json
import logging
import os

import requests


class ActivPassiv:
    """
    Use the Passiv (https://passiv.com) API to automatically buy the recommended stocks.
    API documentation: https://app.swaggerhub.com/apis-docs/passiv/PassivAPI/v1 (as of 2021-04-15, it was outdated
    / missing information)
    """

    def __init__(self, api_key: str, base_url: str, portfolio_name: str, log_level: str):
        self.log = logging.getLogger()
        self.setup_logging(log_level)

        self.api_key = api_key
        self.base_url = base_url
        self.portfolio_name = portfolio_name

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

        portfolio_id = self.get_portfolio_id()

        portfolio_data = self.get(f"/portfolioGroups/{portfolio_id}/info").json()

        self.log.debug(f"Complete Portfolio Data: {json.dumps(portfolio_data)}")

        calculated_trades: list = portfolio_data["calculated_trades"]["trades"]
        calculated_trade_id: str = portfolio_data["calculated_trades"]["id"]

        if len(calculated_trades) == 0:
            self.log.info("There are currently no trade possible to do to allocate your money.")
        else:
            self.log.info(f"There are {len(calculated_trades)} trades possible to allocate your money.")
            self.log.debug({json.dumps(calculated_trades)})

            for trade in calculated_trades:
                self.log.info(f"{trade['action']} {trade['units']} {trade['universal_symbol']['symbol']}. Total: {trade['universal_symbol']['currency']['code']} {trade['price']}")

            self.log.info(f"Executing calculated trade {calculated_trade_id} to rebalance portfolio...")
            response = self.post(f"/portfolioGroups/{portfolio_id}/calculatedtrades/{calculated_trade_id}/placeOrders", data={})
            self.log.debug(f"{response} {response.text}")
            for trade in response.json():
                self.log.info(f"{trade.get('state')} {trade.get('action')}: {trade.get('filled_units')}x{trade.get('universal_symbol', {}).get('symbol')} "
                              f"({trade.get('price')} {trade.get('universal_symbol', {}).get('currency', {}).get('code')}). Commission: {trade.get('commissions')}")

        self.log.info("Exiting")

    def get_portfolio_id(self) -> str:
        """
        :return: The ID of the portfolio to buy stocks from.
        """

        portfolio_groups: dict = self.get("/portfolioGroups").json()
        portfolio_id = None
        for portfolio in portfolio_groups:
            if portfolio.get("name") == self.portfolio_name:
                portfolio_id = portfolio.get("id")
        if not portfolio_id:
            self.log.critical(f"Could not find portfolio {self.portfolio_name}. List of portfolios: {portfolio_groups}")
        return portfolio_id

    def get(self, uri: str) -> requests.Response:
        """
        Perform a GET request to the Passiv API.
        :param uri: The path to fetch (ex. /accounts)
        """
        return self.request("GET", uri)

    def post(self, uri: str, data: dict={}) -> requests.Response:
        """
        Perform a GET request to the Passiv API.
        :param data: Dictionary representing the JSON payload to send.
        :param uri: The path to fetch (ex. /accounts)
        """
        return self.request("POST", uri, json=data)

    def request(self, method: str, uri: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP request to the Passiv API.

        :param method: The HTTP verb (GET, POST, PUT, etc.)
        :param uri: The path to fetch (ex. /accounts)
        """
        response = None
        try:
            response = requests.request(method, url=f"{self.base_url}{uri}",
                                        headers={'Authorization': f"Token {self.api_key}"}, **kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            self.log.exception(e)
            self.log.error(f"Error when requesting {uri}: {e}")
            if response is not None and response.text:
                self.log.error(response.text)
            raise e

    def test_api_connectivity(self):
        """
        Test if the API works
        """
        self.log.debug("Testing the API...")
        response = self.get("/")
        if response.status_code != 200:
            self.log.critical(f"API returned an error. Code: {response.status_code}. Data: {response.text}")
            exit(1)
        self.log.debug(f"API Works! {response.text}")

    def verify_env_file(self):
        """
        Check if the env file is okay and contain the correct data. Exit the program if not.
        """

        if not os.path.exists(".env"):
            self.log.critical(".env file not found. Make sure to copy ")
            exit(1)
        if not self.api_key:
            self.log.critical(
                "Passiv API key not found. Make sure to have a .env file in the working directory and that it "
                "contains passiv_api_key=<apikey> .")
            exit(1)

        if not self.portfolio_name:
            self.log.critical(
                "Portfolio name not found. Set the portfolio name you want to automatically allocate in the .env file. "
                "portfolio_name=\"mygreatportfolio\" .")
            exit(1)
