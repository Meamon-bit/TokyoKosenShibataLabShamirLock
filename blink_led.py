import RPi.GPIO as GPIO
from time import sleep

LED_PIN = 17
GPIO_INITIALIZED = False

def init_gpio():
    """
    GPIOを初期化する関数
    - BCMモードでGPIOを設定
    - LED_PINを出力モードに設定し、初期状態はLOWにする
    - 初期化が完了したらGPIO_INITIALIZEDをTrueにする
    """
    global GPIO_INITIALIZED
    if not GPIO_INITIALIZED:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO_INITIALIZED = True

def blink_led_gpio(duration, count):
    """
    LEDを点滅させる関数
    - duration: LEDが点灯している時間（秒）
    - count: 点滅の回数
    - GPIOが初期化されていない場合は初期化する
    - 指定された回数だけLEDを点滅させる
    - 点滅が完了したらLEDを消灯する
    """
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
    """
    GPIOをクリーンアップする関数
    - GPIOをクリーンアップして、使用したピンをリセットする
    - GPIO_INITIALIZEDをFalseにする
    """
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
