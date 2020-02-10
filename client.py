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
FPS_NUMBER = 60
START_PLAYER_VELOCITY = 5
START_PLAYER_RADIUS = 5
START_PLAYER_POSITION_X = 10
START_PLAYER_POSITION_Y = 10

WIDTH = 600
HEIGHT = 480
SCREEN_RESOLUTION = pygame.display.Info()

GREEN = (84, 200, 0)
GREY = (162, 162, 162)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game fonts
pygame.font.init()
FONT = pygame.font.SysFont('Comic Sans MS', 10)
START_PAGE_FONT = pygame.font.SysFont('Comic Sans MS', 16)
START_PAGE_FONT_LOGO = pygame.font.SysFont('Comic Sans MS', 40)

# Game icon
icon = pygame.image.load('resources/favicon.png')

# Game image
START_PAGE_IMAGE = pygame.image.load('resources/background.png')

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
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((SCREEN_RESOLUTION.current_w / 2) - (WIDTH / 2), (SCREEN_RESOLUTION.current_h / 2) - (HEIGHT / 2))

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Agar.io")
        pygame.display.set_icon(icon)

        self.game()

    def game(self):
        global players, food

        self.server = Network()
        self.server.establishConnection()

        self.username = ''
        self.game_intro()

        player_id = self.server.sendPlayerUsername(self.username)
        threading.Thread(target=self.handleUserInputs(player_id)).start()

    def game_intro(self):
        intro = True
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if (x > 200 and x < 400 and y > 250 and y < 280):
                        intro = False

                elif event.type == KEYDOWN:
                    if event.unicode.isalpha():
                        if len(self.username) < 8:
                            self.username += event.unicode
                    elif event.key == K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == K_RETURN:
                        intro = False

            logo_text = START_PAGE_FONT_LOGO.render('Agar.io', True, BLACK)
            username_hint = START_PAGE_FONT.render('Username: ', True, GREY)
            username_block = START_PAGE_FONT.render(self.username, True, BLACK)
            rect = username_block.get_rect()
            rect.center = self.window.get_rect().center
            play_button_text = START_PAGE_FONT.render('Play', True, WHITE)

            self.window.blit(START_PAGE_IMAGE, START_PAGE_IMAGE.get_rect())
            self.window.blit(logo_text, [233, 145])
            self.window.blit(username_block, [283,213])
            self.window.blit(username_hint, [205,213])
            pygame.draw.rect(self.window, GREY, (200, 210, 200, 30), 1)
            pygame.draw.rect(self.window, GREEN, (200, 250, 200, 30))
            self.window.blit(play_button_text, [283,252])  

            pygame.display.update()

    def handleUserInputs(self, player_id):
        clock = pygame.time.Clock()

        data = 'Position ' + str(START_PLAYER_POSITION_X) + ' ' + str(START_PLAYER_POSITION_Y)
        self.server.sendDataToServer(data)
        players = self.server.receiveDataFromServer()

        data = 'Generate Food'
        self.server.sendDataToServer(data)
        food = self.server.receiveDataFromServer()

        run = True
        while run:
            clock.tick(FPS_NUMBER)
            
            player = players[player_id]
            radius = START_PLAYER_RADIUS + player['radius']

            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if player["x"] - player['velocity'] - radius >= 0:
                    player['x'] = player['x'] - player['velocity']

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if player["x"] + player['velocity'] + radius <= WIDTH:
                    player["x"] = player["x"] + player['velocity']

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if player["y"] - player['velocity'] - radius >= 0:
                    player["y"] = player["y"] - player['velocity']

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if player["y"] + player['velocity'] + radius <= HEIGHT:
                    player["y"] = player["y"] + player['velocity']

            data = 'Position ' + str(player['x']) + ' ' + str(player['y'])
            threading.Thread(target=self.server.sendDataToServer(data)).start()
            players = self.server.receiveDataFromServer()
            
            data = 'Food '
            threading.Thread(target=self.server.sendDataToServer(data)).start()
            food = self.server.receiveDataFromServer()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False  

            self.drawGameComponents(players, food)
            pygame.display.update()

        self.server.disconnectFromServer()
        pygame.quit()
        quit()              

    def drawGameComponents(self, players, food):
        self.window.fill((255, 255, 255))

        for i in range(len(food)):
            snack = food[i]
            pygame.draw.circle(self.window, snack[2], (snack[0], snack[1]), 3)

        for player in players:
            p = players[player]
            pygame.draw.circle(self.window, p['color'], (p['x'], p['y']), START_PLAYER_RADIUS + p['radius'])

            name = FONT.render(p['name'], 1, (0, 0, 0))
            self.window.blit(name, (p['x'] - name.get_width()/2, p["y"] - name.get_height()/2))

        leaderboard_title = FONT.render('Leaderboard', 1, (0,0,0))
        self.window.blit(leaderboard_title, (WIDTH - 80, 5))

        score_list = list(reversed(sorted(players, key = lambda x: players[x]['radius'])))

        leng = min(len(players), 3)
        for count, i in enumerate(score_list[:leng]):
            text = FONT.render(str(count + 1) + '. ' + str(players[i]['name']) + ' ' + str(players[i]['radius']), 1, players[i]['color'])
            self.window.blit(text, (WIDTH - 80, 25 + count * 20))

if __name__ == '__main__':
   app = QApplication([])
   client = Client()
   sys.exit(app.exec_())

   