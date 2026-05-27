CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_name TEXT UNIQUE NOT NULL,
    folder_path TEXT NOT NULL,
    folder_fingerprint TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',

    title TEXT,
    description TEXT,
    category TEXT,
    brand TEXT,
    color TEXT,
    material TEXT,
    style TEXT,
    gender TEXT,
    size_guess TEXT,

    buy_price REAL DEFAULT 0,
    shipping_cost REAL DEFAULT 0,
    listing_price REAL DEFAULT 0,
    sold_price REAL DEFAULT 0,
    profit REAL DEFAULT 0,

    marketplace TEXT DEFAULT 'vinted',
    listing_url TEXT,
    sold_status TEXT DEFAULT 'unsold',

    error TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS item_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    processed_image_path TEXT,
    image_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS vision_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    source TEXT,
    category TEXT,
    brand TEXT,
    colors TEXT,
    pattern TEXT,
    material TEXT,
    style TEXT,
    gender TEXT,
    keywords TEXT,
    confidence REAL,
    raw_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS pricing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    source TEXT,
    base_price REAL,
    final_price REAL,
    confidence REAL,
    details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
