print('\n------------------------------------')

print('Making imports...')
import numpy as np
import cv2
import colors as col
import time
from gd import GD

print('Loading assets...')
cap = cv2.VideoCapture(0)
client = GD()
waiting_for_process = False
waiting_for_cap_open = False
waiting_for_ret = False
is_jumping = False
pTime = 0

palm_cascade = cv2.CascadeClassifier('data/rpalm.xml')
fist_cascade = cv2.CascadeClassifier('data/fist.xml')

print('------------------------------------')
while True:
    try:
        if not cap.isOpened():
            if not waiting_for_cap_open:
                waiting_for_cap_open = True
                print(f'{col.FAIL}Please ensure that your camera is connected and enabled.{col.ENDC}')
            cv2.destroyAllWindows()
            continue
        waiting_for_cap_open = False

        ret, frame = cap.read()

        f_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        f_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame = frame[int(f_h*.25):int(f_h*.75),int(f_w*.25):int(f_w*.75)]
        f_w = frame.shape[1]
        f_h = frame.shape[0]

        if not ret:
            if waiting_for_ret:
                waiting_for_ret = True
                print(f'{col.FAIL}Please ensure that your camera is not currently being used by another program.{col.ENDC}')
            cv2.destroyAllWindows()
            continue
        waiting_for_ret = False

        hwnd = client.get_first_window()
        if not hwnd:
            if not waiting_for_process:
                waiting_for_process = True
                print(f'{col.WARNING}Looking for {client.PROCESS_NAME}...{col.ENDC}')
        else:
            if waiting_for_process:
                waiting_for_process = False
                print(f'{col.OKGREEN}{client.PROCESS_NAME} found.{col.ENDC}')

        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        palms = palm_cascade.detectMultiScale(grayscale, 1.05, 2)
        fist = fist_cascade.detectMultiScale(grayscale, 1.05, 1)

        palm_area = 0
        fist_area = 0

        for (x, y, w, h) in palms:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.putText(frame, 'Release', (x, y+h), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
            palm_area = w*h
            break

        if palm_area <= 0:
            for (x, y, w, h) in fist:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
                roi_frame = frame[y:y+h,x:x+w]
                cv2.putText(frame, 'Jump', (x, y+h), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
                fist_area = w*h
                break

        if hwnd:
            cv2.putText(frame, 'Connected to GD', (0, int(f_h*0.9)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)
            if palm_area >= fist_area:
                if is_jumping:
                    is_jumping = False
                    client.release(hwnd)
            else:
                if not is_jumping:
                    is_jumping = True
                    client.jump(hwnd)
        else:
            cv2.putText(frame, 'Not connected to GD', (0, int(f_h*0.9)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
        
        cTime = time.time()
        cv2.putText(frame, f'FPS:{int(1 / (cTime - pTime))}', (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        cv2.imshow('Hands-Free Controller', frame)
        pTime = cTime
        if cv2.waitKey(1) == ord('q'):
            raise KeyboardInterrupt()
    except KeyboardInterrupt:
        print('------------------------------------')
        if waiting_for_process:
            print(f'{col.WARNING}Aborting. Process not found.{col.ENDC}')
        else:
            print(f'{col.WARNING}Quitting out of the program.{col.ENDC}')
        break
cv2.destroyAllWindows()
cap.release()
print('------------------------------------\n')