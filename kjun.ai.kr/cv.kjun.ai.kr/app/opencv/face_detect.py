import cv2
import os


class FaceDetect:
    def __init__(self):
        # 데이터 디렉토리 경로 설정
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "opencv")
        self._cascade = os.path.join(data_dir, "haarcascade_frontalface_alt.xml")
        self._girl = os.path.join(data_dir, "girl.jpg")
        self._test1 = os.path.join(data_dir, "test1.png")


    def read_file(self):
        cascade = cv2.CascadeClassifier(self._cascade)   #cascade = 얼굴 인식하는 모델
        img = cv2.imread(self._girl)
        face = cascade.detectMultiScale(img, minSize=(150, 150))  #minSize = 얼굴 최소 크기
        if len(face) == 0:
            print("얼굴을 찾을 수 없습니다.")
            quit() #끝내는거 이거 없으면 계속 돌아감
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2) #사각형으로 그어라
        cv2.imwrite("girl-face.png",img)
        cv2.imshow("girl-face.png",img)

    def read_file2(self):
        cascade = cv2.CascadeClassifier(self._cascade)   #cascade = 얼굴 인식하는 모델
        png = cv2.imread(self._test1)
        face = cascade.detectMultiScale(png, minSize=(150, 150))  #minSize = 얼굴 최소 크기
        if len(face) == 0:
            print("얼굴을 찾을 수 없습니다.")
            quit() #끝내는거 이거 없으면 계속 돌아감
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            cv2.rectangle(png, (x, y), (x + w, y + h), (0, 0, 255), 2) #사각형으로 그어라
        cv2.imwrite("test1-face.png",png)
        cv2.imshow("test1-face.png",png)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    face_detect = FaceDetect()
    face_detect.read_file()
    face_detect.read_file2()