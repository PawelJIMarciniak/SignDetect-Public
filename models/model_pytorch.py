import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import numpy as np

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect
from models.models import Sign, Base, Video, FrameCoordinate


class SignLanguageModel(nn.Module):
    def __init__(self, num_classes):
        super(SignLanguageModel, self).__init__()
        self.fc1 = nn.Linear(63, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x



def load_data_from_db(db_path):
    # Connect to the SQLite database using SQLAlchemy
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Display available tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Available tables in the database:", tables)

    # Query the database for videos associated with signs in a specific language (language_id = 1)
    videos = session.query(Video).join(Sign).filter(Sign.languages_id == 1).all()

    data = []
    labels = []

    # Map original sign IDs to a compact range of labels (0 to num_classes-1)
    sign_id_mapping = {sign.id: idx for idx, sign in enumerate(session.query(Sign).filter(Sign.languages_id == 1).order_by(Sign.id))}

    for video in videos:
        video_id = video.id
        sign_id = video.signs_id
        frame_count = video.frame_count
        image_width = video.image_width
        image_height = video.image_height

        # Retrieve 3D coordinates from the 21 keypoints
        frames = session.query(FrameCoordinate).filter(FrameCoordinate.frame_id == video_id).all()

        if len(frames) == 21:
            frame_data = [coord for frame in frames for coord in (frame.x_coordinate, frame.y_coordinate, frame.z_coordinate)]
            data.append(frame_data)
            labels.append(sign_id_mapping[sign_id])

    num_classes  = len(sign_id_mapping)

    print("\n--- Input Data Info ---")
    print(f"Number of samples: {len(data)}")
    if data:
        print("Sample input:", data[0])
    print("Input shape:", np.array(data).shape)

    print("\n--- Output Label Info ---")
    print(f"Number of labels: {len(labels)}")
    if labels:
        print("Sample label:", labels[0])
    print("Number of classes:", num_classes)
    print("Label values:", set(labels))

    print("\n--- Sign ID to Name Mapping ---")
    for actual_id, mapped_id in sign_id_mapping.items():
        sign_name = session.query(Sign).filter(Sign.id == actual_id).first().name
        print(f"id: {actual_id}, mapped_id: {mapped_id}, name: {sign_name}")

    session.close()
    return np.array(data), np.array(labels), num_classes


def train_model(data, labels, num_classes):
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.5, random_state=42)

    # Convert numpy arrays to PyTorch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)
    y_test = torch.tensor(y_test, dtype=torch.long)

    # Initialize the model, loss function, and optimizer
    model = SignLanguageModel(num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    for epoch in range(800):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/800], Loss: {loss.item():.4f}')

    # Evaluate the model on the test set
    model.eval()
    with torch.no_grad():
        outputs = model(X_test)
        _, predicted = torch.max(outputs.data, 1)
        accuracy = (predicted == y_test).sum().item() / y_test.size(0)
        print(f'\nTest Accuracy: {accuracy * 100:.2f}%')

    # Save model weights
    model_save_path = 'model_weights.pth'
    torch.save(model.state_dict(), model_save_path)
    print(f"Model weights saved to {model_save_path}")


if __name__ == "__main__":
    db_path = '../data/gesture_ai_database.db'
    data, labels, num_classes = load_data_from_db(db_path)

    print(f"Min label: {labels.min()}, Max label: {labels.max()}")

    train_model(data, labels, num_classes)
