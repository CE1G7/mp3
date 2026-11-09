import argparse, uvicorn, time, psutil, io, sys
from fastapi import FastAPI, Request, Response, Depends
from PIL import Image
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.util import process_image, log

parser = argparse.ArgumentParser()
parser.add_argument("--log_ip", type=str, default="127.0.0.1")
parser.add_argument("--id", type=str, default="cloud_a")
args = parser.parse_args()

app = FastAPI()


async def get_body(request: Request) -> bytes:
    return await request.body()


@app.post("/image")
def image(request: Request, image_bytes: bytes = Depends(get_body)):
    start_time = time.perf_counter()
    headers = request.headers
    size_kb = len(image_bytes) / 1024
    print(f"Received {size_kb} KB")
    image = Image.frombytes("RGB", (int(headers["image_width"]), int(headers["image_height"])), image_bytes)
    cpu_load = round(psutil.cpu_percent()/100, 2)
    processed_image = process_image(image)
    processing_time_ms = (time.perf_counter() - start_time) * 1000
    log(monitor_ip = args.log_ip, node = args.id, client_ip = request.client.host, headers = request.headers, size_kb = size_kb, cpu_load = cpu_load, offloaded = False, processing_time_ms = processing_time_ms, http_status = 200)
    return Response(processed_image.tobytes())

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)