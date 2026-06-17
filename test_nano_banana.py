import os
from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, ImageParams

def test_nano_banana():
    # Force vertex AI via environment
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    wrapper = GeminiWrapper()
    print("Testing Nano Banana (gemini-3-pro-image) on Vertex AI...")
    
    input_params = InputParams(
        prompt="A highly detailed and photorealistic image of a Nano Banana wearing sunglasses on a beach.",
        model="gemini-3-pro-image"
    )
    image_params = ImageParams(
        output_image_aspect_ratio="1:1"
    )
    
    result = wrapper.generate_image(input_params, image_params)
    
    if result["success"]:
        print("Success! Image generated.")
        print(f"Model used: {result['model_used']}")
        
        # Save to disk
        output_path = "nano_banana_test.png"
        with open(output_path, "wb") as f:
            f.write(result["content"])
        print(f"Image saved to {output_path}")
    else:
        print("Failed to generate image.")
        print(f"Error: {result.get('error')}")
        print(f"Error logs: {result.get('error_log')}")

if __name__ == "__main__":
    test_nano_banana()
