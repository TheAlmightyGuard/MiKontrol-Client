from colorama import Fore

def cogs_status(name : str ,loaded : bool):
    if loaded:
        print("[" + Fore.GREEN + "+" + Fore.RESET + "] '" + name + "' command has loaded...")
    else:
        print("[" + Fore.RED + "-" + Fore.RESET + "] '" + name + "' command failed to load...")