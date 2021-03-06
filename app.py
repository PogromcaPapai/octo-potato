import yt
import reddit
import streamlit as st

# Interfejs
st.title("Danozbieracz")
switch = st.selectbox("Z jakiej strony zbierać?", ["YouTube", "Reddit"])
search = st.text_input("Robot do wyszukania") + " robot"*st.checkbox("Dodaj 'robot' na koniec nazwy", value=True)
amount = st.number_input("Ilość pobieranych wyników (Podaj 0, aby pobrać wszystkie - działa tylko dla reddita)", min_value=0)
replies = st.checkbox("Pobierać z odpowiedziami")
omit = st.checkbox("Pomijać istniejące pliki")
title = st.checkbox("Szukaj tylko w tytułach", value=True)
use_json = st.checkbox("JSON", value=False)


# Przycisk
if switch == "YouTube":
    sort = st.checkbox("Sortować według liczby wyświetleń (youtube)")
    st.button("Pobierz", on_click=yt.download, args=(search, replies, amount, omit, sort, title, use_json))
elif switch == "Reddit":
    sort = st.checkbox("Sortować według liczby komentarzy (reddit)")
    st.button("Pobierz", on_click=reddit.download, args=(search, replies, amount, omit, sort, title, use_json))