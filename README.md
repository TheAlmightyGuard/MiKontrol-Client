<img src="https://github.com/TheAlmightyGuard/MiKontrol-Client/blob/208c7e96ca21a31df711ce277436bd148d5e9bff/images/bot_logo.png" width="120" height="120">

# MiKontrol Client
The MiKontrol Client ('back-end') is a discord-based bot of which will connect into different areas such as different games and social media to connect all into one discord server.
This bot has capability to be a moderator and to be a fun mod with more upcoming features!

### Discord Access
Release Branch: https://discord.com/oauth2/authorize?client_id=1437602024916127784 \
Development Branch (_DEVELOPER ACCESS ONLY_): https://discord.com/oauth2/authorize?client_id=1463680415012491337

# Date of progression
Start of production: March 15th, 2025\
Mikoto Management v0.1a ALPHA-RELEASE: TBD

# Project Roadmap (As of March 15th, 2025)
Below is the roadmap of projects to be made in order. Top to bottom in priority.

## [🟠] - Mikoto Management
* Platform of creation: VSCode
* Language: Python (Discord.py)
* Platform of usage: Discord

### Project Phases:
  * [🟢] Phase 1: Build base structures and confirm connection to DISCORD BO
  * [🟢] Phase 2: Connect with **MONGO DATABASE** & **REDIS**
  * [🟠] Phase 3: Build commands and management systems
  * [🟠] Phase 4: Build host capability for API
                _**TBD later phases**_
 #### Project Code:
  * **MKTO-CLT-1**

## Library Usage:
* discord.py (Backbone of the client)
* pymongo (Asyncronous access to the database)
* redis (Cache-based storage library for task-focused events)
* pydantic (Data Validation for in and out of database)
* uvicorn
* fastapi
* rich (Command line prettyness)

# License
Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
