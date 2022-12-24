from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import OneLineAvatarListItem, OneLineAvatarIconListItem
from kivy.properties import StringProperty

class PopupContent(ScrollView):
    pass

class CommandPopup(MDDialog):
    pass

class SavePopupContent(ScrollView):
    pass

class SavePopupContent(ScrollView):
    pass

class ButtonOK(MDRaisedButton):
    pass

class Script(OneLineAvatarIconListItem):
    pass

class Item(OneLineAvatarListItem): #                                                            RENAME IT!!!!     TO DO!!!!
    source = StringProperty()

class CommandWithoutParameters(OneLineAvatarListItem):
    source = StringProperty()