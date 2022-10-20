# DIYfu, a Waifu Generator

DIYfu generates anime-style images using [Waifu Diffusion](https://huggingface.co/hakurei/waifu-diffusion) and the [InvokeAI](https://github.com/invoke-ai/InvokeAI) fork of [Stable Diffusion](https://github.com/CompVis/stable-diffusion).
This is my first project in Python, so my code is likely full of style issues and standard non-conforming practices. If you see anything that can be improved up, please feel free to create an issue and I'll address it.
# Running

 1. Follow the standard setup instructions for InvokeAI given on their github page.
 2. Enter the conda environment 'invokeai' while in the root directory of the project. 
	(You should have the folders for both InvokeAI and DIYfu in the current directory.)
 3. Install discord&#46;py using `python -m pip install discord`
 4. Follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html) to create a Discord bot account and invte the bot to your server. Place the token generated during these instructions into config.ini in the DIYfu subfolder.
 5. Configure the rest of config.ini as desired.
 6. Run the command `python DIYfu` to execute the program.

# Usage
Type $y followed by up to three integer values for step, cfg, and seed, finally the prompt in quotes.
Here's a basic example:
![Example Command](../media/ExampleCommand.png)  ![Example Image](../media/ExampleImage.png)

# Upcoming
Some features I plan to implement include: 
- A much better syntax for issuing commands to the bot.
- The abillity to load [textual inversion checkpoints](https://huggingface.co/docs/diffusers/training/text_inversion) as an argument, using checkpoints defined by the bot's host.
- A help command to show what the arguments for generating an image are, and what they default to if not specified.
- A command to view the current queue.
- The option to also have the image DM'd to the user prompting it.
Suggestions are welcome.