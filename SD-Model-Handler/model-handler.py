from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, Label, OptionList
from textual.widget import Widget
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual import events
from rich.console import RenderableType
from UIModules import mainMenu as mainm


    


class MainApp(App):
    # def on_mount(self):
        
    CSS_PATH = "./model-handler.css"
    BINDINGS = [
        Binding(key='q', action='quit', description="Quit the App"),
        Binding(key='question_mark', 
        action='help', 
        description="Show Help Screen",
        key_display="?")    
    ]
    
    data = mainm.DisplayData
    mainMenuOpts = mainm.MainMenuOptions()
    listOptions = ["1", "2", "3"]
    mainMenuOpts.allListToOptions(listOptions)

    def compose(self) -> ComposeResult:
       
        yield Container(TitleHeader())
        yield Container(self.mainMenuOpts, mainm.DisplayData())                
        yield Footer()
    def on_option_list_option_selected(self, event) -> None:
     self.query_one(mainm.DisplayData).value = event.option_index
    

            
class TitleHeader(Static):
    def compose(self) -> ComposeResult:
        yield Container(Label("(c)2023 4a50 Industries"), id="left-middle")
        yield Container(Label("Model Hander for Stable Diffusion"),  id="title-text")
        yield Container(Label("v0.1.0(alpha)"), id="right-middle")


if __name__ == "__main__":
    app = MainApp()
    app.run()
