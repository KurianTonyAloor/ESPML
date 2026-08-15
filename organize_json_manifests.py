import os
import shutil
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFESTS_DIR = os.path.join(BASE_DIR, "manifests")
os.makedirs(MANIFESTS_DIR, exist_ok=True)

print("=== REORGANIZING JSON MANIFESTS INTO manifests/ ===")

json_files = glob.glob(os.path.join(BASE_DIR, "*.json"))
for json_path in json_files:
    filename = os.path.basename(json_path)
    dst_path = os.path.join(MANIFESTS_DIR, filename)
    shutil.move(json_path, dst_path)
    print(f"  -> Moved: {filename} -> manifests/{filename}")

print("=== MANIFEST REORGANIZATION COMPLETE ===")
