import threading
import os
#Ask if Java jdk 17 is installed #TODO make it check automatically
user_input = ''
while user_input.lower() not in ('yes', 'no'):
    user_input = input("DO YOU HAVE Java jdk 17 installed? \n Type \"Yes\" or \"No\"(Type \"No\" if you are not sure...)")
if user_input.lower() == "no":
    print("INFO: OK, then install it in the opened window")
    print("WARNING: YOU CANNOT DOWNLOAD MINECRAFT WORLDS BEFORE YOU DO IT.")
    threading.Timer(0.5, os.system, [f'start download_world/jdk-17.0.3.1_windows-x64_bin.exe']).start()
elif user_input.lower() == "yes":
    print("INFO: Ok, I am starting the application")

import kivy
import time
import socket
import bot# DO NOT DELETE THIS LINE. IS USED WITHIN exec() func
import json
import inspect

from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.button import MDFlatButton

kivy.require('2.0.0')

COMMANDS_DELAY = 0.1

from commands import *

#We define these classes here to be able to work with them in the .kv file
from commands_kivy_contents import *

# We define these classes here to be able to work with them in the .kv file
from ui_elements import *

class PenBotApp(MDApp): # kivy automatically connects penbot.kv file by the name of app ("PenBotApp") #TODO rename the app to PenBot

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "Yellow"

        self.all_bots = dict()

        # self.all_commands = { #TODO should we define this parameters in Command's class? #TODO rename all the ids to to the same names as parameters through all the code. So that, I can use the same names in translating commands (in save_script)
        #     'Connect Bot': {
        #         'ui_type': 'MDExpansionPanel',
        #         'icon': 'bot.jpg',
        #         'content': ConnectBotContent,
        #         'command': ConnectBotCommand,
        #         'command_parameters': {                 # Parameter: id
        #             'username': 'nickname', #TODO rename nickname >> username
        #             'ip': 'ip',
        #             'port': 'port',
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'] = bot.Bot'
        #     },
        #     'Move': {
        #         'ui_type': 'MDExpansionPanel',
	    #         'icon': 'move.png',
	    #         'content': MoveContent,
	    #         'command': MoveCommand,
	    #         'command_parameters': {
        #             'axis': 'axis',
        #             'steps': 'steps'
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].move'
        #     },
        #     'Write Message': {
        #         'ui_type': 'MDExpansionPanel',
	    #         'icon': 'chat.png',
	    #         'content': WriteMessageContent,
	    #         'command': WriteMessageCommand,
	    #         'command_parameters': {
        #             'message': 'msg'
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].write_message'
        #     },
        #     'Delay': {
        #         'ui_type': 'MDExpansionPanel',
	    #         'icon': 'delay.jpg',
	    #         'content': DelayContent,
	    #         'command': DelayCommand,
	    #         'command_parameters': {
        #             'delay': 'delay'
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].sleep'
        #     },
        #     'Place Block': {
        #         'ui_type': 'MDExpansionPanel',
	    #         'icon': 'grass_block.png',
	    #         'content': PlaceBlockContent,
	    #         'command': PlaceBlockCommand,
	    #         'command_parameters': {
        #             'offset_x': 'place_offset_x',
        #             'offset_y':'place_offset_y',
        #             'offset_z': 'place_offset_z',
        #             'blockface_str': 'place_blockface'
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].place_block'
        #     },
        #     'Dig Block': {
        #         'ui_type': 'MDExpansionPanel',
        #         'icon': 'pickaxe.png',
        #         'content': DigBlockContent,
        #         'command': DigBlockCommand,
        #         'command_parameters': {
        #             'offset_x': 'dig_offset_x', # TODO Make this names the same and use set instead of dict
        #             'offset_y': 'dig_offset_y',
        #             'offset_z': 'dig_offset_z',
        #             'dig_time': 'dig_time',
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].dig_block'
        #     },
        #     'For Loop Start': {
        #         'ui_type': 'MDExpansionPanel',
        #         'icon': 'loopstart.png',
        #         'content': ForLoopStartContent,
        #         'command': ForLoopStartCommand,
        #         'command_parameters': {
        #             'iters': 'iters'
        #         },
        #         'function_str': None
        #     },
        #     'For Loop End': {
        #         'ui_type': 'Item',
        #         'icon': 'loopend.png',
        #         'content': None,
        #         'command': ForLoopEndCommand,
        #         'command_parameters': None,
        #         'function_str': None
        #     },
        #     'Use Current Item': {
        #         'ui_type': 'Item',
        #         'icon': 'use_item.png',
        #         'content': None,
        #         'command': UseCurrentItemCommand,
        #         'command_parameters': None,
        #         'function_str': 'self.all_bots[\'bot_name\'].use_current_item'
        #     },
        #     'Download World': {
        #         'ui_type': 'Item',
        #         'icon': 'download_world.jpg',
        #         'content': None,
        #         'command': DownloadWorldCommand,
        #         'command_parameters': ['ip', 'port'], #TODO make it look as any other ITEM ui_type object
        #         'function_str': 'bot.start_download_server'
        #     },
        #     'List Xray': {
        #         'ui_type': 'MDExpansionPanel',
        #         'icon': 'list_xray.png',
        #         'content': ListXrayContent,
        #         'command': ListXrayCommand,
        #         'command_parameters': {
        #             'file_name': 'file_name',
        #             'wd': 'wd',
        #             'blocks_limit': 'blocks_limit',
        #             'wanted_blocks': 'wanted_blocks',
        #         },
        #         'function_str': 'bot.create_blocks_dataframe',
        #     },
        #     'Reverse Shell': {
        #         'ui_type': 'MDExpansionPanel',
        #         'icon': 'reverse_shell.png',
        #         'content': ReverseShellContent,
        #         'command': ReverseShellCommand,
        #         'command_parameters': {
        #             'target_os': 'target_os'
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].setup_reverse_shell',
        #     },
        #     'Op': {
        #         'ui_type': 'MDExpansionPanel',
        #         'icon': 'op.png',
        #         'content': OpContent,
        #         'command': OpCommand,
        #         'command_parameters': {
        #             'player': 'player'
        #         },
        #         'function_str': 'self.all_bots[\'bot_name\'].op_player',
        #     },
        # }

    # runs on start of the App
    def on_start(self):
        self.scripts = {}

        # CREATING COMMAND-ADD POPUP #TODO move to another func
        self.popupcontent = PopupContent()

        for command_class in all_commands: # all_commands is a list of command classes in commands.py
            icon_source = r'icons/{}'.format(command_class.icon)
            self.command_item = Item(source=icon_source, text=command_class.name)
            self.popupcontent.ids.list_cmmnds_popup.add_widget(self.command_item)
        self.btn_cancel_command = MDFlatButton(text='Cancel')
        self.popup = MDDialog(title="Command Choosing", type='custom', buttons=[self.btn_cancel_command],
                              content_cls=self.popupcontent, auto_dismiss=False)
        self.btn_cancel_command.on_release = self.popup.dismiss

        # CREATING SAVE-SCRIPT POPUP #TODO move to another func
        self.savepopupcontent = SavePopupContent()
        self.btn_cancel_save = MDFlatButton(text="Cancel")
        self.savepopup = MDDialog(
            title='Saving Script',
            type='custom',
            buttons=[self.btn_cancel_save, MDRaisedButton(text='OK', on_release=self.save_script)],
            content_cls=self.savepopupcontent,
            auto_dismiss=False
        )
        self.btn_cancel_save.on_release = self.savepopup.dismiss

    # opening popup to choose command
    def cmmnd_popup(self): #TODO rename to open_command_choosing
        self.popup.open()

    # adding command
    def cmmnd_add(self, command_panel): #TODO rename
        name = command_panel.text
        command_class = get_command_class(name)

        if command_class.ui_type == 'MDExpansionPanel':
            cmmnd_to_add = MDExpansionPanel(
            								icon=command_panel.source, 
            								panel_cls=MDExpansionPanelOneLine(text=name), 
            								content=command_class.content()
            								)
        elif command_class.ui_type == "Item":
            cmmnd_to_add = CommandWithoutParameters(source=command_panel.source, text=name)

        self.root.ids.list_cmmnds.add_widget(cmmnd_to_add)
        self.popup.dismiss()
    
    def close_save_popup(self, *args): #TODO rename close_command_choosing
        self.savepopup.dismiss()

    def clear_script(self):
        self.root.ids.list_cmmnds.clear_widgets()
        #self.root.ids.list_cmmnds.add_widget(self.create_bot_cmmnd) #TODO Remove to use connect Bot command manually

    def save_popup(self):
        # Opening popup to save script
        self.savepopup.open()

    def save_script(self, button):
        name = self.savepopupcontent.ids['save_name'].text
        self.script = Script(text=name)
        self.script.cmmnds = [] #TODO do we need this line??
        self.savepopup.dismiss()

        # TRANSLATING COMMANDS
        try:
            self.commands_panel_list = self.root.ids.list_cmmnds.children[-1::-1] #TODO why do we reverse this?

            for cmmnd_panel in self.commands_panel_list:
                try: command_name = cmmnd_panel.panel_cls.text
                except AttributeError: command_name = cmmnd_panel.text
                command_class = get_command_class(command_name)
                user_input = get_user_input(cmmnd_panel, command_class)
                command = command_class(*user_input)
                print(command)
                self.script.cmmnds.append(command)

            self.root.ids.list_scripts.add_widget(self.script)

            #Setting indexes
            for k in range(len(self.script.cmmnds)):
                self.script.cmmnds[k].index = k

            self.scripts[name] = self.script.cmmnds
            print(self.script.cmmnds)

        except ValueError as e:
            print('WARNING', e)
            raise_error_popup('Please, check if all the command data is correct.')

    def play_script_with_threading(self, script): #TODO Rename it, it's a kivy object (script)
        """Making scripts work in parallel"""
        threading.Timer(0, lambda script: self.play_script(script), [script]).start()

    def play_script(self, script_widget): #TODO Rename it, it's a kivy object (script)
        # Running commands
        script_name = script_widget.text
        script = self.scripts[script_name]
        connect_bot_command = get_command(script , ConnectBotCommand)
        if connect_bot_command: bot_name = connect_bot_command.username
        else: bot_name = ''
        try:
            if get_command(script, ForLoopStartCommand):
                print("SCRIPT WAS: ")
                print(script)
                script = uncover_for_loops_in_script(script)
                print("SCRIPT IS: ")
                print(script)
            for command in script: #TODO добавь проверку, скачивает ли бот мир сейчас. Bot().connect_localhost. Если да, конекти его к локалхост
                command.execute(app, bot_name)
                time.sleep(COMMANDS_DELAY)

        except ValueError as e:
            print('WARNING', e)
            raise_error_popup('Please, check if all the command data is correct.')

        except socket.gaierror as e:
            print('WARNING', e)
            raise_error_popup('Check if all the connection data is correct.')

