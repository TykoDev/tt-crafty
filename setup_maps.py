import zipfile
import os
import shutil

def setup_maps():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    maps_dir = os.path.join(base_dir, "maps")

    if not os.path.exists(maps_dir):
        os.makedirs(maps_dir)
        print(f"Created maps directory: {maps_dir}")

    # Process Melee.zip
    melee_zip = os.path.join(base_dir, "Melee.zip")
    if os.path.exists(melee_zip):
        print(f"Extracting {melee_zip}...")
        try:
            with zipfile.ZipFile(melee_zip, 'r') as zip_ref:
                # Try standard Blizzard password if needed
                try:
                    zip_ref.extractall(maps_dir)
                    print("Extracted Melee.zip")
                except RuntimeError as e:
                    if 'password required' in str(e):
                        print("Password required. Trying 'iagreetotheeula'...")
                        zip_ref.setpassword(b"iagreetotheeula")
                        zip_ref.extractall(maps_dir)
                        print("Extracted Melee.zip with password.")
                    else:
                        raise e
        except Exception as e:
            print(f"Failed to extract {melee_zip}: {e}")
    else:
        print(f"Warning: {melee_zip} not found.")

    # Process 2025_aug_ladder.zip
    ladder_zip = os.path.join(base_dir, "2025_aug_ladder.zip")
    if os.path.exists(ladder_zip):
        print(f"Extracting {ladder_zip}...")
        ladder_dir = os.path.join(maps_dir, "2025_aug_ladder")
        if not os.path.exists(ladder_dir):
            os.makedirs(ladder_dir)

        try:
            with zipfile.ZipFile(ladder_zip, 'r') as zip_ref:
                zip_ref.extractall(ladder_dir)
            print("Extracted 2025_aug_ladder.zip")
        except Exception as e:
             print(f"Failed to extract {ladder_zip}: {e}")

    else:
        print(f"Warning: {ladder_zip} not found.")

    print("\nMap setup complete.")
    print(f"Maps are located in: {maps_dir}")

if __name__ == "__main__":
    setup_maps()
