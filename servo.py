import bluetooth
from gpiozero import Servo
from time import sleep

# --- 設定 ---
SERVO_PIN = 17 # サーボのGPIOピン
SERVICE_UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# --- サーボのセットアップ ---
servo = Servo(SERVO_PIN)

def move_servo():
    """サーボモーターを動かす関数"""
    try:
        print("サーボモーターを動かします...")
        servo.min()
        sleep(1)
        servo.mid()
        sleep(1)
        servo.max()
        sleep(1)
        servo.mid()
        print("動作完了。")
    except Exception as e:
        print(f"サーボ動作エラー: {e}")

# --- Bluetoothサーバーのセットアップ ---
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]

# サービスをBluetoothで公開（アドバタイズ）
bluetooth.advertise_service(
    server_sock,
    "ServoMotorService",
    service_id=SERVICE_UUID,
    service_classes=[SERVICE_UUID, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

print(f"[*] Bluetoothサーバーがポート {port} で待受中...")

# --- メインループ ---
try:
    move_servo()
    while True:
        client_sock, client_info = server_sock.accept()
        print(f"[*] {client_info[0]} から接続がありました。")

        try:
            data = client_sock.recv(1024).decode('utf-8')
            if data == "MOVE":
                print("MOVEコマンドを受信。")
                move_servo()
                client_sock.send("SERVO_MOVED")
            else:
                client_sock.send("UNKNOWN_COMMAND")

        except bluetooth.btcommon.BluetoothError:
            print("通信エラー (クライアントが切断したようです)")
        finally:
            client_sock.close()
            print(f"[*] {client_info[0]} との接続を終了。")

except KeyboardInterrupt:
    print("\nサーバーを終了します。")
finally:
    server_sock.close()
    servo.detach()