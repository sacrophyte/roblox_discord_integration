import discord
import logging
import os # default module
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageColor

def drawProgressBar(percent, rank):
    ## credit for original progress bar idea: https://github.com/python-pillow/Pillow/discussions/6271#discussioncomment-2693092
    # Solid background color
    outerW, outerH = 310, 50
    offsetX = 30
    offsetFontX = 4
    offsetFontY = 4
    middleW, middleH = outerW/2 - 8, outerH/2 - 8
    im = Image.new("RGBA", (outerW, outerH), (66, 66, 66, 0))

    # For the "foreground image", I'll create a coloured gradient
    w, h = 256, 30
    gradient = Image.linear_gradient("L").crop((0, 0, h, w)).rotate(90, expand=True)
    empty = Image.new("L", gradient.size)
    solid = Image.new("L", gradient.size, 255)
    foreground = Image.merge("RGB", (solid, gradient, empty))

    x, y = (outerW - w) // 2, (outerH - h) // 2

    # print(f"w:{w} h:{h} x:{x} y:{y}")
    # The progress bar
    progress = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(progress, "RGBA")
    draw.rounded_rectangle((0, 0, w, h), 30, fill="#000")

    im.paste(progress, (x, y), progress)

    if percent < 0:
        percent = 0

    if percent > 1:
        percent = 1

    progress_ims = [foreground, progress]
    for i, progress_im in enumerate(progress_ims):
            progress_ims[i] = progress_im.crop((0, 0, int(w * percent), h))
    im.paste(progress_ims[0], (x, y), progress_ims[1])

    id = ImageDraw.Draw(im)

    ## add decorational text
    text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    progress_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    rank_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    greenPercent = int(255*percent)
    levelupColor=ImageColor.getrgb("rgb(255," + str(greenPercent) + ",0)")
    id.text((middleW, middleH), str(round(percent*100)) + "%", font=progress_font)
    id.text((0, offsetFontY), "Level", font=text_font)
    id.text((w + offsetX, offsetFontY), "Level", font=text_font)
    id.text((offsetFontX, middleH-offsetFontY), str(rank), fill="red", font=rank_font)
    id.text((w + offsetX+offsetFontX, middleH-offsetFontY), str(rank+1), fill=levelupColor, font=rank_font)

    im.save("output.png")


# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

load_dotenv() # load all the variables from the env file
client = discord.Client()

@client.event
async def on_ready():
    print(f"{client.user} is ready and online!")
    ## await message.channel.send('I have arrived!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$progressbar'):
        percent = 0.5
        args = message.content.split(" ")
        if len(args) > 2:
            percent = args[1]
            rank = args[2]

        # draw the progress bar to given location, width, progress and color
        drawProgressBar(float(percent), int(rank))

        # embed progress bar
        embed = discord.Embed(title="Clan Rank Progress", color=0x00ff00) #creates embed
        file = discord.File("output.png")
        embed.set_image(url="attachment://output.png")
        await message.channel.send(file=file, embed=embed)

client.run(os.getenv('TOKEN')) # run the client with the token
