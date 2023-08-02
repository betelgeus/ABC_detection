"""
Интеграционное тестирование с реальной моделью
"""

import os
import torch
from fastapi.testclient import TestClient
from ultralytics import YOLO

import main as main
from constants import global_config


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
UPLOAD_DIR = global_config.TEST_DATA_DIR
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
image_path = os.path.join(UPLOAD_DIR, "1690920920325.png")
MODEL_DIR = global_config.TEST_MODEL_DIR
MODEL_DIR = os.path.abspath(MODEL_DIR)
model = YOLO(MODEL_DIR)


def test_results_processing():
    results = model(image_path, device=DEVICE)
    letter_index = 0
    assert main.results_processing(results, letter_index) == False
    letter_index = 14
    assert main.results_processing(results, letter_index) == True


def test_predict():
    letter_index = 0
    assert main.predict(image_path, letter_index) == False
    letter_index = 14
    assert main.predict(image_path, letter_index) == True


# Функция проверяет полный цикл работы main
def test_upload_image():
    client = TestClient(main.app)
    try:
        # Загружаем тестовый файл и данные формы
        with open(image_path, "rb") as f:
            files = {"file": ("1690920920325_1.png", f, "image/png")}
            data = {"letter_index": "0"}

            # Отправляем POST-запрос на сервер
            response = client.post("/upload/", files=files, data=data)

        # Проверяем, что запрос успешно обработан
        assert response.status_code == 200

        # Проверяем, что результат предсказания успешен
        assert response.json() == {"result": False}

        # Проверяем, что файл успешно сохранен
        assert os.path.exists(os.path.join(UPLOAD_DIR, "1690920920325_1.png"))
    finally:
        os.remove(os.path.join(UPLOAD_DIR, "1690920920325_1.png"))

    try:
        with open(image_path, "rb") as f:
            files = {"file": ("1690920920325_1.png", f, "image/png")}
            data = {"letter_index": "14"}

            response = client.post("/upload/", files=files, data=data)

        assert response.status_code == 200
        assert response.json() == {"result": True}
        assert os.path.exists(os.path.join(UPLOAD_DIR, "1690920920325_1.png"))
    finally:
        os.remove(os.path.join(UPLOAD_DIR, "1690920920325_1.png"))
