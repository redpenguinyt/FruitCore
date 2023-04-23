import discord, requests, os
from discord.ext import commands
from PIL import Image
from fruitcore import generate_fruitcore, get_stock_images
from dotenv import load_dotenv

# This bot requires ffmpeg to be installed
# Made by redpenguinyt, do not claim as your own

load_dotenv()
UNSPLASH_CLIENT_ID = "cKakzKM1cx44BUYBnEIrrgN_gnGqt81UcE7GstJEils"
APPLICATION_ID = int(os.getenv('DISCORD_APP_ID'))
TOKEN = os.getenv('DISCORD_TOKEN')
TEST_GUILD = discord.Object(id=os.getenv('DISCORD_GUILD'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix = "fc!",
			owner_ids = [666323445453291561],
			help_command = None,
			intents = intents,
			activity = discord.Activity(type=discord.ActivityType.listening, name="fruitcore"),
			application_id = APPLICATION_ID
		)

	async def setup_hook(self):
		await self.tree.sync()
		self.tree.copy_global_to(guild=TEST_GUILD)

bot = MyBot()

@bot.tree.command()
async def ping(ctx: discord.Interaction):
    await ctx.response.send_message("Pong!", ephemeral=True)

@bot.tree.command()
async def speech_bubble(ctx: discord.Interaction, image_link: str):
    await ctx.response.defer()

    try:
        r = requests.get(image_link)

        print(r.status_code)

        file = open("pre_bubbled.png", "wb")
        file.write(r.content)
        file.close()

        pre_bubbled = Image.open("pre_bubbled.png")
        speech_bubble = Image.open("speech_bubble.png")

        image_width = pre_bubbled.size[0]

        speech_bubble = speech_bubble.resize((image_width, int(image_width*0.32)))

        pre_bubbled.paste(speech_bubble, (0, 0), speech_bubble)

        bubbled = pre_bubbled.convert('RGBA')
        datas = bubbled.getdata()

        newData = []
        for item in datas:
            if item[0] == 49 and item[1] == 51 and item[2] == 56: # detect discord colour
                newData.append((255, 255, 255, 0)) # transparent pixel
            else:
                newData.append(item) # unedited pixel
        bubbled.putdata(newData)
        bubbled.save('bubbled.png', "PNG")

        os.system("ffmpeg -i bubbled.png -vf alettegen -y palette.png")
        os.system('ffmpeg -v warning -i bubbled.png -i palette.png  -lavfi "paletteuse,setpts=6*PTS" -y bubbled.gif')

        pre_bubbled.close()
        speech_bubble.close()

        await ctx.followup.send(file=discord.File("bubbled.gif", filename="bubbled.gif"))
        print("> Success!\n----------------------\n")

    except Exception as e:
        print(f"> Error: {e}\n----------------------\n")
        await ctx.followup.send(f"Error: {e}")

    os.system("rm pre_bubbled.png")
    os.system("rm bubbled.png")
    os.system("rm palette.png")
    os.system("rm bubbled.gif")

@bot.tree.command()
async def list_fruits(ctx: discord.Interaction, fruit: str, image_count: int=5):
    await ctx.response.defer()

    samples = get_stock_images(fruit, image_count)

    samples_text = "**Choose any of the following images for your fruitstep:**\n" + ''.join(f"[{i}]({link}) " for i, link in enumerate(samples))

    await ctx.followup.send(samples_text)

@bot.tree.command()
async def fruitcore(ctx: discord.Interaction, image_link: str, song_link: str, timestamp_from: str="0:00", timestamp_to: str="", bitrate: str="96k"):
    await ctx.response.defer()

    print("> Generating fruitstep")
    print(f"> Image: {image_link}")
    print(f"> Song: {song_link}")
    print(f"> Timestamps: {timestamp_from}-{timestamp_to}")
    print(f"> Bitrate: {bitrate}")

    # Baby-proofing

    error = generate_fruitcore() # generates the fruitcore video, creating a result.mp4 file

    if error == None:
        print("> Success!")
        await ctx.followup.send(file=discord.File("result.mp4", filename="result.mp4"))
    else:
        print(f"> Error: {error}")
        await ctx.followup.send(f"Error: {error}")

    print("\n----------------------\n")
    os.system("rm result.mp4")


if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)