def uncover_for_loops_in_script(script): #TODO check if we really need bot_name here #TODO make it uncover recursively #TODO why does it skip 2nd iteration? # TODO!!! Add an "index" parameter for command classes. So you can check their pos in script # TO-DO 2. Make it work with only For_loop_start instance given
    #Detecting all For Loop commands and their indexes
    fl_start_indexes = []
    fl_stop_indexes = []
    for command in script:
        if command.name == "For Loop Start": fl_start_indexes.append(command.index)
        elif command.name == "For Loop End": fl_stop_indexes.append(command.index)
    #Check if all loops are closed
    if len(fl_start_indexes) != len(fl_stop_indexes):
        print('WARNING', "Some For Loops are not closed")
        raise_error_popup('Please, close all the For Loops.')
        return None

    #Duplicate commands by number of iterations
    for k in range(len(fl_start_indexes)):
        start_loop_command = script[fl_start_indexes[k]]
        iters = int(start_loop_command.iters)
        repeated_commands = script[fl_start_indexes[k]+1:fl_stop_indexes[-1-k]]*iters

        #Remove the For Loop from the initial script
        updated_script = []
        command_indexes_to_be_removed = range(fl_start_indexes[k],fl_stop_indexes[-1-k]+1)
        for command in script:
            if command.index not in command_indexes_to_be_removed:
                updated_script.append(command)

        #Insert the repeated commands to the script
        index_to_insert = fl_start_indexes[k]
        for command in repeated_commands[::-1]: #[::-1] inserting in the reverse sequence
            updated_script.insert(index_to_insert, command)

    #Update the idexes of commands
    for i in range(len(updated_script)):
        updated_script[i].index = i

    #Recursion
    if get_command(updated_script, ForLoopStartCommand):
        updated_script = uncover_for_loops_in_script(updated_script)

    return updated_script

def raise_error_popup(text):
    button_ok = MDRaisedButton(text="OK")
    info_popup = MDDialog(title='ERROR', text=text, auto_dismiss=False, type='custom', buttons=[button_ok])
    info_popup.buttons[0].on_release = info_popup.dismiss
    info_popup.open()

def get_command(commands_list, wanted_command):#TODO rename to get_command_instance
    for command in commands_list:
        if isinstance(command, wanted_command): return command
    return None

def get_user_input(widget, command_class):
    command_args = inspect.getfullargspec(command_class.__init__).args[1:]
    user_input = []
    for arg in command_args:
        user_input.append(eval(f"widget.content.ids.{arg}.text")) # Kivy TextFields have the same names as args of init func of Command Classes
    print(user_input)
    return user_input

def get_command_class(command_name):
    return eval("".join(command_name.split(' ') + ['Command']))

if __name__ == "__main__":
    app = PenBotApp()
    app.run()
