import rsa
import socket


def get_connection():
    host_ip = socket.gethostbyname(socket.gethostname())
    sock = socket.socket()
    sock.bind((host_ip, 9090))
    sock.listen(1)
    return sock.accept()


def key_exchange(nnn, eee, conn):

    client_pubkey_n = conn.recv(1024)
    client_pubkey_n_str = client_pubkey_n.decode()
    nn = int(client_pubkey_n_str)

    nnn1 = str.encode(nnn)
    conn.send(nnn1)

    client_pubkey_e = conn.recv(1024)
    client_pubkey_e_str = client_pubkey_e.decode()
    ee = int(client_pubkey_e_str)

    eee1 = str.encode(eee)
    conn.send(eee1)

    return rsa.key.PublicKey(nn, ee)


def receive_msg(conn, server_privkey):
    data = conn.recv(1024)
    data_encrypted = rsa.decrypt(data, server_privkey)
    return data_encrypted.decode('utf-16')
