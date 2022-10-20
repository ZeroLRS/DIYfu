from tkinter import Image
import transformers
import torch

from tqdm import tqdm

from omegaconf import OmegaConf

from ldm.util import instantiate_from_config
from ldm.models.diffusion.ksampler import KSampler
from ldm.invoke.generator.txt2img import Txt2Img
from ldm.invoke.devices import choose_precision
from ldm.invoke.conditioning import get_uc_and_c

from generator_request_manager import GenerationRequest

class ImageGenerator:

	model = None
	config = None
	device = None
	generator = None
	model = None
	sampler = None

	def load_model_from_config(self, config, ckpt):
		print(f"Loading self.model from {ckpt}")
		pl_sd = torch.load(ckpt, map_location="cpu")

		sd = pl_sd["state_dict"]

		ImageGenerator.model = instantiate_from_config(config.model)

		m, u = self.model.load_state_dict(sd, strict=False)

		self.model.to(torch.device("cuda"))
		self.model.eval()

	def __init__(self, model, config):
		transformers.logging.set_verbosity_error()

		ImageGenerator.model = model
		ImageGenerator.config = config

		config = OmegaConf.load(config)
		self.load_model_from_config(config, model)

		ImageGenerator.device = torch.device("cuda")
		self.model.to(self.device)

		ImageGenerator.sampler = KSampler(self.model, 'euler', device=self.device)
		
		ImageGenerator.generator = Txt2Img(self.model, choose_precision(self.device))
		self.generator.free_gpu_mem = False

	def generate_image(self, request : GenerationRequest, callback):
		shape = [request.samples, 4, 512 // 8, 512 // 8]

		torch.randn(shape, device=self.device)

		data = [request.samples * [request.prompt]]

		self.generator.set_variation(request.seed, 0.0, [])

		for prompts in tqdm(data, desc="data"):
			
			uc, c = get_uc_and_c(
						request.prompt, model = self.model,
						skip_normalize = False,
						log_tokens = False
					)
			
			results = self.generator.generate(
							request.prompt,
							iterations=request.samples,
							seed=request.seed,
							sampler=self.sampler,
							steps=request.steps,
							cfg_scale=request.cfg_scale,
							conditioning=(uc, c),
							ddim_eta=0.0,
							image_callback=callback,  # called after the final image is generated
							step_callback=None,   # called after each intermediate image is generated
							width=512,
							height=512,
							init_img=None,
							init_image=None,
							mask_image=None,
							strength=None,
							threshold=0.0,
							perlin=0.0,
							embiggen=None,
							embiggen_tiles=None,
						)