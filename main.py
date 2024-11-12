import cv2 as cv
import numpy as np
import math
import process_manager
from time import sleep

looking_for_process = None
pressing_down = False
found_pid = 0

print(f'\n\n-------------------------\nOpenCV Version: {cv.__version__}\n-------------------------\n')

capture = cv.VideoCapture(0)

if not capture.isOpened():
    print(f'\033[91mCould not access camera.\033[00m')
    exit()

while True:
    try:
        if looking_for_process == None:
            looking_for_process = True
            print(f'\033[00mWaiting for {process_manager.PROCESS_NAME}...\033[00m')

        temp_pid = process_manager.get_pid()
        if temp_pid:
            if looking_for_process:
                looking_for_process = False
                found_pid = temp_pid
                print(f'\033[92m{process_manager.PROCESS_NAME} process found!...\033[00m')
        else:
            if not looking_for_process:
                looking_for_process = True
                print(f'\033[91mLost {process_manager.PROCESS_NAME} process. Waiting...\033[00m')
                cv.destroyAllWindows()
            continue

    
        success, raw = capture.read()

        if not success:
            print(f'\033[91mError receiving input data.\033[00m')
            break


        img = raw[100:400, 100:400]

        _, thresholded = cv.threshold(
            cv.GaussianBlur(cv.cvtColor(img, cv.COLOR_BGR2GRAY), (35, 35), 0),
            100,
            255,
            cv.THRESH_BINARY_INV,
            cv.THRESH_OTSU
        )

        contours, _ = cv.findContours(thresholded.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        fingers_up = 0
        if contours:
            largest_contour = max(contours, key=lambda x: cv.contourArea(x))
            x, y, w, h = cv.boundingRect(largest_contour)
            cv.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 0)
            hull = cv.convexHull(largest_contour)
            drawing = np.zeros(img.shape, np.uint8)
            cv.drawContours(drawing, [largest_contour], 0, (0, 255, 0), 0)
            cv.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
            hull = cv.convexHull(largest_contour, returnPoints=False)
            defects = cv.convexityDefects(largest_contour, hull)

            cv.drawContours(thresholded, contours, -1, (0, 255, 0), 3)

            if type(defects) != type(None):
                for i in range(defects.shape[0]):
                    # Math stolen from online
                    s, e, f, d = defects[i, 0]
                    start = tuple(largest_contour[s][0])
                    end = tuple(largest_contour[e][0])
                    far = tuple(largest_contour[f][0])
                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                    if angle <= 90:
                        fingers_up += 1

            if fingers_up > 0:
                if pressing_down:
                    process_manager.release(found_pid)
                    pressing_down = False
                cv.putText(img, f'Release', (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255))
            else:
                if not pressing_down:
                    process_manager.jump(found_pid)
                    pressing_down = True
                cv.putText(img, f'Jump', (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0))
            
            # cv.putText(img, f'Fingers up: {fingers_up}', (10, 200), cv.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255)))
        else:
            if pressing_down:
                process_manager.release(found_pid)
                pressing_down = False
        # cv.imshow('PROCESSING', cv.cvtColor(thresholded, cv.COLOR_RGB2RGBA))
        cv.imshow('WIRELESS_GD', cv.cvtColor(img, cv.COLOR_RGB2RGBA))
        if cv.waitKey(1) == ord('q'):
            break
    except KeyboardInterrupt:
        break

capture.release()
cv.destroyAllWindows()
print("Closed.\n")