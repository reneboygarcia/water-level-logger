import RPi.GPIO as GPIO
import time

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


def distance(temperature=20):
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # Save StartTime
    start_time = time.time()
    stop_time = time.time()

    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()

    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()

    # Time difference between start and arrival
    time_elapsed = stop_time - start_time
    # Multiply with the sonic speed (343m/s) and divide by 2 (for round trip)
    # Formula to consider temperature v=331.3+0.606×T
    sound_speed = 331.30 + 0.606 * temperature
    distance = (time_elapsed * sound_speed) / 2

    return distance


if __name__ == "__main__":
    try:
        while True:
            dist = distance()
            print(f"Measured Distance: {dist:.4f}m")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
    finally:
        GPIO.cleanup()
