import cv2
import numpy as np
from imutils.video import VideoStream
import imutils
from time import sleep
import serial
import time

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
    ser.flush()

command_dict = dict(forward = "1", backward = "2", right = "3", left = "4", rotate = "5", grab = "6", ungrab = "7")

# название окна подстройки
WINDOWNAME = "Настройка тона"

# минимальный размер контуров пятна
BLOBSIZE = 200

IS_GRABED = None

GRAB_TRIGGER = 0

GRAB_TIMER = 0

GRAB_LIMIT = 2

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
GRAB_SIZE = 9000      
UNGRAB_SIZE = 42000
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# константы насыщенности и яркости
S_MIN = 100
S_MAX = 255
V_MIN = 50
V_MAX = 255

# распознаваемые цвета
H_PURPLE = (150, 180) # 145, 170   155,175
H_GREEN = (90,110)
H_YELLOW = (20, 35)
H_ORANGE = (0,15)

# определяем функцию проверки размера пятна
def checkSize(w, h):
    if w * h > BLOBSIZE or w >= 35:
        return True
    else:
        return False

# определяем размеры кадра
frameSize = (320, 240)

center_of_frame = frameSize[0]/2

# создаём объект видео потока
vs = VideoStream(src=0, usePiCamera=True, resolution=frameSize, framerate=32).start()

# ждём окончания инициализации видеопотока
sleep(1)

def find_contour(HUE, image):
    # получаем кадр изображения
        #image = vs.read()

        # получаем максимальный и минимальный тон из значения ползунка
        #h_min = cv2.getTrackbarPos("Hue", WINDOWNAME) - 10
        #h_max = cv2.getTrackbarPos("Hue", WINDOWNAME) + 10

        # определяем границы цвета в HSV
        lower_range = np.array([HUE[0], S_MIN, V_MIN])
        upper_range = np.array([HUE[1], S_MAX, V_MAX])

        # конвертируем изображение в HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # создаём маску выбранного цвета
        thresh = cv2.inRange(hsv, lower_range, upper_range)

        # побитово складываем оригинальную картинку и маску
        bitwise = cv2.bitwise_and(image, image, mask=thresh)

        # показываем картинку маски цвета
        cv2.imshow("bitwise", bitwise)

        # удаляем цвет из маски
        gray = cv2.cvtColor(bitwise, cv2.COLOR_BGR2GRAY)

        # ищем контуры в картинке
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        return contours


def send_command(a):
    start_time = time.time()
    data = command_dict[a] +"\n"
    ser.write(bytes(data,"UTF-8"))
    while True:
        end_time = time.time()
        line = ser.readline().decode('utf-8').rstrip()
        print(len(line))
        if line == "OKOK":
            ser.flush()
            break
        if end_time - start_time > 1.5:
            ser.flush()
            break
    pass



