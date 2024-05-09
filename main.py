import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import pyperclip
import keyboard

# Crear y configurar la base de datos
conn = sqlite3.connect('code_library.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS codes (id INTEGER PRIMARY KEY, title TEXT, tags TEXT, code TEXT)
''')
conn.commit()

# Función para agregar o actualizar códigos
def save_code(title, tags, code, code_id=None):
    if code_id:
        c.execute('UPDATE codes SET title = ?, tags = ?, code = ? WHERE id = ?', (title, tags, code, code_id))
    else:
        c.execute('INSERT INTO codes (title, tags, code) VALUES (?, ?, ?)', (title, tags, code))
    conn.commit()
    load_codes()

# Función para eliminar un código
def delete_code():
    index = listbox.curselection()
    if index:
        code_id = listbox.get(index[0])[0]
        c.execute('DELETE FROM codes WHERE id = ?', (code_id,))
        conn.commit()
        load_codes()
    else:
        messagebox.showerror("Error", "Please select a code to delete.")

# Función para cargar códigos en la lista
def load_codes(search_query=None):
    if search_query:
        c.execute("SELECT id, title, tags FROM codes WHERE title LIKE ? OR tags LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        c.execute('SELECT id, title, tags FROM codes')
    records = c.fetchall()
    listbox.delete(0, tk.END)
    for record in records:
        listbox.insert(tk.END, f"{record[0]}: {record[1]}")  # Mostrar ID y título

# Función para seleccionar un código
def select_code(event):
    try:
        index = listbox.curselection()[0]
        item = listbox.get(index)
        code_id = int(item.split(':')[0])  # Extraer ID desde el string
        c.execute('SELECT * FROM codes WHERE id = ?', (code_id,))
        record = c.fetchone()
        title_entry.delete(0, tk.END)
        title_entry.insert(0, record[1])
        tags_entry.delete(0, tk.END)
        tags_entry.insert(0, record[2])
        code_text.delete('1.0', tk.END)
        code_text.insert('1.0', record[3])
        copy_to_clipboard()
    except IndexError:
        pass

def copy_to_clipboard():
    pyperclip.copy(code_text.get('1.0', tk.END))

def show_window():
    root.deiconify()

# Función para buscar códigos
def search_codes():
    search_query = search_entry.get()
    load_codes(search_query)

# Crear la interfaz de usuario
root = tk.Tk()
root.title('Code Library')
root.geometry("800x600")  # Ventana de tamaño ajustable
style = ttk.Style()
style.theme_use('clam')  # Usar un tema más moderno

listbox = tk.Listbox(root, height=15)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox.bind('<<ListboxSelect>>', select_code)

right_frame = ttk.Frame(root)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

search_frame = ttk.Frame(right_frame)
search_frame.pack(fill=tk.X)
search_entry = ttk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
search_button = ttk.Button(search_frame, text='Search', command=search_codes)
search_button.pack(side=tk.LEFT, padx=10)

title_entry = ttk.Entry(right_frame)
title_entry.pack(fill=tk.X, padx=5, pady=5)
tags_entry = ttk.Entry(right_frame)
tags_entry.pack(fill=tk.X, padx=5, pady=5)
code_text = scrolledtext.ScrolledText(right_frame)
code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

button_frame = ttk.Frame(right_frame)
button_frame.pack(fill=tk.X, padx=5, pady=5)
save_button = ttk.Button(button_frame, text='Save', command=lambda: save_code(title_entry.get(), tags_entry.get(), code_text.get('1.0', tk.END), int(listbox.get(listbox.curselection()[0]).split(':')[0]) if listbox.curselection() else None))
save_button.pack(side=tk.LEFT, padx=5)
delete_button = ttk.Button(button_frame, text='Delete', command=delete_code)
delete_button.pack(side=tk.LEFT, padx=5)
copy_button = ttk.Button(button_frame, text='Copy', command=copy_to_clipboard)
copy_button.pack(side=tk.LEFT, padx=5)

load_codes()

# Registrar la combinación de teclas y asociarla con la función show_window
keyboard.add_hotkey('ctrl+shift+o', show_window)

root.mainloop()
