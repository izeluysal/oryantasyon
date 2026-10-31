-- Eğitim şeması: platform geneli içerik (ekranlar, sorular) ve işletmeye bağlı öğrenme kayıtları.
-- Elle çalıştırılır: python test/migration_uygula.py md/oryantasyon/02_training_schema.sql
-- İçerik tabloları (training_screens, training_questions) tüm işletmelerde ortak referans veridir; kiracı verisi
-- değildir ve bu yüzden business_id taşımaz. Öğrenme kayıtları (progress, answers) işletmeye bağlıdır.

BEGIN;

CREATE TABLE IF NOT EXISTS training_screens (
    training_screen_id SERIAL PRIMARY KEY,
    screen_code VARCHAR(20) NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    bullets JSONB NOT NULL DEFAULT '[]'::jsonb,
    note TEXT NOT NULL DEFAULT '',
    table_data JSONB,
    voice_text TEXT NOT NULL DEFAULT '',
    audio_file VARCHAR(100),
    coins INTEGER NOT NULL DEFAULT 0,
    bonus_coins INTEGER NOT NULL DEFAULT 0,
    timer_seconds INTEGER NOT NULL DEFAULT 0,
    is_critical BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL,
    CONSTRAINT chk_training_screens_coins CHECK (coins >= 0 AND bonus_coins >= 0 AND timer_seconds >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_training_screens_screen_code ON training_screens (screen_code);
CREATE INDEX IF NOT EXISTS idx_training_screens_sort_order ON training_screens (sort_order);

CREATE TABLE IF NOT EXISTS training_questions (
    training_question_id SERIAL PRIMARY KEY,
    training_screen_id INTEGER NOT NULL REFERENCES training_screens (training_screen_id) ON DELETE RESTRICT,
    sort_order INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_index INTEGER NOT NULL,
    explanation TEXT NOT NULL DEFAULT '',
    coins INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT chk_training_questions_coins CHECK (coins >= 0),
    CONSTRAINT chk_training_questions_correct_index CHECK (correct_index >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_training_questions_screen_sort
    ON training_questions (training_screen_id, sort_order);

-- Ekran bazlı ilerleme: ilk görüntüleme (started_at) zamanlı ekranlarda süreyi belirler.
CREATE TABLE IF NOT EXISTS training_progress (
    training_progress_id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses (business_id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE RESTRICT,
    training_screen_id INTEGER NOT NULL REFERENCES training_screens (training_screen_id) ON DELETE RESTRICT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    bonus_coins INTEGER NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_training_progress_user_screen ON training_progress (user_id, training_screen_id);
CREATE INDEX IF NOT EXISTS idx_training_progress_business_id ON training_progress (business_id);

-- Soru bazlı yanıt kaydı: kullanıcı başına tek satır; deneme sayısı ve kazanılan coin burada tutulur.
CREATE TABLE IF NOT EXISTS training_answers (
    training_answer_id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses (business_id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE RESTRICT,
    training_question_id INTEGER NOT NULL REFERENCES training_questions (training_question_id) ON DELETE RESTRICT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    is_first_try BOOLEAN NOT NULL DEFAULT FALSE,
    coins_earned INTEGER NOT NULL DEFAULT 0,
    answered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_training_answers_user_question ON training_answers (user_id, training_question_id);
CREATE INDEX IF NOT EXISTS idx_training_answers_business_id ON training_answers (business_id);

COMMIT;
