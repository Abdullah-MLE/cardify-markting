import os
import time
import base64
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/gcp-key.json"

client = genai.Client(
    vertexai=True,
    project="project-d3cc105c-93d6-42fa-abc",
    location="global"
)

model_id = "gemini-3.1-flash-lite-image"

config = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    response_modalities=["TEXT", "IMAGE"],
    image_config=types.ImageConfig(
        aspect_ratio="1:1",
        image_size="1K",
        output_mime_type="image/png",
    ),
)

def generate_single_image(index):
    start_time = time.time()
    prompt = f"A futuristic coffee shop with neon sign #{index} with clear Arabic text typography, 8k resolution, cinematic lighting."
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config,
        )
        saved = False
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_data))
                    image.save(f"batch_image_{index}.png")
                    saved = True
        elapsed = time.time() - start_time
        return index, True, elapsed, "Saved successfully" if saved else "No image returned"
    except Exception as e:
        elapsed = time.time() - start_time
        return index, False, elapsed, str(e)

def run_stress_test(total_requests=20):
    print(f"Triggering {total_requests} parallel requests...")
    overall_start = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=total_requests) as executor:
        futures = [executor.submit(generate_single_image, i + 1) for i in range(total_requests)]
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            status_text = "PASS" if res[1] else "FAIL"
            print(f"[{status_text}] Request #{res[0]} finished in {res[2]:.2f}s")

    total_time = time.time() - overall_start
    success_count = sum(1 for r in results if r[1])
    failed_count = total_requests - success_count

    print("\n" + "=" * 40)
    print(f"Total Duration: {total_time:.2f} seconds")
    print(f"Successful: {success_count}/{total_requests}")
    print(f"Failed: {failed_count}/{total_requests}")
    print("=" * 40)

    if failed_count > 0:
        print("\nErrors encountered:")
        for idx, success, _, err in results:
            if not success:
                print(f"Request #{idx}: {err}")

if __name__ == "__main__":
    run_stress_test(20)