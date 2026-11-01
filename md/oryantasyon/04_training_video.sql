-- Eğitim ekranlarına slayt videosu: static/video/sNN.mp4 (poster sNN.jpg). Tekrar çalıştırılabilir.
-- Videolar test/build_training_videos.py ile üretilir; dosya adı ses dosyasıyla aynı sırayı izler.

BEGIN;

ALTER TABLE training_screens ADD COLUMN IF NOT EXISTS video_file VARCHAR(100);

UPDATE training_screens SET video_file = replace(audio_file, '.mp3', '.mp4') WHERE video_file IS NULL AND audio_file IS NOT NULL;

COMMIT;
