import threading  # добавляем модуль многопоточности для одновременных приема и передачи
import socket  # добавляем модуль сокетов для коннекта
import rsa  # добавляем модуль rsa для шифрования
from datetime import datetime  # добавляем модуль времени

host_ip = socket.gethostbyname(socket.gethostname())  # получаем свой локальный айпишник
server_pubkey, server_privkey = rsa.newkeys(1024)  # генерируем пару ключей
print("This is TELEGRAM THAT YOU'VE DESERVED\nYou're the host with local ip", host_ip, "\nWaiting for connection...")

sock = socket.socket()  # создаем сокет
sock.bind((host_ip, 9090))  # биндим сервер к нашему локальному айпишнику и порту 9090
sock.listen(1)  # начинаем прослушку с одним возможным подключением
conn, addr = sock.accept()  # подключаемся к клиенту

print("CONNECTED:", addr)  # дальше как в клиенте


def key_exchange():
    nnn = str(getattr(server_pubkey, 'n'))
    eee = str(getattr(server_pubkey, 'e'))

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

    global client_pubkey
    client_pubkey = rsa.key.PublicKey(nn, ee)

key_exchange()

print("The encryption key is successfully received!", "\nType your message here...")


def receive():
    while True:
        data = conn.recv(1024)
        data_encrypted = rsa.decrypt(data, server_privkey)
        data_decoded = data_encrypted.decode()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(now, 'Message:', data_decoded)


def transmit():
    while True:
        msg = input()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(now, 'You:', msg)
        msg_as_bytes = str.encode(msg)
        msg_crypto = rsa.encrypt(msg_as_bytes, client_pubkey)
        conn.send(msg_crypto)


t1 = threading.Thread(target=transmit)
t2 = threading.Thread(target=receive)
t1.start()
t2.start()
t1.join()
t2.join()