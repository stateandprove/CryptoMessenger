from datetime import datetime
from PyQt5 import QtCore, QtWidgets
import rsa
import socket
import threading

import msgrconnections

server_pubkey, server_privkey = rsa.newkeys(2048)
print("host ip", socket.gethostbyname(socket.gethostname()))
conn, addr = msgrconnections.get_connection()
client_pubkey = msgrconnections.key_exchange(str(getattr(server_pubkey, 'n')),
                                             str(getattr(server_pubkey, 'e')),
                                             conn)


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MY TELEGRAM")
        MainWindow.resize(687, 390)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

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

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 687, 21))
        self.menubar.setObjectName("menubar")

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MY TELEGRAM"))
        self.sendButton.setText(_translate("MainWindow", "Send"))

    def send(self):
        try:
            if len(self.lineEdit.text()) > 0 and not self.lineEdit.text().isspace():
                conn.send(rsa.encrypt(self.lineEdit.text().encode('utf-16'), client_pubkey))
                self.textBrowser.append(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
                                        f' You: {self.lineEdit.text()}')
            self.lineEdit.clear()
        except Exception:
            self.textBrowser.append(f'Message length is exceeded: {len(self.lineEdit.text())}/120')

    def receive(self):
        while True:
            message = msgrconnections.receive_msg(conn, server_privkey)
            self.textBrowser.append(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
                                    f' Message: {message}')

    def receive_thread(self):
        t = threading.Thread(target=self.receive)
        t.start()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.receive_thread()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