while True:
    
        image = vs.read()
        
        if IS_GRABED is None:
            
            contours_ORANGE = find_contour(H_ORANGE, image)
            contours_YELLOW = find_contour(H_YELLOW, image)
       
            # если контуры найдены...
            if len(contours_ORANGE) != 0 and len(contours_YELLOW) != 0:

                # находим контуры бОльшего размера
                c_YELLOW = max(contours_YELLOW, key = cv2.contourArea)
                c_ORANGE = max(contours_ORANGE, key = cv2.contourArea)
                c = max([c_YELLOW, c_ORANGE],key = cv2.contourArea)
                
                
                # получаем координаты прямоугольника, в который они вписаны
                x,y,w,h = cv2.boundingRect(c)

                # если прямоугольник достаточного размера...
                if checkSize(w, h):

                    # выводим его
                    #print(w*h, end="")
                    cv2.rectangle(image, (x, y), (x+w, y+h), RECTCOLOR, RTHICK)
                    if w * h >= GRAB_SIZE and GRAB_TRIGGER == 0:
                        GRAB_TRIGGER = 1
                        GRAB_TIMER = time.time()
                    if time.time() - GRAB_TIMER >= GRAB_LIMIT and GRAB_TRIGGER == 1 :
                        send_command("forward")
                        GRAB_TIMER = 0
                        GRAB_TRIGGER = 0
                        send_command("grab")
                        print("Grab")
                        if c == c_YELLOW:
                            IS_GRABED = "yellow"
                        if c == c_ORANGE:
                            IS_GRABED = "orange"
                    elif (x+w/2) < (center_of_frame - 20):
                        send_command("left")
                    elif (x+w/2) > (center_of_frame + 20):
                        send_command("right")
                    elif w * h < GRAB_SIZE:
                        send_command("forward")
                    continue
             # если контуры найдены...
            elif len(contours_ORANGE) != 0 and len(contours_YELLOW) == 0:
            
                # находим контуры бОльшего размера
                
                c = max(contours_ORANGE,key = cv2.contourArea)
                # получаем координаты прямоугольника, в который они вписаны
                x,y,w,h = cv2.boundingRect(c)

                # если прямоугольник достаточного размера...
                if checkSize(w, h):

                    # выводим его
                    #print(w*h, end="")
                    cv2.rectangle(image, (x, y), (x+w, y+h), RECTCOLOR, RTHICK)
                    if w * h >= GRAB_SIZE and GRAB_TRIGGER == 0:
                        GRAB_TRIGGER = 1
                        GRAB_TIMER = time.time()
                    if time.time() - GRAB_TIMER >= GRAB_LIMIT and GRAB_TRIGGER == 1 :
                        send_command("forward")
                        GRAB_TIMER = 0
                        GRAB_TRIGGER = 0
                        send_command("grab")
                        print("Grab")
                        IS_GRABED = "orange"
                    elif (x+w/2) < (center_of_frame - 20):
                        send_command("left")
                    elif (x+w/2) > (center_of_frame + 20):
                        send_command("right")
                    elif w * h < GRAB_SIZE:
                        send_command("forward")
                    continue
             # если контуры найдены...
            elif len(contours_ORANGE) == 0 and len(contours_YELLOW) != 0:

                # находим контуры бОльшего размера
                c = max(contours_YELLOW,key = cv2.contourArea)
                # получаем координаты прямоугольника, в который они вписаны
                x,y,w,h = cv2.boundingRect(c)

                # если прямоугольник достаточного размера...
                if checkSize(w, h):

                    # выводим его
                    print(w*h, end="")
                    cv2.rectangle(image, (x, y), (x+w, y+h), RECTCOLOR, RTHICK)
                    
                    if w * h >= GRAB_SIZE and GRAB_TRIGGER == 0:
                        GRAB_TRIGGER = 1
                        GRAB_TIMER = time.time()
                    if time.time() - GRAB_TIMER >= GRAB_LIMIT and GRAB_TRIGGER == 1 :
                        send_command("forward")
                        GRAB_TIMER = 0
                        GRAB_TRIGGER = 0
                        send_command("grab")
                        print("Grab")
                        IS_GRABED = "yellow"
                    elif (x+w/2) < (center_of_frame - 20):
                        send_command("left")
                    elif (x+w/2) > (center_of_frame + 20):
                        send_command("right")
                    elif w * h < GRAB_SIZE:
                        send_command("forward")
                    continue
            
            send_command("rotate")
            
        if IS_GRABED == "yellow":
            
            contours_GREEN = find_contour(H_GREEN, image)
            
            if len(contours_GREEN) != 0:

                # находим контуры бОльшего размера
                c = max(contours_GREEN,key = cv2.contourArea)
                # получаем координаты прямоугольника, в который они вписаны
                x,y,w,h = cv2.boundingRect(c)

                # если прямоугольник достаточного размера...
                if checkSize(w, h):

                    # выводим его
                    print(w*h, end="")
                    cv2.rectangle(image, (x, y), (x+w, y+h), RECTCOLOR, RTHICK)
                    
                    if w * h >= UNGRAB_SIZE:
                        send_command("forward")
                        send_command("ungrab")
                        send_command("backward")
                        for i in range(13):
                            send_command("rotate")
                        print("UNGrab")
                        IS_GRABED = None
                    elif (x+w/2) < (center_of_frame - 20):
                        send_command("left")
                    elif (x+w/2) > (center_of_frame + 20):
                        send_command("right")
                    elif w * h < UNGRAB_SIZE:
                        send_command("forward")
                    continue
            
            send_command("rotate")
    
        if IS_GRABED == "orange":
            
            contours_PURPLE = find_contour(H_PURPLE, image)
            
            if len(contours_PURPLE) != 0:

                # находим контуры бОльшего размера
                c = max(contours_PURPLE,key = cv2.contourArea)
                # получаем координаты прямоугольника, в который они вписаны
                x,y,w,h = cv2.boundingRect(c)

                # если прямоугольник достаточного размера...
                if checkSize(w, h):

                    # выводим его
                    print(w*h, end="")
                    cv2.rectangle(image, (x, y), (x+w, y+h), RECTCOLOR, RTHICK)
                    
                    if w * h >= UNGRAB_SIZE:
                        send_command("forward")
                        send_command("ungrab")
                        send_command("backward")
                        for i in range(13):
                            send_command("rotate")
                        print("UNGrab")
                        IS_GRABED = None
                    elif (x+w/2) < (center_of_frame - 20):
                        send_command("left")
                    elif (x+w/2) > (center_of_frame + 20):
                        send_command("right")
                    elif w * h < UNGRAB_SIZE:
                        send_command("forward")
                    continue
            
            send_command("rotate")
        # Показываем картинку с квадратом выделения
        #cv2.imshow("Image", image)

        # Если была нажата клавиша ESC
        #k = cv2.waitKey(1)
        #if k == 27:

            # прерываем выполнение цикла
            #break

# закрываем все окна
cv2.destroyAllWindows()

# останавливаем видео поток
vs.stop()
