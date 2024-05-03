# SyncTEd
Synchronized text editor over TCP, for live editing with others.
Written in Python with PyGame.

## Run
1. Install requirements: `pip install -r requirements.txt`
2. Run main.py: `python3 main.py`

## Usage
This text editor consist from 2 parts: host and client.
They are ran on different devices. Host must be ran first.
Which one is host is set in "conf.txt" located in project directory.
Host must be on LAN, port-forwarded or tunneled with [ngrok](https://ngrok.com/). Port and host address must be set in "conf.txt".
SyncTEd requires small latency, bellow 150ms is recommended.

In "conf.txt" are several more settings:
- Host - if True: this is host, if False: this is client
- Ask save - set False to stop it from asking to save
- Encryption - if True, asymmetric RSA encryption will be used for communication
- Tab spaces - change how many spaces wide will be tab
- Window width and height - in pixels
- Client address and port - hosts address and port on which client will connect (only for client)
- Host local address and port - address and port on which will client connect (only for host)

Keys:
- Up, Down, Left, Right arrows
- Tab
- Shift
- Caps Lock
- Save: Ctrl+S
- Load: Ctrl+L

[Encryption setup](encryption_setup.md)

[ngrok setup](use_with_ngrok.md)

## Building
### Linux
1. Clone this repository: `git clone https://github.com/mzivic7/SyncTEd.git`
2. `cd SyncTEd`
3. Install requirements: `pip install -r requirements.txt`
4. run build script: `python build.py`
### Windows
1. Install [Python](https://www.python.org/) 3.10 or later
2. Clone this repository, unzip it
3. Open terminal, cd to unzipped folder
4. Install requirements: `pip install -r requirements.txt`
5. Run build script: `python build.py`

## To Do
- Send data larger than 2048 bits
- Quit without waiting to connect
- Smart tab (add correct number of spaces, backspace deletes whole tab)
- Auto add indentation on newline
- Line wrapping
- Scrolling and scrollbar
- Selecting (mouse, click, keyboard)
- Work with large ping
- Multi-threaded server
