# -*- coding: utf-8 -*-

from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.clipboard import Clipboard

with open("dialog.kv", "r", encoding="utf-8") as f:
    Builder.load_string(f.read())


class InputPopup(Popup):
    defaulttext = StringProperty()

    def __init__(self, on_apply, on_cancel=None, defaulttext='', **kwargs):
        self.apply = on_apply
        self.cancel = on_cancel
        self.defaulttext = defaulttext
        super(InputPopup, self).__init__(**kwargs)

    def on_test(self):
        print('test')

    def on_cancel(self):
        if self.cancel:
            self.cancel()
        self.dismiss()

    def on_ok(self):
        self.apply(self.ids['text'].text)
        self.dismiss()


class ErrorPopup(Popup):
    message = StringProperty()

    def __init__(self, message, **kwargs):
        self.message = message
        super(ErrorPopup, self).__init__(**kwargs)

    def on_press(self):
        self.dismiss()


class YesNoPopup(Popup):
    message = StringProperty()

    def __init__(self, message, yes=None, no=None, **kwargs):
        self.message = message
        self.yes = yes
        self.no = no
        super(YesNoPopup, self).__init__(**kwargs)

    def on_yes(self):
        if self.yes is not None:
            self.yes()
        self.dismiss()

    def on_no(self):
        if self.no is not None:
            self.no()
        self.dismiss()


class EditPopup(Popup):
    removable = BooleanProperty()

    def __init__(self, item, on_apply=None, on_remove=None, removable=True, **kwargs):
        self.item = item
        self.callback_apply = on_apply
        self.callback_remove = on_remove
        self.removable = removable
        super(EditPopup, self).__init__(**kwargs)

    def copy_text(self, text):
        Clipboard.copy(text)

    def on_key(self):
        def on_yes():
            self.copy_text(self.item.key)
        message = "'" + self.item.key + "'" + "will be copied to the clipboard"
        YesNoPopup(title='Confirm', message=message, yes=on_yes).open()

    def on_value(self):
        def on_yes():
            self.copy_text(self.item.value)
        message = "'" + self.item.value + "'" + "will be copied to the clipboard"
        YesNoPopup(title='Confirm', message=message, yes=f).open()

    def on_cancel(self):
        self.dismiss()

    def on_apply(self):
        key = self.ids['t_key'].text
        value = self.ids['t_value'].text
        if key.find(':') != -1 or value.find(':') != -1:
            ErrorPopup(title="Error", message="You cannot use the character ':'").open()
            return
        else:
            # data update
            self.item.key = key
            self.item.value = value
            # callback
            if self.callback_apply is not None:
                self.callback_apply()
            self.dismiss()

    def on_remove(self):
        def on_yes():
            if self.callback_remove is not None:
                self.callback_remove()
            self.dismiss()
        message = "Changes can not be undone, is it OK?"
        YesNoPopup(title="Remove", message=message, yes=on_yes).open()


if __name__ == '__main__':
    pass
