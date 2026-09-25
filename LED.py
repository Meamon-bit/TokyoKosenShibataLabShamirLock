import RPi.GPIO as GPIO
from time import sleep

LED_PIN = 17
GPIO_INITIALIZED = False

def init_gpio():
    global GPIO_INITIALIZED
    if not GPIO_INITIALIZED:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO_INITIALIZED = True

def blink_led_gpio(duration, count):
    """LEDを指定回数点滅"""
    # 念のため初期化されていなければ呼ぶ
    if not GPIO_INITIALIZED:
        init_gpio()
    try:
        for _ in range(count):
            GPIO.output(LED_PIN, GPIO.HIGH)
            sleep(duration)
            GPIO.output(LED_PIN, GPIO.LOW)
            sleep(duration)
    finally:
        GPIO.output(LED_PIN, GPIO.LOW)

def cleanup_gpio():
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
