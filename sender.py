import time
import utime
import socket
import network
from machine import Pin, SoftI2C, I2C

#SSIDとパスワードの設定
sta_ssid = ""
sta_password = ""

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(sta_ssid, sta_password)

while not sta.isconnected():
    pass

print("ST Mode: Connected to WiFi")

sta_ip = sta.ifconfig()[0]

s = socket.socket()

#IPアドレスの設定
ap_ip = ""  
port = 80

# サーバに接続
s.connect(socket.getaddrinfo(ap_ip, port)[0][-1])

#I2C設定
#i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000) 
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000) 

address = 0x18
#address = 0x1A

#LIS3DH設定
i2c.writeto_mem(address, 0x20, bytes([0x57]))
#i2c.writeto_mem(address, 0x23, bytes([0x08]))

sec = 0

while True:
    try:
        # 時間
        time_data = utime.ticks_ms() / 1000
        
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

        # データ変換
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

        #送るデータの設定
        send_data =  round(out_z, 6)
        s.send(str(send_data))

        sec += 0.3
        # 一時停止
        time.sleep(0.3)

        #60秒間計測
        if sec >= 60.0:        
            print("STモードを終了します")
            s.close()
            break
        
    except Exception  as e:
        print("Error:", e)