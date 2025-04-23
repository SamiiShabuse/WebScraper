import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin

from dotenv import load_dotenv
import os

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
print(SERPAPI_KEY)

