""" 
 * Copyright 2019 Kamil Łobiński <kamilobinski@gmail.com>.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License. """

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys, socket, pickle, threading
import random, os, pygame, contextlib

""" 
 *
 * @Author Kamil Łobiński <kamilobinski@gmail.com>
 *
"""

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.56.1'
        self.port = 55550
        self.addr = (self.host, self.port)

    def establishConnection(self):
        self.client.connect(self.addr)

    def sendPlayerUsername(self, username):
        self.client.send(pickle.dumps(username))

    def sendDataToServer(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except socket.error as e:
            print(e)

    def receiveDataFromServer(self):
        while True:
            data_received_from_server = self.client.recv(1024)
            data_from_server_decoded = pickle.loads(data_received_from_server)
            print(str(data_from_server_decoded))

    def disconnectFromServer(self):
        self.client.close()

        

class Client(QMainWindow):

    def __init__(self, parent=None):
        super(Client, self).__init__(parent)
        # Client UI
        self.initUI()
        self.refresh()

        # Client networking
        self.game()

    def initUI(self):
        vbox = QVBoxLayout()

        window = QWidget()
        window.setLayout(vbox)
        self.setCentralWidget(window)

        self.setGeometry(2720, 400, 300, 300)
        self.setWindowTitle('Game client')
        self.show()

    def game(self):
        global players

        self.server = Network()
        self.server.establishConnection()

        username = input("Please enter your name: ")
        threading.Thread(target=self.server.sendPlayerUsername(username)).start()

        data = input("Please enter data to send: ")
        threading.Thread(target=self.server.sendDataToServer(data)).start()
        threading.Thread(target=self.server.receiveDataFromServer).start()

        
    def closeEvent(self, event):
        self.server.disconnectFromServer()
        print('zamykam')



    def refresh(self):
        self.update()

if __name__ == '__main__':
   app = QApplication([])
   client = Client()
   sys.exit(app.exec_())

   