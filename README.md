# SyncTEd
Synchronised text editor over TCP, for live editing with others.
Written in Python with PyGame.
## Run
1. Install requirements: `pip install -r requirements.txt`
2. Run main.py: `puthon3 main.py`
## Usage
This text editor consist from 2 parts: host and client.
They are ran on different devices. Host must be firts.
Which one is host is set in "conf.txt" located in "data" folder in project dir.
Afther that, host must be port-forwareded or tunneled with [ngrok](https://ngrok.com/). Port and host adress must be set in "conf.txt"
In "conf.txt" are several more settings:
- Host - if True: this is host, if False: this is client
- Save on quit - set False to stop it from asking to save on quit
- Tab spaces num - change how many spaces wide will be tab
- Window width and heigth - in pixels
- Client address and port - this config is only for client, hosts adress and port on which client will connect
- Host local address and port - this config is only for host, address and port on which will client cnnect 
Keys:
- Up, Down, Left, Right arrows
- Tab
- Save: CTRL+S
- Load: CTRL+L
[basic ngrok setup](use_with_ngrok.md)
## Building
### Linux
1. Clone this repositiry: `git clone https://github.com/mzivic7/SyncTEd.git`
2. `cd SyncTEd`
3. Install requirements: `pip install -r requirements.txt`
4. run build script: `python3 build.py`
### Windows
1. Install [Python](https://www.python.org/) 3.9 or later
2. Clone this repository, unzip it
3. Open terminal, cd to unzipped folder
4. Install requirements: `pip install -r requirements.txt`
5. Run build script: `python build.py`
## Future progress
There will be implemented some more features like:
- Scrolling
- Save to loaded file
- Capital letters
- Quit without waiting to connect
- Line wrapping
- Encryption with paspharse
