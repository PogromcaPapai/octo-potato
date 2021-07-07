import yt
import reddit
import streamlit as st

st.title("Danozbieracz")
switch = st.selectbox("Z jakiej strony zbierać?", ['YouTube', "Reddit"])

if switch == 'YouTube':
    search = st.text_input("Robot do wyszukania") + " robot"
    amount = st.number_input("Ilość pobieranych wyników", min_value=0)
    replies = st.checkbox("Pobierać z odpowiedziami")

    st.button("Pobierz", on_click=yt.download, args=(search, replies, amount))

elif switch == 'Reddit':
    search = st.text_input("Robot do wyszukania") + " robot"
    amount = st.number_input("Ilość pobieranych wyników", min_value=0)
    replies = st.checkbox("Pobierać z odpowiedziami")
    
    st.button("Pobierz", on_click=reddit.download, args=(search, replies, amount))