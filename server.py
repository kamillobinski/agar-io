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
import subprocess, random, math, os
from bot import *

""" 
 *
 * @Author Kamil Łobiński <kamilobinski@gmail.com>
 *
"""

# Constant variables
START_PLAYER_POSITION_X = 10
START_PLAYER_POSITION_Y = 10
START_PLAYER_RADIUS = 0
START_PLAYER_VELOCITY = 5
PLAYER_COLORS = [(95, 10, 135), (177, 221, 241), (217, 4, 41), (159, 135, 175), (136, 82, 127), (97, 67, 68), (51, 44, 35), (95, 10, 135), (177, 221, 241), (217, 4, 41), (159, 135, 175), (136, 82, 127), (97, 67, 68), (51, 44, 35)]
FOOD_COLORS = [(0, 250, 255), (103, 255, 0), (255, 0, 169), (0, 255, 0), (0, 111, 255), (255, 70, 0), (255, 248, 0), (255, 0, 34), (184, 0, 255)]

CLIENT_WINDOW_WIDTH = 600
CLIENT_WINDOW_HEIGHT = 480

# Dynamic variables
players = {}
food = []

class Network:

    def __init__(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.56.1'
        self.port = 55550
        self.addr = (self.host, self.port)

        global players, food
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
        server.addInformation('[CLIENT] Client ' + name + ' ready for game')

        color = random.choice(PLAYER_COLORS)
        players[self.client_id] = {'x':START_PLAYER_POSITION_X, 'y':START_PLAYER_POSITION_Y, 'color':color, 'name':name, 'radius':START_PLAYER_RADIUS, 'velocity':START_PLAYER_VELOCITY}

        data_for_client_id = pickle.dumps(self.client_id)
        connection.send(data_for_client_id)

    def getClientData(self, connection, address, client_id):
        while True:
            try: 
                data = connection.recv(2048 * 4)
                if not data:
                    server.addInformation('[CONNECTION] Client ' + players[client_id]['name'] + ' disconnected from server')
                    del players[client_id]
                    connection.close()
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

                        self.checkForPlayerCollision(players)

                        data = pickle.dumps(players)
                    elif data_received.split(' ')[0] == 'Generate':
                        self.generateFood(food, 20)
                        data = pickle.dumps(food)

                    elif data_received.split(' ')[0] == 'Food':
                        if len(food) < 10:
                            self.generateFood(food, 10)
                        self.checkForEatenFood(players, food)
                        data = pickle.dumps(food)

                    connection.send(data)

            except Exception as ex:
                print(ex)
                break

    # Game functions
    def changePlayerVelocity(self, p):
            if p['radius'] == 0:
                p['velocity'] = START_PLAYER_VELOCITY
            elif p['radius'] > 5 and p['radius'] % 5 == 0:
                if p['velocity'] > 1:
                    p['velocity'] = math.floor(p['velocity'] * 0.95)

    def checkForEatenFood(self, players, food):
        for player in players:
            p = players[player]
            player_pos_x = p['x']
            player_pos_y = p['y']
            for snack in food:
                food_pos_x = snack[0]
                food_pos_y = snack[1]

                calculated = math.sqrt((food_pos_x - player_pos_x)**2 + (food_pos_y - player_pos_y)**2)

                if calculated <= 5 + p['radius']:
                    food.remove(snack)
                    p['radius'] = p['radius'] + 1
                    self.changePlayerVelocity(p)

    def checkForPlayerCollision(self, players):
        p_sorted_list = sorted(players, key=lambda number: players[number]['radius'])
        for number, playerFirst in enumerate(p_sorted_list):
            for playerSecond in p_sorted_list[number + 1:]:
                p1_pos_x = players[playerFirst]['x']
                p1_pos_y = players[playerFirst]['y']
                p2_pos_x = players[playerSecond]['x']
                p2_pos_y = players[playerSecond]['y']

                calculated = math.sqrt((p1_pos_x - p2_pos_x)**2 + (p1_pos_y - p2_pos_y)**2)

                if calculated < players[playerSecond]['radius'] - players[playerFirst]['radius'] * 0.6:
                    players[playerSecond]['radius'] = players[playerSecond]['radius'] + players[playerFirst]['radius']
                    players[playerFirst]['radius'] = 0
                    self.changePlayerVelocity(players[playerFirst])
                    self.changePlayerVelocity(players[playerSecond])

    def generateFood(self, food, number_to_generate):
        for n in range(number_to_generate):
            x = random.randrange(10, CLIENT_WINDOW_WIDTH - 10)
            y = random.randrange(10, CLIENT_WINDOW_HEIGHT - 10)
            color = random.choice(FOOD_COLORS)
            food.append((x, y, color))
        server.addInformation('[GAME] Server generated more food')

    def deleteBot(self, bot_id):
        del players[bot_id]



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
        vbox.addWidget(self.botGroup)
        vbox.addWidget(self.textArea)

        window = QWidget()
        window.setLayout(vbox)
        self.setCentralWidget(window)

        self.setGeometry(100, 400, 300, 300)
        self.setWindowTitle('Agar.io server')
        self.setWindowIcon(QIcon('resources/favicon.png'))

    def createComponents(self):
        self.bot_status = 0
        self.start_bot_button = QPushButton('Start bot', self)
        self.start_bot_button.clicked.connect(self.createThread)
        self.disable_bot_button = QPushButton('Disable bot', self)
        self.disable_bot_button.clicked.connect(self.disableBot)

        botGroupLayout = QHBoxLayout()
        botGroupLayout.addWidget(self.start_bot_button)
        botGroupLayout.addWidget(self.disable_bot_button)

        self.botGroup = QGroupBox('Bot')
        self.botGroup.setLayout(botGroupLayout)


        self.serverIP = QLabel('IP: ', self)
        self.serverPORT = QLabel('Port: ', self)

        serverPropertiesGroupLayout = QVBoxLayout()
        serverPropertiesGroupLayout.addWidget(self.serverIP)
        serverPropertiesGroupLayout.addWidget(self.serverPORT)
        
        self.serverPropertiesGroup = QGroupBox('Server properties')
        self.serverPropertiesGroup.setLayout(serverPropertiesGroupLayout)

        self.textArea = QTextEdit()
        self.textArea.setReadOnly(True)    
        self.textArea.setWordWrapMode(QTextOption.NoWrap)   

    def fillServerProperties(self):
        self.serverIP.setText('IP: ' + self.network.host)
        self.serverPORT.setText('Port: ' + str(self.network.port))

    def addInformation(self, info):
        self.textArea.insertPlainText(info + '\n')
        self.textArea.moveCursor(QTextCursor.End)

    def checkToClean(self):
        text_lines = self.textArea.blockCount()
        if text_lines > 100:
            self.textArea.clear()

    def refresh(self):
        self.update()

    def createThread(self):
        self.bot_status = 1
        self.start_bot_button.setDisabled(True)
        self.disable_bot_button.setDisabled(False)
        threading.Thread(target=self.botOnOFF).start()

    def disableBot(self):
        self.bot_status = 0
        self.disable_bot_button.setDisabled(True)
        self.start_bot_button.setDisabled(False)
        threading.Thread(target=self.botOnOFF).start()

    def botOnOFF(self):
        if self.bot_status is 1:
            bot.addBotToGame()
            bot.run = True
        elif self.bot_status is 0:
            bot.run = False

if __name__ == '__main__':
    app = QApplication([])
    server = Server()
    server.show()
    bot = Bot()
    sys.exit(app.exec_())

   