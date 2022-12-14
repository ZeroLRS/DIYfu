import datetime
import shlex

import discord
from discord.ext import commands

from generator_request_manager import GenerationRequest, GenerationRequestManager

class DIYfuBot:
    MAX_STEP_LIMIT = 100
    COMMAND_PREFIX = '$'

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
        DIYfuBot.bot = commands.Bot(command_prefix=DIYfuBot.COMMAND_PREFIX, intents=intents)

        # Add in our custom commands
        self.bot.add_command(DIYfuBot.defaults)
        self.bot.add_command(DIYfuBot.queue)

        # Remove the help command and replace it with a custom one
        self.bot.remove_command('help')
        self.bot.add_command(DIYfuBot.help)

        # Overwrite the default message handler with a custom one
        self.bot.on_message = DIYfuBot.handle_message

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

    async def handle_message(message : discord.Message):
        # Ignore any messages that come from the bot or are empty
        if (DIYfuBot.bot.user.id == message.author.id or len(message.content) == 0):
            return
        
        # We want to use a special command handler for any command not set up the standard way
        if (message.content[0] == DIYfuBot.COMMAND_PREFIX):
            # If the command sent isn't in the normal command list, forward it to the complex command handler
            if (message.content.split()[0][1:] not in DIYfuBot.bot.all_commands.keys()):
                await DIYfuBot.handle_complex_command(message)
                return
            else:
                # Otherwise, run normal commands as ususal
                await DIYfuBot.bot.process_commands(message)

    async def handle_complex_command(message : discord.Message):
        # split the message into arguments for processing them
        args = shlex.split(message.content)

        # Handle the image generation request complex command if the first character after the command prefix is 'y'
        if (len(args[0]) > 1):
            if (args[0][1] == 'y'):
                await DIYfuBot.handle_image_generation_request(message, args)

    async def handle_image_generation_request(message : discord.Message, args):
        request = GenerationRequest(userid=message.author.id, channel=message.channel.id)

        # every character in the first arguement after the command prefix and the 'y' are arguments that will be passed to the generator
        argument_index = 1
        found_prompt = False
        if (len(args[0]) > 2):
            for char in args[0][2:]:
                if (char == 's'):
                    request.seed = int(args[argument_index])
                elif (char == 'i'):
                    request.steps = int(args[argument_index])
                elif (char == 'c'):
                    request.cfg_scale = float(args[argument_index])
                elif (char == 'd'):
                    # Disabled defaults listed by (p)refix, (s)uffix, or (n)egative
                    for neg_default in args[argument_index]:
                        if (neg_default in ('p', 'P')):
                            request.use_prefixes = False
                        if (neg_default in ('s', 'S')):
                            request.use_suffixes = False
                        if (neg_default in ('n', 'N')):
                            request.use_negative = False
                elif (char == 'p'):
                    request.initial_prompt = args[argument_index]
                    found_prompt = True
                argument_index += 1

        #if a 'p' was not specified, assume that the last argument is the prompt
        if (found_prompt == False):
            if (len(args) > argument_index):
                request.initial_prompt = args[argument_index]
                found_prompt = True

        # Add the new request to the queue
        GenerationRequestManager.add_request(request)

        print("Sending request: " + str(vars(request)))
        await message.channel.send("Request recieved!")
  
    @commands.command()
    async def help(ctx : commands.Context, *args):
        message = ("Use $y followed by any optional commands to generate an image.\n\n"
                    "For example: `$ys 101 \"A mountain\" ` will generate a picture of a mountain using the seed 101.\n\n"
                    "The full list of commands is:\n"
                    "`s`: The seed to use for the image's generation\n"
                    "`i`: The number of iterations the image should take to generate\n"
                    "`c`: The cfg_scale value to use when generating the image.\n"
                    "`d`: Disables the default (p)refix, (s)uffix, and/or (n)egative prompt additions\n"
                    "`p`: Can be used to place the prompt somewhere other than the end\n\n"
                    "For example: `$yscipd 777 5 200 \"A green car\" ps` will generate an image of a green car with: a seed of 777, a cfg value of 5, taking 200 steps of generation, and ignoring the prefix and suffix default prompt additions.")
        await ctx.send(message)

    @commands.command()
    async def defaults(ctx : commands.Context, *args):
        seed_text = "a random number"
        if (GenerationRequest.seed != -1):
            seed_text = f"fixed to {GenerationRequest.seed}"
        message = ("Default Prompt Additions:\n"
                    f"Prefixes: `{GenerationRequestManager.prompt_prefixes}`\n"
                    f"Suffixes: `{GenerationRequestManager.prompt_suffixes}`\n"
                    f"Negative: `{GenerationRequestManager.prompt_negative}`\n\n"
                    "Default command values:\n"
                    f"`s`: {seed_text}\n"
                    f"`i`: {GenerationRequest.steps} steps\n"
                    f"`c`: a cfg of {GenerationRequest.cfg_scale}\n"
                    f"`d`: prefixes: `{str(GenerationRequest.use_prefixes)}`, suffixes: `{str(GenerationRequest.use_suffixes)}`, negatives: `{str(GenerationRequest.use_negative)}`")
        await ctx.send(message)

    @commands.command()
    async def queue(ctx : commands.Context, *args):
        # Build our embed that is sent to the channel
        embed : discord.Embed = discord.Embed(title="Image Generation Queue",
                            colour=0x00FFFF)

        # If there is a processing request and the image generator is working on it, post that
        if(GenerationRequestManager.current_request != None and GenerationRequestManager.currently_generating == True):
            request = GenerationRequestManager.current_request
            prompt = request.initial_prompt
            if (len(prompt) > 50):
                prompt = prompt[0:50] + "..."
            embed.add_field(name=f"Generating Now", value=f"<@{request.userid}>: `{prompt}`", inline=False)
        # There is never a case where there is no image being generated and there's a queue, so there's no reason to check
        else:
            embed.description = "Not currently generating any images."
            await ctx.send(embed=embed)
            return

        # If the queue is empty, append that and send the message
        if (GenerationRequestManager.generate_queue.empty() == True):
            embed.description += "The queue is empty!"
            await ctx.send(embed=embed, inline=False)
            return

        # If there is something in the queue, append each item in a numbered list
        iter = 1
        for request in list(GenerationRequestManager.generate_queue.queue):
            prompt = request.initial_prompt
            if (len(prompt) > 50):
                prompt = prompt[0:50] + "..."
            embed.add_field(name=f"#{str(iter)} in Queue", value = f"<@{request.userid}>: `{prompt}`", inline=False)
            iter += 1

        # Send the embed
        await ctx.send(embed=embed)

# For testing/debugging purposes, it's nice to be able to run the bot independent of the image generator
if (__name__ == "__main__"):
    import configparser
    import os

    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.dirname(__file__)) + ('\config.ini'))

    DIYfuBot.token = config['DIYfu']['discord_token']

    bot = DIYfuBot()
    bot.start_bot()