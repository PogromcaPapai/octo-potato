import yt
import reddit
import streamlit as st

# Interfejs
st.title("Danozbieracz")
switch = st.selectbox("Z jakiej strony zbierać?", ["YouTube", "Reddit"])
search = st.text_input("Robot do wyszukania") + " robot"
amount = st.number_input("Ilość pobieranych wyników (Podaj 0, aby pobrać wszystkie - działa tylko dla reddita)", min_value=0)
replies = st.checkbox("Pobierać z odpowiedziami")
omit = st.checkbox("Pomijać istniejące pliki")


# Przycisk
if switch == "YouTube":
    st.button("Pobierz", on_click=yt.download, args=(search, replies, amount, omit))
elif switch == "Reddit":
    st.button("Pobierz", on_click=reddit.download, args=(search, replies, amount, omit))