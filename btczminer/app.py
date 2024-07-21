
from toga import (
    App,
    MainWindow
)

from .miner import MiningWindow


class BTCZMiner(App):
    @property
    def version(self):
        return self._version
    @version.setter
    def version(self, value):
        self._version = value

    @property
    def formal_name(self):
        return self._formal_name
    @formal_name.setter
    def formal_name(self, value):
        self._formal_name = value
        
    @property
    def app_id(self):
        return self._app_id
    @app_id.setter
    def app_id(self, value):
        self._app_id = value

    @property
    def home_page(self):
        return self._home_page
    @home_page.setter
    def home_page(self, value):
        self._home_page = value

    @property
    def author(self):
        return self._author
    @author.setter
    def author(self, value):
        self._author = value

    def windows_screen_center(self, size):
        
        screen_size = self.app.screens[0].size
        screen_width, screen_height = screen_size
        window_width, window_height = size
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        return (x, y)
        
        
    def startup(self):

        self.main_window = MainWindow(
            title=self.formal_name,
            size=(800, 550),
            resizable=False,
            minimizable=False
        )
        position_center = self.windows_screen_center(
                self.main_window.size
        )
        self.main_window.position = position_center
        self.main_window.content = MiningWindow(self.app)


def main():
    app = BTCZMiner()
    app.icon="resources/app_logo"
    app.formal_name = "BTCZ-Miner"
    app.app_id = "com.btcz"
    app.home_page = "https://www.getbtcz.com"
    app.author = "BTCZCommunity"
    app.version = "1.0.0"
    return app


def main():
    return BTCZMiner()
