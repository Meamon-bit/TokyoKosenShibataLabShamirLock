from pyzbar.pyzbar import decode
import time
import check
import check_if_reset
import scan_qrcode
import remove
import led #LED光らせる用(17ピンから信号送るよ)
import read
import shamir
import output_file
import time
import asyncio
import openSESAME

addr = "DC:A6:32:82:B6:DB" #相手（受け取り側）のMACアドレス
port = 1
LED_Error_duration = 0.1
LED_Error_count = 20
LED_Success_duration = 1
LED_Success_count = 1
mymac = "AA:BB:CC:DD:EE:FF"
mysecret = "00112233445566778899aabbccddeeff"



def Share_restore(threshold, ramp, secret_length, shares, path):
    share_info = Shamir.Shamir(0, threshold=threshold)
    restore_list = [(item[0], item[1]) for item in shares]
    data = share_info.restore_number(shares=restore_list, ramp=ramp, secret_length=secret_length)
    output = output_file.OutputFile(number=data)
    output.export_file(file_path=path)


def deshamir():
    file_path = "data_restored.txt"
    shares_out = []
    read_qr = read.Read(share_data=shares_out)

    threshold = None
    ramp = None
    secret_length = None
    collected_x_values = set()

    print("秘密の復元を開始します...")

    while True:
        if threshold:
            print(f"\n--- シェアを {len(shares_out)} / {threshold} 個集めました ---")
            if len(shares_out) >= threshold:
                print("必要な数のシェアが集まりました。復元を開始します。")
                break
            print("次のQRコードをスキャンしてください:")
        else:
            print("\n--- 1枚目のQRコードをスキャンしてください: ---")

        qr_data = scan_qrcode.scan_qrcode()
        if qr_data=="Error":return True
        if check_if_reset.check_if_reset(qr_data):
            return True
        elif check_if_reset.check_if_close(qr_data):
            asyncio.rn(openSESAME.closeSESAME())

        if qr_data is None:
            print("スキャンがキャンセルまたは失敗しました。")
            led.blink_led_gpio(LED_Error_duration, LED_Error_count)#ここでLED1チカらせる（Error）

            if len(shares_out) < (threshold or 1):
                print("シェアが足りないため、処理を中断します。")
                return
            break

        try:
            t, r, s, _ = read_qr.Read_QR(qr_data)
        except (IndexError, ValueError, TypeError) as e:
            print(f"QRデータ形式エラー: {e}。もう一度試してください。")
            continue

        if threshold is None:
            threshold = t
            ramp = r
            secret_length = s
            print(f"メタデータを設定: 閾値={threshold}, Ramp={ramp}")

        if shares_out:
            last_share_x = shares_out[-1][0]
            if last_share_x not in collected_x_values:
                collected_x_values.add(last_share_x)
                print(f"シェア {last_share_x} を追加しました。")
                LED.blink_led_gpio(LED_Success_duration, LED_Success_count)#ここでLEDちからせる(Success )
            else:
                shares_out.pop()
                print(f"シェア {last_share_x} は既にスキャン済みです。")

    if len(shares_out) >= threshold:
        try:
            print(f"復元中... {file_path} に保存します。")
            Share_restore(threshold, ramp, secret_length, shares_out, file_path)
            print(f"復元に成功しました！ {file_path} を確認してください。")
            if check.check()==True:
                asyncio.run(openSESAME.openSESAME())
                time.sleep(30)
                asyncio.run(openSESAME.closeSESAME())
        except Exception as e:
            print(f"\n復元中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("シェアが足りないため、復元を中止しました。")
    return True

led.init_gpio()
while(deshamir()):
    print("もっかい実行")

remove.remove_file("data_restored.txt")
led.cleanup_gpio()
