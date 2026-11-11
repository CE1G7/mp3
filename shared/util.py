import requests, hashlib, sys, time, io, argparse, uvicorn, psutil, datetime, os, collections
from PIL import Image, ImageFilter, ImageEnhance

PART_HEIGHT = 64 # pixel rows per part
ROUNDS = 3 # processing rounds


def process_part(part: Image.Image):
    for i in range(ROUNDS):
        part = part.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        enhancer = ImageEnhance.Sharpness(part)
        part = enhancer.enhance(2.0)
    return part.filter(ImageFilter.FIND_EDGES)


def process_image(image: Image.Image):
    output = Image.new("RGB", image.size)
    for y in range(0, image.height, PART_HEIGHT):
        box = (0, y, image.width, min(y + PART_HEIGHT, image.height))
        output.paste(process_part(image.crop(box)), (0, y))
    return output


def process_image_offload(image_bytes: io.BytesIO, offload_url: str, headers: dict, offload_split: float = 0.5):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    cut_y = min(round(image.height/PART_HEIGHT*offload_split)*PART_HEIGHT, image.height)
    box = (0, 0, image.width, cut_y)
    image_cut_local = image.crop(box)
    box = (0, cut_y, image.width, image.height)
    image_cut_cloud = image.crop(box)
    try:
        headers["image_width"] = str(image.width)
        headers["image_height"] = str(image.height - cut_y)
        r = requests.post(offload_url, data=image_cut_cloud.tobytes(), headers=headers)
        r.raise_for_status()
        processed_image_cloud = Image.frombytes("RGB", (image.width, image.height - cut_y), r.content)
        processed_image_local = process_image(image_cut_local)
        image_merged = Image.new("RGB", image.size)
        image_merged.paste(processed_image_local, (0, 0))
        image_merged.paste(processed_image_cloud, (0, cut_y))
        image_hash = hashlib.sha256(image_merged.tobytes()).hexdigest()
        return image_hash
    except Exception as e:
        print(f"Request failed: {e}")
    return 0


def process_image_local(image_bytes: io.BytesIO):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_hash = hashlib.sha256(process_image(image).tobytes()).hexdigest()
    return image_hash


def log(monitor_ip: str, node: str, client_ip: str, headers: dict, size_kb: float, cpu_load: float, offloaded: bool, processing_time_ms: float, http_status: int):
    log = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "node": node,
    "cpu_load": round(cpu_load, 2),
    "client_ip": client_ip,
    "client_id": headers["id"],
    "size_kb": round(size_kb, 2),
    "offloaded": offloaded,
    "processing_time_ms": round(processing_time_ms, 2),
    "http_status": http_status
    }
    print(f"Request Log: {log}")
    try:
        r = requests.post(f"http://{monitor_ip}:9000/log", json = log, timeout = 0.5)
    except Exception as e:
        print(f"Logging unavailable: {e}")

RATE_LIMIT = os.environ.get("RATE_LIMIT", "off") == "on"
RATE_MAX = int(os.environ.get("RATE_MAX", "5"))
RATE_WINDOW_S = float(os.environ.get("RATE_WINDOW_S", "10"))
_hits = collections.defaultdict(collections.deque)


def allowed(key: str):
    if not RATE_LIMIT:
        return True
    now = time.time()
    dq = _hits[key]
    dq.append(now)
    while dq and now - dq[0] > RATE_WINDOW_S:
        dq.popleft()
    return len(dq) <= RATE_MAX
