# octo-potato

repo na skrypt zbierający komentarze z yt oraz reddita. Nazwa wylosowana przez github :p

## Instalacja

Potrzebne będą:

- Python 3.9 (możliwe jest, że na starszych wersjach działa, ale nie miałem okazji sprawdzić)
- Dostęp do YouTube API przez API Key (Opisane [tutaj](https://developers.google.com/youtube/v3/getting-started#before-you-start))
- Dostęp do Reddit API (Opisane [tutaj](https://gilberttanner.com/blog/scraping-redditdata), w sekcji Getting Started od "To get the authentication information...")

Przepis:

1. Pobierz i rozpakuj zawartość repozytorium
2. Utwórz plik `key.py` z zawartością:

   ```python
   YT_KEY = "[Twój YouTube API Key]"

   REDDIT_CLIENT_ID = '[Twój Reddit Client ID]'
   REDDIT_CLIENT_SECRET = '[Twój Reddit Client Secret]'
   REDDIT_USER_AGENT = '[Twój Reddit User Agent]'
   ```

3. Uruchom w linii komend (zakładam działanie na Windowsie) plik `install.bat` (wpisanie jego pełnej ścieżki wystarczy). Plik ten utworzy wirtualne środowisko i pobierze potrzebne biblioteki. Windows Defender może protestować, ale to fałszywy alarm. 
4. Możliwa jest instalacja bezpośrednio na komputerze, do tego wystarczy wpisać w linii komend `python -m pip install -r install.txt` będąc w folderze repozytorium.
5. Uruchom program plikiem `run.bat`.
6. `yt.py` oraz `reddit.py` mogą być uruchamiane pomijając interfejs użytkownika, wymagane jest wtedy jednak aktywowanie wirtualnego środowiska (`.venv\Scripts\activate.bat`), bądź korzystanie z instalacji bespośrednio na komputerze

## Uwagi na temat działania programu

### Nie wszystkie komentarze zostają zebrane

> Finally, note that the value of submission.num_comments may not match up 100% with the number of comments extracted via PRAW.
> This discrepancy is normal as that count includes deleted, removed, and spam comments.
> ~ Dokumentacja PRAW

Podobnie YouTube może czasem mieć podobne problemy, informacje o takich filmach zawarte są w ostrzeżeniach.

### Pliki bez komentarzy

Niektóre filmy mają wyłączone komentarze, wtedy można się spodziewać pustych plików

### Niespodziewane błędy

Starałem się przetestować całość jak najdokładniej, ale mogłem nie spotkać się z jakimś problemem. Hit me up.

### Daily Quota

Większość serwisów posiada określoną maksymalną liczbę dziennych zapytań. W przypadku Reddita nigdy do niego nie dotarłem, ale YouTube jest dość konserwatywny. Jeśli pojawi się z nim problem warto uruchomić request ponownie następnego dnia z włączoną opcją pomijania istniejących plików. Wyniki, w związku z metodą działania silników wyszukiwania, będą się niestety lekko różniły.
