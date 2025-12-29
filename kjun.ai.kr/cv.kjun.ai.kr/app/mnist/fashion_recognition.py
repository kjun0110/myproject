# Fashion-MNIST 패션 아이템 인식 문제를 신경망으로 풀어봅니다.
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import numpy as np
import struct
import os


class FashionMNISTNet(nn.Module):
    """Fashion-MNIST 패션 아이템 인식을 위한 신경망 모델"""

    def __init__(self):
        super(FashionMNISTNet, self).__init__()
        # Flatten(input_shape=(28, 28)) -> Dense(128, activation='relu') -> Dense(10, activation='softmax')
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.fc2 = nn.Linear(128, 10)
        """
        relu (Rectified Linear Unit 정류한 선형 유닛)
        미분 가능한 0과 1사이의 값을 갖도록 하는 알고리즘
        softmax
        nn (neural network)의 최상위층에서 사용되며 classification을 위한 function
        결과를 확률값으로 해석하기 위한 알고리즘
        """

    def forward(self, x):
        x = self.flatten(x)  # (batch_size, 28, 28) -> (batch_size, 784)
        x = F.relu(self.fc1(x))  # ReLU 활성화 함수
        x = self.fc2(x)  # 최종 출력 (softmax는 CrossEntropyLoss에서 처리)
        return x


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
            # (num_images, rows*cols) -> (num_images, rows, cols)로 reshape
            images = np.array(images, dtype=np.float32).reshape(num_images, rows, cols)
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


def load_fashion_mnist_data(data_dir):
    """Fashion-MNIST 데이터를 로드합니다."""
    train_images = load_idx_file(os.path.join(data_dir, "train-images-idx3-ubyte"))
    train_labels = load_idx_file(os.path.join(data_dir, "train-labels-idx1-ubyte"))
    test_images = load_idx_file(os.path.join(data_dir, "t10k-images-idx3-ubyte"))
    test_labels = load_idx_file(os.path.join(data_dir, "t10k-labels-idx1-ubyte"))

    return (train_images, train_labels), (test_images, test_labels)


def train_model(model, train_loader, optimizer, criterion, device):
    """모델을 학습시킵니다."""
    model.train()
    total_loss = 0
    num_batches = 0

    for batch_images, batch_labels in train_loader:
        batch_images = batch_images.to(device)
        batch_labels = batch_labels.to(device)

        # 순전파
        optimizer.zero_grad()
        outputs = model(batch_images)
        loss = criterion(outputs, batch_labels)

        # 역전파 및 최적화
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


def evaluate_model(model, test_loader, device):
    """모델의 정확도를 평가합니다."""
    model.eval()
    correct = 0
    total = 0
    total_loss = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            loss = F.cross_entropy(outputs, labels)
            total_loss += loss.item()

    accuracy = 100 * correct / total
    avg_loss = total_loss / len(test_loader)
    return accuracy, avg_loss


def plot_image(i, predictions_array, true_label, img, class_names):
    """단일 이미지와 예측 결과를 시각화합니다."""
    predictions_array, true_label, img = predictions_array[i], true_label[i], img[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])

    plt.imshow(img, cmap=plt.cm.binary)

    predicted_label = np.argmax(predictions_array)
    if predicted_label == true_label:
        color = "blue"
    else:
        color = "red"

    plt.xlabel(
        "{} {:2.0f}% ({})".format(
            class_names[predicted_label],
            100 * np.max(predictions_array),
            class_names[true_label],
        ),
        color=color,
    )


def plot_value_array(i, predictions_array, true_label):
    """예측 확률 분포를 막대 그래프로 시각화합니다."""
    predictions_array, true_label = predictions_array[i], true_label[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    thisplot = plt.bar(range(10), predictions_array, color="#777777")
    plt.ylim([0, 1])
    predicted_label = np.argmax(predictions_array)

    thisplot[predicted_label].set_color("red")
    thisplot[true_label].set_color("blue")


if __name__ == "__main__":
    # 클래스 이름 정의
    class_names = [
        "T-shirt/top",
        "Trouser",
        "Pullover",
        "Dress",
        "Coat",
        "Sandal",
        "Shirt",
        "Sneaker",
        "Bag",
        "Ankle boot",
    ]

    # 디바이스 설정 (GPU가 있으면 사용, 없으면 CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"사용 디바이스: {device}")

    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "fashion-mnist")

    # Fashion-MNIST 데이터 로드
    print("Fashion-MNIST 데이터 로딩 중...")
    (train_images, train_labels), (test_images, test_labels) = load_fashion_mnist_data(
        data_dir
    )

    # 데이터 시각화 (처음 25개 이미지)
    plt.figure(figsize=(10, 10))
    for i in range(25):
        plt.subplot(5, 5, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(train_images[i].numpy(), cmap=plt.cm.binary)
        plt.xlabel(class_names[train_labels[i].item()])
    plt.savefig("fashion_mnist_samples.png")
    print("샘플 이미지가 fashion_mnist_samples.png로 저장되었습니다.")
    # plt.show()  # 주석 해제하면 이미지가 표시됩니다

    # 데이터셋 및 데이터로더 생성
    train_dataset = TensorDataset(train_images, train_labels)
    test_dataset = TensorDataset(test_images, test_labels)

    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # 모델 생성
    model = FashionMNISTNet().to(device)

    # 손실 함수 및 옵티마이저 설정
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())

    # 신경망 모델 학습
    print("학습 시작...")
    num_epochs = 5

    for epoch in range(num_epochs):
        avg_loss = train_model(model, train_loader, optimizer, criterion, device)
        print(f"Epoch: {epoch + 1}/{num_epochs}, Avg. loss = {avg_loss:.4f}")

    print("최적화 완료!")

    # 테스트 정확도 평가
    print("정확도 평가 중...")
    test_accuracy, test_loss = evaluate_model(model, test_loader, device)
    print(f"\n테스트 정확도: {test_accuracy:.2f}%")
    print(f"테스트 손실: {test_loss:.4f}")

    # 예측 수행
    print("예측 수행 중...")
    model.eval()
    predictions = []
    with torch.no_grad():
        for images, _ in test_loader:
            images = images.to(device)
            outputs = model(images)
            # softmax를 적용하여 확률값으로 변환
            probs = F.softmax(outputs, dim=1)   #소프트 맥스 선명도 올리는거 부드럽게
            predictions.extend(probs.cpu().numpy())

    predictions = np.array(predictions)
    print(f"예측 결과 샘플 (인덱스 3): {predictions[3]}")

    # 예측 결과 시각화
    num_rows = 5
    num_cols = 3
    num_images = num_rows * num_cols
    plt.figure(figsize=(2 * 2 * num_cols, 2 * num_rows))
    for i in range(num_images):
        plt.subplot(num_rows, 2 * num_cols, 2 * i + 1)
        plot_image(
            i, predictions, test_labels.numpy(), test_images.numpy(), class_names
        )
        plt.subplot(num_rows, 2 * num_cols, 2 * i + 2)
        plot_value_array(i, predictions, test_labels.numpy())
    plt.tight_layout()
    plt.savefig("fashion_mnist_predictions.png")
    print("예측 결과가 fashion_mnist_predictions.png로 저장되었습니다.")
    # plt.show()  # 주석 해제하면 이미지가 표시됩니다
