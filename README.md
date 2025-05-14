# 🧠 SignDetect

**SignDetect** is a Python desktop app that recognizes **ASL (American Sign Language)** alphabet signs from camera images in real time.

---

⚠️ This is a public demo version of the original SignDetect project.  
It contains the full working code, but omits test files, database content, and commit history for clarity and privacy.

---

## 📸 Screenshots

<img alt="demo" src="media\main_frame.png"/>
<img alt="demo" src="media\probability_over_time_graph.png"/>

---

## ✨ Main features

- 🎯 Sign language recognition from camera image
- 🧠 Using PyTorch model trained on hand points (detected by MediaPipe)
- 📊 Dynamic graph with real-time classification probability
- 🎛️ Interactive GUI with buttons to control view, recording and work modes
- 🌗 Changing themes (dark, light, system)

---

## 👉 Using the App

- **Start Recording/Stop Recording** – Starts and Ends the gesture checking process.
- **Check Single Frame** – Analyzes a single frame.
- **Show Last Frame/Show Live Camera** – Toggles between a live camera image and a photo of the last checked frame.
- **Theme Selector** – Allows you to select a theme (Dark/Light/System).
- **Show/Hide Plot** – Toggles a graph showing the probability of characters.

---

## 🛠️ How does the app work?

1. In processing mode, a new frame from the camera is captured every 10 ms.
2. The characteristic points of the hand are extracted from each frame (via MediaPipe)
3. The points are passed to the PyTorch model, which predicts the sign
4. The results are:
- displayed in a table with probabilities
- plotted on a graph (time / sign)

---

## ✅ Requirements

- Python: 3.11.11 (another interpreter may cause problems with some libraries, e.g. MediaPipe)
- OS: Windows 11 (tested), should also work on Linux/macOS, but not tested
- Camera: Required for the app to work (video recording device)

---

## 🚀 How to run?

### 1. Clone the repository:

```bash
git clone https://github.com/PawelJIMarciniak/SignDetect-Public
cd SignDetect-Public
```

### 2. Create a virtual environment (optional)

```bash
python -m venv venv
source venv/bin/activate # or .\venv\Scripts\activate on Windows
```

### 3. Install requirements:

```bash
pip install -r requirements.txt
```

### 4. Run the application:

```bash
python main.py
```

---

## 🧠 Model

The sign classification model is built with **PyTorch** and trained using **3D hand landmarks** (21 keypoints × 3 coordinates) detected by **MediaPipe Hands**.

### 🗃️ Dataset

- Collected using camera input and stored in a local SQLite database (`gesture_ai_database.db`)
- Each sample consists of **63 features**: (x, y, z) coordinates of 21 hand keypoints
- Signs are labeled and stored in the `Sign` table, associated with `Video` and `FrameCoordinate` entries

### 🧠 Architecture

A simple **fully-connected feedforward neural network (MLP)**:

- `Input layer`: 63 neurons
- `Hidden layers`: 128 → 64 neurons (ReLU activations)
- `Output layer`: one neuron per class (softmax applied during evaluation)

### 📊 Output

- Model predicts one of **29 classes**: 26 ASL alphabet signs (**A–Z**) plus three extra symbols:
  - `SPACE` (word separator)
  - `DEL` (delete/backspace)
  - `NOTHING` (not used because the program does not show empty predictions)

### 📈 Training

- Data split: 50% train / 50% test (using `train_test_split`)
- Loss: `CrossEntropyLoss`
- Optimizer: `Adam`, learning rate = 0.001
- Epochs: 800
- Accuracy: ~99% on validation set

Model weights are saved to `model_weights.pth` after training.

The training script and model definition can be found in `models/model_pytorch.py`.

---

## 📫 Contact

If you have questions or want to get in touch:<br>
[pawelj.i.marciniak@gmail.com](mailto:pawelj.i.marciniak@gmail.com) <br>
[LinkedIn](https://www.linkedin.com/in/pawel-marciniak-39a53b298) | [GitHub](https://github.com/PawelJIMarciniak)