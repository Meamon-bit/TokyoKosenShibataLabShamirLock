from pyzbar.pyzbar import decode
import time
import remove
import blink_led # LED光らせる用(17ピンから信号送るよ)
import Shamir
import output_file
import asyncio
import openSESAME
import write_log
import database
import scan_ic
from datetime import datetime, timedelta # timedeltaを追加
import RPi.GPIO as GPIO

port = 1
LED_ERROR_DURATION = 0.1
LED_ERROR_COUNT = 20
LED_SUCCESS_DURATION = 1
LED_SUCCESS_COUNT = 1

# グローバル変数の初期化
last_lock_time = datetime.now()

def Share_restore(threshold, ramp, secret_length, shares, path):
    """
    シェアを復元してファイルに保存する関数
    """
    share_info = Shamir.Shamir(0, threshold=threshold)
    restore_list = [(item[0], item[1]) for item in shares]
    data = share_info.restore_number(shares=restore_list, ramp=ramp, secret_length=secret_length)
    output = output_file.OutputFile(number=data)
    output.export_file(file_path=path)

def read_id_with_timeout(reader, timeout_sec):
    """
    MyCardReaderのread_idを別スレッドで実行し、指定秒数でタイムアウトさせる補助関数
    """
    async def _async_wait():
        return await asyncio.wait_for(asyncio.to_thread(reader.read_id), timeout=timeout_sec)
    
    try:
        return asyncio.run(_async_wait())
    except asyncio.TimeoutError:
        return "__TIMEOUT__"


def deshamir():
    """
    シェアの復元を行う関数
    """
    global last_lock_time
    file_path = "data_restored.txt"
    shares_out = []
    scanned_users = []

    # 初期値として、あり得ない数値（例: -1）を設定しておく
    last_minute = -1

    threshold = None
    ramp = None
    secret_length = None
    collected_x_values = set()


    print("秘密の復元を開始します...")

    while True:
        now = datetime.now()

        # 前回施錠（または起動）から15分以上経過したか判定
        if now >= last_lock_time + timedelta(minutes=15):
            print(f"前回から15分以上経過したため（現在 {now.strftime('%H:%M:%S')}）、SESAMEを施錠します")
            try:
                GPIO.output(17, GPIO.HIGH)
                asyncio.run(openSESAME.closeSESAME())
                write_log.write_log("DOOR", key_id=-1, action="Lock automatically")
                GPIO.output(17, GPIO.LOW)
            except Exception as e:
                print(f"SESAMEの施錠に失敗しました: {e}")

            # 最後に施錠した時間を「今」に更新する
            last_lock_time = now

        if threshold:
            print(f"\n--- シェアを {len(shares_out)} / {threshold} 個集めました ---")
            if len(shares_out) >= threshold:
                print("必要な数のシェアが集まりました。復元を開始します。")
                break
            print("次のQRコードをスキャンしてください:")
        else:
            print("\n--- 1枚目のQRコードをスキャンしてください: ---")

        cr = scan_ic.MyCardReader()
        
        # --- 150秒のタイムアウト待ち ---
        ic_id = read_id_with_timeout(cr, timeout_sec=150.0)
        
        # --- 【修正】150秒タイムアウト時のリセット処理 ---
        if ic_id == "__TIMEOUT__":
            print(f"\n[TIMEOUT] 150秒間スキャンがなかったため、集めたシェアを削除してリセットします。")
            
            # 内部状態をすべて初期化して、1枚目の待ち受けに戻す
            shares_out.clear()
            scanned_users.clear()
            collected_x_values.clear()
            threshold = None
            ramp = None
            secret_length = None
            continue

        if ic_id is None:
            print("スキャンがキャンセルまたは失敗しました。")
            write_log.write_log("ERROR", action="Scan was canceled")
            blink_led.blink_led_gpio(LED_ERROR_DURATION, LED_ERROR_COUNT)

            if len(shares_out) < (threshold or 1):
                print("シェアが足りないため、処理を中断します。")
                write_log.write_log("ERROR", action="Not enough shares collected, aborting process")
                return False
            break

        if ic_id == "45d0ba5edffd761e97742069dc177342acd07c41c53677fb3e9edebeb47dd85b":
            print("クローズ用ICがスキャンされました。処理をリセットします。")
            blink_led.blink_led_gpio(LED_SUCCESS_DURATION, LED_SUCCESS_COUNT)
            write_log.write_log("DOOR", key_id="-", action="Closed by Close-IC")
            asyncio.run(openSESAME.closeSESAME())
            return True
            
        blink_led.blink_led_gpio(LED_SUCCESS_DURATION, LED_SUCCESS_COUNT)
        try:
            result = database.read_database(ic_id, shares_out)
            
            if result is None:
                print("データベースの読み込みに失敗しました。もう一度スキャンしてください。")
                write_log.write_log("ERROR", action=f"Database read failed for IC ID {ic_id}")
                continue
                
            t, r, s, shid, key_id, user_name = result
            
            if shid not in scanned_users:
                scanned_users.append(shid)
                print(f"shareid:{shid}が追加されました")
                write_log.write_log("USER", key_id=key_id, ic_id=ic_id, user_name=user_name)
        except (IndexError, ValueError, TypeError) as e:
            print(f"QRデータ形式エラー: {e}。もう一度試してください。")
            write_log.write_log("ERROR", action=f"QR data format error for IC ID {ic_id}: {e}")

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
                blink_led.blink_led_gpio(LED_SUCCESS_DURATION, LED_SUCCESS_COUNT)
            else:
                shares_out.pop()
                print(f"シェア {last_share_x} は既にスキャン済みです。")

    if len(shares_out) >= threshold:
        try:
            print(f"復元中... {file_path} に保存します。")
            Share_restore(threshold, ramp, secret_length, shares_out, file_path)
            print(f"復元に成功しました！ {file_path} を確認してください。")
            if database.check_key(key_id) == True:
                write_log.write_log("DOOR", key_id=key_id, action="Unlock signal sent")
                asyncio.run(openSESAME.openSESAME())
                
                print("解錠しました。60秒間待機します...")
                time.sleep(60)
                
                write_log.write_log("DOOR", key_id=key_id, action="Lock signal sent")
                asyncio.run(openSESAME.closeSESAME())
        except Exception as e:
            print(f"\n復元中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("シェアが足りないため、復元を中止しました。")
        write_log.write_log("ERROR", action="Not enough shares collected, aborting process")
    return True

# --- メインの実行ループ ---
blink_led.init_gpio()
while(1):
    deshamir()
    print("もっかい実行")
blink_led.cleanup_gpio()