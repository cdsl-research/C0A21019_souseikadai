#加速度センサーデータを受け取る側
import socket
import network
import time
import re
import ure
import _thread
import time
import utime
from machine import Pin, SoftI2C, I2C, PWM


#I2C設定
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000) 
address = 0x18
#address = 0x1A

#LIS3DH設定
i2c.writeto_mem(address, 0x20, bytes([0x57]))
#i2c.writeto_mem(address, 0x23, bytes([0x08]))

f = open('test.csv', 'w')
f.write("time"+","+"r_z"+","+"s_z"+","+"sabunn"+","+"kennti"+"\n")
f.close()

#計測時間用の変数
sec = 0

# アクセスポイント（AP）モードの設定
ap_ssid = "ESP32-AP"
ap_password = "ap_password"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ap_ssid, password=ap_password)
print(ap)

# APのIPアドレスを取得
ap_ip = ap.ifconfig()[0]

# 受信用のソケットの設定
s = socket.socket()
port = 80
s.bind((ap_ip, port))
s.listen(1)

print("APモード: 接続待機中", ap_ip)

while True:
    client, addr = s.accept()
    print("Connected by", addr)

    while True:
        try:            
            # 時間
            time_data = utime.ticks_ms() / 1000
            time.sleep(0.1)
            data = client.recvfrom(1024)
            keisann = str(data[0])
        
            # 少し待機
            utime.sleep_ms(100)
         

            #数値だけを取り出す
            k = keisann.replace("b'", "").replace("'", "")

            # 文字列を浮動小数点数に変換
            if k.startswith("0"):
                parts = k.split(".")
                # 2番目の部分を取得
                second_part = parts[1]
                # 切り捨てる桁数
                truncate_digits = 6
                # 切り捨てた結果を表示
                result = f"{parts[0]}.{second_part[:truncate_digits]}"
            
            elif k.startswith("-"):
                # "-" で分割
                parts = k.split("-")
                # 最後の要素を取得
                last_part = parts[-1]
                # 切り捨てる桁数
                truncate_digits = 6
                # 切り捨てた結果を表示
                result = "-" + last_part[:truncate_digits]
            elif k.startswith("1"):
                parts = k.split(".")
                # 2番目の部分を取得
                second_part = parts[1]
                # 切り捨てる桁数
                truncate_digits = 6
                # 切り捨てた結果を表示
                result = f"{parts[0]}.{second_part[:truncate_digits]}"
            else:
                result = "no"
                
            print(result)                   
    
            sensor_z = float(result)    
        
        
            #データ読み込み
            """
            xl = i2c.read_byte_data(address, 0x28)
            xh = i2c.read_byte_data(address, 0x29)
            yl = i2c.read_byte_data(address, 0x2A)
            yh = i2c.read_byte_data(address, 0x2B)
            zl = i2c.read_byte_data(address, 0x2C)
            zh = i2c.read_byte_data(address, 0x2D)
            """
            xl = i2c.readfrom_mem(address, 0x28, 1)[0]
            xh = i2c.readfrom_mem(address, 0x29, 1)[0]
            yl = i2c.readfrom_mem(address, 0x2A, 1)[0]
            yh = i2c.readfrom_mem(address, 0x2B, 1)[0]
            zl = i2c.readfrom_mem(address, 0x2C, 1)[0]
            zh = i2c.readfrom_mem(address, 0x2D, 1)[0]

            #print(xl, yl, zl)
            #print(xh, yh, zh)
            #"""
            #データ変換
            out_x = (xh << 8 | xl) >> 4
            out_y = (yh << 8 | yl) >> 4
            out_z = (zh << 8 | zl) >> 4
            
            #極性判断
            if out_x >= 2048:
                out_x -= 4096
            
            if out_y >= 2048:
                out_y -= 4096
            
            if out_z >= 2048:
                out_z -= 4096

            
            #物理量（加速度）に変換
            out_x = out_x / 1024
            out_y = out_y / 1024
            out_z = out_z / 1024
            
            
            #計算処理  
            sabunn = out_z - sensor_z
            if sabunn < -0.3087:
                check = 1
            else:
                check = 0
            
            print("send:" + str(sensor_z) + "  " + "receive:" + str(out_z))
            print("sabunn："+ str(sabunn))
            
            #ファイル書き込み
            
            sec+=0.3
            #一時停止
            time.sleep(0.3)
            f = open('test.csv', "a")

            f.write(str(time_data)+","+str(out_z)+","+str(sensor_z)+"," + str(sabunn)+","+ str(check) +"\n")
            f.close()

            #60秒間計測
            if sec > 60.0:           
                client.close()
                break

      
        except Exception as e:
            print("Error:", e)
         
            
# ソケットを閉じる
client.close()
s.close()