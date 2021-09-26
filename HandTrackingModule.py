import cv2
import mediapipe as mp
import time
import math

class handDet():
        def __init__(self, mode = False, maxHands = 2, detectionCon = 0.7, trackCon = 0.5):
                self.mode = mode
                self.maxHands = maxHands
                self.detectionCon = detectionCon
                self.trackCon = trackCon

                self.mpHand = mp.solutions.hands
                self.hands = self.mpHand.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
                self.mpDraw = mp.solutions.drawing_utils

        def findHands(self, img, draw=True):
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.result = self.hands.process(imgRGB)
                #print(self.result.multi_hand_landmarks)

                if self.result.multi_hand_landmarks:
                        for handLms in self.result.multi_hand_landmarks:
                                if draw:
                                        self.mpDraw.draw_landmarks(img, handLms, self.mpHand.HAND_CONNECTIONS)

                return img

        def findPose(self, img, handNo = 0, draw = True):
                xList = []
                yList = []
                bbox = []
                self.lmList = [] #LandMark list which  contain all the values
                #imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                #self.result = self.hands.process(imgRGB)
                if self.result.multi_hand_landmarks:   #any Landmark detected or not
                        myHand = self.result.multi_hand_landmarks[handNo]

                        for id, lm in enumerate(myHand.landmark):
                                #print(id, lm) # id number and landmarks
                                h, w, c = img.shape
                                cx, cy = int(lm.x*w), int(lm.y*h) #hand center value x,y
                                #print(id, cx, cy)
                                xList.append(cx)
                                yList.append(cy)
                                self.lmList.append([id, cx, cy])

                                xmin, xmax = min(xList), max(xList)
                                ymin, ymax = min(yList), max(yList)
                                bbox =  xmin, ymin, xmax, ymax #bounding box
                                if draw:
                                        cv2.circle(img, (cx, cy), 6, (255, 0, 0), cv2.FILLED)
                                        #cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)

                        if draw:
                                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0, 255, 0), 2)
                                        
                return self.lmList, bbox

        def fingersUp(self):
                self.tipIds = [4, 8, 12, 16, 20]
                fingers = []
                #thumb
                if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
                        fingers.append(1)
                else:
                        fingers.append(0)

                #4 Fingers
                for id in range(1, 5):
                        if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                                fingers.append(1)
                        else:
                                fingers.append(0)
                return fingers

        def findDistance(self, p1, p2, img, draw = True):
                #p1 and p2 positions
                x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
                x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if draw:
                        cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                        cv2.circle(img, (x2, y2), 15, (0, 0, 255), cv2.FILLED)
                        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)

                length = math.hypot(x2 - x1, y2 - y1)
                return length, img, [x1, y1, x2, y2, cx, cy]


def main():
        cTime = 0
        pTime = 0
        cap = cv2.VideoCapture(0)
        det = handDet()


        while True:
                success, img = cap.read()
                img = det.findHands(img)
                lmList, bbox = det.findPose(img)
                #lmList = det.findPose(img)
                if len(lmList) != 0:
                       #print(lmList)
                       fingers = det.fingersUp()
                       #print(fingers, fingers.count(1))

                cTime = time.time()
                fps = 1/(cTime - pTime)
                pTime = cTime
                
                cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 0, 0), 2)
                cv2.imshow('video', img)
                cv2.waitKey(1)

        



if __name__ == "__main__":
        main()
