import customtkinter as ctk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId

# ------------------ MongoDB Connection ------------------
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["movies_db"]  # Movies database
    collection = db["movies"]  # Movies collection
except Exception as e:
    print("Error connecting to MongoDB:", e)
    exit()

# ------------------ CRUD Functions ------------------
def insert_data():
    title = entry_title.get().strip()
    genre = entry_genre.get().strip()
    year = entry_year.get().strip()

    if title and genre and year.isdigit():
        try:
            collection.insert_one({"title": title, "genre": genre, "year": int(year)})
            messagebox.showinfo("Success", "Movie record inserted successfully!")
            clear_fields()
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Input Error", "Please enter valid Title, Genre, and Year (number).")

def fetch_data():
    for row in tree.get_children():
        tree.delete(row)
    for doc in collection.find().sort("_id", 1):  # Show oldest first
        tree.insert("", "end", iid=str(doc["_id"]), values=(doc["title"], doc["genre"], doc["year"]))

def update_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a record to update.")
        return

    record_id = ObjectId(selected[0])
    title = entry_title.get().strip()
    genre = entry_genre.get().strip()
    year = entry_year.get().strip()

    if title and genre and year.isdigit():
        try:
            collection.update_one({"_id": record_id}, {"$set": {"title": title, "genre": genre, "year": int(year)}})
            messagebox.showinfo("Success", "Movie record updated successfully!")
            clear_fields()
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Input Error", "Please enter valid Title, Genre, and Year (number).")

def delete_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a record to delete.")
        return

    record_id = ObjectId(selected[0])
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
    if confirm:
        try:
            collection.delete_one({"_id": record_id})
            messagebox.showinfo("Success", "Movie record deleted successfully!")
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def clear_fields():
    entry_title.delete(0, "end")
    entry_genre.delete(0, "end")
    entry_year.delete(0, "end")

def select_record(event):
    selected = tree.selection()
    if selected:
        record = collection.find_one({"_id": ObjectId(selected[0])})
        if record:
            clear_fields()
            entry_title.insert(0, record["title"])
            entry_genre.insert(0, record["genre"])
            entry_year.insert(0, str(record["year"]))

# ------------------ CustomTkinter Setup ------------------
ctk.set_appearance_mode("dark")   # 🌙 Dark Mode
ctk.set_default_color_theme("dark-blue")  # Dark blue theme

root = ctk.CTk()
root.title("🎬 Movies Management System (Dark Mode)")
root.geometry("800x550")

# Title
title_label = ctk.CTkLabel(root, text="🎬 Movies Management System", font=ctk.CTkFont(size=22, weight="bold"))
title_label.pack(pady=15)

# Form Frame
form_frame = ctk.CTkFrame(root, corner_radius=15)
form_frame.pack(pady=10, padx=20, fill="x")

entry_title = ctk.CTkEntry(form_frame, placeholder_text="🎥 Enter Movie Title", width=200)
entry_title.grid(row=0, column=0, padx=10, pady=10)

entry_genre = ctk.CTkEntry(form_frame, placeholder_text="🎭 Enter Genre", width=200)
entry_genre.grid(row=0, column=1, padx=10, pady=10)

entry_year = ctk.CTkEntry(form_frame, placeholder_text="📅 Enter Year", width=100)
entry_year.grid(row=0, column=2, padx=10, pady=10)

# Buttons
btn_frame = ctk.CTkFrame(root, corner_radius=15)
btn_frame.pack(pady=5)

ctk.CTkButton(btn_frame, text="➕ Add", command=insert_data, fg_color="#2ecc71", hover_color="#27ae60").grid(row=0, column=0, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="✏ Update", command=update_data, fg_color="#3498db", hover_color="#2980b9").grid(row=0, column=1, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="🗑 Delete", command=delete_data, fg_color="#e74c3c", hover_color="#c0392b").grid(row=0, column=2, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="📖 Read", command=fetch_data, fg_color="#f39c12", hover_color="#d35400").grid(row=0, column=3, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="🧹 Clear", command=clear_fields, fg_color="#7f8c8d", hover_color="#636e72").grid(row=0, column=4, padx=10, pady=5)

# Table Frame
tree_frame = ctk.CTkFrame(root, corner_radius=15)
tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

columns = ("Title", "Genre", "Year")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

# Style for dark theme Treeview
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background="#2c3e50",
                foreground="white",
                rowheight=30,
                fieldbackground="#2c3e50")
style.map("Treeview", background=[("selected", "#3498db")])

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=200)
tree.pack(fill="both", expand=True)

tree.bind("<<TreeviewSelect>>", select_record)

# Fetch initial data
fetch_data()

root.mainloop()
