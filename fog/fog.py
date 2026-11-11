import requests, hashlib, sys, time, io, argparse, uvicorn, psutil
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.util import process_image_local, process_image_offload, log, allowed

parser = argparse.ArgumentParser()
parser.add_argument("--cloud_ip", type=str, default="127.0.0.1")
parser.add_argument("--log_ip", type=str, default="127.0.0.1")
parser.add_argument("--id", type=str, default="fog_a")
args = parser.parse_args()

headers = {
    "id": args.id
}


app = FastAPI()


async def get_body(request: Request) -> bytes:
    return await request.body()


@app.post("/image")
def image(request: Request, image_bytes: bytes = Depends(get_body)):
    start_time = time.perf_counter()
    size_kb = len(image_bytes) / 1024
    cpu_load = round(psutil.cpu_percent()/100, 2)
    client_ip = request.client.host
    if not allowed(client_ip):
        log(args.log_ip, args.id, client_ip, request.headers, size_kb, cpu_load, False, 0.0, 429)
        return Response(status_code=429)
    offloaded = False
    if cpu_load > 0.5 or size_kb > 256:
        offloaded = True
        image_hash = process_image_offload(image_bytes = image_bytes, offload_url = f"http://{args.cloud_ip}:8080/image", headers = headers, offload_split = 0.5)
    else: 
        image_hash = process_image_local(image_bytes)
    processing_time_ms = (time.perf_counter() - start_time) * 1000
    print(f"Pic hash processed: {image_hash}")
    if image_hash:
        log(monitor_ip = args.log_ip, node = args.id, client_ip = client_ip, headers = request.headers, size_kb = size_kb, cpu_load = cpu_load, offloaded = offloaded, processing_time_ms = processing_time_ms, http_status = 200)
        return Response(content=image_hash, status_code=200)
    else:
        log(monitor_ip = args.log_ip, node = args.id, client_ip = client_ip, headers = request.headers, size_kb = size_kb, cpu_load = cpu_load, offloaded = offloaded, processing_time_ms = processing_time_ms, http_status = 500)
        return Response(status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)