from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, Label, OptionList
from textual.widget import Widget
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual import events
from rich.console import RenderableType
import json
import shared as shared
from  pathlib import Path
import os



class MainMenuOptions(OptionList):    
    
    menuOpts = None         
        
    def allListToOptions(self):        
        print(f'shared: {shared.ROOT_PATH}')
        jsonPath =  os.path.join(shared.ROOT_PATH, 'UIModules/json/UIMenuOptions.json')
        print(jsonPath)
        with open(jsonPath, "r") as f:
            self.menuOpts = json.load(f)["main_menu_option_list"]
        for i in self.menuOpts:
            print(i)
            self.add_option(i)
    def getOptionList(self):
        return self
        

     
class MainMenuSelectionOptionPane(Widget):
    optList = MainMenuOptions()   
    optList.allListToOptions()

    def compose(self) -> ComposeResult:
        yield Container(Label("Main Menu"), self.optList, DisplayData(), id="Main_Menu_Container")

class DisplayData(Static):
    value = reactive("rValue Here")
    def render(self) -> RenderResult:
        return f"Value: {str(self.value)}"