from pathlib import Path

HERE = Path(__file__).parent
# data cache dir
DATA_DIR = HERE / '../data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
SEARCH_RESULT_CACHE_PATH = str(DATA_DIR / 'search-cache.json')
