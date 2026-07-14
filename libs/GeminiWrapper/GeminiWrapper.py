import time
import requests
import io
import logging
import base64
from PIL import Image
from typing import Any, Callable, Dict, List, Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

from .config import config
from .models import InputParams, TextParams, ImageParams, OutputResult

try:
    from config import config as root_config
except ImportError:
    root_config = None

load_dotenv()


class GeminiWrapper:
    """Wrapper around the google-genai SDK for text and image generation with
    automatic model fallback, retry logic, and media processing."""

    def __init__(self, client: Optional[genai.Client] = None):
        if client is None:
            if root_config and getattr(root_config, "GCP_PROJECT_ID", None):
                self.client = genai.Client(
                    vertexai=True, 
                    project=root_config.GCP_PROJECT_ID, 
                    location="global"
                )
                self.image_client = genai.Client(
                    vertexai=True, 
                    project=root_config.GCP_PROJECT_ID, 
                    location="global"
                )
            else:
                self.client = genai.Client()
                self.image_client = self.client
        else:
            self.client = client
            self.image_client = client
        self.logger = logging.getLogger("GeminiWrapper")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_text(
        self,
        input_params: InputParams,
        text_params: Optional[TextParams] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate text content using the Gemini API."""
        if text_params is None:
            text_params = TextParams()

        model = input_params.model or config.default_text_model
        models_to_try = self._prioritize_models(model, config.text_fallback_models)
        gen_config, contents = self._prepare_model_inputs(
            input_params=input_params, text_params=text_params, **kwargs
        )

        def extract_text(response: Any) -> Any:
            result = response.parsed if text_params.response_schema else response.text
            if text_params.response_schema and isinstance(result, dict):
                try:
                    if hasattr(text_params.response_schema, "model_validate"):
                        return text_params.response_schema.model_validate(result)
                    elif isinstance(text_params.response_schema, type):
                        return text_params.response_schema(**result)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to convert dict to Pydantic model: {e}"
                    )
            return result

        def api_call(model_name: str) -> Any:
            return self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=gen_config,
            )

        output = self._execute_with_retry(
            models_to_try=models_to_try,
            api_call=api_call,
            result_extractor=extract_text,
            max_retries_per_model=config.text_max_retries_per_model,
            overall_max_retries=config.text_overall_max_retries,
            operation_name="Text generation",
        )
        return self._finalize(output)

    def generate_image(
        self,
        input_params: InputParams,
        image_params: Optional[ImageParams] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate an image using the Gemini API."""
        if image_params is None:
            image_params = ImageParams()

        model = input_params.model or config.default_image_model
        models_to_try = self._prioritize_models(model, config.image_models)
        
        prompt_text = input_params.prompt or "A generic placeholder image"
        sys_text = input_params.system_instruction or ""
        aspect_ratio = image_params.output_image_aspect_ratio or config.default_output_image_aspect_ratio
        
        # Combine system instruction, user prompt, and aspect ratio guidance
        full_prompt_parts = []
        if sys_text:
            full_prompt_parts.append(sys_text)
        full_prompt_parts.append(prompt_text)
        full_prompt_parts.append(f"Requested Aspect Ratio: {aspect_ratio}")
        
        full_prompt = "\n\n".join(full_prompt_parts)

        def api_call(model_name: str) -> Any:
            if "gemini" in model_name.lower():
                input_list = []
                max_dim = input_params.processed_image_size or config.default_image_max_dimension
                if input_params.media:
                    for media_url in input_params.media:
                        try:
                            media_bytes, content_type = self._download_media(media_url)
                            if content_type and content_type.startswith("image"):
                                media_bytes = self._resize_image(media_bytes, max_dim)
                            input_list.append({
                                "type": "image",
                                "mime_type": content_type or "image/png",
                                "data": base64.b64encode(media_bytes).decode("utf-8")
                            })
                        except Exception as exc:
                            self.logger.warning(f"Failed to process media '{media_url}': {exc}")
                
                if full_prompt:
                    input_list.append({"type": "text", "text": full_prompt})
                
                return self.client.interactions.create(
                    model=model_name,
                    input=input_list
                )
            else:
                image_config = types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio=aspect_ratio,
                )
                return self.image_client.models.generate_images(
                    model=model_name,
                    prompt=full_prompt,
                    config=image_config,
                )

        def extract_image(response: Any) -> bytes:
            try:
                # 1. Try to extract from interactions API response
                if hasattr(response, "steps"):
                    for step in response.steps:
                        if getattr(step, "type", "") == "model_output":
                            for content_block in step.content:
                                if getattr(content_block, "type", "") == "image":
                                    return base64.b64decode(content_block.data)
            except Exception as exc:
                self.logger.warning(f"Failed to extract from interactions API: {exc}")

            try:
                # 2. Try to extract from generate_content response (Gemini models fallback)
                if hasattr(response, "candidates") and response.candidates:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            return part.inline_data.data
            except Exception as exc:
                self.logger.warning(f"Failed to extract inline_data: {exc}")

            try:
                # 3. Try to extract from generate_images response (Imagen models)
                if hasattr(response, "generated_images") and response.generated_images:
                    return response.generated_images[0].image.image_bytes
            except Exception as exc:
                self.logger.warning(f"Failed to extract image_bytes: {exc}")
                
            raise ValueError("No image data found in response.")

        output = self._execute_with_retry(
            models_to_try=models_to_try,
            api_call=api_call,
            result_extractor=extract_image,
            max_retries_per_model=config.image_max_retries_per_model,
            overall_max_retries=config.image_overall_max_retries,
            operation_name="Image generation",
        )
        return self._finalize(output)

    # ------------------------------------------------------------------
    # Retry / execution engine
    # ------------------------------------------------------------------

    def _execute_with_retry(
        self,
        models_to_try: List[str],
        api_call: Callable[[str], Any],
        result_extractor: Callable,
        max_retries_per_model: int,
        overall_max_retries: int,
        operation_name: str,
    ) -> OutputResult:
        """Try each model in *models_to_try* up to *max_retries_per_model*
        times, capped by *overall_max_retries* total attempts."""
        output = OutputResult()
        total_attempts = 0

        for model_name in models_to_try:
            if total_attempts >= overall_max_retries:
                break

            for attempt in range(max_retries_per_model):
                if total_attempts >= overall_max_retries:
                    break
                total_attempts += 1

                try:
                    self.logger.debug(
                        f"{operation_name} attempt {total_attempts} with model "
                        f"'{model_name}' (attempt {attempt + 1}/{max_retries_per_model})"
                    )

                    response = api_call(model_name)

                    result = result_extractor(response)

                    output.content = result
                    output.model_used = model_name
                    output.success = True
                    output.retry_attempts = total_attempts
                    output.raw_response = response
                    output.token_usage = self._extract_token_usage(response)
                    return output

                except Exception as exc:
                    error_msg = (
                        f"{operation_name} failed on model '{model_name}' "
                        f"(attempt {attempt + 1}): {exc}"
                    )
                    self.logger.warning(error_msg)
                    output.error_log.append(error_msg)
                    output.error = str(exc)

                    if attempt < max_retries_per_model - 1:
                        time.sleep(config.retry_delay_seconds)

        output.retry_attempts = total_attempts
        output.success = False
        return output

    # ------------------------------------------------------------------
    # Input preparation helpers
    # ------------------------------------------------------------------

    def _prepare_model_inputs(
        self,
        input_params: InputParams,
        text_params: Optional[TextParams] = None,
        image_params: Optional[ImageParams] = None,
        **kwargs,
    ) -> tuple:
        """Build the generation config and contents list from the params."""
        media_parts = self._process_media_to_parts(input_params)
        contents = self._build_contents(input_params.prompt, media_parts)
        gen_config = self._build_config(
            input_params=input_params,
            text_params=text_params,
            image_params=image_params,
            **kwargs,
        )
        return gen_config, contents

    def _process_media_to_parts(self, input_params: InputParams) -> List[Any]:
        """Download / resize media items and convert to genai Part objects."""
        parts: List[Any] = []
        if not input_params.media:
            return parts

        max_dim = input_params.processed_image_size or config.default_image_max_dimension
        media_res = input_params.media_resolution or config.default_media_resolution

        for media_url in input_params.media:
            try:
                media_bytes, content_type = self._download_media(media_url)

                if content_type and content_type.startswith("image"):
                    media_bytes = self._resize_image(media_bytes, max_dim)

                part = types.Part.from_bytes(
                    data=media_bytes,
                    mime_type=content_type or "image/jpeg",
                )
                parts.append(part)
            except Exception as exc:
                self.logger.warning(f"Failed to process media '{media_url}': {exc}")

        return parts

    def _build_contents(
        self, prompt: Optional[str], media_parts: List[Any]
    ) -> List[Any]:
        """Combine text prompt and media parts into a contents list."""
        contents: List[Any] = []
        if media_parts:
            contents.extend(media_parts)
        if prompt:
            contents.append(prompt)
        return contents if contents else [""]

    def _build_config(
        self,
        input_params: InputParams,
        text_params: Optional[TextParams] = None,
        image_params: Optional[ImageParams] = None,
        **kwargs,
    ) -> types.GenerateContentConfig:
        """Construct a ``GenerateContentConfig`` from the parameter objects."""
        config_kwargs: Dict[str, Any] = {}

        # System instruction
        system_instruction = (
            input_params.system_instruction or config.default_system_instruction
        )
        config_kwargs["system_instruction"] = system_instruction

        # Text-specific settings
        if text_params:
            if text_params.response_schema:
                config_kwargs["response_schema"] = text_params.response_schema
                config_kwargs["response_mime_type"] = (
                    text_params.response_mime_type or config.default_response_mime_type
                )
            if text_params.tools:
                config_kwargs["tools"] = text_params.tools
            if text_params.tool_config:
                config_kwargs["tool_config"] = text_params.tool_config

        # Image-specific settings
        if image_params:
            config_kwargs["response_modalities"] = ["TEXT", "IMAGE"]
            aspect_ratio = (
                image_params.output_image_aspect_ratio
                or config.default_output_image_aspect_ratio
            )
            config_kwargs["image_generation_config"] = types.ImageGenerationConfig(
                aspect_ratio=aspect_ratio,
            )

        # Merge any extra kwargs
        config_kwargs.update(kwargs)

        return types.GenerateContentConfig(**config_kwargs)

    # ------------------------------------------------------------------
    # Media helpers
    # ------------------------------------------------------------------

    def _download_media(self, url: str) -> tuple:
        """Download media from *url* and return ``(bytes, content_type)``."""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "image/jpeg")
        return response.content, content_type

    def _resize_image(self, image_bytes: bytes, max_dimension: int) -> bytes:
        """Resize an image so its longest side is at most *max_dimension* px."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size

            if max(width, height) <= max_dimension:
                return image_bytes

            if width >= height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))

            img = img.resize((new_width, new_height), Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buf = io.BytesIO()
            img_format = img.format or "JPEG"
            img.save(buf, format=img_format)
            return buf.getvalue()
        except Exception as exc:
            self.logger.warning(f"Image resize failed, using original: {exc}")
            return image_bytes

    def _extract_image_from_response(self, response: Any) -> Optional[bytes]:
        """Pull the first image blob out of a Gemini response."""
        try:
            if not response.candidates:
                return None
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    return part.inline_data.data
        except Exception as exc:
            self.logger.warning(f"Error extracting image from response: {exc}")
        return None

    # ------------------------------------------------------------------
    # Token / model helpers
    # ------------------------------------------------------------------

    def _extract_token_usage(self, response: Any) -> Dict[str, int]:
        """Extract token counts from the response usage metadata."""
        usage: Dict[str, int] = {"input": 0, "output": 0}
        try:
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                meta = response.usage_metadata
                usage["input"] = getattr(meta, "prompt_token_count", 0) or 0
                usage["output"] = getattr(meta, "candidates_token_count", 0) or 0
        except Exception:
            pass
        return usage

    def _prioritize_models(
        self, preferred: str, fallback_list: List[str]
    ) -> List[str]:
        """Return a deduplicated list with *preferred* first, then the rest
        of *fallback_list* in order."""
        models = [preferred]
        for m in fallback_list:
            if m not in models:
                models.append(m)
        return models

    # ------------------------------------------------------------------
    # Finalisation
    # ------------------------------------------------------------------

    def _finalize(self, output: OutputResult) -> Dict[str, Any]:
        """Convert the internal ``OutputResult`` to a plain dict for callers."""
        return {
            "content": output.content,
            "model_used": output.model_used,
            "token_usage": output.token_usage,
            "success": output.success,
            "error": output.error,
            "retry_attempts": output.retry_attempts,
            "error_log": output.error_log,
        }
