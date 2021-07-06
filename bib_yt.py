from typing import Callable
from os.path import isdir
from os import mkdir

def do_until_no_next(func: Callable, *args, **kwargs):
    """
    YT (jak w sumie wiele stron) wykorzystuje mechanizm dzielenia wyników na strony, aby umożliwić ich efektywne przesyłanie. 
    Ta funkcja wykonuje wybrany request (funkcję func z arumentami args i kwargs) w taki sposób, aby zwrócić wszystkie strony w formie jednej dużej listy.
    """
    full = []
    wyniki = func(*args, **kwargs)
    full.extend(wyniki.items)
    next_token = wyniki.nextPageToken
    while next_token:
        wyniki = func(*args, page_token=next_token, **kwargs)
        full.extend(wyniki.items)
        next_token = wyniki.nextPageToken
    return wyniki

def save_file(folder: str, name: str, url: str, comments: list[str], count: int):
    HEADER = f'<COSAR ROBOT="" DOH="" PORTAL="" PRESENTATION="" AUTHOR="" INTERACTION="" URL="{url}"> \n\tLiczba komentarzy pod filmem = {count}\n\tLiczba komentarzy w pliku = {len(comments)}\n'
    FOOTER = '</COSAR>'
    
    if not isdir('data'):
        mkdir('data')
    if not isdir(f'data/{folder}'):
        mkdir(f'data/{folder}')
    
    with open(f'data/{folder}/{name}.xml', 'w', encoding='utf8') as f:
        f.write(HEADER)
        f.writelines(("\n\t%s\n" % i.replace('\n', '\n\t') for i in comments))
        f.write(FOOTER)