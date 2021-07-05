from typing import Callable


def do_until_no_next(func: Callable, *args, **kwargs):
    """
    YT (jak w sumie wiele stron) wykorzystuje mechanizm dzielenia wyników na strony, aby umożliwić ich efektywne przesyłanie. 
    Ta funkcja wykonuje wybrany request (funkcję func z arumentami args i kwargs) w taki sposób, aby zwrócić wszystkie strony w formie jednej dużej listy.
    """
    full = []
    wyniki = func(*args, limit=50, **kwargs)
    full.extend(wyniki.items)
    next_token = wyniki.nextPageToken
    while next_token:
        wyniki = func(
            *args, limit=50, page_token=next_token, **kwargs
        )
        full.extend(wyniki.items)
        next_token = wyniki.nextPageToken
    return wyniki

def save_file(url: str, comments: list[str]):
    pass