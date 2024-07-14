import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="stock.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            quantity INTEGER NOT NULL,
                            purchase_price REAL NOT NULL,
                            sale_price REAL NOT NULL,
                            total_purchase_value REAL NOT NULL,
                            total_sale_value REAL NOT NULL,
                            gain REAL NOT NULL,
                            loss REAL NOT NULL,
                            last_updated TEXT NOT NULL)''')
        self.conn.commit()

    def add_product(self, name, quantity, purchase_price, sale_price):
        total_purchase_value = quantity * purchase_price
        self.cursor.execute('''INSERT INTO stock (name, quantity, purchase_price, sale_price, total_purchase_value, total_sale_value, gain, loss, last_updated)
                               VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)''',
                            (name, quantity, purchase_price, sale_price, total_purchase_value, 0, datetime.now()))
        self.conn.commit()

    def update_product(self, name, quantity, purchase_price, sale_price):
        self.cursor.execute('''UPDATE stock
                               SET quantity = ?, purchase_price = ?, sale_price = ?, total_purchase_value = quantity * ?, last_updated = ?
                               WHERE name = ?''',
                            (quantity, purchase_price, sale_price, purchase_price, datetime.now(), name))
        self.conn.commit()

    def delete_product(self, name):
        self.cursor.execute('DELETE FROM stock WHERE name = ?', (name,))
        self.conn.commit()

    def add_stock(self, name, quantity):
        self.cursor.execute('''UPDATE stock
                               SET quantity = quantity + ?, total_purchase_value = total_purchase_value + ? * purchase_price, last_updated = ?
                               WHERE name = ?''',
                            (quantity, quantity, datetime.now(), name))
        self.conn.commit()

    def remove_stock(self, name, quantity):
        self.cursor.execute('''SELECT quantity, sale_price, total_sale_value, gain, loss FROM stock WHERE name = ?''', (name,))
        result = self.cursor.fetchone()
        if result and result[0] >= quantity:
            new_quantity = result[0] - quantity
            new_sale_value = result[2] + quantity * result[1]
            gain = new_sale_value - result[0] * result[1]
            loss = 0 if gain > 0 else -gain
            self.cursor.execute('''UPDATE stock
                                   SET quantity = ?, total_sale_value = ?, gain = ?, loss = ?, last_updated = ?
                                   WHERE name = ?''',
                                (new_quantity, new_sale_value, max(gain, 0), max(loss, 0), datetime.now(), name))
            self.conn.commit()
            return True
        return False

    def get_all_products(self):
        self.cursor.execute('SELECT * FROM stock')
        return self.cursor.fetchall()
    
    def export_to_csv(self, filename):
        import csv
        self.cursor.execute('SELECT * FROM stock')
        rows = self.cursor.fetchall()
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([i[0] for i in self.cursor.description])  # Write headers
            writer.writerows(rows)

    def import_from_csv(self, filename):
        import csv
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip the header row
            self.cursor.executemany('''INSERT INTO stock (id, name, quantity, purchase_price, sale_price, total_purchase_value, total_sale_value, gain, loss, last_updated)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', reader)
        self.conn.commit()
