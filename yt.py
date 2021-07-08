from genericpath import isfile
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
    """
    Funkcja wykonująca wyszukiwanie, oryginał z pyyoutube nie spełniał stawianych wymagań

    :param api: Obiekt API reprezentujący połączenie z YouTube API
    :type api: Api
    :param q: Zapytanie
    :type q: str
    :param amount: Liczba
    :type amount: int
    :return: [description]
    :rtype: [type]
    """
    args = {"part": None, "q": q, "type": "video", "maxResults": amount}
    if amount <= 0:
        st.error(
            "`pyyoutube` nie dopuszcza *zerowych ilości*, ale można wpisać absurdalnie wysoką wartość"
        )
        st.stop()

    res_data = api.paged_by_page_token(resource="search", args=args, count=amount)

    return SearchListResponse.from_dict(res_data)


@st.cache
def find_videos(api: Api, search_term: str, amount: int) -> list[SearchResult]:
    """
    Zbiera listę wszystkich wyników wyszukiwania na bazie podanego hasła
    """
    return new_search(api, q=search_term, amount=amount)


def get_videos(api: Api, results: SearchListResponse):
    """
    Zwraca filmy dla podanych wyników wyszukiwania
    """
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


def get_comments(api: Api, thread: CommentThread, collect_replies: bool) -> list[str]:
    """
    Pobiera komentarze w danym wątku

    :param api: obiekt API reprezentujący połączenie
    :type api: Api
    :param thread: Wątek komentarzy
    :type thread: CommentThread
    :param collect_replies: Czy pobierać odpowiedzi na komentarze?
    :type collect_replies: bool
    :return: Lista sformatowanych komentarzy
    :rtype: list[str]
    """
    first = thread.snippet.topLevelComment
    comments = [
        comment_format(first.snippet.authorDisplayName, first.snippet.textDisplay)
    ]

    if collect_replies and thread.replies:
        if thread.snippet.totalReplyCount > len(thread.replies.comments):
            with st.spinner(f"Pobieranie {thread.snippet.totalReplyCount} odpowiedzi"):
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


def download(search_term: str, collect_replies: bool, amount: int, omit: bool):
    """
    Główna funkcja - wykonuje przeszukiwanie, a następnie iterując po postach zbiera i zapisuje sformatowane komentarze do pliku XML

    :param search_term: Pojęcie do wyszukiwania
    :type search_term: str
    :param collect_replies: Czy pobierać odpowiedzi do komentarzy?
    :type collect_replies: bool
    :param amount: Liczba postów do pobrania, 0 pobiera wszystkie
    :type amount: int
    :param omit: Czy pomijać już pobrane dane?
    :type omit: bool
    """
    api = Api(api_key=YT_KEY)

    try:

        with st.spinner("Zbieranie wyników wyszukiwania"):
            result = find_videos(api, search_term, amount)
            vids = get_videos(api, result)
            st.info(f"Znaleziono {len(vids)} filmów")

        with st.spinner("Zbieranie komentarzy i informacji o filmach"):
            progress_bar = st.progress(0 / len(vids))
            warns = []
            omitted = 0
            for i, vid in enumerate(vids):

                # Pomijanie istniejących plików
                if omit and isfile(f"yt/{search_term}/{vid.id}.xml"):
                    omitted += 1
                    continue

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
                    (get_comments(api, thread, collect_replies) for thread in threads),
                    [],
                )
                if collect_replies and len(comments) != official_count:
                    warns.append(
                        f"Dla wideo o ID {vid.id} odnaleziono {len(comments)} komentarzy, a system zadeklarował {official_count}"
                    )

                # Zapisywanie
                save_file(f"yt/{search_term}", vid.id, url, comments, official_count)

                progress_bar.progress((i + 1) / len(vids))

        if omitted > 0:
            warns.append(
                f"Program pominął {omitted} postów, gdyż ich pliki już istniały."
            )
        if warns:
            st.warning("\n - ".join(["**Ostrzeżenia**:"] + warns))

    except PyYouTubeException as e:
        if (
            e.message
            == 'The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.'
        ):
            st.error("Osiągnięto limit requestów na dziś")
        else:
            raise e


# Wpisując w poniższe pola odpowiednie wartości i uruchamiając ten plik można korzystać z programu bez interfejsu
if __name__ == "__main__":
    HASLO_WYSZUKIWANE = ""
    CZY_UWZGLEDNIAC_ODPOWIEDZI = True
    CZY_POMIJAC_ISTNIEJACE_PLIKI = True
    LICZBA_POSTOW = 100

    download(
        HASLO_WYSZUKIWANE,
        CZY_UWZGLEDNIAC_ODPOWIEDZI,
        LICZBA_POSTOW,
        CZY_POMIJAC_ISTNIEJACE_PLIKI,
    )
