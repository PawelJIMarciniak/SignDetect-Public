import cv2

from sign_predictor import SignPredictor
from gesture_gui import GestureGUI


class GestureApp:
    def __init__(self, camera_index=0):
        """
        The main application class responsible for integrating the predictive model, camera, and GUI.
        Supports recording, displaying results, and updating the interface in real time.
        """

        print("[INFO] Initializing resources...")

        # App state and prediction tracking
        self.app_state = {"recording": False, "single_frame_mode": False, "live_view": True}
        self.probability_tracker = {}

        # Initialize the camera
        print(f"[INFO] Initializing the camera at index {camera_index}...")
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            raise RuntimeError(f"[Error] Failed to open camera at index {camera_index}.")

        # Load prediction model
        self.sign_predictor = SignPredictor()

        # Initialize GUI
        print("[INFO] Initializing GUI components...")
        self.gui = GestureGUI(
            toggle_recording = self.toggle_recording,
            record_single_frame = self.record_single_frame,
            toggle_live_view = self.toggle_live_view,
            probability_tracker = self.probability_tracker,
            signs_dict = self.sign_predictor.signs_dict
        )

        self.video_label = self.gui.video_label

        print("[INFO] All resources initialized successfully.")

    def run(self):
        print("[INFO] Starting application...")
        self.update_frame()
        self.gui.root.mainloop()

    def update_frame(self):
        ret, frame = self.camera.read()
        frame = cv2.flip(frame, 1)

        if not ret:
            print("[WARN] Camera read failed.")
            return

        if self.app_state['recording']:
            probabilities = self.sign_predictor.process_frame(frame)

            if probabilities is not None:
                self.gui.display_predictions(probabilities)
                self.gui.last_processed_frame = frame.copy()

                if self.app_state["single_frame_mode"]:
                    self.stop_recording()
                    self.show_last_frame()

        if self.app_state["live_view"]:
            self.gui.display_image(frame)
        elif self.gui.last_processed_frame is not None:
            self.gui.display_image(self.gui.last_processed_frame)

        # Refresh Loop
        self.gui.video_label.after(10, lambda: self.update_frame())

    def start_recording(self):
        self.show_live_camera()
        self.app_state.update({"recording": True, "single_frame_mode": False})
        self.gui.record_button.config(text="Stop Recording")
        self.gui.highlight_video_frame("red")
        print("[INFO] Recording started.")

    def stop_recording(self):
        self.app_state.update({"recording": False, "single_frame_mode": False})
        self.gui.record_button.config(text="Start Recording")
        self.gui.highlight_video_frame("grey")
        print("[INFO] Recording finished.")

    def toggle_recording(self):
        if self.app_state['recording']:
            self.stop_recording()
        else:
            self.start_recording()

    def record_single_frame(self):
        self.app_state.update({"recording": True, "single_frame_mode": True})
        print("[INFO] Scheduled single-frame processing.")

    def show_live_camera(self):
        self.app_state['live_view'] = True
        self.gui.toggle_view_button.config(text="Show Last Frame")
        self.gui.highlight_video_frame("grey")

    def show_last_frame(self):
        self.stop_recording()
        self.app_state['live_view'] = False
        self.gui.toggle_view_button.config(text="Show Live Camera")
        self.gui.highlight_video_frame("yellow")

    def toggle_live_view(self):
        if self.app_state['live_view']:
            self.show_last_frame()
        else:
            self.show_live_camera()

    def cleanup_resources(self):
        print("[INFO] Releasing camera resources...")
        self.camera.release()
        print("[INFO] Closing OpenCV windows...")
        cv2.destroyAllWindows()
        print("[INFO] Resources released successfully.")
