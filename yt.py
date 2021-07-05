from os import mkdir
from time import asctime

import streamlit as st
from pyyoutube import Api
from pyyoutube.models.comment import CommentThread
from pyyoutube.models.search_result import SearchResult
from pyyoutube.models.video import Video, VideoListResponse

from key import KEY
from bib_yt import *

@st.cache
def find_videos(api: Api, search_term: str) -> list[SearchResult]:
    """
    Zbiera listę wszystkich wyników wyszukiwania na bazie podanego hasła
    """
    return do_until_no_next(api.search_by_keywords, q=search_term, search_type="video")


def get_videos(api: Api, results: list[SearchResult]):
    return [
        api.get_video_by_id(i).items.items[0] for i in results
    ]  # ID powinno być zawsze unikalne


def get_video_url(vid: Video) -> str:
    return f"https://youtu.be/{vid.id}"


def get_comment_count(vid: Video) -> int:
    return vid.statistics.commentCount


def get_comment_threads(api: Api, video: Video):
    """
    Zbiera listę wszystkich comment threads w danym filmie
    """
    return do_until_no_next(api.get_comment_threads, video_id=video.id, text_format="plainText")


def comment_format(author: str, text: str, reply_to: str = None) -> str:
    rep = f", in reply to {reply_to}" if reply_to else ""
    return f"{author}{rep}: \n{text}"


def get_comments(api: Api, thread: CommentThread, replies: bool) -> list[str]:
    first = thread.snippet.topLevelComment
    comments = [
        comment_format(first.snippet.authorDisplayName, first.snippet.textDisplay)
    ]

    if replies:
        if thread.snippet.totalReplyCount > len(thread.replies.comments):
            found = do_until_no_next(api.get_comments, parent_id=first.id, text_format='plainText')
        else:
            # Jeżeli wszystkie odpowiedzi się zmieściły w threadzie, to nie wysyłamy nowego requestu
            found = thread.replies.comments
            
        for reply in found:
            comments.append(
                comment_format(
                    author=reply.snippet.authorDisplayName,
                    text=reply.snippet.textDisplay,
                    reply_to=first.snippet.authorDisplayName,
                )
            )
    return comments


def download(search_term: str, replies: bool, key: str):
    api = Api(api_key=key)

    with st.spinner("Zbieranie wyników wyszukiwania"):
        result = find_videos(api, search_term)
        vids = get_videos(api, result)

    with st.spinner("Zbieranie komentarzy i informacji o filmach"):
        progress_bar = st.progress(0 / len(vids))
        for i, vid in enumerate(vids):

            # Zbieranie danych o wideo
            url = get_video_url(vid)
            comm_count = get_comment_count(vid)
            threads = get_comment_threads(api, vid, replies)
            comments = sum(
                (get_comments(api, thread, replies) for thread in threads.items), []
            )
            assert len(comments) == comm_count
            
            # Zapisywanie
            st.header(url)
            st.write(comm_count)
            st.write(comments)

            progress_bar.progress((i + 1) / len(vids))


KEY = st.text_input("API Key", value=KEY)
search = st.text_input("Robot do wyszukania") + " robot"
replies = st.checkbox("Pobierać z odpowiedziami")

st.button("Pobierz", on_click=download, args=(search, replies, KEY))
