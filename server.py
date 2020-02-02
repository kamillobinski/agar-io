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
import subprocess, random

""" 
 *
 * @Author Kamil Łobiński <kamilobinski@gmail.com>
 *
"""

# Constant variables
START_PLAYER_POSITION_X = 10
START_PLAYER_POSITION_Y = 10
PLAYER_COLORS = [(255, 255, 255), (95, 10, 135), (177, 221, 241), (217, 4, 41), (159, 135, 175), (136, 82, 127), (97, 67, 68), (51, 44, 35), (255, 255, 255), (95, 10, 135), (177, 221, 241), (217, 4, 41), (159, 135, 175), (136, 82, 127), (97, 67, 68), (51, 44, 35)]

CLIENT_WINDOW_WIDTH = 600
CLIENT_WINDOW_HEIGHT = 480

# Dynamic variables
actual_connections = {}
players = {}
food = []

class Network:

    def __init__(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.56.1'
        self.port = 55550
        self.addr = (self.host, self.port)

        global actual_connections, players, food
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
                print(ex)
                pass

    def getClientUsername(self, connection, address):
        self.client_id = self.client_id + 1

        data = connection.recv(1024) 
        name = pickle.loads(data)
        name = str(name)
        server.addInformation('[CLIENT] Client ' + name)

        actual_connections[self.client_id] = {'name':name}
        color = PLAYER_COLORS[self.client_id]
        players[self.client_id] = {'x':START_PLAYER_POSITION_X, 'y':START_PLAYER_POSITION_Y, 'color':color, 'name':name}

        data_for_client_id = pickle.dumps(self.client_id)
        connection.send(data_for_client_id)

    def getClientData(self, connection, address, client_id):
        while True:
            try: 
                data = connection.recv(2048 * 4)
                if not data:
                    del actual_connections[client_id]
                    del players[client_id]
                    server.addInformation('[CONNECTION] Client ' + name + ' disconnected from server')
                    break
                if data == b'':
                    pass
                else:       
                    data_received = pickle.loads(data)
                    if data_received.split(' ')[0] == 'Position':
                        split_data = data_received.split(' ')
                        x = int(split_data[1])
                        y = int(split_data[2])

                        players[client_id]['x'] = x
                        players[client_id]['y'] = y

                        data = pickle.dumps(players)
                    elif data_received.split(' ')[0] == 'Generate':
                        self.generateFood(food, 20)
                        data = pickle.dumps(food)
                    
                    connection.send(data)

            except Exception as ex:
                print(ex)
                break

    # Game functions
    def generateFood(self, food, number_to_generate):
        for n in range(number_to_generate):
            x = random.randrange(0, CLIENT_WINDOW_HEIGHT)
            y = random.randrange(0, CLIENT_WINDOW_WIDTH)
            food.append((x, y))



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
        self.textArea.setWordWrapMode(QTextOption.NoWrap)            

    def fillServerProperties(self):
        self.serverIP.setText('IP: ' + self.network.host)
        self.serverPORT.setText('Port: ' + str(self.network.port))

    def addInformation(self, info):
        self.textArea.insertPlainText(info + '\n')
        self.checkToClean()

    def checkToClean(self):
        text_lines = self.textArea.blockCount()
        if text_lines > 100:
            self.textArea.clear()

    def refresh(self):
        self.update()

if __name__ == '__main__':
    app = QApplication([])
    server = Server()
    server.show()
    sys.exit(app.exec_())

   