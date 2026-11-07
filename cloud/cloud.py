import argparse, uvicorn, time, psutil, io, sys
from fastapi import FastAPI, Request, Response
from PIL import Image
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.util import process_image, log

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="127.0.0.1")
parser.add_argument("--log_ip", type=str, default="127.0.0.1")
parser.add_argument("--id", type=str, default="cloud_a")
args = parser.parse_args()

app = FastAPI()


@app.post("/image")
async def image(request: Request):
    start_time = time.perf_counter()
    headers = request.headers
    image_bytes = await request.body()
    size_kb = len(image_bytes) / 1024
    print(f"Received {size_kb} KB")
    cpu_load = round(psutil.cpu_percent()/100, 2)
    image = Image.frombytes("RGB", (int(headers["image_width"]), int(headers["image_height"])), image_bytes)
    processed_image = process_image(image)
    processing_time_ms = time.perf_counter() - start_time
    log(monitor_ip = args.log_ip, node = args.id, headers = request.headers, size_kb = size_kb, cpu_load = cpu_load, offloaded = False, processing_time_ms = processing_time_ms, http_status = 0)
    return Response(processed_image.tobytes())

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)