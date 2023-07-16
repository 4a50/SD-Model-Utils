from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, Label, OptionList
from textual.widget import Widget
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual import events
from rich.console import RenderableType

class MainMenuOptions(OptionList):    
    def allListToOptions(self, listStr):
        for i in listStr:
            self.add_option(i)
        

     

class DisplayData(Static):
    value = reactive("rValue Here")
    def render(self) -> RenderResult:
        return f"Value: {str(self.value)}"