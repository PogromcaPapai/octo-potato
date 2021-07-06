from logging import warn
from os import mkdir
import os
from pyyoutube.error import PyYouTubeException

import streamlit as st
from pyyoutube import Api
from pyyoutube.models.comment import CommentThread
from pyyoutube.models.search_result import SearchListResponse, SearchResult, SearchResultId
from pyyoutube.models.video import Video, VideoListResponse

from key import KEY
from bib_yt import *

@st.cache
def find_videos(api: Api, search_term: str) -> list[SearchResult]:
    """
    Zbiera listę wszystkich wyników wyszukiwania na bazie podanego hasła
    """
    # sprawdzić, czy to coś daje
    # return api.search_by_keywords(q=search_term, search_type="video", limit = 50, count = 50)
    return do_until_no_next(api.search_by_keywords, q=search_term, search_type="video", limit = 50, count = 50)


def get_videos(api: Api, results: SearchListResponse):
    return [
        api.get_video_by_id(video_id=i.id.videoId).items[0] for i in results.items
    ]  # ID powinno być zawsze unikalne


def get_video_url(vid: Video) -> str:
    return f"https://youtu.be/{vid.id}"


def get_comment_count(vid: Video) -> int:
    return int(vid.statistics.commentCount) if vid.statistics.commentCount else 0

@st.cache
def get_comment_threads(api: Api, video: Video):
    """
    Zbiera listę wszystkich comment threads w danym filmie
    """
    # return api.get_comment_threads(video_id=video.id, text_format="plainText", count=None)
    return do_until_no_next(api.get_comment_threads, video_id=video.id, text_format="plainText", count=None)


def comment_format(author: str, text: str, reply_to: str = None) -> str:
    rep = f", in reply to {reply_to}" if reply_to else ""
    return f"{author}{rep}: \n{text}"


def get_comments(api: Api, thread: CommentThread, replies: bool) -> list[str]:
    first = thread.snippet.topLevelComment
    comments = [
        comment_format(first.snippet.authorDisplayName, first.snippet.textDisplay)
    ]

    if replies and thread.replies:
        if thread.snippet.totalReplyCount > len(thread.replies.comments):
            # found = api.get_comments(parent_id=first.id, text_format='plainText', count = None).items
            found = do_until_no_next(api.get_comments, parent_id=first.id, text_format='plainText', count=None).items
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
    
    try:
                
        with st.spinner("Zbieranie wyników wyszukiwania"):
            result = find_videos(api, search_term)
            vids = get_videos(api, result)

        with st.spinner("Zbieranie komentarzy i informacji o filmach"):
            progress_bar = st.progress(0 / len(vids))
            warns = []
            for i, vid in enumerate(vids):

                # Zbieranie danych o wideo
                url = get_video_url(vid)
                official_count = get_comment_count(vid)
                
                # Pobieranie wątków komentarzy
                try:
                    threads = get_comment_threads(api, vid)
                except PyYouTubeException as e:
                    if e.message.endswith('has disabled comments.'):
                        warns.append(f'Wideo o ID {vid.id} nie posiada komentarzy')
                        continue
                    else:
                        raise e
                    
                # Zbieranie i formatowanie komentarzy
                comments = sum(
                    (get_comments(api, thread, replies) for thread in threads.items), []
                )
                if replies and len(comments) != official_count:
                    warns.append(f'Dla wideo o ID {vid.id} odnaleziono {len(comments)} komentarzy, a system zadeklarował {official_count}')
                
                # Zapisywanie
                save_file(search_term, vid.id, url, comments, official_count)

                progress_bar.progress((i + 1) / len(vids))
            st.warning("\n - ".join(['Ostrzeżenia:']+warns))
                
    except PyYouTubeException as e:
        if e.message=='The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.':
            st.error("Osiągnięto limit requestów na dziś")
        else:
            raise e


KEY = st.text_input("API Key", value=KEY)
search = st.text_input("Robot do wyszukania") + " robot"
replies = st.checkbox("Pobierać z odpowiedziami")

st.button("Pobierz", on_click=download, args=(search, replies, KEY))