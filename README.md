# DIYfu, a Waifu Generator
  
DIYfu generates anime-style images using [Waifu Diffusion](https://huggingface.co/hakurei/waifu-diffusion) and the [InvokeAI](https://github.com/invoke-ai/InvokeAI) fork of [Stable Diffusion](https://github.com/CompVis/stable-diffusion).

This is my first project in Python, so my code is likely full of style issues and standard non-conforming practices. If you see anything that can be improved upon, please feel free to create an issue and I'll address it.

# Running
  
1. Follow the standard setup instructions for InvokeAI given on their github page.

2. Enter the conda environment 'invokeai' while in the root directory of the project.

(You should have the folders for both InvokeAI and DIYfu in the current directory.)

3. Install discord&#46;py using `python -m pip install discord`

4. Follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html) to create a Discord bot account and invte the bot to your server. Place the token generated during these instructions into config.ini in the DIYfu subfolder.

5. Configure the rest of config.ini as desired.

6. Run the command `python DIYfu` to execute the program.
  
# Usage
Use $y followed by any optional commands to generate an image.
  
For example: `$ys 101 "A mountain"` will generate a picture of a mountain using the seed 101.
  
The full list of commands is:

`s`: The seed to use for the image's generation  

`i`: The number of iterations the image should take to generate  

`c`: The cfg_scale value to use when generating the image  

`d`: Disables the default (p)refix, (s)uffix, and/or (n)egative prompt additions  

`p`: Can be used to place the prompt somewhere other than the end  
  
For example: `$yscipd 777 5 200 "A green car" ps` will generate an image of a green car with: a seed of 777, a cfg value of 5, taking 200 steps of generation, and ignoring the prefix and suffix default prompt additions.
  
![Example Command](../media/ExampleCommand.png) ![Example Image](../media/ExampleImage.png)
  
This information can be found in the bot using the `$help` command.  
A list of default values (from `config.ini`) can be shown via the `$defaults` command.  
The current queue of users waiting for generation can be viewed with the `$queue` command.  
  
# Recent Additions

- The defaults command now also shows the default command values

- A command to view the current queue
  
# Upcoming

Some features I plan to implement include:

- The abillity to load [textual inversion checkpoints](https://huggingface.co/docs/diffusers/training/text_inversion) as an argument, using checkpoints defined by the bot's host.

- The option to also have the image DM'd to the user prompting it.

Suggestions are welcome.