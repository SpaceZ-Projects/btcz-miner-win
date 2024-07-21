
import os
import asyncio
import subprocess
import psutil
import re

from toga import (
    App,
    Box,
    Label,
    Selection,
    TextInput,
    Button,
    Divider,
    ScrollContainer
)
from toga.widgets.base import Widget
from toga.constants import Direction
from toga.colors import WHITE, RED, YELLOW, BLACK

from .styles.box import BoxStyle
from .styles.label import LabelStyle
from .styles.selection import SelectionStyle
from .styles.input import InputStyle
from .styles.button import ButtonStyle
from .styles.container import ContainerStyle

from .download import DownloadMiniZ, DownloadGminer, DownloadLolminer




class MiningWindow(Box):
    def __init__(
        self,
        app:App,
        id: str | None = None,
        style=None,
        children: list[Widget] | None = None,
    ):
        style = BoxStyle.mining_main_box
        super().__init__(id, style, children)
        self.app = app

        data_path = self.app.paths.data
        self.miners_dir = os.path.join(data_path)

        
        self.select_miner_txt = Label(
            "Select Miner :",
            style=LabelStyle.select_miner_txt
        )
        self.select_miner = Selection(
            items=[
                {"miner": ""},
                {"miner": "MiniZ"},
                {"miner": "Gminer"},
                {"miner": "Lolminer"}
            ],
            accessor="miner",
            style=SelectionStyle.select_miner,
            on_change=self.verify_miners_apps
        )
        self.select_miner_box = Box(
            style=BoxStyle.select_miner_box
        )
        self.select_pool_txt = Label(
            "Mining Pool :",
            style=LabelStyle.select_pool_txt
        )
        self.select_pool = Selection(
            items=[
                {"pool": ""},
                {"pool": "2Mars"},
                {"pool": "Darkfibersmines"},
                {"pool": "PCmining"},
                {"pool": "Swgroupe"}
            ],
            accessor="pool",
            style=SelectionStyle.select_pool,
            on_change=self.update_server_selection
        )
        self.select_pool_box = Box(
            style=BoxStyle.select_pool_box
        )
        self.select_server_txt = Label(
            "Server :",
            style=LabelStyle.select_server_txt
        )
        self.select_server = Selection(
            enabled=False,
            style=SelectionStyle.select_server,
            accessor="region"
        )
        self.select_server_box = Box(
            style=BoxStyle.select_server_box
        )
        self.worker_name_txt = Label(
            "Worker :",
            style=LabelStyle.worker_name_txt
        )
        self.worker_name = TextInput(
            placeholder= "Worker Name",
            style=InputStyle.worker_name
        )
        self.worker_name_box = Box(
            style=BoxStyle.worker_name_box
        )
        self.address_txt = Label(
            "Address :",
            style=LabelStyle.select_address_txt
        )
        self.address_input = TextInput(
            placeholder="Paste T address",
            style=InputStyle.address_input
        )
        self.address_box = Box(
            style=BoxStyle.select_address_box
        )
        self.mining_button = Button(
            "Start",
            enabled=True,
            style=ButtonStyle.mining_button,
            on_press=self.verify_mining_params
        )
        self.divider = Divider(
            direction=Direction.HORIZONTAL
        )
        self.mining_output_box = Box(
            style=BoxStyle.mining_output_box
        )
        self.mining_output = ScrollContainer(
            content=self.mining_output_box,
            style=ContainerStyle.mining_output
        )
        
        self.app.add_background_task(
            self.display_window
        )

    
    async def display_window(self, widget):
        self.app.commands.clear()
        self.select_miner.value = self.select_miner.items[0]
        self.select_pool.value = self.select_pool.items[0]
        self.select_miner_box.add(
            self.select_miner_txt,
            self.select_miner
        )
        self.select_pool_box.add(
            self.select_pool_txt,
            self.select_pool
        )
        self.select_server_box.add(
            self.select_server_txt,
            self.select_server
        )
        self.worker_name_box.add(
            self.worker_name_txt,
            self.worker_name
        )
        self.address_box.add(
            self.address_txt,
            self.address_input
        )
        self.add(
            self.select_miner_box,
            self.select_pool_box,
            self.select_server_box,
            self.worker_name_box,
            self.address_box,
            self.mining_button,
            self.divider,
            self.mining_output
        )
        await asyncio.sleep(1)
        self.app.main_window.show()
    


    async def verify_miners_apps(self, selection):
        selected_value = self.select_miner.value.miner
        miners = {
            "MiniZ": {
                "executable": "miniZ.exe",
                "dir_name": "MiniZ"
            },
            "Gminer": {
                "executable": "miner.exe",
                "dir_name": "Gminer"
            },
            "Lolminer": {
                "executable": "lolMiner.exe",
                "dir_name": "Lolminer"
            }
        }
        if not os.path.exists(self.miners_dir):
            os.makedirs(self.miners_dir)

        if selected_value in miners:
            miner_details = miners[selected_value]
            miner_executable = miner_details["executable"]
            miner_dir = os.path.join(self.miners_dir, miner_details["dir_name"])
            miner_path = os.path.join(miner_dir, miner_executable)

            if not os.path.exists(miner_dir):
                await self.ask_for_download(selected_value, miner_dir)
            elif not os.path.exists(miner_path):
                await self.ask_for_download(selected_value, miner_dir)

    
            
    async def ask_for_download(self, selected_app, miner_dir):
        async def on_confirm(window, result):
            if result is True:
                self.select_miner.enabled = False
                if not os.path.exists(miner_dir):
                    os.makedirs(miner_dir, exist_ok=True)
                if selected_app == "MiniZ":
                    DownloadMiniZ(
                        self.app,
                        self.select_miner,
                        miner_dir
                    )
                elif selected_app == "Gminer":
                    DownloadGminer(
                        self.app,
                        self.select_miner,
                        miner_dir
                    )
                elif selected_app == "Lolminer":
                    DownloadLolminer(
                        self.app,
                        self.select_miner,
                        miner_dir
                    )

            if result is False:
                self.select_miner.value = self.select_miner.items[0]
        self.app.main_window.question_dialog(
            "Download miner...",
            f"{selected_app} was not found in {miner_dir}. Would you like to download it?",
            on_result=on_confirm
        )

    
    async def update_server_selection(self, selection):
        selected_value = self.select_pool.value.pool
        if selected_value == "2Mars":
            server_items = [
                {"region": "Canada", "server": "btcz.ca.2mars.biz:1234"},
                {"region": "USA", "server": "btcz.us.2mars.biz:1234"},
                {"region": "Netherlands", "server": "btcz.eu.2mars.biz:1234"},
                {"region": "Singapore", "server": "btcz.sg.2mars.biz:1234"}
            ]
        elif selected_value == "Darkfibersmines":
            server_items = [
                {"region": "USA", "server": "142.4.211.28:4000"},
            ]
        elif selected_value == "PCmining":
            server_items = [
                {"region": "Germany", "server": "btcz.pcmining.xyz:3333"}
            ]
        elif selected_value == "Swgroupe":
            server_items = [
                {"region": "France", "server": "swgroupe.fr:2001"}
            ]
        else:
            self.select_server.items.clear()
            self.select_server.enabled = False
            return
        
        self.select_server.items = server_items
        self.select_server.enabled = True


    
    async def verify_mining_params(self, button):
        if not self.select_miner.value.miner:
            self.app.main_window.error_dialog(
                "Missing Miner Selection",
                "Please select a mining application."
            )
            return
        elif not self.select_pool.value.pool:
            self.app.main_window.error_dialog(
                "Missing Pool Selection",
                "Please select a mining pool."
            )
            return
        elif not self.worker_name.value:
            self.app.main_window.error_dialog(
                "Missing Worker Name",
                "Please set a worker name."
            )
            self.worker_name.focus()
            return
        elif not self.address_input.value:
            self.app.main_window.error_dialog(
                "Missing Address",
                "Please set a your mining address."
            )
            self.address_input.focus()
            return
        else:
            self.mining_button_stop()
            self.disable_params()
            await self.prepare_mining_command()



    async def prepare_mining_command(self):

        selected_miner = self.select_miner.value.miner
        selected_server = self.select_server.value.server
        worker_name = self.worker_name.value
        address = self.address_input.value
        miners_dir = os.path.join(self.app.paths.data)
        miner_path = os.path.join(miners_dir, selected_miner)
        if selected_miner == "MiniZ":
            miner_file = os.path.join(miner_path, 'miniZ.exe')
            command = [f'{miner_file} --url {address}.{worker_name}@{selected_server} --pass x --par 144,5 --pers BitcoinZ']
        elif selected_miner == "Gminer":
            miner_file = os.path.join(miner_path, 'miner.exe')
            command = [f'{miner_file} --server {selected_server} --user {address}.{worker_name} --algo 144_5 --pers BitcoinZ']
        elif selected_miner == "Lolminer":
            miner_file = os.path.join(miner_path, 'lolMiner.exe')
            command = [f'{miner_file}  --pool {selected_server} --user {address}.{worker_name} -a EQUI144_5 --pers BitcoinZ']
        print(command)

        await self.start_mining_command(command)



    async def start_mining_command(self, command):
        try:
            self.process = await asyncio.create_subprocess_shell(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.mining_button.on_press = self.stop_mining
            self.mining_button.enabled = True
            clean_regex = re.compile(r'\x1b\[[0-9;]*[mGK]|[^a-zA-Z0-9\s\[\]=><.%()/,`\'":]')
            while True:
                stdout_line = await self.process.stdout.readline()
                if stdout_line:
                    decoded_line = stdout_line.decode().strip()
                    cleaned_line = clean_regex.sub('', decoded_line)
                    mining_output_txt = Label(
                        cleaned_line,
                        style=LabelStyle.mining_output_txt
                    )
                    self.mining_output_box.add(
                        mining_output_txt
                    )
                    self.mining_output.vertical_position = self.mining_output.max_vertical_position
                else:
                    break
            await self.process.wait()

            remaining_stdout = await self.process.stdout.read()
            remaining_stderr = await self.process.stderr.read()
            
            if remaining_stdout:
                remaining_stdout_txt = Label(
                    remaining_stdout.decode().strip(),
                    style=LabelStyle.mining_output_txt
                )
                self.mining_output_box.add(
                    remaining_stdout_txt
                )
            if remaining_stderr:
                remaining_stderr_txt = Label(
                    remaining_stderr.decode().strip(),
                    style=LabelStyle.mining_output_txt
                )
                self.mining_output_box.add(
                    remaining_stderr_txt
                )

        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            self.add_mining_button()
            self.enable_params()

    

    async def stop_mining(self, button):
        selected_miner = self.select_miner.value.miner
        if selected_miner == "MiniZ":
            process_name =  "miniZ.exe"
        elif selected_miner == "Gminer":
            process_name = "miner.exe"
        elif selected_miner == "Lolminer":
            process_name = "lolMiner.exe"
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    print(f"Killing process {proc.pid} - {proc.info['name']}...")
                    proc.kill()
            print(f"All processes named {process_name} killed.")
            self.process.terminate()
        except Exception as e:
            print(f"Exception occurred while killing process: {e}")
    

    def disable_params(self):
        self.select_miner.enabled = False
        self.select_pool.enabled = False
        self.select_server.enabled = False
        self.worker_name.readonly = True
        self.address_input.readonly = True


    def enable_params(self):
        self.select_miner.enabled = True
        self.select_pool.enabled = True
        self.select_server.enabled = True
        self.worker_name.readonly = False
        self.address_input.readonly = False
    
    
    def add_mining_button(self):
        self.app.on_exit = self.close_window
        self.mining_button.style.color = BLACK
        self.mining_button.style.background_color = YELLOW
        self.mining_button.text = "Start"
        self.mining_button.on_press = self.verify_mining_params
        self.mining_button.enabled = True

    
    def mining_button_stop(self):
        self.app.on_exit = self.disable_closing_window
        self.mining_button.enabled = False
        self.mining_button.style.color = WHITE
        self.mining_button.style.background_color = RED
        self.mining_button.text = "Stop"
    

    def disable_closing_window(self, window):
        return


        
    def close_window(self, window):
        self.app.exit()