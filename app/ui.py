# -*- coding: utf-8 -*-

# import from builtin
from sys import exit
# import from kivy
from kivy.uix.modalview import ModalView
from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
# import from userscripts
from dialog import InputPopup, ErrorPopup, EditPopup, YesNoPopup
from manager import Manager
from dataobject import DataPair


class MainView(ModalView):

    def getcurrententry(self):
        file_adapter = self.ids['lvfile'].adapter
        if len(file_adapter.selection) == 0:
            return None
        else:
            fileindex = file_adapter.selection[0].index
            entry = file_adapter.data[fileindex]
            return entry

    def fire_fileview_update(self):
        # update left-side(FILE) listview( Where is explicit function like listview.update()? )
        self.ids['lvfile'].adapter.data = []
        self.ids['lvfile'].adapter.data = self.manager.files
        self.fire_itemview_update()

    def fire_itemview_update(self):
        # update right-side(ITEM) listview
        self.block = True
        self.ids['lvitem'].adapter.data = []
        self.ids['lvitem'].adapter.data = self.getcurrententry().data.pairs
        self.block = False

    def file_sync(self):
        self.manager.update(self.getcurrententry())

    def file_changed(self, file_adapter, *args):
        # update item list
        if len(file_adapter.selection) != 0:
            selected = file_adapter.selection[0]
            file = file_adapter.data[selected.index]
            self.block = True   # block non-manual event
            list_adapter = self.ids['lvitem'].adapter
            list_adapter.data = file.data.pairs
            self.block = False

    def list_changed(self, list_adapter, *args):
        # show item edit dialog
        if len(list_adapter.selection) != 0:
            if not self.block:
                selected = list_adapter.selection[0]
                item = list_adapter.data[selected.index]
                def item_update():
                    self.fire_itemview_update()
                    self.file_sync()
                def item_remove():
                    itemlist = self.getcurrententry().data.pairs
                    itemlist.pop(selected.index)
                    list_adapter.data = itemlist
                    self.manager.update(self.getcurrententry())
                EditPopup(title="Edit", item=item, on_apply=item_update, on_remove=item_remove).open()

    def on_file_add(self):
        def on_apply(inputtext):
            if ('/' in inputtext) or ('\\' in inputtext):
                ErrorPopup(message="You cannot use these characters '/','\\'.").open()
            else:
                success = self.manager.add(inputtext)
                if success:
                    self.fire_fileview_update()
                else:
                    ErrorPopup(message="The name is already used.").open()

        InputPopup(on_apply=on_apply, title='Add new category').open()

    def on_file_remove(self):
        def file_remove():
            self.manager.remove(self.getcurrententry())
            self.fire_fileview_update()

        YesNoPopup(message="Changes can not be undone, is it OK?", title="Remove", yes=file_remove).open()

    def on_file_rename(self):
        def file_rename(newname):
            self.manager.rename(self.getcurrententry(), newname)
            self.fire_fileview_update()

        curname = self.getcurrententry().title
        InputPopup(on_apply=file_rename, defaulttext=curname, title='Change category name').open()

    def on_item_add(self):
        item = DataPair("", "")
        def item_append():
            self.getcurrententry().data.pairs.append(item)
            self.fire_itemview_update()
            self.file_sync()

        EditPopup(title="New item", item=item, on_apply=item_append, removable=False).open()

    def on_change_password(self):
        def change_password(newpass):
            self.manager.update_password(newpass)
        InputPopup(on_apply=change_password, title='Input new password').open()

    def listview_select(self, list_adapter, index):
        view = list_adapter.get_view(index)
        if view:
            list_adapter.handle_selection(view)

    def initialize(self, passphrase):
        self.block = False

        # Make instance of Manager
        manager = Manager(passphrase)
        if not manager.load():
            print('error: Data load failed on initialization. exit.')
            exit()
        self.manager = manager

        # Initialize FILE listview
        def file_args_converter(index, rec):
            return {
                'text': rec.title,
                'size_hint_y': None,
                'height': 60
            }
        file_adapter = ListAdapter(
            data=manager.files,
            args_converter=file_args_converter,
            selection_mode='single',
            allow_empty_selection=False,
            cls=Factory.MyListItem
        )
        file_adapter.bind(on_selection_change=self.file_changed)
        self.ids['lvfile'].adapter = file_adapter

        # Initialize ITEM listview
        def item_args_converter(index, rec):
            return {
                'text': rec.key + ': ' + rec.value,
                'size_hint_y': None,
                'height': 60
            }
        list_adapter = ListAdapter(
            data=[],
            args_converter=item_args_converter,
            selection_mode='single',
            allow_empty_selection=False,
            cls=Factory.MyListItem
        )
        list_adapter.bind(on_selection_change=self.list_changed)
        self.ids['lvitem'].adapter = list_adapter

        # Make drop-down menu( config )
        self.config_menu = Factory.ConfigMenu()
        self.ids['f_config'].bind(on_release=self.config_menu.open)
        def on_select(menu, item):
            if item == 'm_change':
                self.on_change_password()
        self.config_menu.bind(on_select=on_select)

        # Select first file
        self.listview_select(file_adapter, 0)

    def on_start(self, app):
        # Input user password
        def on_apply(passphrase):
            self.initialize(passphrase)  # start initialize
        def on_cancel():
            app.stop()  # end
        InputPopup(on_apply=on_apply, on_cancel=on_cancel, title='Input your password').open()

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        # Wait for on_start event dispatch
        # Password input popup can't open here because eventloop is not started yet.


class PassStoreApp(App):
    def get_application_name(self):
        return "passstore"

    def build(self):
        # Load kv files for UI
        # Builder.load_file("ui.kv")  # load_file use default encoding, so it is bad for some people
        with open("ui.kv", "r", encoding="utf-8") as f:
            Builder.load_string(f.read())  # use load_string as an alternative

        mainview = MainView(width=800)
        self.bind(on_start=mainview.on_start)
        return mainview


if __name__ == '__main__':
    pass
