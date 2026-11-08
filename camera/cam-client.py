import requests, random, os, argparse, psutil, sys
from pathlib import Path
from time import sleep

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.util import process_image_local

parser = argparse.ArgumentParser()
parser.add_argument("--dos", action="store_true")
parser.add_argument("--fog_ip", type=str, default="127.0.0.1")
parser.add_argument("--name", type=str, default="cam_x")
args = parser.parse_args()

headers = {
    "Content-Type": "image/jpeg",
    "id": args.name
}

if __name__ == "__main__":
    print(f"Camera client running\n{vars(args)}")
    print(headers)
    while True:
        if not args.dos:
            sleep(10)
        file = "bigcat.jpg"
        if random.randint(0,1) and not args.dos:
            file = "smallcat.jpg"
        print(f"Sending pic of size {os.path.getsize(file) / 1024:.2f} KB")
        with open(file, "rb") as f:
            try:
                pic = f.read()
                r = requests.post(f"http://{args.fog_ip}:8000/image", data=pic, headers=headers)
                if not args.dos:
                    r.raise_for_status()
                    processed_image_hash = r.text
                    print(r.status_code)
                    print(f"Received hash: {processed_image_hash}")
                    check_hash = process_image_local(pic)
                    print(f"Check hash:    {check_hash}")
                    if processed_image_hash == check_hash:
                        print("Hashes MATCHED")
                    else:
                        print("Hashes no machie...")
            except Exception as e:
                print(f"Request failed: {e}")
        print(f"CPU load: {psutil.cpu_percent()/100:.2f}")