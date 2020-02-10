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
from pygame.locals import *

""" 
 *
 * @Author Kamil Łobiński <kamilobinski@gmail.com>
 *
"""

pygame.init()

# Constant variables
WIDTH = 600
HEIGHT = 480
FPS_NUMBER = 60
START_PLAYER_VELOCITY = 5
START_PLAYER_RADIUS = 5
START_PLAYER_POSITION_X = 10
START_PLAYER_POSITION_Y = 10

# Dynamic variables
players = {}
food = []

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '192.168.56.1'
        self.port = 55550
        self.addr = (self.host, self.port)

    def establishConnection(self):
        self.client.connect(self.addr)

    def sendBotUsername(self, username):
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



class Bot():
    direction = 0

    def __init__(self):
        print('Bot initialised.')

    def addBotToGame(self):
        self.server = Network()
        # Bot connects to server.
        # Sends own username and gets back assigned id from server.
        self.server.establishConnection()
        self.bot_id = self.server.sendBotUsername('bot')
        threading.Thread(target = self.createBotMovement(self.bot_id)).start()

    def createBotMovement(self, bot_id):
        clock = pygame.time.Clock()

        # Bot sends own coordinates and receives list of all players with details,
        # such as: position(x, y), color, name, radius, velocity.
        ## Required at the beginning and only performed once.
        data = 'Position ' + str(START_PLAYER_POSITION_X) + ' ' + str(START_PLAYER_POSITION_Y)
        self.server.sendDataToServer(data)
        players = self.server.receiveDataFromServer()

        # Bot sends message to server and receives list of food that is currently on the map.
        ## Required at the beginning and only performed once.
        data = 'Food '
        threading.Thread(target=self.server.sendDataToServer(data)).start()
        food = self.server.receiveDataFromServer()

        self.run = True
        while self.run:
            # Main game loop performs at 60 frames per second.
            clock.tick(FPS_NUMBER)
        
            bot = players[self.bot_id]
            radius = START_PLAYER_RADIUS + bot['radius']

            # Gain mass or attack.
            if radius < 10:
                # If radius is < 10 our bot only gathers food.
                nearest_food = self.checkForTheNearestFood(bot, food)
                self.moveToTarget(bot, nearest_food[0], nearest_food[1])
            else:
                # If radius is > 10 our bot starts to look for enemies.
                nearest_player = self.checkForTheNearestPlayer(bot, players)
                if bot['x'] - nearest_player[0] < 150 and bot['y'] - nearest_player[1] < 150 and nearest_player[2] > 7:
                    # If the distance from bot to the nearest player is less than 150 (from x and y)
                    # and the enemy radius is > (START_PLAYER_RADIUS + 7), bot moves toward the marked player.
                    self.moveToTarget(bot, nearest_player[0], nearest_player[1])
                else:
                    # When enemy is not around, bot still collects food.
                    nearest_food = self.checkForTheNearestFood(bot, food)
                    self.moveToTarget(bot, nearest_food[0], nearest_food[1])

            # Move bot in the previously assigned direction.
            self.update(bot)

            # Bot sends own coordinates and receives list of all players with details,
            # such as: position(x, y), color, name, radius, velocity.
            data = 'Position ' + str(bot['x']) + ' ' + str(bot['y'])
            threading.Thread(target=self.server.sendDataToServer(data)).start()
            players = self.server.receiveDataFromServer()
            
            # Bot sends message to server and receives list of food that is currently on the map.
            data = 'Food '
            threading.Thread(target=self.server.sendDataToServer(data)).start()
            food = self.server.receiveDataFromServer()

        self.server.disconnectFromServer()
        pygame.quit()
        quit()

    def checkForTheNearestFood(self, bot, food):
        nearest = min(food, key=lambda x: (x[0] - bot['x'])**2 + (x[1] - bot['y'])**2)
        return nearest

    # Function checks for the nearest player and 
    # returns its x, y and radius.
    def checkForTheNearestPlayer(self, bot, players):
        nearest_list = []
        nearest_list.clear()
        for player in players:
            p = players[player]
            if p['x'] != bot['x'] and p['y'] != bot['y']:
                nearest_list.append((p['x'], p['y'], p['radius']))

        if len(nearest_list) != 0:
            nearest = min(nearest_list, key = lambda x: (x[0] - bot['x'])**2 + (x[1] - bot['y'])**2)
        else:
            nearest = [10, 10, 0]

        return nearest

    # Function determines the direction of 
    # the route to the destination.
    def moveToTarget(self, bot, x, y):
        distance_X = bot['x'] - x
        distance_Y = bot['y'] - y

        if bot['x'] > x and distance_X > 4 + bot['radius']:
            self.moveLeft()
        elif bot['x'] < x and distance_X < -4 - bot['radius']:
            self.moveRight()
        elif bot['x'] == x or distance_X >= -4 - bot['radius'] and distance_X <= 4 + bot['radius']:
            if bot['y'] > y:
                self.moveUp()
            elif bot['y'] < y:
                self.moveDown()

    # Function that moves bot in the 
    # specified direction.
    def update(self, bot):
        if self.direction == 0:
            bot['y'] = bot['y'] - bot['velocity']
        elif self.direction == 1:
            bot['y'] = bot['y'] + bot['velocity']
        elif self.direction == 2:
            bot['x'] = bot['x'] - bot['velocity']
        elif self.direction == 3:
            bot['x'] = bot['x'] + bot['velocity']

    def moveUp(self):
        self.direction = 0
    
    def moveDown(self):
        self.direction = 1

    def moveLeft(self):
        self.direction = 2

    def moveRight(self):
        self.direction = 3

    def disableBot(self):
        quit()


if __name__ == '__main__':
   app = QApplication([])
   bot = Bot()
   sys.exit(app.exec_())