from pyyoutube.error import PyYouTubeException

import streamlit as st
from pyyoutube import Api
from pyyoutube.models.comment import CommentThread
from pyyoutube.models.search_result import (
    SearchListResponse,
    SearchResult,
    SearchResultId,
)
from pyyoutube.models.video import Video, VideoListResponse

from bib import *
from key import YT_KEY


def new_search(api: Api, q: str, amount: int):

    args = {
        "part": None,
        'q':q,
        'type':'video',
        'maxResults':amount
    }

    res_data = api.paged_by_page_token(resource="search", args=args, count=amount)

    return SearchListResponse.from_dict(res_data)


@st.cache
def find_videos(api: Api, search_term: str, amount: int) -> list[SearchResult]:
    """
    Zbiera listę wszystkich wyników wyszukiwania na bazie podanego hasła
    """
    return new_search(api, q=search_term, amount=amount)


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
    return api.get_comment_threads(
        video_id=video.id, text_format="plainText", count=None
    ).items


def get_comments(api: Api, thread: CommentThread, replies: bool) -> list[str]:
    first = thread.snippet.topLevelComment
    comments = [
        comment_format(first.snippet.authorDisplayName, first.snippet.textDisplay)
    ]

    if replies and thread.replies:
        if thread.snippet.totalReplyCount > len(thread.replies.comments):
            found = api.get_comments(
                parent_id=first.id, text_format="plainText", count=None
            ).items
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


def download(search_term: str, replies: bool, amount: int):
    api = Api(api_key=YT_KEY)

    try:

        with st.spinner("Zbieranie wyników wyszukiwania"):
            result = find_videos(api, search_term, amount)
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
                    if not e.message.endswith("has disabled comments."):
                        raise e
                    warns.append(f"Wideo o ID {vid.id} nie posiada komentarzy")
                    continue
                # Zbieranie i formatowanie komentarzy
                comments = sum(
                    (get_comments(api, thread, replies) for thread in threads.items), []
                )
                if replies and len(comments) != official_count:
                    warns.append(
                        f"Dla wideo o ID {vid.id} odnaleziono {len(comments)} komentarzy, a system zadeklarował {official_count}"
                    )

                # Zapisywanie
                save_file(f'yt/{search_term}', vid.id, url, comments, official_count)

                progress_bar.progress((i + 1) / len(vids))
            st.warning("\n - ".join(["Ostrzeżenia:"] + warns))

    except PyYouTubeException as e:
        if (
            e.message
            == 'The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.'
        ):
            st.error("Osiągnięto limit requestów na dziś")
        else:
            raise e

if __name__=='__main__':
    HASLO_WYSZUKIWANE = 'genshin'
    CZY_UWZGLEDNIAC_ODPOWIEDZI = True
    LICZBA_POSTOW = 100
    
    download(HASLO_WYSZUKIWANE, CZY_UWZGLEDNIAC_ODPOWIEDZI, LICZBA_POSTOW)