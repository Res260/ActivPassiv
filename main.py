import os

import dotenv

from ActivPassiv import ActivPassiv

if __name__ == '__main__':
    dotenv.load_dotenv()
    activ_passiv = ActivPassiv(api_key=os.getenv("passiv_api_key", ""), base_url=os.getenv("passiv_api_url", ""),
                               portfolio_name=os.getenv("portfolio_name", ""), log_level=os.getenv("log_level", "INFO"))
    activ_passiv.activ_passiv()

