import binascii
import nfc
import hashlib

class MyCardReader(object):
    """
    ICカードリーダークラス
    - on_connect: カードがタッチされたときに呼び出されるメソッド。カードのIDを保存する。
    - read_id: ICカードを読み取るメソッド。カードがタッチされるのを待ち、IDを返す。エラーが発生した場合はNoneを返す。
    """
    def __init__(self):
        self.id = None  # 読み取ったIDを一時的に保存する変数

    def on_connect(self, tag):
        # タッチされた瞬間に、この中でIDを保存してしまう
        self.id = binascii.hexlify(tag.identifier).decode('utf-8')
        print(f"カードがタッチされました: {self.id}")
        return True # 接続終了を伝える

    def read_id(self):
        self.id = None
        print("--- Please Touch")
        # with構文を使うと、何があっても確実にUSBデバイスを解放してくれます
        try:
            with nfc.ContactlessFrontend('usb') as clf:
                clf.connect(rdwr={
                    'targets': ['106A', '106B', '212F'], 
                    'on-connect': self.on_connect
                })
            hash_id = hashlib.sha256(self.id.encode()).hexdigest()
            return hash_id
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None