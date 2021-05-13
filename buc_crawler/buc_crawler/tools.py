import re
import typing
from requests import get


def is_not_firm(url: str) -> bool:
    result = re.search(r'\/firm', url)
    return False if result else True
