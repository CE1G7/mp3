import requests, random, os, argparse, psutil
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("--ddos", action="store_true")
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
        if not args.ddos:
            sleep(10)
        file = "bigcat.jpg"
        # if random.randint(0,1):
        #     file = "smallcat.jpg"
        print(f"Sending pic of size {os.path.getsize(file) / 1024:.2f} KB")
        with open(file, "rb") as f:
            try:
                r = requests.post(f"http://{args.fog_ip}:8000/image", data=f.read(), headers=headers)
                if not args.ddos:
                    r.raise_for_status()
                print(r.status_code, r.text)
            except Exception as e:
                print(f"Request failed: {e}")
        print(f"CPU load: {psutil.cpu_percent()/100:.2f}")