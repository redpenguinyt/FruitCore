# FruitCore Discord bot
The fruitcore discord bot generates fruitcore videos. You can [add it to your server by clicking here](https://discord.com/api/oauth2/authorize?client_id=1084925019500580986&permissions=2147862528&scope=bot%20applications.commands) or you can run it on your own machine by downloading the source code here on GitHub.

## Features
- `/fruitcore <image_link> <song_link> [timestamp_from] [timestamp_to] [bitrate]` generates and posts a FruitCore video. the `song_link` parameter has only been tested with YouTube, Soundcloud and Bandcamp. It does not work with Spotify.
- `/list_fruits <fruit> [image_count]` returns a list of images to use with `/fruitcore`
- `/ping` quickly checks if the bot is running
- `/speech_bubble <image_link>` takes the image link you give it and returns the same image with a speech bubble overlay

## Running on your own
Make sure you have a `.env` file with the parameters **DISCORD_TOKEN** (the bot's token), **DISCORD_APP_ID** (the bot's application id) and **DISCORD_GUILD** (for your discord server's guild id).

Also make sure you have FFmpeg installed. The installation process process varies from OS to OS so check the official [FFmpeg website](https://ffmpeg.org/)

Then just enter the main directory and run `pip install -r requirements.txt` then `python bot.py`. This bot has been tested with Python 3.11.3