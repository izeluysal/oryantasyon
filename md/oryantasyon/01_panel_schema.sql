-- Panel (platform) şeması: işletmeler, kullanıcılar, ayarlar, loglar, giriş koruması.
-- Elle çalıştırılır: python test/migration_uygula.py md/oryantasyon/01_panel_schema.sql
-- Numaralı dosyalar geriye dönük düzenlenmez; değişiklik yeni numaralı dosya olarak eklenir.

BEGIN;

CREATE TABLE IF NOT EXISTS businesses (
    business_id SERIAL PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    publish_url VARCHAR(255) NOT NULL,
    business_admin_user_id INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_businesses_publish_url ON businesses (lower(publish_url)) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_businesses_is_deleted ON businesses (is_deleted);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses (business_id) ON DELETE RESTRICT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    theme VARCHAR(10) NOT NULL DEFAULT 'light',
    language VARCHAR(2) NOT NULL DEFAULT 'tr',
    sidebar_collapsed BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_users_role CHECK (role IN ('yonetici', 'isletme_yoneticisi', 'isletme_kullanicisi', 'denetim')),
    CONSTRAINT chk_users_theme CHECK (theme IN ('light', 'dark')),
    CONSTRAINT chk_users_language CHECK (language IN ('tr')),
    -- Rolün kapsamı veritabanı kısıtıyla zorlanır: kapsamsız işletme rolü tüm işletmeleri görürdü.
    CONSTRAINT chk_users_scope CHECK (
        (role = 'yonetici' AND business_id IS NULL) OR
        (role <> 'yonetici' AND business_id IS NOT NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email ON users (lower(email)) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_business_id ON users (business_id);
CREATE INDEX IF NOT EXISTS idx_users_is_deleted ON users (is_deleted);

-- Tekrar çalıştırılabilir olması için kısıt yalnızca yoksa eklenir (businesses ile users birbirine bağlıdır).
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_businesses_business_admin_user_id') THEN
        ALTER TABLE businesses
            ADD CONSTRAINT fk_businesses_business_admin_user_id
            FOREIGN KEY (business_admin_user_id) REFERENCES users (user_id) ON DELETE SET NULL;
    END IF;
END
$$;

-- Çalışma zamanı ayarları: platform satırı (business_id NULL) varsayılandır, işletme satırı onun yerine geçer.
CREATE TABLE IF NOT EXISTS config (
    config_id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL DEFAULT '{}'::jsonb,
    business_id INTEGER REFERENCES businesses (business_id) ON DELETE RESTRICT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_config_setting_key_platform ON config (setting_key) WHERE business_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_config_setting_key_business
    ON config (setting_key, business_id) WHERE business_id IS NOT NULL;

-- Aktivite logu: yalnızca-ekleme tablosu, is_deleted taşımaz. Retention: 2 yıl (CSV'ye aktarılıp tablodan kaldırılır).
CREATE TABLE IF NOT EXISTS userslogs (
    userslog_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (user_id) ON DELETE SET NULL,
    business_id INTEGER REFERENCES businesses (business_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    detail TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_userslogs_created_at ON userslogs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_userslogs_business_id ON userslogs (business_id);
CREATE INDEX IF NOT EXISTS idx_userslogs_user_id ON userslogs (user_id);

-- Uygulama hataları (yalnızca-ekleme).
CREATE TABLE IF NOT EXISTS error_log (
    error_log_id BIGSERIAL PRIMARY KEY,
    error_code VARCHAR(10) NOT NULL,
    url VARCHAR(500),
    reason TEXT,
    ip_address VARCHAR(45),
    user_id INTEGER REFERENCES users (user_id) ON DELETE SET NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_error_log_created_at ON error_log (created_at DESC);

-- Başarısız giriş denemeleri: IP bazlı sayaç; e-posta için FK yoktur (kayıtsız adres de denenebilir).
CREATE TABLE IF NOT EXISTS login_attempts (
    login_attempt_id BIGSERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    email VARCHAR(255),
    reason VARCHAR(30) NOT NULL,
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_created_at ON login_attempts (ip_address, created_at DESC);

-- IP blokları: süresi dolan kayıt silinmez, blocked_until geçmişte kalır.
CREATE TABLE IF NOT EXISTS ip_blocks (
    ip_block_id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    blocked_until TIMESTAMPTZ NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    is_notified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ip_blocks_ip_blocked_until ON ip_blocks (ip_address, blocked_until DESC);

COMMIT;
