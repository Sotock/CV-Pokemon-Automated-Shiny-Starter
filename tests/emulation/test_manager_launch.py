from instances.instance_manager import launch_instance, remove_instance

instance_id, instance_dir, process = launch_instance("FireRed Starter")

print("Instance ID:", instance_id)
print("Directory created:", instance_dir.exists())
print("Temporary ROM exists:", len(list(instance_dir.glob("*.gba"))) == 1)
print("Temporary save exists:", len(list(instance_dir.glob("*.sav"))) == 1)
print("mGBA Process ID:", process.pid)

input("Press Enter after confirming FireRed loaded your save...")

process.terminate()
process.wait()
remove_instance(instance_dir)

print("Process exited:", process.poll() is not None)
print("Directory removed:", not instance_dir.exists())