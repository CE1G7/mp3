import requests, hashlib, sys, time, io, argparse, uvicorn, psutil
from fastapi import FastAPI, Request, Response, HTTPException
from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.util import process_image_local, process_image_offload, log

parser = argparse.ArgumentParser()
parser.add_argument("--cloud_ip", type=str, default="127.0.0.1")
parser.add_argument("--log_ip", type=str, default="127.0.0.1")
parser.add_argument("--id", type=str, default="fog_a")
args = parser.parse_args()

headers = {
    "id": args.id
}


app = FastAPI()


@app.post("/image")
async def image(request: Request):
    start_time = time.perf_counter()
    image_bytes = await request.body()
    size_kb = len(image_bytes) / 1024
    cpu_load = round(psutil.cpu_percent()/100, 2)
    if cpu_load > 0.1 or size_kb > 256:
        image_hash = process_image_offload(image_bytes = image_bytes, offload_url = f"http://{args.cloud_ip}:8080/image", headers = headers, offload_split = 0.5)
    else: 
        image_hash = process_image_local(image_bytes)
    processing_time_ms = time.perf_counter() - start_time
    print(f"Pic hash processed: {image_hash}")
    log(monitor_ip = args.log_ip, node = args.id, headers = request.headers, size_kb = size_kb, cpu_load = cpu_load, offloaded = False, processing_time_ms = processing_time_ms, http_status = 0)
    if image_hash:
        return Response(content=image_hash, status_code=200)
    else:
        return Response(status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)