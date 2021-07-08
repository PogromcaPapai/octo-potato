import yt
import reddit
import streamlit as st

st.title("Danozbieracz")
switch = st.selectbox("Z jakiej strony zbierać?", ['YouTube', "Reddit"])
search = st.text_input("Robot do wyszukania") + " robot"
amount = st.number_input("Ilość pobieranych wyników (Podaj 0, aby pobrać wszystkie)", min_value=0)
replies = st.checkbox("Pobierać z odpowiedziami")
omit = st.checkbox("Pomijać istniejące pliki")

if switch == 'YouTube':
    st.button("Pobierz", on_click=yt.download, args=(search, replies, amount, omit))
elif switch == 'Reddit':
    st.button("Pobierz", on_click=reddit.download, args=(search, replies, amount, omit))
    
"""
> Finally, note that the value of submission.num_comments may not match up 100% with the number of comments extracted via PRAW.
> This discrepancy is normal as that count includes deleted, removed, and spam comments.
> ~ Dokumentacja PRAW

Podobnie YouTube może czasem mieć podobne problemy, informacje o takich filmach zawarte są w ostrzeżeniach
"""