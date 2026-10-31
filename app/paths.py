"""Kalıcı klasör yolları: web'e kapalı dosya alanı ve herkese açık görsel alanı."""
import os

PROJECT_NAME = "oryantasyon"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Konteynerde bu klasörler named volume'dur; yerelde aynı adlı klasörler proje kökünde kullanılır.
FILES_DIR = os.path.join(ROOT_DIR, PROJECT_NAME + "files")
IMAGES_DIR = os.path.join(ROOT_DIR, PROJECT_NAME + "gorseller")
LOGS_DIR = os.path.join(FILES_DIR, "logs")
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")
VERSION_PATH = os.path.join(ROOT_DIR, "version.txt")
