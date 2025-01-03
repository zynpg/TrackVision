import cv2
import numpy as np
import time


OPENCV_OBJECT_TRACKERS= {"csrt": cv2.legacy.TrackerCSRT_create,
                         "kcf": cv2.legacy.TrackerCSRT_create,
                         "boosting": cv2.legacy.TrackerCSRT_create,
                         "mil": cv2.legacy.TrackerCSRT_create,
                         "tld": cv2.legacy.TrackerCSRT_create,
                         "medianflow": cv2.legacy.TrackerCSRT_create,
                         "mosse": cv2.legacy.TrackerCSRT_create,
                         }
tracker_name= "medianflow"
trackers= cv2.legacy.MultiTracker_create()



cap = cv2.VideoCapture(0)

ret, frame = cap.read()
if not ret:
    print("Kamera açılamadı")
    exit()

roi = cv2.selectROI("Nesne Seçimi", frame, fromCenter=False, showCrosshair=True)

x, y, w, h = roi
track_window = (x, y, w, h)
roi_image = frame[y:y+h, x:x+w]

hsv_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
f=0

while True:
    ret, frame = cap.read()
    if ret:

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        dist = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

        ret, track_window = cv2.meanShift(dist, track_window, term_crit)

        x, y, w, h = track_window
        frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)


        #cv2.imshow("Nesne Takibi", frame)

    (success, boxes) = trackers.update(frame)
    info = [("Tracker", tracker_name),
            ("Success", "Yes" if success else "No")]  # takip ettiğimiz bir şey varsa yes yoksa no yaz

    string_text = ""

    for (i, (k, p)) in enumerate(info):  # infodakileri numaralandırır, i elemanın numarası demek
        text = f"{k} : {p}"
        string_text = string_text + text + ""

    cv2.putText(frame, string_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0))

    for box in boxes:
        (x, y, w, h) = [int(p) for p in box]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        box = cv2.selectROI("Frame", frame, fromCenter=False)
        tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
        trackers.add(tracker, frame, box)

    elif key == ord('q'):
        break
    f += 1


cap.release()
cv2.destroyAllWindows()
