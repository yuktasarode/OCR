import math

import numpy as np
from rapidocr_onnxruntime import RapidOCR


class RapidRecognizer:
    def __init__(self, engine=None):
        self.engine = engine or RapidOCR()

    def recognize(self, image: np.ndarray) -> tuple[str, float]:
        result, _ = self.engine(image)
        if not result:
            return "", 0.0
        ordered = sorted(result, key=lambda item: (min(point[0] for point in item[0]), min(point[1] for point in item[0])))
        text = " ".join(item[1] for item in ordered)
        confidence = sum(float(item[2]) for item in ordered) / len(ordered)
        return text, round(confidence, 4)


class TrOCRRecognizer:
    def __init__(self, model_name: str = "microsoft/trocr-small-handwritten"):
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel

        self.processor = TrOCRProcessor.from_pretrained(model_name, use_fast=False)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.model.eval()

    def recognize(self, image: np.ndarray) -> tuple[str, float]:
        import torch
        from PIL import Image

        pil_image = Image.fromarray(image).convert("RGB")
        pixel_values = self.processor(images=pil_image, return_tensors="pt").pixel_values
        with torch.inference_mode():
            output = self.model.generate(
                pixel_values,
                max_new_tokens=48,
                return_dict_in_generate=True,
                output_scores=True,
            )
        text = self.processor.batch_decode(output.sequences, skip_special_tokens=True)[0]
        token_probabilities = []
        for token_index, logits in enumerate(output.scores):
            token = output.sequences[0, token_index + 1]
            token_probabilities.append(torch.softmax(logits[0], dim=-1)[token].item())
        confidence = math.prod(token_probabilities) ** (1 / len(token_probabilities)) if token_probabilities else 0.0
        return text.strip(), round(confidence, 4)
