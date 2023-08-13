import json
from pathlib import Path
from typing import Dict

import pandas as pd
import requests

from ..config import SEARCH_RESULT_CACHE_PATH, rpc

session = requests.Session()
# key word cache
SEARCH_RESULT_DICT: Dict[str, dict] = dict()
# info ID cache
BASE_INFO_CACHE: Dict[str, pd.Series] = dict()
path = Path(SEARCH_RESULT_CACHE_PATH)
if path.exists():
    load_success = False
    with path.open('r', encoding='utf-8') as f:
        try:
            SEARCH_RESULT_DICT = json.load(f)
            load_success = True
        except:
            pass
    if not load_success:
        path.open('w').close()
