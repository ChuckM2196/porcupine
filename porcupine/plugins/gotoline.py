from tkinter import simpledialog    # type: ignore

from porcupine import actions, get_tab_manager, tabs


def gotoline() -> None:
    tab = get_tab_manager().select()
    assert isinstance(tab, tabs.FileTab)

    # simpledialog isn't ttk yet, but it's not a huge problem imo
    lineno = simpledialog.askinteger(
        "Go to Line", "Type a line number and press Enter:",
        parent=tab.winfo_toplevel())
    if lineno is not None:    # not cancelled
        # there's no need to do a bounds check because tk ignores out-of-bounds
        # text indexes
        column = tab.textwidget.index('insert').split('.')[1]
        tab.textwidget.mark_set('insert', '%d.%s' % (lineno, column))
        tab.textwidget.see('insert')

    tab.on_focus()


def setup() -> None:
    actions.add_command("Edit/Go to Line", gotoline, '<Control-l>',
                        tabtypes=[tabs.FileTab])
