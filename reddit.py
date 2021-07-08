from genericpath import isfile
import praw
from key import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
import streamlit as st
from bib import save_file, comment_format

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
r_all = reddit.subreddit("all")

def _forest_iterate(commentforest: praw.models.comment_forest.CommentForest, reply_to: str) -> list[str]:
    comments = []
    for i in commentforest:
        c = [comment_format(i.author, i.body, reply_to)]
        if i.replies:
            c.extend(_forest_iterate(i.replies, i.author))
        comments += c    
    return comments

def get_comments(post: praw.models.Submission, collect_replies: bool) -> list[str]:
    formatted_comments = []
    post.comments.replace_more(limit=0)
    for comm in post.comments:
        formatted_comments.append(comment_format(comm.author, comm.body))
        if collect_replies:
            formatted_comments.extend(_forest_iterate(comm.replies, comm.author))
    return formatted_comments

def download(search_term: str, collect_replies: bool, amount: int, omit: bool):
    
    with st.spinner("Zbieranie wyników wyszukiwania"):
        if amount > 0:
            posts = r_all.search(search_term, limit=amount)
        else:
            posts = r_all.search(search_term, limit=None)
            amount = 1000 # "Most of reddit’s listings contain a maximum of 1000 items"
        
    with st.spinner("Zbieranie komentarzy i informacji o postach"):
        progress_bar = st.progress(0 / amount)
        warns = []
        omitted = 0
        for i, post in enumerate(posts):
            
            # Pomijanie istniejących plików
            if omit and isfile(f'reddit/{search_term}/{post.id}.xml'):
                omitted += 1
                continue
            
            # Zbieranie danych o poście
            post_id = post.id
            url = "https://www.reddit.com" + post.permalink
            official_count = post.num_comments
            
            # Pobieranie komentarzy
            comments = get_comments(post, collect_replies)
            if collect_replies and len(comments) != official_count:
                warns.append(
                    f"Dla postu o ID {post_id} odnaleziono {len(comments)} komentarzy, a system zadeklarował {official_count}"
                )

            # Zapisywanie
            save_file(f'reddit/{search_term}', post_id, url, comments, official_count)
            
            progress_bar.progress((i + 1) / amount)
 
    st.info(f"Znaleziono {i+1} postów")           
    if omitted > 0:
        warns.append(f"Program pominął {omitted} postów, gdyż ich pliki już istniały.")
    if warns:
        st.warning("\n - ".join(["**Ostrzeżenia**:"] + warns))


if __name__=="__main__":
    HASLO_WYSZUKIWANE = ''
    CZY_UWZGLEDNIAC_ODPOWIEDZI = True
    CZY_POMIJAC_ISTNIEJACE_PLIKI = True
    LICZBA_POSTOW = 100
    
    download(HASLO_WYSZUKIWANE, CZY_UWZGLEDNIAC_ODPOWIEDZI, LICZBA_POSTOW, CZY_POMIJAC_ISTNIEJACE_PLIKI)