import tkinter as tk
from tkinter import messagebox, filedialog
from database import Database

class MainView(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("Gestion de Stock")

        # Interface utilisateur
        self.label_produit = tk.Label(self, text="Nom du produit :")
        self.label_produit.pack(pady=10)

        self.entry_produit = tk.Entry(self, width=50)
        self.entry_produit.pack()

        self.label_quantite = tk.Label(self, text="Quantité :")
        self.label_quantite.pack()

        self.entry_quantite = tk.Entry(self, width=50)
        self.entry_quantite.pack()

        self.label_purchase_price = tk.Label(self, text="Prix d'achat unitaire :")
        self.label_purchase_price.pack()

        self.entry_purchase_price = tk.Entry(self, width=50)
        self.entry_purchase_price.pack()

        self.label_sale_price = tk.Label(self, text="Prix de vente unitaire :")
        self.label_sale_price.pack()

        self.entry_sale_price = tk.Entry(self, width=50)
        self.entry_sale_price.pack()

        self.frame_boutons = tk.Frame(self)
        self.frame_boutons.pack(pady=10)

        self.btn_ajouter = tk.Button(self.frame_boutons, text="Ajouter Produit", command=self.ajouter_produit)
        self.btn_ajouter.pack(side=tk.LEFT, padx=5)

        self.btn_entrer = tk.Button(self.frame_boutons, text="Entrée Stock", command=self.entrer_stock)
        self.btn_entrer.pack(side=tk.LEFT, padx=5)

        self.btn_sortir = tk.Button(self.frame_boutons, text="Sortie Stock", command=self.sortir_stock)
        self.btn_sortir.pack(side=tk.LEFT, padx=5)

        self.btn_supprimer = tk.Button(self.frame_boutons, text="Supprimer Produit", command=self.supprimer_produit)
        self.btn_supprimer.pack(side=tk.LEFT, padx=5)

        self.btn_export_csv = tk.Button(self.frame_boutons, text="Exporter CSV", command=self.export_csv)
        self.btn_export_csv.pack(side=tk.LEFT, padx=5)

        self.btn_import_csv = tk.Button(self.frame_boutons, text="Importer CSV", command=self.import_csv)
        self.btn_import_csv.pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(self, width=80)
        self.listbox.pack()

        self.update_listbox()

    def ajouter_produit(self):
        produit = self.entry_produit.get().strip()
        quantite = self.entry_quantite.get().strip()
        purchase_price = self.entry_purchase_price.get().strip()
        sale_price = self.entry_sale_price.get().strip()

        if quantite.isdigit() and float(purchase_price) > 0 and float(sale_price) > 0:
            self.db.add_product(produit, int(quantite), float(purchase_price), float(sale_price))
            self.update_listbox()
            self.entry_produit.delete(0, tk.END)
            self.entry_quantite.delete(0, tk.END)
            self.entry_purchase_price.delete(0, tk.END)
            self.entry_sale_price.delete(0, tk.END)
            messagebox.showinfo("Ajout réussi", f"Produit '{produit}' ajouté au stock avec une quantité de {quantite}.")
        else:
            messagebox.showerror("Erreur", "Veuillez saisir des informations valides pour le produit.")

    def supprimer_produit(self):
        try:
            produit = self.listbox.get(self.listbox.curselection())
            produit_name = produit.split(" - ")[0]

            if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le produit '{produit_name}' ?"):
                self.db.delete_product(produit_name)
                self.update_listbox()
                messagebox.showinfo("Suppression réussie", f"Produit '{produit_name}' supprimé du stock.")
        except tk.TclError:
            messagebox.showerror("Erreur", "Aucun produit sélectionné.")

    def entrer_stock(self):
        produit = self.entry_produit.get().strip()
        quantite = self.entry_quantite.get().strip()

        if quantite.isdigit() and int(quantite) > 0:
            self.db.add_stock(produit, int(quantite))
            self.update_listbox()
            self.entry_quantite.delete(0, tk.END)
            messagebox.showinfo("Entrée réussie", f"{quantite} unités ajoutées au produit '{produit}'.")
        else:
            messagebox.showerror("Erreur", "Veuillez saisir des informations valides pour l'entrée de stock.")

    def sortir_stock(self):
        produit = self.entry_produit.get().strip()
        quantite = self.entry_quantite.get().strip()

        if quantite.isdigit() and int(quantite) > 0:
            if self.db.remove_stock(produit, int(quantite)):
                self.update_listbox()
                self.entry_quantite.delete(0, tk.END)
                messagebox.showinfo("Sortie réussie", f"{quantite} unités retirées du produit '{produit}'.")
            else:
                messagebox.showerror("Erreur", f"Quantité insuffisante pour le produit '{produit}'.")
        else:
            messagebox.showerror("Erreur", "Veuillez saisir des informations valides pour la sortie de stock.")

    def export_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            self.db.export_to_csv(filename)
            messagebox.showinfo("Exportation réussie", f"Données exportées vers {filename}.")

    def import_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.db.import_from_csv(filename)
            self.update_listbox()
            messagebox.showinfo("Importation réussie", f"Données importées depuis {filename}.")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for row in self.db.get_all_products():
            produit, quantite, purchase_price, sale_price, total_purchase_value, total_sale_value, gain, loss, last_updated = row[1:]
            self.listbox.insert(tk.END, f"{produit} - Quantité: {quantite} - Prix d'achat unitaire: {purchase_price} - Prix de vente unitaire: {sale_price} - Valeur d'achat totale: {total_purchase_value} - Valeur de vente totale: {total_sale_value} - Gain: {gain} - Pertes: {loss} - Dernière mise à jour: {last_updated}")

if __name__ == "__main__":
    db = Database()
    app = MainView(db)
    app.mainloop()
