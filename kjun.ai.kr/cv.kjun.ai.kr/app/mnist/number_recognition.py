# 머신러닝 학습의 Hello World 와 같은 MNIST(손글씨 숫자 인식) 문제를 신경망으로 풀어봅니다.
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import struct
import os


def load_idx_file(filename):
    """IDX 파일 형식의 MNIST 데이터를 로드합니다."""
    with open(filename, "rb") as f:
        # IDX 파일 헤더 읽기
        magic = struct.unpack(">I", f.read(4))[0]
        if magic == 2051:  # 이미지 파일
            num_images = struct.unpack(">I", f.read(4))[0]
            rows = struct.unpack(">I", f.read(4))[0]
            cols = struct.unpack(">I", f.read(4))[0]
            images = []
            for _ in range(num_images):
                image = []
                for _ in range(rows * cols):
                    pixel = struct.unpack(">B", f.read(1))[0]
                    image.append(pixel)
                images.append(image)
            return (
                torch.tensor(images, dtype=torch.float32) / 255.0
            )  # 0-255를 0-1로 정규화
        elif magic == 2049:  # 레이블 파일
            num_labels = struct.unpack(">I", f.read(4))[0]
            labels = []
            for _ in range(num_labels):
                label = struct.unpack(">B", f.read(1))[0]
                labels.append(label)
            return torch.tensor(labels, dtype=torch.long)
    return None


def load_mnist_data(data_dir):
    """MNIST 데이터를 로드합니다."""
    train_images = load_idx_file(os.path.join(data_dir, "train-images.idx3-ubyte"))
    train_labels = load_idx_file(os.path.join(data_dir, "train-labels.idx1-ubyte"))
    test_images = load_idx_file(os.path.join(data_dir, "t10k-images.idx3-ubyte"))
    test_labels = load_idx_file(os.path.join(data_dir, "t10k-labels.idx1-ubyte"))

    return (train_images, train_labels), (test_images, test_labels)


class MNISTNet(nn.Module):
    """MNIST 손글씨 숫자 인식을 위한 신경망 모델"""

    def __init__(self):
        super(MNISTNet, self).__init__()
        # 784(입력 특성값) -> 256 (히든레이어 뉴런 갯수) -> 256 (히든레이어 뉴런 갯수) -> 10 (결과값 0~9 분류)
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 10)

    def forward(self, x):
        # 입력값에 가중치를 곱하고 ReLU 함수를 이용하여 레이어를 만듭니다.
        x = F.relu(self.fc1(x))
        # L1 레이어의 출력값에 가중치를 곱하고 ReLU 함수를 이용하여 레이어를 만듭니다.
        x = F.relu(self.fc2(x))
        # 최종 모델의 출력값은 10개의 분류를 가지게 됩니다.
        x = self.fc3(x)
        return x


def train_model(model, train_loader, optimizer, criterion, device):
    """모델을 학습시킵니다."""
    model.train()
    total_cost = 0
    num_batches = 0

    for batch_xs, batch_ys in train_loader:
        batch_xs = batch_xs.to(device)
        batch_ys = batch_ys.to(device)

        # 순전파
        optimizer.zero_grad()
        outputs = model(batch_xs)
        loss = criterion(outputs, batch_ys)

        # 역전파 및 최적화
        loss.backward()
        optimizer.step()

        total_cost += loss.item()
        num_batches += 1

    return total_cost / num_batches


def evaluate_model(model, test_loader, device):
    """모델의 정확도를 평가합니다."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    return accuracy


if __name__ == "__main__":
    # 디바이스 설정 (GPU가 있으면 사용, 없으면 CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"사용 디바이스: {device}")

    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "number-mnist")

    # MNIST 데이터 로드
    print("MNIST 데이터 로딩 중...")
    (train_images, train_labels), (test_images, test_labels) = load_mnist_data(data_dir)

    # 데이터셋 및 데이터로더 생성
    train_dataset = TensorDataset(train_images, train_labels)
    test_dataset = TensorDataset(test_images, test_labels)

    batch_size = 100    #한 묶음당 100개 데이터
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)   #shuffle 데이터를 섞어줌 즉 썻던 데이터 다시 사용
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # 모델 생성
    model = MNISTNet().to(device)

    # 손실 함수 및 옵티마이저 설정
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 신경망 모델 학습
    print("학습 시작...")
    num_epochs = 15

    for epoch in range(num_epochs):
        avg_cost = train_model(model, train_loader, optimizer, criterion, device)
        print(f"Epoch: {epoch + 1:04d}, Avg. cost = {avg_cost:.3f}")

    print("최적화 완료!")

    # 결과 확인
    print("정확도 평가 중...")
    accuracy = evaluate_model(model, test_loader, device)
    print(f"정확도: {accuracy:.2f}%")
