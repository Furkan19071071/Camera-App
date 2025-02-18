import sys
from collections import deque
import cv2
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QGridLayout,
                             QDialog, QFormLayout, QLineEdit)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
import time


class VideoRecorder(QThread):
    finished = pyqtSignal()

    def __init__(self, idx, frame_queue, save_directory):
        super().__init__()
        self.idx = idx
        self.frame_queue = frame_queue
        self.save_directory = save_directory
        self.recording = True
        self.mutex = QMutex()

    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG codec
        file_name = f"{self.save_directory}/kamera_{self.idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        out = cv2.VideoWriter(file_name, fourcc, 30, (1280, 720))

        frame_rate = 30  # Kayıt için sabit FPS
        frame_interval = 1.0 / frame_rate
        last_frame_time = time.time()

        while self.recording:
            current_time = time.time()
            elapsed_time = current_time - last_frame_time

            if elapsed_time >= frame_interval:
                self.mutex.lock()
                if len(self.frame_queue) > 0:
                    frame = self.frame_queue.popleft()  # Kuyruktan frame al
                    out.write(frame)
                    last_frame_time = current_time  # Son frame zamanını güncelle
                self.mutex.unlock()
            else:
                # Kuyruk boşsa bekle
                time.sleep(0.001)

        out.release()
        self.finished.emit()

    def stop(self):
        self.recording = False


class CameraPreviewApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rtsp_urls = []
        self.caps = []
        self.frame_queues = [deque(maxlen=500) for _ in range(6)]  # Her kamera için bir frame kuyruğu
        self.recording_threads = [None] * 6
        self.save_directory = os.path.join(os.getcwd(), "kamera_kayitlarim")
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(16)

    def initUI(self):
        self.setWindowTitle("Kamera Ön İzleme")
        self.setGeometry(100, 100, 1200, 800)
        self.layout = QGridLayout()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout)
        self.preview_labels = []
        for i in range(6):
            label = QLabel(self)
            label.setFixedSize(300, 200)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid black;")
            label.setText("Kamera Yok")
            label.mousePressEvent = self.create_label_click_handler(i)
            self.layout.addWidget(label, i // 3, i % 3)
            self.preview_labels.append(label)

        self.add_camera_button = QPushButton("Kamera Ekle", self)
        self.add_camera_button.clicked.connect(self.add_camera)
        self.layout.addWidget(self.add_camera_button, 2, 0, 1, 3)

        self.start_recording_button = QPushButton("Video Kaydı Başlat", self)
        self.start_recording_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_recording_button, 3, 0, 1, 2)

        self.stop_recording_button = QPushButton("Video Kaydı Durdur", self)
        self.stop_recording_button.clicked.connect(self.stop_recording)
        self.layout.addWidget(self.stop_recording_button, 3, 2, 1, 1)

    def create_label_click_handler(self, idx):
        def label_click_event(event):
            if idx < len(self.rtsp_urls):
                self.open_camera_view(idx)

        return label_click_event

    def update_frames(self):
        for idx, cap in enumerate(self.caps):
            if cap:
                ret, frame = cap.read()
                if ret:
                    frame_resized = cv2.resize(frame, (1280, 720))
                    self.frame_queues[idx].append(frame_resized)  # Frame'i kuyruğa ekliyoruz

                    # Ön izleme için gösterecek görüntüyü güncelle
                    rgb_image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    qt_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qt_image)
                    scaled_pixmap = pixmap.scaled(self.preview_labels[idx].size(), Qt.KeepAspectRatio)
                    self.preview_labels[idx].setPixmap(scaled_pixmap)

    def add_camera(self):
        dialog = CameraDialog(self)
        if dialog.exec_():
            rtsp_url = dialog.get_url()
            if rtsp_url:
                self.rtsp_urls.append(rtsp_url)
                cap = cv2.VideoCapture(rtsp_url)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.caps.append(cap)
                self.update_frames()

    def open_camera_view(self, cam_idx):
        self.camera_view = CameraApp(self.rtsp_urls[cam_idx])
        self.camera_view.show()

    def start_recording(self):
        for idx, frame_queue in enumerate(self.frame_queues):
            if len(self.caps) > idx and not self.recording_threads[idx]:
                # Kuyruğu temizle
                frame_queue.clear()
                thread = VideoRecorder(idx, frame_queue, self.save_directory)
                self.recording_threads[idx] = thread
                thread.start()

    def stop_recording(self):
        for idx, thread in enumerate(self.recording_threads):
            if thread:  # Yalnızca kayıtta olan kameraları durdur
                thread.stop()
                thread.wait()  # İş parçacığı işini bitirene kadar bekle
                self.recording_threads[idx] = None

    def closeEvent(self, event):
        self.stop_recording()
        for cap in self.caps:
            cap.release()
        event.accept()


class CameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Kamera Ekle")
        self.setGeometry(200, 200, 300, 150)
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.url_input = QLineEdit(self)
        self.layout.addRow("RTSP URL:", self.url_input)
        self.button_box = QVBoxLayout()
        self.ok_button = QPushButton("Ekle", self)
        self.cancel_button = QPushButton("İptal", self)
        self.button_box.addWidget(self.ok_button)
        self.button_box.addWidget(self.cancel_button)
        self.layout.addRow(self.button_box)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_url(self):
        return self.url_input.text()


class CameraApp(QMainWindow):
    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(self.rtsp_url)
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)  # 33.3 ms 30 fps için

    def initUI(self):
        self.setWindowTitle("Kamera Görüntüsü")
        self.setGeometry(100, 100, 900, 700)
        self.layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout)
        self.label = QLabel(self)
        self.layout.addWidget(self.label)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.label.size(), Qt.KeepAspectRatio)
            self.label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraPreviewApp()
    window.show()
    sys.exit(app.exec_())
