"""Find URLs in code and make them clickable."""

import tkinter
from typing import Iterable, List, Tuple
import webbrowser

from porcupine import get_tab_manager, tabs, utils


def find_urls(text: tkinter.Text) -> Iterable[Tuple[str, str]]:
    searching_begins_here = '1.0'
    while True:
        match_start = text.search(
            r'\mhttps?://[a-z]', searching_begins_here, 'end',
            nocase=True, regexp=True)
        if not match_start:     # empty string means not found
            break

        # urls end on space, quote or end of line
        end_of_line = f'{match_start} lineend'
        match_end = text.search(r'''["' ]''', match_start, end_of_line, regexp=True) or end_of_line

        # support parenthesized urls and commas/dots after urls
        if text.get(f'{match_end} - 1 char') in {',', '.'}:
            match_end += ' - 1 char'
        if text.get(f'{match_end} - 1 char') in {')', '}', '>'}:    # '}' is useful for tcl code
            match_end += ' - 1 char'

        yield (match_start, match_end)
        searching_begins_here = match_end


def _index2tuple(text_index: str) -> Tuple[int, int]:
    lineno, column = map(int, text_index.split('.'))
    return (lineno, column)


class UrlTagger:

    def __init__(self, textwidget: tkinter.Text) -> None:
        self._tag_count = 0
        self._textwidget = textwidget
        self._bindings: List[str] = []

        self._textwidget.tag_config('clickable_url', underline=True)
        self._textwidget.tag_bind('clickable_url', '<Button-1>', self._on_click, add=True)
        self._textwidget.tag_bind('clickable_url', '<Enter>', self._mouse_enters_url, add=True)
        self._textwidget.tag_bind('clickable_url', '<Leave>', self._mouse_leaves_url, add=True)

    def tag_urls(self, junk: object = None) -> None:
        self._textwidget.tag_remove('clickable_url', '1.0', 'end')
        for start, end in find_urls(self._textwidget):
            self._textwidget.tag_add('clickable_url', start, end)

    def _mouse_enters_url(self, junk: object) -> None:
        self._textwidget['cursor'] = 'hand2'

    def _mouse_leaves_url(self, junk: object) -> None:
        self._textwidget['cursor'] = ''

    def _on_click(self, event: tkinter.Event) -> None:
        cursor = _index2tuple(self._textwidget.index(f'@{event.x},{event.y}'))

        # tag_ranges() is a painful method to use
        ranges = list(map(str, self._textwidget.tag_ranges('clickable_url')))
        for start, end in zip(ranges[0::2], ranges[1::2]):
            if _index2tuple(start) <= cursor <= _index2tuple(end):
                url = self._textwidget.get(start, end)
                webbrowser.open(url)
                break


def on_new_tab(event: utils.EventWithData) -> None:
    tab = event.data_widget()
    if isinstance(tab, tabs.FileTab):
        tagger = UrlTagger(tab.textwidget)
        tab.textwidget.bind('<<ContentChanged>>', tagger.tag_urls, add=True)
        tagger.tag_urls()


def setup() -> None:
    utils.bind_with_data(get_tab_manager(), '<<NewTab>>', on_new_tab, add=True)
