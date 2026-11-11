import requests, random, os, argparse, psutil, sys
from pathlib import Path
from time import sleep

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.util import process_image_local

parser = argparse.ArgumentParser()
parser.add_argument("--dos", action="store_true")
parser.add_argument("--id_rotate", action="store_true")
parser.add_argument("--fog_ip", type=str, default="127.0.0.1")
parser.add_argument("--id", type=str, default="cam_x")
args = parser.parse_args()

headers = {
    "Content-Type": "image/jpeg",
    "id": args.id
}

if __name__ == "__main__":
    print(f"Camera client running\n{vars(args)}")
    print(headers)
    with open("bigcat.jpg", "rb") as f:
        bigcat = f.read()
    with open("smallcat.jpg", "rb") as f:
        smallcat = f.read()
    n = 0
    while True:
        pic = bigcat
        if not args.dos:
            sleep(10)
            if random.randint(0,1):
                pic = smallcat
        print(f"Sending pic of size {len(pic) / 1024:.2f} KB")
        if args.id_rotate:
            headers["id"] = f"{args.id}_{n}"
            n += 1
        if not args.dos:
            try:
                r = requests.post(f"http://{args.fog_ip}:8000/image", data=pic, headers=headers)
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
        else:
            try:
                r = requests.post(f"http://{args.fog_ip}:8000/image", data=pic, headers=headers, timeout=0.2)
            except:# requests.exceptions.Timeout:
                pass

        print(f"CPU load: {psutil.cpu_percent()/100:.2f}")
