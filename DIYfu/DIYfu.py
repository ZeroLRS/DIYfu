import configparser
import os

from image_generator import ImageGenerator
from discord_bot import DIYfuBot
from generator_request_manager import GenerationRequestManager, GenerationRequest

class WaifuGenerator:
	
	model = "invokeai\models\ldm\waifu-diffusion-1.3\wd-v1-3-full.ckpt"
	config = "invokeai\configs\stable-diffusion\\v1-inference.yaml"

	generator = None
	request_manager = None
	discord = None
	
	def __init__(self):
		print("Loading config...")
		self.load_config()

		print("Beginning spool up generator...")
		WaifuGenerator.generator = ImageGenerator(self.model, self.config)

		print("Setting up request manager...")
		WaifuGenerator.request_manager = GenerationRequestManager(self.generator, self.bot_send_waifu)

		print("Launching bot...")
		WaifuGenerator.discord = DIYfuBot()
		self.discord.start_bot()

	def bot_send_waifu(self, request, img_location):
		# Create a new task on the discord bot's async loop to send the image to the requester
		self.discord.bot.loop.create_task(self.discord.send_waifu(request, img_location))

	def load_config(self):
		# Load all of the variables in config.ini and stick them in appropriate locations
		config = configparser.ConfigParser()
		config.read(os.path.abspath(os.path.dirname(__file__)) + ('\config.ini'))

		WaifuGenerator.model = config['DIYfu']['model_location']
		WaifuGenerator.config = config['DIYfu']['config_location']
		
		GenerationRequestManager.output_location = config['DIYfu']['output_location']
		
		GenerationRequestManager.prompt_prefixes = config['DIYfu']['prompt_prefixes']
		GenerationRequestManager.prompt_suffixes = config['DIYfu']['prompt_suffixes']
		GenerationRequestManager.prompt_negative = config['DIYfu']['prompt_negative']

		GenerationRequest.seed = int(config['RequestDefaults']['seed'])
		GenerationRequest.steps = int(config['RequestDefaults']['steps'])
		GenerationRequest.samples = int(config['RequestDefaults']['samples'])
		GenerationRequest.cfg_scale = int(config['RequestDefaults']['cfg_scale'])
		GenerationRequest.use_prefixes = config['RequestDefaults']['use_prefixes'] == 'True'
		GenerationRequest.use_suffixes = config['RequestDefaults']['use_suffixes'] == 'True'
		GenerationRequest.use_negative = config['RequestDefaults']['use_negative'] == 'True'

		DIYfuBot.token = config['DIYfu']['discord_token']

if __name__ == "__main__":
	gen = WaifuGenerator()