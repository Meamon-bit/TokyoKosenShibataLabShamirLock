import asyncio
import sys # エラー表示用

from gomalock.sesame5 import Sesame5

# ラズパイのBluetooth接続が不安定な場合、タイムアウトを少し長めに設定
MAC_ADDRESS = ""
SECRET_KEY = ""

TIMEOUT_SEC = 20 


async def openSESAME():
    print("解錠コマンドを送信します...")
    try:
        async with asyncio.timeout(TIMEOUT_SEC):
            async with Sesame5(MAC_ADDRESS, SECRET_KEY) as sesame5:
                # 状態確認（オプション）
                if sesame5.mech_status.is_in_unlock_range:
                     print("確認: 既に解錠されています。")
                     return

                await sesame5.unlock("gomalock")
                print(">> 解錠コマンド送信完了")
                
    except asyncio.TimeoutError:
        print("エラー: 解錠処理がタイムアウトしました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

async def closeSESAME():
    print("施錠プロセスを開始します...")
    
    retry_count = 0
    while retry_count < 3: # 無限ループではなく3回までリトライにする
        try:
            async with asyncio.timeout(TIMEOUT_SEC):
                print(f"接続試行中... ({retry_count+1}/3)")
                async with Sesame5(MAC_ADDRESS, SECRET_KEY) as sesame5:
                    
                    print("接続成功。現在の状態を確認中...")
                    # 1. 既に施錠されているか確認
                    if sesame5.mech_status.is_in_lock_range:
                        print("確認: 既に施錠されています。")
                        return # 成功終了

                    # 2. 施錠コマンド送信
                    print(f"現在の電圧: {sesame5.mech_status.battery_voltage}V")
                    print("施錠コマンドを送信します...")
                    await sesame5.lock("gomalock")

                    # 3. 実際に鍵が回るのを待機して確認
                    # ステータス更新が来るまで最大10秒待つ (1秒 x 10回)
                    print("施錠完了を待機しています...")
                    for i in range(10): 
                        await asyncio.sleep(1)
                        # ステータスはバックグラウンドで自動更新されます
                        if sesame5.mech_status.is_in_lock_range:
                            print(">> 施錠成功を確認しました！")
                            return # 成功終了
                        print(f"待機中... {i+1}秒")

                    # ループを抜けた＝10秒待っても施錠通知が来なかった
                    print("警告: 施錠コマンドは送りましたが、完了通知が届きませんでした。")
                    # ここでループを抜けても良いですが、念のため再試行します
        
        except asyncio.TimeoutError:
            print("エラー: 通信がタイムアウトしました。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            import traceback
            traceback.print_exc() # 詳細なエラーを表示

        print("3秒待機して再試行します...")
        await asyncio.sleep(3)
        retry_count += 1

    print("最終エラー: 3回試行しましたが、施錠を完了できませんでした。")

if __name__ == "__main__":
    # ここを closeSESAME() に変更しました
    asyncio.run(closeSESAME())