def check_if_reset(data):
    # QRコードをスキャンして内容を取得

    if not data:
        print("QRコードを読み取れませんでした。")
        return

    # 判定
    if data.strip().lower() == "reset":
        print(" テキストの内容は 'reset' です。")
        # ここにリセット処理を追加してもOK（例：reset_system() など）
        return True
    else:
        print(" テキストの内容は 'reset' ではありません。")
        print(f"（内容: {data}）")
        return False
    
def check_if_close(data):
    # QRコードをスキャンして内容を取得

    if not data:
        print("QRコードを読み取れませんでした。")
        return
    # 判定
    if data.strip().lower() == "close":
        print(" テキストの内容は 'close' です。")
        # ここにリセット処理を追加してもOK（例：reset_system() など）
        return True
    else:
        print(" テキストの内容は 'close' ではありません。")
        print(f"（内容: {data}）")
        return False


