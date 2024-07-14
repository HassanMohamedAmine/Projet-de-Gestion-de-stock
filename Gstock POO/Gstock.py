import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importation pour les styles ttk
import csv
import os

class Product:
    def __init__(self, nom, quantite, prix_achat_unitaire, prix_vente_unitaire, valeur_totale_achat, valeur_totale_vente, gain_total, perte_totale):
        self.nom = nom
        self.quantite = quantite
        self.prix_achat_unitaire = prix_achat_unitaire
        self.prix_vente_unitaire = prix_vente_unitaire
        self.valeur_totale_achat = valeur_totale_achat
        self.valeur_totale_vente = valeur_totale_vente
        self.gain_total = gain_total
        self.perte_totale = perte_totale

    def add_stock(self, quantite):
        self.quantite += quantite
        self.valeur_totale_achat += quantite * self.prix_achat_unitaire
        self.calculate_gain_loss()

    def remove_stock(self, quantite):
        if self.quantite >= quantite:
            self.quantite -= quantite
            self.valeur_totale_vente += quantite * self.prix_vente_unitaire
            self.calculate_gain_loss()
            return True
        else:
            return False

    def calculate_gain_loss(self):
        if self.valeur_totale_vente >= self.valeur_totale_achat:
            self.gain_total = self.valeur_totale_vente - self.valeur_totale_achat
            self.perte_totale = 0
        else:
            self.perte_totale = self.valeur_totale_achat - self.valeur_totale_vente
            self.gain_total = 0

class StockController:
    def __init__(self):
        self.stock = {}
        self.conn = sqlite3.connect('stock.db')
        self.create_tables()
        self.load_data_from_db()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                nom TEXT PRIMARY KEY,
                quantite INTEGER,
                prix_achat_unitaire REAL,
                prix_vente_unitaire REAL,
                valeur_totale_achat REAL,
                valeur_totale_vente REAL,
                gain_total REAL,
                perte_totale REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_produit TEXT,
                quantite INTEGER,
                prix_vente_unitaire REAL,
                valeur_totale_vente REAL,
                FOREIGN KEY (nom_produit) REFERENCES produits (nom)
            )
        ''')
        self.conn.commit()

    def add_product(self, nom, quantite, prix_achat_unitaire, prix_vente_unitaire):
        if nom and quantite.isdigit() and int(quantite) > 0 and self.is_float(prix_achat_unitaire) and self.is_float(prix_vente_unitaire):
            product = Product(
                nom, int(quantite), float(prix_achat_unitaire), float(prix_vente_unitaire), 
                int(quantite) * float(prix_achat_unitaire), 0, 0, 0
            )
            self.stock[nom] = product
            self.save_product_to_db(product)
            self.export_to_csv()
            return True
        else:
            return False

    def remove_product(self, nom):
        if nom in self.stock:
            del self.stock[nom]
            self.delete_product_from_db(nom)
            self.export_to_csv()
            return True
        else:
            return False

    def add_stock(self, nom, quantite):
        if nom in self.stock and quantite.isdigit() and int(quantite) > 0:
            product = self.stock[nom]
            product.add_stock(int(quantite))
            self.update_product_in_db(product)
            self.export_to_csv()
            return True
        else:
            return False

    def remove_stock(self, nom, quantite):
        if nom in self.stock and quantite.isdigit() and int(quantite) > 0:
            product = self.stock[nom]
            if product.remove_stock(int(quantite)):
                self.update_product_in_db(product)
                self.save_sale_to_db(nom, int(quantite), product.prix_vente_unitaire)
                self.export_to_csv()
                return True
            else:
                return False
        else:
            return False

    def save_sale_to_db(self, nom, quantite, prix_vente_unitaire):
        cursor = self.conn.cursor()
        valeur_totale_vente = quantite * prix_vente_unitaire
        cursor.execute('''
            INSERT INTO ventes (nom_produit, quantite, prix_vente_unitaire, valeur_totale_vente)
            VALUES (?, ?, ?, ?)
        ''', (nom, quantite, prix_vente_unitaire, valeur_totale_vente))
        self.conn.commit()

    def get_stock(self):
        return {
            nom: {
                "quantite": product.quantite,
                "prix_achat_unitaire": product.prix_achat_unitaire,
                "prix_vente_unitaire": product.prix_vente_unitaire,
                "valeur_totale_achat": product.valeur_totale_achat,
                "valeur_totale_vente": product.valeur_totale_vente,
                "gain_total": product.gain_total,
                "perte_totale": product.perte_totale
            } for nom, product in self.stock.items()
        }

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def load_data_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM produits')
        rows = cursor.fetchall()
        for row in rows:
            product = Product(*row)
            self.stock[product.nom] = product

    def save_product_to_db(self, product):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO produits (nom, quantite, prix_achat_unitaire, prix_vente_unitaire, valeur_totale_achat, valeur_totale_vente, gain_total, perte_totale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product.nom, product.quantite, product.prix_achat_unitaire, product.prix_vente_unitaire, 
            product.valeur_totale_achat, product.valeur_totale_vente, product.gain_total, product.perte_totale
        ))
        self.conn.commit()

    def update_product_in_db(self, product):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE produits
            SET quantite = ?, prix_achat_unitaire = ?, prix_vente_unitaire = ?, valeur_totale_achat = ?, valeur_totale_vente = ?, gain_total = ?, perte_totale = ?
            WHERE nom = ?
        ''', (
            product.quantite, product.prix_achat_unitaire, product.prix_vente_unitaire, product.valeur_totale_achat, 
            product.valeur_totale_vente, product.gain_total, product.perte_totale, product.nom
        ))
        self.conn.commit()

    def delete_product_from_db(self, nom):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM produits WHERE nom = ?', (nom,))
        self.conn.commit()

    def export_to_csv(self):
        file_path = "stock_data.csv"
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Nom', 'Quantité', 'Prix d\'achat unitaire', 'Prix de vente unitaire', 
                'Valeur totale d\'achat', 'Valeur totale de vente', 'Gain total', 'Perte totale'
            ])
            for product in self.stock.values():
                writer.writerow([
                    product.nom, product.quantite, product.prix_achat_unitaire, product.prix_vente_unitaire,
                    product.valeur_totale_achat, product.valeur_totale_vente, product.gain_total, product.perte_totale
                ])
        messagebox.showinfo("Exportation CSV", f"Données exportées avec succès vers {file_path}")

