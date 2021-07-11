from typing import Callable
from os.path import isdir
from os import mkdir

def save_file(folder: str, name: str, url: str, comments: list[str], count: int):
    """
    Zapisuje plik do podanego folderu (tworząc go, jeśli nie istniał) pod określoną nazwą
    """
    HEADER = f'<COSAR ROBOT="" DOH="" PORTAL="" PRESENTATION="" AUTHOR="" INTERACTION="" URL="{url}"> \n\tLiczba komentarzy pod materiałem = {count}\n\tLiczba komentarzy w pliku = {len(comments)}\n'
    FOOTER = '</COSAR>'
    
    address = 'data'
    for i in folder.split('/'):
        address = address + '/' + i
        if not isdir(address):
            mkdir(address)
    
    with open(f'data/{folder}/{name}.xml', 'w', encoding='utf8') as f:
        f.write(HEADER)
        f.writelines(("\n\t%s\n" % i.replace('\n', '\n\t') for i in comments))
        f.write(FOOTER)

        
def comment_format(author: str, text: str, reply_to: str = None) -> str:
    """Funkcja używana do formatowania komentarzy"""
    rep = f", in reply to {reply_to}" if reply_to else ""
    return f"{author}{rep}: \n{text}"