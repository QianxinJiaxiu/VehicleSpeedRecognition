import cv2
import numpy as np
import math


def virtualLoop(img, loop):  # loop[0]旋转中心x [1]旋转中心y [2]旋转角度 [3]长 [4]宽
    '虚拟线圈内的灰度平均值'
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
    h, w = img.shape  # 1920*1080
    theta = loop[2]
    matRotate = cv2.getRotationMatrix2D((loop[0], loop[1]), theta, 1)
    img = cv2.warpAffine(img, matRotate, (w, h))  # 仿射变换
    width = loop[3]
    height = loop[4]
    sum = 0  # 灰度总值
    for i in range(height):
        for j in range(width):
            sum += img[int(loop[1] - height / 2 + j)
                       ][int(loop[0] - width / 2 + i)]
    mean = sum / (width * height)  # 平均灰度值
    return mean


def draw(img, loop):  # loop[0]旋转中心x [1]旋转中心y [2]旋转角度 [3]长 [4]宽
    '画出虚拟线圈'
    x = loop[0]
    y = loop[1]
    theta = loop[2]
    width = loop[3]
    height = loop[4]
    angle = -theta * math.pi / 180.0
    cosA = math.cos(angle)
    sinA = math.sin(angle)
    # (x0,y1),(x1, y1), (x2, y2), (x3, y3)为旋转前的线圈4个端点
    # (x0n,y1n),(x1n, y1n),(x2n, y2n),(x3n, y3n)为旋转后的线圈4个端点
    x1 = x - 0.5 * width
    y1 = y - 0.5 * height

    x0 = x + 0.5 * width
    y0 = y1

    x2 = x1
    y2 = y + 0.5 * height

    x3 = x0
    y3 = y2

    x0n = int((x0 - x) * cosA - (y0 - y) * sinA + x)
    y0n = int((x0 - x) * sinA + (y0 - y) * cosA + y)

    x1n = int((x1 - x) * cosA - (y1 - y) * sinA + x)
    y1n = int((x1 - x) * sinA + (y1 - y) * cosA + y)

    x2n = int((x2 - x) * cosA - (y2 - y) * sinA + x)
    y2n = int((x2 - x) * sinA + (y2 - y) * cosA + y)

    x3n = int((x3 - x) * cosA - (y3 - y) * sinA + x)
    y3n = int((x3 - x) * sinA + (y3 - y) * cosA + y)

    cv2.line(img, (x0n, y0n), (x1n, y1n), (0, 0, 255))
    cv2.line(img, (x1n, y1n), (x2n, y2n), (0, 0, 255))
    cv2.line(img, (x2n, y2n), (x3n, y3n), (0, 0, 255))
    cv2.line(img, (x3n, y3n), (x0n, y0n), (0, 0, 255))

    return img


cap = cv2.VideoCapture('test_video.mp4')
velocity = None
k = 0  # 当前帧
while 1:
    k += 1
    # get a frame
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (450, 800))  # 调整大小，缩小2.4倍，减少工作量
        loop1 = [80, 485, 7, 30, 7]  # 两个线圈的位置、大小
        loop2 = [185, 525, 7, 40, 7]
        if k == 1:
            flag = False
            # loop 0旋转中心x 1旋转中心y 2旋转角度 3长 4宽
            a = virtualLoop(frame, loop1)  # 首帧的loop1平均灰度
            b = virtualLoop(frame, loop2)  # 首帧的loop2平均灰度
        else:
            m = virtualLoop(frame, loop1)  # 之后视频帧的loop1平均灰度
            n = virtualLoop(frame, loop2)  # 之后视频帧的loop2平均灰度

            change1 = abs(m - a)
            change2 = abs(n - b)
            if change1 > 25 and flag == False:  # 可调整阈值
                flag = True
                inframe = k  # 起始帧数
                print("The vehicle has passed the first virtual coil")
                continue  # 防止奇异值
            if change2 > 25 and flag == True:
                flag = False
                outFrame = k  # 终止帧数
                velocity = 10*108 / (outFrame - inframe)
                time = 5.45 / (velocity * 10 / 36)
                print("The vehicle has passed the second virtual coil")
                print("The speed is：", velocity, "Km/h")
                print("Expect the car to hit the line in ", time, "s\n")
        if flag:
            frame = cv2.putText(frame, "The vehicle has passed the first virtual coil", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
        elif velocity:
            frame = cv2.putText(frame, "The vehicle has passed the second virtual coil", (10, 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
            frame = cv2.putText(frame, "The speed is " + str('%.2f' % velocity) + "Km/h", (10, 55),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
            frame = cv2.putText(frame, "Expect the car to hit the line in " + str('%.2f' % time) + "s", (10, 75),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
        frame = draw(frame, loop1)
        frame = draw(frame, loop2)
        # show a frame
        cv2.imshow("capture", frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break  # 等待100ms，如果期间检测到了键盘输入q，则退出
    else:
        break  # ret为0即到视频末尾

# 释放视频对象和窗口
cap.release()
cv2.destroyAllWindows()
