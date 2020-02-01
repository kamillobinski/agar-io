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

pygame.init()

# Constant variables
FPS_NUMBER = 30 
START_PLAYER_VELOCITY = 10
START_PLAYER_RADIUS = 5

WIDTH = 600
HEIGHT = 480

START_PLAYER_POSITION_X = 10
START_PLAYER_POSITION_Y = 10

# Dynamic variables
players = {}

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
        
        data_received_from_server = self.client.recv(1024)
        data_received_from_server_decoded = pickle.loads(data_received_from_server)
        return int(data_received_from_server_decoded)

    def sendDataToServer(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except socket.error as e:
            print(e)

    def receiveDataFromServer(self):
        data_received_from_server = self.client.recv(2048*4)
        data_from_server_decoded = pickle.loads(data_received_from_server)
        return data_from_server_decoded

    def disconnectFromServer(self):
        self.client.close()

        

class Client(QMainWindow):

    def __init__(self, parent=None):
        super(Client, self).__init__(parent)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 300)

        # setup pygame window
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Agar.io")

        self.game()

    def game(self):
        global players

        self.server = Network()
        self.server.establishConnection()

        username = 'kamillobinski'
        player_id = self.server.sendPlayerUsername(username)
        print('player_id = ' + str(player_id))

        threading.Thread(target=self.handleUserInputs(player_id)).start()

    def handleUserInputs(self, player_id):
        clock = pygame.time.Clock()

        data = 'Position ' + '10' + ' ' + '10'
        self.server.sendDataToServer(data)
        players = self.server.receiveDataFromServer()

        run = True
        while run:
            clock.tick(FPS_NUMBER)
            
            player = players[player_id]
            velocity = START_PLAYER_VELOCITY
            radius = START_PLAYER_RADIUS
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if player["x"] - velocity - radius >= 0:
                    player['x'] = player['x'] - velocity

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if player["x"] + velocity + radius <= WIDTH:
                    player["x"] = player["x"] + velocity

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if player["y"] - velocity - radius >= 0:
                    player["y"] = player["y"] - velocity

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if player["y"] + velocity + radius <= HEIGHT:
                    player["y"] = player["y"] + velocity

            data = 'Position ' + str(player['x']) + ' ' + str(player['y'])

            threading.Thread(target=self.server.sendDataToServer(data)).start()
            players = self.server.receiveDataFromServer()
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False  

            self.drawGameComponents(players)
            pygame.display.update()

        self.server.disconnectFromServer()
        pygame.quit()
        quit()

    def drawGameComponents(self, players):
        self.WIN.fill((255, 255, 255))

        for player in players:
            p = players[player]
            pygame.draw.circle(self.WIN, (255, 128, 0), (p['x'], p['y']), START_PLAYER_RADIUS)


        

if __name__ == '__main__':
   app = QApplication([])
   client = Client()
   sys.exit(app.exec_())

   