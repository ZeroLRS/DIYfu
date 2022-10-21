import queue
import threading
import os
import random
from matplotlib.style import use
import numpy as np
from pathlib import Path

from ldm.invoke.pngwriter import PngWriter

class GenerationRequest:
	seed = -1
	steps = 100
	samples = 1
	cfg_scale = 12
	use_prefixes = True
	use_suffixes = True
	use_negative = True

	def __init__(self, userid=-1, channel=-1, seed=seed,
				steps=steps, samples=samples, cfg_scale=cfg_scale,
				use_prefixes=use_prefixes, use_suffixes=use_suffixes, use_negative=use_negative,
				prompt=''):
		self.initial_prompt = prompt
		self.use_negative = use_negative
		self.use_suffixes = use_suffixes
		self.use_prefixes = use_prefixes
		self.steps = steps
		self.samples = samples
		self.cfg_scale = cfg_scale
		self.userid = userid
		self.channel = channel
		self.prompt = ''

		# If the user didn't define a seed to use, randomly generate one
		if(seed == -1):
			self.seed = random.randrange(0, np.iinfo(np.uint32).max)
		else:
			self.seed = seed

class GenerationRequestManager:

	# These affixes are added to all prompts that don't set the appropriate disable flags
	prompt_prefixes = '1girl, '
	prompt_suffixes = ', anime, highres, deep eyes, well drawn, '
	prompt_negative = '[multiple arms, deformed, blurry, bad anatomy, disfigured, poorly drawn face, poorly drawn hands, bad hands], '

	# Output our waifu images to this folder
	output_location = "GeneratedWaifus"

	# The queue of requests that are pending
	generate_queue = None

	# If the image generator is busy generating
	currently_generating = False

	# The callback function for when an image is done generating
	done_generating_callback = None

	# The current request running on the image generator
	current_request = None

	# The image generator
	generator = None

	# The thread where we process the requests queue
	request_processor = None

	def __init__(self, generator, finished_callback, output_location=output_location):
		if (not (self.generate_queue == None)):
			return
		
		GenerationRequestManager.generator = generator
		GenerationRequestManager.output_location = output_location
		GenerationRequestManager.done_generating_callback = finished_callback

		GenerationRequestManager.generate_queue = queue.Queue()

		# Ensure our output directory exists
		Path(output_location).mkdir(exist_ok=True)

		GenerationRequestManager.request_processor = threading.Thread(target=self.process_requests)
		self.request_processor.start()

	def process_requests(self):
		print("Starting request processing loop")

		while(True):
			# If there is no image currently generating, and there's something in the queue
			if(self.currently_generating == False and not self.generate_queue.empty()):
				# Mark that a generation is occuring and then start one
				GenerationRequestManager.currently_generating = True
				self.generate_next()

	def generate_next(self):
		# Get oldest request from the queue
		GenerationRequestManager.current_request = self.generate_queue.get()

		# Build our prompt using the prefix, suffix, and negatives if they are enabled
		prompt_composit = self.current_request.initial_prompt
		if (self.current_request.use_prefixes == True):
			prompt_composit = self.prompt_prefixes + prompt_composit
			
		if (self.current_request.use_suffixes == True):
			prompt_composit = prompt_composit + self.prompt_suffixes

		if (self.current_request.use_negative):
			prompt_composit = prompt_composit + self.prompt_negative

		# Re-add the new prompt back to the request
		self.current_request.prompt = prompt_composit

		print(f"Sending request from {self.current_request.userid} to generator")

		# Call the image generator to create the actual image, giving a callback to the done generating function
		self.generator.generate_image(request = self.current_request, callback = self.done_generating)

	@classmethod
	def add_request(cls, request):
		# Put a new request into the queue
		cls.generate_queue.put(request)

	def done_generating(self, image, seed, first_seed):
			outpath = self.output_location + "\\" + str(self.current_request.userid)

			# Ensure our final output directory exists
			Path(outpath).mkdir(exist_ok=True)

			# Build a png from our image and save it
			pngwriter = PngWriter(outpath)
			prefix = pngwriter.unique_prefix()
			name = f'{prefix}.{seed}.png'

			# Also write the prompt and seed to the .png file, this is preserved even after discord upload
			pngwriter.save_image_and_prompt_to_png(
				image, dream_prompt=f'{self.current_request.prompt} -S{seed}', name=name)
				
			print(f"Saving image to: {outpath}\\{name}")

			# Callback to another function that handles doing something with the image post-generation
			self.done_generating_callback(self.current_request, f"{outpath}\\{name}")

			# Declare that we are not currently generating and can start another
			GenerationRequestManager.currently_generating = False