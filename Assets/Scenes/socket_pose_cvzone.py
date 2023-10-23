import cv2
import mediapipe as mp
import numpy as np
from cvzone.PoseModule import PoseDetector
import socket

# 서버 설정
HOST = '127.0.0.1'  # 서버의 IP 주소
PORT = 12345  # 사용할 포트 번호

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f'Server is listening on {HOST}:{PORT}')

client_socket, client_address = server_socket.accept()
print(f'Connected by {client_address}')

detector = PoseDetector()

# 위치 정보
# pose_ind = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]         # 몸통

pose_name = ['N','Leyei','Leye','Leyeo','Reyei','Reye','Reyeo','Lear','Rear','LM','RM',
             'LS','RS','LE','RE','LW','RW',
             'LP','RP','LK','RK','LA','RA']
# 코(Nose), 왼쪽 눈 안쪽(Leyei), 왼쪽 눈(Leye), 왼쪽 눈 바깥쪽(Leyeo),
# 오른쪽 눈 안쪽(Reyei), 오른쪽 눈(Reye), 오른쪽 눈 바깥쪽(Reyeo),
# 왼쪽 귀(Lear), 오른쪽 귀(Rear), 왼쪽 입(LM), 오른쪽 입(RM),
# 왼쪽 어깨(LS), 오른쪽 어깨(RS), 왼쪽 팔꿈치(LE), 오른쪽 팔꿈치(RE), 왼쪽 손목(LW), 오른쪽 손목(RW),
# 왼쪽 골반(LP), 오른쪽 골반(RP), 왼쪽 무릎(LK), 오른쪽 무릎(RK), 왼똑 발목(LA), 오른쪽 발목(RA)

## 영상촬영

print("영상촬영시작")

cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()
    if not ret:
        print("카메라를 찾을 수 없습니다.")

        # 동영상을 불러올 경우는 'continue' 대신 'break'를 사용합니다.
        break

    image = detector.findPose(image)

    lmList, bboxInfo = detector.findPosition(image)
    pose_dict = dict(zip(pose_name, lmList))

    # 유니티에게 값을 데이터를 보냄
    data = client_socket.recv(1024)
    if not data:
        break
    else:
        # print(f'Received from Unity: {data.decode()}') # 유니티에서 보낸 데이터를 파이썬에서 확인하는 코드
        client_socket.sendall(str(lmList).encode())      # 2차원 배열: lmList, 딕셔너리: pose_dict

cap.release()
client_socket.close()