class MainView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Gestion de Stock")

        # Style pour les widgets ttk
        style = ttk.Style(self)
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))

        # Ajout de couleurs aux widgets
        style.map('TButton',
                  foreground=[('pressed', 'black'), ('active', 'black')],
                  background=[('pressed', '!disabled', 'white'), ('active', 'white')])
        style.map('TEntry',
                  foreground=[('active', 'black')],
                  background=[('active', 'white')])

        # Interface utilisateur
        self.create_widgets()

    def create_widgets(self):
        self.label_produit = ttk.Label(self, text="Nom du produit :")
        self.label_produit.pack(pady=10)

        self.entry_produit = ttk.Entry(self, width=50, style='TEntry')
        self.entry_produit.pack()

        self.label_quantite = ttk.Label(self, text="Quantité :")
        self.label_quantite.pack()

        self.entry_quantite = ttk.Entry(self, width=50, style='TEntry')
        self.entry_quantite.pack()

        self.label_purchase_price = ttk.Label(self, text="Prix d'achat unitaire :")
        self.label_purchase_price.pack()

        self.entry_purchase_price = ttk.Entry(self, width=50, style='TEntry')
        self.entry_purchase_price.pack()

        self.label_sale_price = ttk.Label(self, text="Prix de vente unitaire :")
        self.label_sale_price.pack()

        self.entry_sale_price = ttk.Entry(self, width=50, style='TEntry')
        self.entry_sale_price.pack()

        self.frame_boutons = ttk.Frame(self)
        self.frame_boutons.pack(pady=10)

        self.btn_ajouter = ttk.Button(self.frame_boutons, text="Ajouter Produit", command=self.ajouter_produit, style='TButton')
        self.btn_ajouter.pack(side=tk.LEFT, padx=5)

        self.btn_entrer = ttk.Button(self.frame_boutons, text="Entrée Stock", command=self.entrer_stock, style='TButton')
        self.btn_entrer.pack(side=tk.LEFT, padx=5)

        self.btn_sortir = ttk.Button(self.frame_boutons, text="Sortie Stock", command=self.sortir_stock, style='TButton')
        self.btn_sortir.pack(side=tk.LEFT, padx=5)

        self.btn_supprimer = ttk.Button(self.frame_boutons, text="Supprimer Produit", command=self.supprimer_produit, style='TButton')
        self.btn_supprimer.pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(self, width=80)
        self.listbox.pack()

        self.update_listbox()

    def ajouter_produit(self):
        produit = self.entry_produit.get().strip()
        quantite = self.entry_quantite.get().strip()
        purchase_price = self.entry_purchase_price.get().strip()
        sale_price = self.entry_sale_price.get().strip()

        if self.controller.add_product(produit, quantite, purchase_price, sale_price):
            self.update_listbox()
            self.clear_entries()
        else:
            messagebox.showerror("Erreur", "Veuillez saisir des informations valides pour le produit.")

    def supprimer_produit(self):
        try:
            produit = self.listbox.get(self.listbox.curselection())
            produit_nom = produit.split(" - ")[0]

            if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le produit '{produit_nom}' ?"):
                if self.controller.remove_product(produit_nom):
                    self.update_listbox()
        except tk.TclError:
            messagebox.showerror("Erreur", "Aucun produit sélectionné.")

    def entrer_stock(self):
        produit = self.entry_produit.get().strip()
        quantite = self.entry_quantite.get().strip()

        if self.controller.add_stock(produit, quantite):
            self.update_listbox()
            self.entry_quantite.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Veuillez saisir des informations valides pour l'entrée de stock.")

    def sortir_stock(self):
        produit = self.entry_produit.get().strip()
        quantite = self.entry_quantite.get().strip()

        if self.controller.remove_stock(produit, quantite):
            self.update_listbox()
            self.entry_quantite.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Veuillez saisir des informations valides pour la sortie de stock.")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for produit, details in self.controller.get_stock().items():
            gain_loss_info = f"Gain: {details['gain_total']}" if details['gain_total'] > 0 else f"Perte: {details['perte_totale']}"
            self.listbox.insert(tk.END, 
                f"{produit} - Quantité: {details['quantite']} - Prix d'achat unitaire: {details['prix_achat_unitaire']} - Prix de vente unitaire: {details['prix_vente_unitaire']} - Valeur d'achat totale: {details['valeur_totale_achat']} - Valeur de vente totale: {details['valeur_totale_vente']} - {gain_loss_info}"
            )

    def clear_entries(self):
        self.entry_produit.delete(0, tk.END)
        self.entry_quantite.delete(0, tk.END)
        self.entry_purchase_price.delete(0, tk.END)
        self.entry_sale_price.delete(0, tk.END)

if __name__ == "__main__":
    controller = StockController()
    app = MainView(controller)
    app.mainloop()
