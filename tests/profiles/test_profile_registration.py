from pathlib import Path
from profiles.profile_manager import import_save, register_profile

PROJECT_DIR = Path(__file__).resolve().parents[2]

rom_path = PROJECT_DIR / "roms" / "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba"

save_path = rom_path.with_suffix(".sav")
profile_name = "FireRed Starter"

imported_save = import_save(save_path, profile_name)
metadata_path = register_profile(profile_name, rom_path)

print("Imported save exists:", imported_save.is_file())
print("Profile metadata exists:", metadata_path.is_file())
print("Original save exists:", save_path.is_file())