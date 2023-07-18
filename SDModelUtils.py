import shared as shared
import os
from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, Label, OptionList
from textual.widget import Widget
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual import events
from rich.console import RenderableType
import pathlib
from UIModules.components import mainMenu as mainm
class MainApp(App):    
    shared.ROOT_PATH = os.getcwd()       
    print(f'rrot {shared.ROOT_PATH}')
    CSS_PATH = "./SDModelUtils.css"
    BINDINGS = [
        Binding(key='q', action='quit', description="Quit the App"),
        Binding(key='question_mark', 
        action='help', 
        description="Show Help Screen",
        key_display="?")    
    ]
    
    data = mainm.DisplayData
    # mainMenuOpts = mainm.MainMenuOptions()
    # # listOptions = ["1", "2", "3"]
    # mainMenuOpts.allListToOptions()

    def compose(self) -> ComposeResult:
       
        yield Container(TitleHeader())
        yield mainm.MainMenuSelectionOptionPane()
        # yield Container(self.mainMenuOpts, mainm.DisplayData(), id="Main_Menu_Container")                
        yield Footer()

    def on_option_list_option_selected(self, event) -> None:
     self.query_one(mainm.DisplayData).value = event.option_index
    #  self.query_one(mainm.MainMenuOptions).display = False
    

            
class TitleHeader(Static):
    def compose(self) -> ComposeResult:
        yield Container(Label("(c)2023 4a50 Industries"), id="left-middle")
        yield Container(Label("Model Hander for Stable Diffusion"),  id="title-text")
        yield Container(Label("v0.1.0(alpha)"), id="right-middle")


if __name__ == "__main__":    
    
    app = MainApp()
    app.run()
