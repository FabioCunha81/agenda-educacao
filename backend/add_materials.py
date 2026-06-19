import sqlite3

db_path = 'd:/agenda_eventos_ols/backend/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

materials = [
    ('Ventarolas', 1, ''),
    ('Adesivos', 1, ''),
    ('Folders', 1, ''),
    ('Revistinhas educativas', 1, '')
]

for mat in materials:
    # Check if exists to avoid duplicates
    cursor.execute("SELECT id FROM schedules_kit WHERE name=?", (mat[0],))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO schedules_kit (name, is_active, source_id) VALUES (?, ?, ?)", mat)

conn.commit()
conn.close()
print("Materials added to DB successfully.")
