print('\n------------------------------------')

print('Making imports...')
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
is_moving_left = False
is_moving_right = False
pTime = 0

print('Loading mediapipe...')
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=1,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
index_tip = 8
click_lm_1 = 12
click_lm_2 = 4
winname = 'Handcam'
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

        index_pose = (w//2, h)
        click_pose_left = (w//2, h*2)
        click_pose_right = (w//2, h*2)

        results = hands.process(frame)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                lms = handLms.landmark
                lmIndex = lms[index_tip]
                lm_click_1 = lms[click_lm_1]
                lm_click_2 = lms[click_lm_2]
                if lmIndex:
                    index_pose = (int(lmIndex.x*w), int(lmIndex.y*h))
                if lm_click_1 and lm_click_2:
                    if lm_click_1.x < lm_click_2.x:
                        click_pose_left = (int(lm_click_1.x*w), int(lm_click_1.y*h))
                        click_pose_right = (int(lm_click_2.x*w), int(lm_click_2.y*h))
                    else:
                        click_pose_left = (int(lm_click_2.x*w), int(lm_click_2.y*h))
                        click_pose_right = (int(lm_click_1.x*w), int(lm_click_1.y*h))
                        
        jump_line_col = (255, 255, 255)
        left_line_col = (255, 255, 255)
        right_line_col = (255, 255, 255)

        left_x_limit = w//4
        right_x_limit = (w//4*3)

        if hwnd:
            cv2.putText(frame, 'Connected to GD', (0, int(h*0.9)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)
            if ((click_pose_left[0] - click_pose_right[0]) * (index_pose[1] - click_pose_right[1]) - (click_pose_left[1] - click_pose_right[1]) * (index_pose[0] - click_pose_right[0])) < 0:
                if not is_jumping:
                    client.jump(hwnd)
                is_jumping = True
                jump_line_col = (0, 0, 255)
            else:
                if is_jumping:
                    client.jump_release(hwnd)
                is_jumping = False
                jump_line_col = (0, 255, 0)

            if index_pose[0] < left_x_limit or click_pose_left[0] < left_x_limit or click_pose_right[0] < left_x_limit:
                if not is_moving_left:
                    is_moving_left = True
                    client.left(hwnd)
                left_line_col = (0, 255, 0)
            else:
                if is_moving_left:
                    is_moving_left = False
                    client.left_release(hwnd)

            if index_pose[0] > right_x_limit or click_pose_left[0] > right_x_limit or click_pose_right[0] > right_x_limit:
                if not is_moving_right:
                    is_moving_right = True
                    client.right(hwnd)
                right_line_col = (0, 255, 0)
            else:
                if is_moving_right:
                    is_moving_right = False
                    client.right_release(hwnd)
        else:
            cv2.putText(frame, 'Not connected to GD', (0, int(h*0.9)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

        cv2.circle(frame, index_pose, 3, (255, 255, 255), -1)
        cv2.line(frame, index_pose, click_pose_left, jump_line_col, 2)
        cv2.line(frame, index_pose, click_pose_right, jump_line_col, 2)
        cv2.line(frame, click_pose_left, click_pose_right, (255, 255, 255), 1)

        cv2.line(frame, (left_x_limit, 0), (left_x_limit, h), left_line_col, 1)
        cv2.line(frame, (right_x_limit, 0), (right_x_limit, h), right_line_col, 1)

        cTime = time.time()
        cv2.putText(frame, f'FPS:{int(1 / (cTime - pTime))}', (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        cv2.imshow(winname, frame)
        pTime = cTime

        if cv2.waitKey(1) == ord('q') or not cv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE):
            break
    except KeyboardInterrupt:
        print('------------------------------------')
        if waiting_for_process:
            print(f'{col.WARNING}Aborting...{col.ENDC}')
        break
cv2.destroyAllWindows()
cap.release()
print('------------------------------------\n')
