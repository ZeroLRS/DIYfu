import datetime

import discord
from discord.ext import commands

from generator_request_manager import GenerationRequest, GenerationRequestManager

class DIYfuBot:
    MAX_STEP_LIMIT = 100

    bot = None
    token = None

    def __init__(self, token=token):
        if (not token == None):
            self.token = token

        # The bot need to have these permissions to run properly
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        # Build our bot to respond to the $ prefix
        DIYfuBot.bot = commands.Bot(command_prefix='$', intents=intents)

        # Register the commands to the bot
        self.bot.add_command(y)

    def start_bot(self):
        # Run the bot. At this point, the thread will just follow the bot,
        #   so don't try to do anything afterwards
        self.bot.run(self.token)

    async def send_waifu(self, request, img_location):
        # The title cannot be longer than 255 characters
        title = request.initial_prompt
        if (len(title) > 255):
            title = title[0:252] + '...'

        # Build our embed that is sent to the channel
        embed = discord.Embed(title=f"{title}",
                            description=f"Prompt By: <@{request.userid}>",
                            timestamp = datetime.datetime.now(),
                            colour=0x00FFFF)
        embed.set_footer(text=(f"seed:\t'{request.seed}'\n"
                        f"steps:\t'{request.steps}'\n"
                        f"cfg:\t'{request.cfg_scale}'"))
        
        # Attach the generated waifu image to the embed and upload it to discord
        file = discord.File(img_location, filename=f"{request.userid}.{request.seed}.png")
        embed.set_image(url=f"attachment://{request.userid}.{request.seed}.png")
        
        # Get the channel to send the embed and image to
        channel = self.bot.get_channel(request.channel)

        # Send the embed and image
        await channel.send(file=file, embed=embed)

#Please refactor this into something more flexible, thanks
#syntax is y, i = steps, s = seed, c = cgf
@commands.command()
async def y(ctx, *args):
    prompt_arg = 1
    request = GenerationRequest()
    request.steps = min(int(args[0]), DIYfuBot.MAX_STEP_LIMIT)
    if(args[1].isdigit()):
        request.cfg_scale = int(args[1])
        prompt_arg += 1
        if (args[2].isdigit()):
            request.seed = args[2]
            prompt_arg += 1

    request.initial_prompt = args[prompt_arg]
    request.userid = ctx.message.author.id
    request.channel = ctx.channel.id
    GenerationRequestManager.add_request(request)
    await ctx.send("Request recieved!")