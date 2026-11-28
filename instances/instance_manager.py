from pathlib import Path
import shutil
import uuid

PROJECT_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = PROJECT_DIR / "temp"

# Creates an isolated temporary directory with a unique instance identifier.
def create_instance():
    instance_id = uuid.uuid4().hex[:8]
    instance_dir = TEMP_DIR / instance_id
    instance_dir.mkdir(parents=True, exist_ok=False)
    return instance_id, instance_dir

# Removes an instance directory and its temporary files.
def remove_instance(instance_dir):
    shutil.rmtree(instance_dir)