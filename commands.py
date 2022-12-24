from minecraft.networking.packets.serverbound.play import PlayerBlockPlacementPacket
from commands_kivy_contents import *
import bot

#IMPORTANT: command parameters must have the same variable names throughout all the scripts (penbot.kv -> commands.py -> bot.py)

class MoveCommand:
    name = 'Move'
    priority = 0 # Executing priority. Commands with higher one will be executed first #TODO check if its needed at all
    ui_type = 'MDExpansionPanel'
    icon = 'move.png'
    content = MoveContent
    def __init__(self, axis, steps):
        self.axis = axis
        self.steps = steps

    def execute(self, app, bot_name):
        app.all_bots[bot_name].move(self)

class WriteMessageCommand: #TODO rename to write message
    name = 'Write Message'
    priority = 0  # Executing priority. Commands with higher one will be executed first #TODO check if its needed at all
    ui_type = 'MDExpansionPanel'
    icon = 'chat.png'
    content = WriteMessageContent
    def __init__(self, message):
        self.message = message

    def execute(self, app, bot_name):
        app.all_bots[bot_name].write_message(self)

class ConnectBotCommand:
    name = 'Connect Bot'
    priority = 1
    connect_localhost = False # Used to determine if connecting to download_world server #TODO check if its needed at all
    ui_type = 'MDExpansionPanel'
    icon = 'bot.jpg'
    content = ConnectBotContent
    def __init__(self, username, ip, port):
        self.username = username
        self.ip = ip
        self.port = port

    def execute(self, app, bot_name):
        try:
            if not app.all_bots[bot_name].connection.connected:
                app.all_bots[bot_name] = bot.Bot(self)
        except KeyError:
            app.all_bots[bot_name] = bot.Bot(self)

class DelayCommand:
    name = 'Delay'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'delay.jpg'
    content = DelayContent
    def __init__(self, delay):
        self.delay = delay

    def execute(self, app, bot_name):
        app.all_bots[bot_name].sleep(self)

class PlaceBlockCommand:
    name = 'Place Block'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'grass_block.png'
    content = PlaceBlockContent
    inside_block = False
    hand = PlayerBlockPlacementPacket.Hand.MAIN
    def __init__(self, place_offset_x, place_offset_y, place_offset_z, blockface_str): #TODO pass parameters via dictionary
        self.place_offset_x = place_offset_x
        self.place_offset_y = place_offset_y
        self.place_offset_z = place_offset_z
        self.blockface_str = blockface_str

    def execute(self, app, bot_name):
        app.all_bots[bot_name].place_block(self)

class ForLoopStartCommand: # TODO RENAME "for loop" to "repeat"
    name = 'For Loop Start'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'loopstart.png'
    content = ForLoopStartContent
    def __init__(self, iters):
        self.iters = iters

class ForLoopEndCommand:
    name = 'For Loop End'
    priority = 0
    ui_type = 'Item'
    icon = 'loopend.png'
    def __init__(self):
        pass

class UseCurrentItemCommand:
    name = 'Use Current Item'
    priority = 0
    ui_type = 'Item'
    icon = 'use_item.png'
    hand = "MAIN"
    def __init__(self):
        pass

    def execute(self, app, bot_name):
        app.all_bots[bot_name].use_current_item(self)

class DigBlockCommand:
    name = 'Dig Block'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'pickaxe.png'
    content = DigBlockContent
    def __init__(self, dig_offset_x, dig_offset_y, dig_offset_z, dig_time): #TODO pass parameters via dictionary
        self.dig_offset_x = dig_offset_x
        self.dig_offset_y = dig_offset_y
        self.dig_offset_z = dig_offset_z
        self.dig_time = dig_time

    def execute(self, app, bot_name):
        app.all_bots[bot_name].dig_block(self)

class DownloadWorldCommand: #TODO Rename to "Start Download Server"?
    name = 'Download World'
    priority = 0
    ui_type = 'Item'
    icon = 'download_world.jpg'
    def __init__(self, **kwargs):
        pass

    def execute(self, app, bot_name):
        bot.start_download_server()

class ListXrayCommand:
    name = 'List Xray'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'list_xray.png'
    content = ListXrayContent
    def __init__(self, file_name, wd, blocks_limit, wanted_blocks): #TODO pass parameters via dictionary
        self.file_name = file_name
        self.wd = wd
        self.blocks_limit = blocks_limit
        self.wanted_blocks = wanted_blocks

    def execute(self, app, bot_name): #TODO Remove not-used parameters
        bot.create_blocks_dataframe(self)

class ReverseShellCommand:
    name = 'Reverse Shell'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'reverse_shell.png'
    content = ReverseShellContent
    def __init__(self, rce_ssh_host, ssh_password, target_os):
        self.target_os = target_os
        self.rce_ssh_host = rce_ssh_host
        self.ssh_password = ssh_password

    def execute(self, app, bot_name):
        app.all_bots[bot_name].setup_reverse_shell(self)

class OpCommand:
    name = 'Op'
    priority = 0
    ui_type = 'MDExpansionPanel'
    icon = 'op.png'
    content = OpContent
    def __init__(self, op_ssh_host, player):
        self.op_ssh_host = op_ssh_host
        self.player = player

    def execute(self, app, bot_name):
        app.all_bots[bot_name].op_player(self)

all_commands = (
                MoveCommand, WriteMessageCommand,
                ConnectBotCommand, DelayCommand,
                PlaceBlockCommand, ForLoopStartCommand,
                ForLoopEndCommand, UseCurrentItemCommand,
                DigBlockCommand, DownloadWorldCommand,
                ListXrayCommand, ReverseShellCommand,
                OpCommand,
                )
