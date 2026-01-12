import time
import os, platform

from rich.progress import Progress
from rich.console import Console
from rich.table import Table

from models.internal import CogModel
class CogsStatus:
    COGS : list[CogModel] = []


    def cogs_status(self):
        existFailed = False

        table = Table(title="LOADED COGS STATUS")
        table_error = Table(title="DIAGNOSTIC SYSTEM FOR COGS - ISSUES DETECTED")

        table.add_column("Command Name", style="cyan", no_wrap=True)
        table.add_column("File Path", style="green")
        table.add_column("Status", justify="right", style="green")

        for data in self.COGS:
            if data.status is False:
                existFailed = True
            table.add_row(data.commandName, data.filePath, "✅" if data.status else "❌")

        console = Console()
        console.print(table)

        if existFailed:

            table_error.add_column("Command Name", style="cyan", no_wrap=True)
            table_error.add_column("File Path", style="green")
            # table_error.add_column("Status", justify="right", style="green")
            table_error.add_column("Error", style="red", no_wrap=False)
            
            for data in self.COGS:
                if data.status is False:
                    table_error.add_row(data.commandName, data.filePath, data.error if data.error is not None else "No additional error info.")
            console.print(table_error)

    def cog_status_append(self, cog: CogModel):
        self.COGS.append(cog)

    def clear_console(self):
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
        time.sleep(1)

    def pre_loading(self):

        self.clear_console()
            

        with Progress() as progress:

            task1 = progress.add_task("[blue]Connecting to Discord...", total=100)
            task2 = progress.add_task("[green]Initializing Bot Client...", total=100)

            while not progress.finished:
                progress.update(task1, advance=0.9)
                progress.update(task2, advance=0.3)
                time.sleep(0.02)

        time.sleep(1)
        self.clear_console()

def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
    time.sleep(1)

def pre_loading():

    clear_console()
        

    with Progress() as progress:

        task1 = progress.add_task("[blue]Connecting to Discord...", total=100)
        task4 = progress.add_task("[blue]Connecting to MongoDB Asynchronous...", total=100)
        task2 = progress.add_task("[green]Initializing Bot Client...", total=100)
        task3 = progress.add_task("[green]Intizializing FastAPI...", total=100)

        while not progress.finished:
            progress.update(task1, advance=0.9)
            progress.update(task4, advance=0.35)
            progress.update(task2, advance=0.3)
            progress.update(task3, advance=0.2)
            time.sleep(0.02)

    time.sleep(1)
    clear_console()
    
