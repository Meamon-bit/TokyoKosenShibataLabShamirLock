def check():
    # 比較対象の文字列
    original_data = "aiueo"  # もともと持っているデータ（文字列）

    # ファイルのパス
    file_path = "data_restored.txt"

    # ファイルの中身を読み込む
    with open(file_path, "r") as f:
        file_data = f.read().strip()  # 前後の空白や改行を除去
    
    
    # 比較
    if original_data == file_data:
        print("データは一致します。")
        return True
    else:
        print("データは一致しません。")
        return False
