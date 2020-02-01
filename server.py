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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys, socket, pickle, threading
import subprocess

""" 
 *
 * @Author Kamil Łobiński <kamilobinski@gmail.com>
 *
"""

# Dynamic variables
actual_connections = {}

class Network:

    def __init__(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.56.1'
        self.port = 55550
        self.addr = (self.host, self.port)

        global actual_connections
        self.client_id = 0

    def runServer(self):
        self.prepareServerForConnection()
        threading.Thread(target=self.serverLoop).start()

    def prepareServerForConnection(self):
        self.serv.bind(self.addr)
        self.serv.listen(5) 

    def serverLoop(self):
        while True:
            try:
                server.addInformation('[INFO] Server waiting for new connection')
                conn, address = self.serv.accept()
                server.addInformation('[CONNECTION] Server established new connection')
                threading.Thread(target=self.serverLoop).start()
                threading.Thread(target=self.getClientUsername(conn, address)).start()
                threading.Thread(target=self.getClientData(conn, address, self.client_id)).start()
            
            except Exception as ex:
                #server.textArea.insertPlainText('[ERROR] Server caught error.')
                print(ex)
                pass

    def getClientUsername(self, connection, address):
        self.client_id = self.client_id + 1

        data = connection.recv(1024) 
        name = pickle.loads(data)
        name = str(name)
        server.addInformation('[CLIENT] Client ' + name)
        actual_connections[self.client_id] = {'name':name}

        print('sending')
        data_for_client_id = pickle.dumps(self.client_id)
        connection.send(data_for_client_id)
        print('sent id' + str(data_for_client_id))

    def getClientData(self, connection, address, client_id):
        while True:
            data = connection.recv(2048)
            if not data:
                del actual_connections[client_id]
                server.addInformation('[CONNECTION] Client ' + name + ' disconnected from server')
                connection.close()
                break
            if data == b'':
                pass
            else:       
                data_reveived = pickle.loads(data)
                server.addInformation('[CLIENT] Client ' + actual_connections[client_id]['name'] + ' sent: ' + str(data_reveived))

                data_for_client = pickle.dumps(actual_connections[client_id]['name'])
                connection.send(data_for_client) 



class Server(QMainWindow):

    def __init__(self, parent=None):
        super(Server, self).__init__(parent)
        self.initUI()

        self.network = Network()
        self.network.runServer()

        self.fillServerProperties()
        self.refresh()

    def initUI(self):
        self.createComponents()

        vbox = QVBoxLayout()
        vbox.addWidget(self.serverPropertiesGroup)
        vbox.addWidget(self.textArea)

        window = QWidget()
        window.setLayout(vbox)
        self.setCentralWidget(window)

        self.setGeometry(2400, 400, 300, 300)
        self.setWindowTitle('Game server')

    def createComponents(self):
        self.serverIP = QLabel('IP: ', self)
        self.serverPORT = QLabel('Port: ', self)

        serverPropertiesGroupLayout = QVBoxLayout()
        serverPropertiesGroupLayout.addWidget(self.serverIP)
        serverPropertiesGroupLayout.addWidget(self.serverPORT)
        
        self.serverPropertiesGroup = QGroupBox('Server properties')
        self.serverPropertiesGroup.setLayout(serverPropertiesGroupLayout)

        self.textArea = QPlainTextEdit()
        self.textArea.setReadOnly(True)                

    def fillServerProperties(self):
        self.serverIP.setText('IP: ' + self.network.host)
        self.serverPORT.setText('Port: ' + str(self.network.port))

    def addInformation(self, info):
        self.textArea.insertPlainText(info + '\n')

    #def moveTextAreaCursorToEnd(self):
        #self.textArea.verticalScrollBar().setValue(self.textArea.verticalScrollBar().maximum())

    def refresh(self):
        self.update()

if __name__ == '__main__':
    app = QApplication([])
    server = Server()
    server.show()
    sys.exit(app.exec_())

   