import re
import cv2
import os


class Lena:
    def __init__(self):
        #데이터 디렉토리 경로 설정
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "opencv")
        self._cascade = os.path.join(data_dir, "haarcascade_frontalface_alt.xml")
        self._lena = os.path.join(data_dir, "lena.jpg")
        self.fname = os.path.join(data_dir, "lena-face.png")

    def read_file(self):
        cascade = cv2.CascadeClassifier(self._cascade)
        img = cv2.imread(self._lena)
        face = cascade.detectMultiScale(img, minSize=(50, 50))
        if len(face) == 0:
            print("얼굴을 찾을 수 없습니다.")
            quit()
        faces = self._face.copy()
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            img = self.execute(img, (x, y, x + w, y + h), 10)
        cv2.imwrite("lena-face.png", img)
        cv2.imshow("lena-face.png", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def execute(img, rect, size):
        original = faces.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        unchanged = img.copy() #unchanged = 바꾸기 전으로 원복
        """
        이미지 읽기에는 위 3가지 속성이 존재함.
        대신에 1, 0, -1 을 사용해도 됨.
        """
        cv2.imshow('Original', original)
        cv2.imshow('Gray', gray)
        cv2.imshow('Unchanged', unchanged)
        cv2.waitKey(0)
        cv2.destroyAllWindows() # 윈도우종료        

if __name__ == "__main__":
    lena = Lena()
    lena.read_file()
    lena.execute()









