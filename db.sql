CREATE TABLE users (
  id SERIAL PRIMARY KEY NOT NULL
  email TEXT NOT NULL,
  username TEXT NOT NULL,
  hash TEXT NOT NULL,
  profile_photo_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  bio TEXT,
  confirmed INTEGER DEFAULT 0,
  token TEX
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY NOT NULL,
  author_id INTEGER NOT NULL,
  author_username TEXT NOT NULL,
  photo_URL TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_author
    FOREIGN KEY(author_id)
      REFERENCES users(id)
);

-- To rename a table
ALTER TABLE posts RENAME TO posts_old;
-- Then it can be created again