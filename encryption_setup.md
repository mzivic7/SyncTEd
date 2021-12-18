To enable encryption of all transferred data, both host and client must enable encryption in conf.txt.

RSA encryption with asymetric 2048-bit keys is used. Host and peer must exchange their public keys.

Setup:
1. Both host and client edit conf.txt:
- Set encryption = True
2. Host load / generate keys
- Host can run SyncTEd and it will first ask to open file containing private key, if none is selected, it will generate key-pair, then ask to load client public key
- There is also "gen_keys" in main directory, which will generate new key-pair.
- Key-pair is generated in "data" directory.
3. Client repeat process same as host did in step 3.
4. Both host and client exchange their public keys.
- public key is in "data" directory with name "publc_key.pem"
- Host should saves clients public key in "data" directory as "peer_public_key.pem" or load it after launching SyncTEd.
- Client should do same with hosts public key.
5. Host run SyncTEd first, than client. If keys are correct, connection should be established.

Note:

SyncTEd will ask first for private key, and then for peer public key.

If there is private key in "data" directory, SyncTEd won't ask to load it.

If there is peer public key in "data" directory, SyncTEd won't ask to load it.

Loaded keys from dialog are not saved.
