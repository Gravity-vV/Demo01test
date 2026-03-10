import urllib.request
import os
import stat
import json

base_url = "https://binaries.soliditylang.org/linux-amd64/"
versions = ["0.4.26", "0.5.17", "0.6.12", "0.7.6", "0.8.20"]

# Ensure ~/.solc-select/artifacts exists
solc_dir = os.path.expanduser("~/.solc-select/artifacts")
os.makedirs(solc_dir, exist_ok=True)

# Fetch list.json to know the exact build files
print("Fetching list.json...")
req = urllib.request.Request(base_url + "list.json", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    list_data = json.loads(response.read().decode())

releases = list_data.get("releases", {})

for v in versions:
    if v not in releases:
        print(f"Version {v} not found in releases!")
        continue
        
    filename = releases[v]
    url = base_url + filename
    
    target_dir = os.path.join(solc_dir, f"solc-{v}")
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, f"solc-{v}")
    
    if os.path.exists(target_path):
        print(f"solc-{v} already exists")
        continue
        
    print(f"Downloading {v} from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response, open(target_path, 'wb') as out_file:
            out_file.write(response.read())
        
        # Make executable
        st = os.stat(target_path)
        os.chmod(target_path, st.st_mode | stat.S_IEXEC)
        print(f"Successfully installed solc {v}")
    except Exception as e:
        print(f"Error downloading {v}: {e}")

