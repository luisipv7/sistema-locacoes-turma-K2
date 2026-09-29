CREATE DATABASE IF NOT EXISTS `rent-all` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `rent-all`;
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  -- O UNIQUE já está definido implicitamente aqui
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(30) NOT NULL DEFAULT 'admin',
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
-- O ALTER TABLE antigo foi removido para evitar o erro de duplicação do índice UNIQUE.
INSERT INTO users (username, hashed_password, role, is_active)
VALUES (
    'admin',
    'pbkdf2_sha256\$600000K5NUReY4sfCrQzbQLYx5jA==GpH9UhA9tooqUxeNU76S7BMUY9VzcXvIz/b1JiasbiM=',
    'admin',
    TRUE
  ) ON DUPLICATE KEY
UPDATE username = username;