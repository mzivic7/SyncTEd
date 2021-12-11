1. Create account on [ngrok](https://ngrok.com/)
2. Download ngrok
3. Get authtoken and run cmd in dir where is ngrok downloaded then run: 
- on windows: `ngrok authtoken <your_authtoken>`
- on linux: `./ngrok authtoken <your_authtoken>`
4. Start ngrok
- on windows: `ngrok tcp <port>`
- on linux: `./ngrok tcp <port>`
Pick some unused port number.
5. Edit "conf.txt":
- Set `host = True`
- Set `host_local_address = localhost`
- Set `host_local_port = ` to be same as port in ngrok.
6. Read public address and port:
In cmd now should aper interface with green "online".
Find line "Forwarding:"
Copy address without "tcp://" and ":xxxx" at the end. this is address to whichj client should connect.
This ":xxxx" is port to which client should connect.
7. Host should now run SyncTEd and wait for client.
8. Client side:
Edit "conf.txt":
- Set `host = False`
- Set `host_local_address = ` to be address that ngrok outputed to host.
- Set `host_local_port = ` to be same as port ngrok outputed with address.
Client should now run SyncTEd, and connection should be established.

In ngrok can also be set region, this will decrese latency.
Use this command instead one in step 4:
- on windows: `ngrok tcp -region <region code> <port>`
- on linux: `./ngrok tcp -region <region code> <port>`
