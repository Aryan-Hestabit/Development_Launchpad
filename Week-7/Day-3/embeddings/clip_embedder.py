import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import CLIP_MODEL, IMAGE_WEIGHT, TEXT_WEIGHT


class CLIPEmbedder:

    def __init__(self, model_name: str = CLIP_MODEL):
        self.model     = CLIPModel.from_pretrained(model_name)
        self.model.eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def _image_vec(self, pixel_values) -> torch.Tensor:
        out       = self.model.vision_model(pixel_values=pixel_values)
        projected = self.model.visual_projection(out.pooler_output)
        return F.normalize(projected, dim=-1)

    def _text_vec(self, input_ids, attention_mask) -> torch.Tensor:
        out       = self.model.text_model(input_ids=input_ids, attention_mask=attention_mask)
        projected = self.model.text_projection(out.pooler_output)
        return F.normalize(projected, dim=-1)

    def embed_image(self, source) -> np.ndarray:
        img    = Image.open(source).convert("RGB") if isinstance(source, str) else source.convert("RGB")
        inputs = self.processor(images=img, return_tensors="pt")
        with torch.no_grad():
            vec = self._image_vec(inputs["pixel_values"])
        return vec.squeeze().numpy().astype("float32")

    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.processor(text=[text], return_tensors="pt", truncation=True)
        with torch.no_grad():
            vec = self._text_vec(inputs["input_ids"], inputs["attention_mask"])
        return vec.squeeze().numpy().astype("float32")

    def embed_fused(self, source, combined_text: str) -> np.ndarray:
        image_vec = self.embed_image(source)
        text_vec  = self.embed_text(combined_text)
        fused     = IMAGE_WEIGHT * image_vec + TEXT_WEIGHT * text_vec
        # re-normalise so the fused vector stays on the unit sphere
        fused     = fused / (np.linalg.norm(fused) + 1e-8)
        return fused.astype("float32")