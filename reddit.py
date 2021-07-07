import praw
from key import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
import streamlit as st
from bib import save_file, comment_format

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
r_all = reddit.subreddit("all")

def _forest_iterate(commentforest: praw.models.comment_forest.CommentForest, reply_to: str):
    comments = []
    for i in commentforest:
        c = [comment_format(i.author, i.body, reply_to)]
        if i.replies:
            c.extend(_forest_iterate(i.replies, i.author))
        comments += c    
    return comments

def get_comments(post: praw.models.Submission, collect_replies: bool):
    formatted_comments = []
    post.comments.replace_more(limit=0)
    for comm in post.comments:
        formatted_comments.append(comment_format(comm.author, comm.body))
        if collect_replies:
            formatted_comments.extend(_forest_iterate(comm.replies, comm.author))
    return formatted_comments

def download(search_term: str, collect_replies: bool, amount: int):
    
    with st.spinner("Zbieranie wyników wyszukiwania"):
        posts = r_all.search(search_term, limit=amount)
        
    with st.spinner("Zbieranie komentarzy i informacji o postach"):
        progress_bar = st.progress(0 / amount)
        warns = []
        st.write("""
                 > Finally, note that the value of submission.num_comments may not match up 100% with the number of comments extracted via PRAW.
                 > This discrepancy is normal as that count includes deleted, removed, and spam comments.
                 > ~ Dokumentacja paczki PRAW
                 """)
        for i, post in enumerate(posts):
            
            # Zbieranie danych o poście
            post_id = post.id
            url = "https://www.reddit.com" + post.permalink
            official_count = post.num_comments
            
            # Pobieranie komentarzy
            comments = get_comments(post, collect_replies)

            # Zapisywanie
            save_file(f'reddit/{search_term}', post_id, url, comments, official_count)
            progress_bar.progress((i + 1) / amount)
        st.warning("\n - ".join(["Ostrzeżenia:"] + warns))


if __name__=="__main__":
    HASLO_WYSZUKIWANE = 'genshin'
    CZY_UWZGLEDNIAC_ODPOWIEDZI = True
    LICZBA_POSTOW = 100
    
    download(HASLO_WYSZUKIWANE, CZY_UWZGLEDNIAC_ODPOWIEDZI, LICZBA_POSTOW)