import os
import subprocess

def run_command(command):
    """Helper function to run shell commands and return output."""
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e.output.decode('utf-8')}")
        return None

def enable_i2c():
    """Enable I2C interface if not already enabled."""
    print("Enabling I2C interface...")
    result = run_command("sudo raspi-config nonint do_i2c 0")
    if result is None:
        print("I2C interface enabled.")
    else:
        print("Error enabling I2C:", result)

def check_i2c_device():
    """Check if DS3231 is detected on the I2C bus."""
    print("Checking for DS3231 RTC on I2C bus...")
    result = run_command("sudo i2cdetect -y 1")
    if "68" or "57" in result:
        print("DS3231 detected on I2C bus at address 0x68.")
        return True
    else:
        print("DS3231 not detected. Please check wiring.")
        return False

def load_rtc_driver():
    """Load the RTC driver and bind DS3231 to the I2C bus."""
    print("Loading DS3231 RTC driver...")
    run_command("sudo modprobe rtc-ds1307")
    result = run_command("sudo bash -c 'echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device'")
    if result is None:
        print("RTC driver loaded successfully.")
    else:
        print("Error loading RTC driver:", result)

def read_rtc_time():
    """Read the time from the DS3231 RTC."""
    print("Reading time from DS3231 RTC...")
    result = run_command("sudo hwclock -r")
    if result:
        print("RTC time:", result)
    else:
        print("Failed to read RTC time.")

def sync_system_time_from_rtc():
    """Synchronize the Raspberry Pi's system time from the DS3231 RTC."""
    print("Syncing system time from DS3231 RTC...")
    result = run_command("sudo hwclock -s")
    if result is None:
        print("System time synced from RTC.")
    else:
        print("Error syncing system time:", result)

def sync_rtc_from_system_time():
    """Set the DS3231 RTC time from the Raspberry Pi's system time."""
    print("Syncing DS3231 RTC from system time...")
    result = run_command("sudo hwclock -w")
    if result is None:
        print("RTC time synced from system.")
    else:
        print("Error syncing RTC time:", result)

def disable_fake_hwclock():
    """Disable the fake-hwclock package to prevent it from interfering."""
    print("Disabling fake-hwclock...")
    run_command("sudo apt-get remove -y fake-hwclock")
    run_command("sudo update-rc.d -f fake-hwclock remove")
    print("fake-hwclock disabled.")

def configure_rtc_auto_sync_on_boot():
    """Configure the system to automatically sync from DS3231 RTC on boot."""
    print("Configuring RTC to auto-sync on boot...")
    boot_config_file = "/boot/config.txt"
    with open(boot_config_file, "a") as file:
        file.write("\ndtoverlay=i2c-rtc,ds3231\n")
    print("Configuration added to /boot/config.txt.")
    disable_fake_hwclock()

def main():
    print("Starting DS3231 RTC sync process...")

    # Step 1: Enable I2C interface
    enable_i2c()

    # Step 2: Check if DS3231 RTC is detected
    if not check_i2c_device():
        return

    # Step 3: Load the RTC driver
    load_rtc_driver()

    # Step 4: Read the current RTC time
    read_rtc_time()

    # Step 5: Sync system time from RTC
    sync_system_time_from_rtc()

    # Step 6: Sync RTC time from system if necessary
    # Uncomment the line below if you want to sync RTC from system time instead
    sync_rtc_from_system_time()

    # Step 7: Configure RTC auto-sync on boot
    configure_rtc_auto_sync_on_boot()

    # Reboot the system for changes to take effect
    print("Rebooting system to apply changes...")
    #run_command("sudo reboot")

if __name__ == "__main__":
    main()
