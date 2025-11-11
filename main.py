#!/usr/bin/env python3


from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Container

from textual.events import Mount
from textual.widgets import Header, SelectionList, Input, Button, Static
from textual.widgets.selection_list import Selection
from lollypop import Lollypop, LollypopPlaylist


class SelectionListApp(App[None]):
    CSS_PATH = "main.tcss"
    TITLE = "Pop Mix"
    SUB_TITLE = " Playlist creator for Lollypop"

    def compose(self) -> ComposeResult:
        self.lollypop = Lollypop()
        self.tracks = self.lollypop.get_tracks()
        self.selections = [(str(track), track.id) for track in self.tracks]
        self.filtered = self.selections
        self.lollypop.close()
        self.selected = []

        yield Header()
        with Horizontal(id="search_container"):
            yield Input(placeholder="Search", id="search")
            yield Button("Select All", variant="warning", id="select_all")
            yield Button("Deselect All", variant="error", id="deselect_all")
        with Horizontal(id="main"):
            self.selection_list = SelectionList(*self.selections)
            yield self.selection_list
            self.selected_list = VerticalScroll(id="selected")
            yield self.selected_list
        with Horizontal(id="playlist"):
            yield Input(placeholder="Playlist name", id="playlist_name")
            yield Button("Create", variant="primary", id="submit")

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "All Songs"
        self.query_one(VerticalScroll).border_title = "Selected Songs"

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.selected_list.remove_children()
        self.selected = [
            item
            for item in self.selections
            if item[1] in self.query_one(SelectionList).selected
        ]
        for item in self.selected:
            self.selected_list.mount(Static(item[0]))

    @on(Input.Changed)
    def handle_input(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self.filtered = [
                item
                for item in self.selections
                if event.value.lower() in item[0].lower()
            ]
            self.selection_list.set_options(self.filtered)

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        sel_list = self.query_one(SelectionList)
        if event.button.id == "submit":
            name = self.query_one("#playlist_name").value.strip()
            if len(name) < 1:
                self.notify("Playlist name cant be empty", severity="error")
            elif len(self.selected) < 1:
                self.notify("Selection cant be empty", severity="error")
            else:
                selected_ids = [item[1] for item in self.selected]
                uris = [track.uri for track in self.tracks if track.id in selected_ids]
                lp = LollypopPlaylist()
                lp.create(name, uris)
                self.notify(f"Created playlist: {name} ({len(uris)} tracks)")
                sel_list.deselect_all()
                self.query_one("#playlist_name").clear()
                self.query_one("#search").clear()

        elif event.button.id == "select_all":
            if len(self.filtered) > 20:
                self.notify(
                    "Can not select more than 20 item in one go", severity="error"
                )
            else:
                for item in self.filtered:
                    sel_list.select(Selection(item[0], item[1]))
        elif event.button.id == "deselect_all":
            if len(self.filtered) > 20:
                self.notify(
                    "Can not deselect more than 20 item in one go", severity="error"
                )
            else:
                for item in self.filtered:
                    sel_list.deselect(Selection(item[0], item[1]))


if __name__ == "__main__":
    SelectionListApp().run()
