from datetime import datetime
from PyQt5 import QtCore, QtWidgets

import socket
import threading

import rsa


class UIMainWindow(object):
    """
    Main window class
    """

    def setup_ui(self, main_window):
        """
        Initialing the main window
        """
        main_window.setObjectName("CryptoMessenger")
        main_window.resize(687, 390)

        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        main_window.setCentralWidget(self.centralwidget)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 330, 521, 25))
        self.lineEdit.setPlaceholderText("Type your message...")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.returnPressed.connect(self.send)

        self.sendButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendButton.setGeometry(QtCore.QRect(560, 330, 110, 25))
        self.sendButton.setObjectName("sendButton")
        self.sendButton.clicked.connect(self.send)

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(20, 10, 651, 301))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.append(f'Connected to {str(addr)}')

        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 687, 21))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        """
        Sets the text and titles of the widgets
        """
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "CryptoMessenger"))
        self.sendButton.setText(_translate("MainWindow", "Send"))

    def send(self):
        """
        Sending a message
        """
        try:
            if len(self.lineEdit.text()) > 0 and not self.lineEdit.text().isspace():
                conn.send(rsa.encrypt(self.lineEdit.text().encode('utf-16'), client_pubkey))
                self.textBrowser.append(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
                                        f' You: {self.lineEdit.text()}')
            self.lineEdit.clear()
        except Exception:
            self.textBrowser.append(f'Message length is exceeded: '
                                    f'{len(self.lineEdit.text())}/120')

    def receive(self):
        """
        Receiving a message
        """
        while True:
            message = receive_msg(conn, server_privkey)
            self.textBrowser.append(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
                                    f' Message: {message}')

    def receive_thread(self):
        """
        A thread for receiving messages
        """
        t = threading.Thread(target=self.receive)
        t.start()


def get_connection():
    """
    Performs the connection between server and client
    :return: a new socket.
    """
    host_ip = socket.gethostbyname(socket.gethostname())
    conn_sock = socket.socket()
    conn_sock.bind((host_ip, 9090))
    conn_sock.listen(1)
    return conn_sock.accept()


def key_exchange(n_attr, e_attr, exchange_conn):
    """
    Performs the public key exchange according to the following scheme:

    1. Server receives the 'n' attribute from a client;
    2. Server sends its 'n' attribute to a client;
    3. Server receives the 'e' attribute from a client;
    4. Server sends its 'e' attribute to a client;
    5. Function returns a client's public key instance with
       received 'n' and 'e' attributes.

    :param n_attr: the 'n' attribute of an RSA public key instance.
    :param e_attr: the 'e' attribute of an RSA public key instance.
    :param exchange_conn: the exchange socket.
    :return: a client's public key instance.
    """
    client_pubkey_n_bytes = exchange_conn.recv(1024)
    client_pubkey_n = int(client_pubkey_n_bytes.decode())

    server_pubkey_n_bytes = n_attr.encode()
    exchange_conn.send(server_pubkey_n_bytes)

    client_pubkey_e_bytes = exchange_conn.recv(1024)
    client_pubkey_e = int(client_pubkey_e_bytes.decode())

    server_pubkey_e_bytes = e_attr.encode()
    exchange_conn.send(server_pubkey_e_bytes)

    return rsa.key.PublicKey(client_pubkey_n, client_pubkey_e)


def receive_msg(rec_conn, srv_privkey):
    """
    Decrypts a message from a client and returns an utf-16 decoded string
    """
    msg = rec_conn.recv(1024)
    data_encrypted = rsa.decrypt(msg, srv_privkey)
    return data_encrypted.decode('utf-16')


if __name__ == "__main__":
    # connecting, getting client's public key
    server_pubkey, server_privkey = rsa.newkeys(2048)
    print("host ip", socket.gethostbyname(socket.gethostname()))
    conn, addr = get_connection()
    client_pubkey = key_exchange(str(getattr(server_pubkey, 'n')),
                                 str(getattr(server_pubkey, 'e')),
                                 conn)

    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UIMainWindow()
    ui.receive_thread()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
