import sqlite3

db_path = 'd:/agenda_eventos_ols/backend/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

vehicles = [
    ('Van – TEC0I38', 1, ''),
    ('Van – TEC0I37', 1, ''),
    ('Ônix – TUC2D95', 1, ''),
    ('Ônix – TTQ5J61', 1, ''),
    ('Fiorino – RJO3D88', 1, '')
]

for vehicle in vehicles:
    cursor.execute("SELECT id FROM schedules_vehicle WHERE name=?", (vehicle[0],))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO schedules_vehicle (name, is_active, source_id) VALUES (?, ?, ?)", vehicle)

conn.commit()
conn.close()
print("Vehicles added to DB successfully.")
