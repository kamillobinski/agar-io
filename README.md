<h1 align="center">
  Agar.io
  <br>
</h1>

<h4 align="center">Popular game clone developed using pygame.</h4>

<p align="center">
<img alt="Project version" src="https://img.shields.io/badge/version-1.0.0-orange">
<a href="https://github.com/kamillobinski/Agar.io/issues"> <img alt="GitHub issues" src="https://img.shields.io/github/issues/kamillobinski/Agar.io"></a>
<a href="https://github.com/kamillobinski/Agar.io/stargazers"> <img alt="GitHub stars" src="https://img.shields.io/github/stars/kamillobinski/Agar.io"></a>
<a href="https://github.com/kamillobinski/Agar.io/blob/master/LICENSE"> <img alt="GitHub license" src="https://img.shields.io/github/license/kamillobinski/Agar.io"></a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#download">Download</a> •
  <a href="#dependencies">Dependencies</a> •
  <a href="#license">License</a>
</p>

![screenshot](https://github.com/kamillobinski/Agar.io/blob/master/readme-files/agar.gif?raw=true)

## Key Features

* Control your cell using WASD or arrow keys.
* Each cell displays username.
* Eat food and other players in order to grow your character.
  - Players who haven't eaten yet cannot be eaten by others.
* Food respawns:
  - if it's number is less than 10.
  - when new player enters the game.
* Cell's mass is the number of food particles eaten.
* Dynamic leaderboard in the top right corner.
* Game logic is handled by the server.
* Client side is used only for rendering game components.

###### Update 1.1.0
* Added bot that can be launched from server.
* Functions:
  - Detecting the nearest food from current position.
  - Gathering food when radius is less than 10.
  - Looking for the nearest player when radius is more than 10.
  - If the player is close enough, it performs attack.
  - After collision with player, goes back to collecting food.
  
## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python](https://www.python.org/downloads/). From your command line:

```bash
# Clone this repository
$ git clone https://github.com/kamillobinski/Agar.io
```

After succesfull cloning, change both server and client IP address:

```python
self.host = '192.168.56.1'
self.port = 55550
```

Lastly remember to launch server before client.

## Download

Not available. Please check the intructions [above](#how-to-use).

## Dependencies

- Pygame ```pip install pygame```
- PyQt5 ```pip install PyQt5```

## Support

Show some :heart: and star the repo to support the project.

## You may also like...

- [Instagram](https://github.com/kamillobinski/instagram) - Popular social networking website clone.
- [Weather app](https://github.com/kamillobinski/Weather-App) - Desktop app with local weather

## License

Apache 2.0

---

> Gmail [Kamil Łobiński](mailto:kamilobinski@gmail.com) &nbsp;&middot;&nbsp;
> GitHub [@kamillobinski](https://github.com/kamillobinski) &nbsp;&middot;&nbsp;
> LinkedIn [Kamil Łobiński](https://www.linkedin.com/in/kamillobinski/?locale=en_US)

