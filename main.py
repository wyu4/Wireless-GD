print('\n------------------------------------')

print('Making imports...')
import numpy as np
import cv2
import mediapipe as mp
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

print('Loading mediapipe...')
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=1,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
index_tip = 8
thumb_tip = 4
mpDraw = mp.solutions.drawing_utils

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

        raw_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        raw_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame = frame[int(raw_h*.25):int(raw_h*.75),int(raw_w*.25):int(raw_w*.75)]
        h,w,c = frame.shape

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

        index_pose = (w, h)
        thumb_pose = (w, h)

        results = hands.process(frame)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lms = handLms.landmark
                lmIndex = lms[index_tip]
                lmThumb = lms[thumb_tip]
                if lmIndex:
                    index_pose = (int(lmIndex.x*w), int(lmIndex.y*h))
                if lmThumb:
                    thumb_pose = (int(lmThumb.x*w), int(lmThumb.y*h))

        line_col = (255, 255, 255)

        if hwnd:
            cv2.putText(frame, 'Connected to GD', (0, int(h*0.9)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)
            if index_pose[1] > thumb_pose[1]:
                if not is_jumping:
                    client.jump(hwnd)
                is_jumping = True
                line_col = (0, 0, 255)
            else:
                if is_jumping:
                    client.release(hwnd)
                is_jumping = False
                line_col = (0, 255, 0)
        else:
            cv2.putText(frame, 'Not connected to GD', (0, int(h*0.9)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

        cv2.circle(frame, index_pose, 3, (255, 255, 255), -1)
        cv2.line(frame, index_pose, thumb_pose, line_col, 2)
        cv2.line(frame, (index_pose[0]-(w//10), thumb_pose[1]), thumb_pose, (255, 255, 255), 1)

        cTime = time.time()
        cv2.putText(frame, f'FPS:{int(1 / (cTime - pTime))}', (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        cv2.imshow('Handcam', frame)
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