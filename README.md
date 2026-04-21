[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)\
[![forthebadge](https://forthebadge.com/images/badges/0-percent-optimized.svg)](https://forthebadge.com) 
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com) 
[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com) 
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) 
[![forthebadge](https://forthebadge.com/images/badges/powered-by-electricity.svg)](https://forthebadge.com) 
[![forthebadge](https://forthebadge.com/images/badges/designed-in-ms-paint.svg)](https://forthebadge.com)

# IgnoBot.py
This is the successor of IgnoBot.js, which was either very slow or simply not working at all.\
**_So_**, IgnoBot is now a :duck:,
_finally_ works **much** faster and is written using the [Python](https://www.python.org/) programming language :D.

## Requirements
All the requirements can be installed by using `pip install -r new.requirements.txt`
In case you're wondering, [here are all the libraries used.](requirements.txt)


### Note
> This bot was tested and developed using Python 3.10. I know it works with python 3.9, as this is the version that is often used by hosting providers. I don't know if it works with any past version, but will not be testing versions myself, as that would take *too long*, ~~sorry~~.
> You can download the latest version of Python [here.](https://python.org/downloads)

## Commands list
<details>
  <summary>Animals Cog</summary>

  | Command   | Description                                             | Parameters |
  |-----------|---------------------------------------------------------|------------|
  | animal    | Animal images/videos                                    | None       |
  | duckimage | Sends you a cute duck image :3                          | None       |
  | duckvideo | Sends you a cute duck video :3                          | None       |
  | catimage  | Sends you a cute cat image :3                           | None       |
  | catvideo  | Sends you a cute cat video :3                           | None       |
  | cattos    | Sends more cats images. Only works in specific servers. | None       |
</details>

<details>
  <summary>Decoder Cog</summary>

  |   |   |   |
  |---|---|---|
  |   |   |   |
  |   |   |   |

</details>

<details>
  <summary>Osu Cog</summary>

  | Command         | Description                | Parameters                |
  |-----------------|----------------------------|---------------------------|
  | map             | Get beatmap information    | beatmap_id: int = None    |
  | set             | Get beatmapset information | beatmapset_id: int = None |
  | beatmap_to_json | Convert beatmap to JSON    | beatmap_id: int = None    |
</details>
<details>
  <summary>Economy Cog</summary>
  
  | Command | Description          | Parameters |
  |---------|----------------------|------------|
  | balance | Check user's balance |            |
</details>
<details>
  <summary>Help Cog</summary>
  
  | Command | Description | Parameters |
  |---------|-------------|------------|
  | help    |             |            |
</details>

| Command                       | Description                                                                                     | Parameters                    | Cog                                     |
|-------------------------------|-------------------------------------------------------------------------------------------------|-------------------------------|-----------------------------------------|
| Encode                        | Takes a string, encodes it into b64 format and DMs it to the user.                              | - String to encode            | [decoder.py](./cogs/decoder.py)         |
| Decode                        | Takes a string in b64 format, decodes it into the original string and DMs it to the user.       | - B64 format string to decode | [decoder.py](./cogs/decoder.py)         |
| Beep                          | Just sends "**Beep**" in the channel it's used. Used for quick testing.                         | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| Bad                           | Just sends "**Bad**" in the channel it's used. Used for quick testing.                          | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| amicool                       | Tells you if you're cool or not. You should try it, as it only tells the truth (joke).          | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| uwuduck                       | Sends an :uwuduck:. Very cute command.                                                          | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| anniqty                       | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| mof                           | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| nou                           | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| pronto <br/> Aliases: pronto? | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| fennec                        | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| annispam                      | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| silvio                        | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| osuskins                      | Personal [osu!](https://osu.ppy.sh) skin repo. Doesn't return a valid repository at the moment. | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| shid                          | osu! meme command. Don't think too much about it.                                               | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| python                        | Personal meme command. Don't think too much about it.                                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| duckimage                     | Returns a random duck image from [r/duck](https://reddit.com/r/duck).                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| duckvideo                     | Returns a random duck video from [r/duck](https://reddit.com/r/duck).                           | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| catimage                      | Returns a random cat image from [r/cats](https://reddit.com/r/cats).                            | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| catvideo                      | Returns a random cat video from [r/cats](https://reddit.com/r/cats).                            | No parameters                 | [dumb.py](./cogs/dumb.py)               |
| cattos                        | Private cat command. Don't think too much about it.                                             | No parameters.                | [dumb.py](./cogs/dumb.py)               |
| kayo                          | Returns the anime's info and download.                                                          | - Anime name                  | [hentie.py](./cogs/hentie.py)           |
| level                         | Returns an embed with the level and xp of the respective user.                                  | - User (Optional)             | [levelsystem.py](cogs/level_system.py) |
|                               |                                                                                                 |                               |                                         |

https://discord.com/oauth2/authorize?client_id=913424314290815007&permissions=397770484806&scope=bot%20applications.commands \

New readme soon™

~krypt has smol pp

~But Atlas has smallest pp
