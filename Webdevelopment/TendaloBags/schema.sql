CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    email text,
    password text
);
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  bag_id INTEGER REFERENCES bags(id) ON DELETE CASCADE);
