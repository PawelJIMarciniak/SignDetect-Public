import cv2
import numpy as np
import mediapipe as mp
import torch
from typing import Optional, Dict

from models.model_pytorch import SignLanguageModel


class SignPredictor:
    def __init__(self):
        # Mapping of model class indices to corresponding sign labels (A-Z, DEL, NOTHING, SPACE)
        self.signs_dict = {i: chr(65 + i) for i in range(26)}  # A-Z
        self.signs_dict.update({26: 'DEL', 27: 'NOTHING', 28: 'SPACE'})

        self.sign_model = self.load_sign_model()
        self.mp_hands, self.hands, self.mp_drawing = None, None, None
        self.initialize_mediapipe_model()

    @staticmethod
    def load_sign_model(model_path: str = 'models/model_weights.pth', num_classes: int = 29) -> SignLanguageModel:
        print("[INFO] Initializing Sign Language Model...")
        sign_model = SignLanguageModel(num_classes)
        sign_model.load_state_dict(torch.load(model_path))
        sign_model.eval()
        return sign_model

    def initialize_mediapipe_model(self):
        print("[INFO] Initializing MediaPipe model...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame: np.ndarray) -> Optional[Dict[str, float]]:
        if frame is None:
            return None

        landmarks_list, results = self.extract_hand_landmarks(frame)

        if landmarks_list:
            for _, landmarks in zip(results.multi_hand_landmarks, landmarks_list):
                try:
                    predictions = self.predict_from_landmarks(landmarks)
                    return predictions
                except Exception as e:
                    print(f"[ERROR] Prediction failed: {e}")
                    return None

        return None

    def extract_hand_landmarks(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        landmarks_list = []

        if not results.multi_hand_landmarks or not results.multi_handedness:
            print("[INFO] No hands detected.")
            return [], results

        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label

            # Extract normalized landmarks as (x, y, z)
            single_hand_landmarks = [[p.x, p.y, p.z] for p in hand_landmarks.landmark]

            if hand_label == 'Left':
                landmarks_list.append(single_hand_landmarks)
            elif hand_label == 'Right':
                # Mirror X-axis to simulate right hand
                mirrored = [[1 - p[0], p[1], p[2]] for p in single_hand_landmarks]
                landmarks_list.append(mirrored)

            # Draw landmarks for visual feedback
            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            # Only use first detected hand
            break

        return landmarks_list, results

    def predict_from_landmarks(self, landmarks: list[list[float]]) -> Optional[dict[str, float]]:
        try:
            landmarks_array = np.array(landmarks).flatten()
            landmarks_tensor = torch.tensor(landmarks_array, dtype=torch.float32).unsqueeze(0)

            with torch.no_grad():
                output = self.sign_model(landmarks_tensor)
                probabilities = torch.softmax(output, dim=1).squeeze().numpy()
                prediction = {
                    self.signs_dict.get(i, f"Sign ID {i}"): round(prob, 6)
                    for i, prob in enumerate(probabilities)
                }
            return prediction

        except Exception as e:
            print(f"[ERROR] Prediction error: {e}")
            return None

    @staticmethod
    def connect_to_database():
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models.models import Base, Sign

        print("[INFO] Connecting to the database...")
        database_path = 'sqlite:///data/gesture_ai_database.db'
        engine = create_engine(database_path)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        print("[INFO] Loading signs from the database...")
        signs_from_db = session.query(Sign).filter(Sign.languages_id == 1).order_by(Sign.id).all()
        signs_dict = {index: sign.name for index, sign in enumerate(signs_from_db)}

        # session.close()

        return session, signs_dict
