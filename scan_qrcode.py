import cv2
from pyzbar.pyzbar import decode
import time


def scan_qrcode():
    cap = cv2.VideoCapture(0)
    start = time.time()
    timeout=300#とりま5分
    while True:
        if time.time() - start > timeout:
            print("タイムアウトしました")
            return "Error"
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objs = decode(frame)
        for obj in decoded_objs:
            data = obj.data.decode("utf-8")
            #print("QRコード:", data)
            if data:
                cap.release()
                return data
