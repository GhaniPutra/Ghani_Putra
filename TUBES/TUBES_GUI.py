import mysql.connector
import random
from tkinter import *
from tkinter import ttk, messagebox
import tkinter as tk

# Fungsi untuk menghasilkan ID acak
def generate_random_id():
    return random.randint(10000, 99999)

# Koneksi ke database
def create_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root', 
        password='', 
        database='perpus'
    )
    return connection

# Fungsi untuk menambahkan buku (Admin)
def add_book(judul, pengarang, stok):
    conn = create_connection()
    cursor = conn.cursor()
    id_buku = generate_random_id()
    cursor.execute("INSERT INTO buku (id, judul_buku, pengarang, stok) VALUES (%s, %s, %s, %s)", (id_buku, judul, pengarang, stok))
    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Berhasil", f"Buku '{judul}' berhasil ditambahkan.")

# Fungsi untuk mengupdate buku (Admin)
def update_book(judul, pengarang, stok):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Update pengarang dan stok berdasarkan judul buku
    cursor.execute("UPDATE buku SET pengarang = %s, stok = %s WHERE judul_buku = %s", (pengarang, stok, judul))
    hasil = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return hasil

# Fungsi untuk menghapus buku (Admin)
def delete_book(judul):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Cek apakah buku sedang dipinjam
    cursor.execute("SELECT * FROM peminjaman WHERE judul_buku = %s", (judul,))
    peminjaman = cursor.fetchall()
    
    if peminjaman:
        messagebox.showwarning("Error", f"Buku '{judul}' tidak bisa dihapus karena sedang dipinjam.")
    else:
        cursor.execute("DELETE FROM buku WHERE judul_buku = %s", (judul,))
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", f"Buku '{judul}' berhasil dihapus.")
        else:
            messagebox.showwarning("Error", f"Buku '{judul}' tidak ditemukan.")
    
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk melihat buku
def view_books():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buku")
    books = cursor.fetchall()
    conn.close()
    return books

# Fungsi untuk menghapus user (Admin)
def delete_user(nama):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Cek apakah user sedang meminjam buku
    cursor.execute("SELECT * FROM peminjaman WHERE nama_user = %s", (nama,))
    peminjaman = cursor.fetchall()
    
    if peminjaman:
        print(f"User '{nama}' tidak bisa dihapus karena sedang meminjam buku.")
    else:
        cursor.execute("DELETE FROM user WHERE nama_user = %s", (nama,))
        if cursor.rowcount > 0:
            print(f"User '{nama}' berhasil dihapus.")
        else:
            print(f"User '{nama}' tidak ditemukan.")
    
    conn.commit()
    cursor.close()
    conn.close()

def borrow_book(user_name, book_title):
    conn = create_connection()
    cursor = conn.cursor()

    # Cek apakah user sudah ada di database
    cursor.execute("SELECT id FROM user WHERE nama_user = %s", (user_name,))
    user_result = cursor.fetchone()

    if not user_result:
        cursor.execute("INSERT INTO user (nama_user) VALUES (%s)", (user_name,))
        user_id = cursor.lastrowid
    else:
        user_id = user_result[0]

    # Cek apakah buku tersedia
    cursor.execute("SELECT id, stok FROM buku WHERE judul_buku = %s", (book_title,))
    result = cursor.fetchone()

    if result:
        book_id, stock = result
        if stock > 0:
            cursor.execute("INSERT INTO peminjaman (id_user, id_buku, nama_user, judul_buku, tgl_pinjam) VALUES (%s, %s, %s, %s, CURDATE())",
                           (user_id, book_id, user_name, book_title))
            cursor.execute("UPDATE buku SET stok = stok - 1 WHERE id = %s", (book_id,))
            conn.commit()
            messagebox.showinfo("Berhasil", f"User '{user_name}' berhasil meminjam buku '{book_title}'.")
        else:
            messagebox.showwarning("Stok Habis", f"Buku '{book_title}' sedang dipinjam.")
    else:
        messagebox.showwarning("Buku Tidak Ditemukan", f"Buku '{book_title}' tidak ditemukan.")

    cursor.close()
    conn.close()

def return_book(user_name, book_title):
    conn = create_connection()
    cursor = conn.cursor()

    # Cek apakah buku ada
    cursor.execute("SELECT id FROM buku WHERE judul_buku = %s", (book_title,))
    book_result = cursor.fetchone()

    if book_result:
        book_id = book_result[0]

        cursor.execute("SELECT * FROM peminjaman WHERE id_user = (SELECT id FROM user WHERE nama_user = %s) AND id_buku = %s", (user_name, book_id))
        borrow_results = cursor.fetchall()

        if borrow_results:
            for borrow_result in borrow_results:
                cursor.execute("DELETE FROM peminjaman WHERE id_user = (SELECT id FROM user WHERE nama_user = %s) AND id_buku = %s", (user_name, book_id))
                cursor.execute("UPDATE buku SET stok = stok + 1 WHERE id = %s", (book_id,))
                conn.commit()
            messagebox.showinfo("Berhasil", f"Buku '{book_title}' berhasil dikembalikan oleh user '{user_name}' dan tersedia lagi.")
        else:
            messagebox.showwarning("Buku Belum Dipinjam", f"User '{user_name}' belum meminjam buku '{book_title}'.")
    else:
        messagebox.showwarning("Buku Tidak Ditemukan", f"Buku '{book_title}' tidak ditemukan.")

    cursor.close()
    conn.close()

def admin_menu():
    root = tk.Tk()
    root.title("Admin Buku Perpustakaan")

    # Frame untuk input
    frame_input = tk.Frame(root)
    frame_input.pack(pady=20, anchor="w")

    tk.Label(frame_input, text="Judul Buku:").grid(row=0, column=0)
    entry_title = tk.Entry(frame_input, width=30)
    entry_title.grid(row=0, column=1)

    tk.Label(frame_input, text="Pengarang:").grid(row=1, column=0)
    entry_author = tk.Entry(frame_input, width=30)
    entry_author.grid(row=1, column=1)

    tk.Label(frame_input, text="Stok:").grid(row=2, column=0)
    entry_stock = tk.Entry(frame_input, width=30)  # Menambahkan width=30
    entry_stock.grid(row=2, column=1)

    # Tombol aksi
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)

    def clear_entries():
        entry_title.delete(0, tk.END)
        entry_author.delete(0, tk.END)
        entry_stock.delete(0, tk.END)

    def load_books():
        for row in tree.get_children():
            tree.delete(row)

        books = view_books()
        for book in books:
            tree.insert("", tk.END, values=(book[0], book[1], book[2], book[3]))

    def on_tree_select(event):
        # Mengambil data dari baris yang dipilih di Treeview
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            values = item["values"]
            # Mengisi input field dengan data yang dipilih
            entry_title.delete(0, tk.END)
            entry_title.insert(0, values[1])
            entry_author.delete(0, tk.END)
            entry_author.insert(0, values[2])
            entry_stock.delete(0, tk.END)
            entry_stock.insert(0, values[3])

    def on_add():
        title = entry_title.get()
        author = entry_author.get()
        stock = entry_stock.get()
        
        if title and author and stock:
            try:
                stock = int(stock)
                add_book(title, author, stock)
                clear_entries()
                load_books()
            except ValueError:
                messagebox.showwarning("Error", "Stok harus berupa angka.")
        else:
            messagebox.showwarning("Error", "Semua kolom harus diisi.")

    def on_update():
        title = entry_title.get()
        author = entry_author.get()
        stock = entry_stock.get()
        
        if title and author and stock:
            try:
                stock = int(stock)
                result = globals()['update_book'](title, author, stock)
                if result > 0:
                    messagebox.showinfo("Berhasil", f"Buku '{title}' berhasil diperbarui.")
                else:
                    messagebox.showwarning("Gagal", f"Buku dengan judul '{title}' tidak ditemukan.")
                clear_entries()
                load_books()
            except ValueError:
                messagebox.showwarning("Error", "Stok harus berupa angka.")
        else:
            messagebox.showwarning("Error", "Semua kolom harus diisi.")

    def on_delete():
        title = entry_title.get()
        if title:
            delete_book(title)
            clear_entries()
            load_books()
        else:
            messagebox.showwarning("Error", "Masukkan judul buku yang ingin dihapus.")

    def on_view_borrowers():
        # Menyembunyikan jendela admin dan membuka jendela peminjaman
        root.withdraw()

        # Membuka jendela baru untuk menampilkan peminjaman
        borrower_window = tk.Toplevel(root)
        borrower_window.title("Daftar Peminjaman")

        # Menampilkan data peminjaman dalam Treeview
        tree_borrowers = ttk.Treeview(borrower_window, columns=("ID", "ID User", "Nama User", "ID Buku", "Judul Buku", "Tanggal Pinjam"), show="headings")
        tree_borrowers.pack(padx=10, pady=10)

        # Definisikan kolom
        tree_borrowers.heading("ID", text="ID Peminjaman")
        tree_borrowers.heading("ID User", text="ID User")
        tree_borrowers.heading("Nama User", text="Nama User")
        tree_borrowers.heading("ID Buku", text="ID Buku")
        tree_borrowers.heading("Judul Buku", text="Judul Buku")
        tree_borrowers.heading("Tanggal Pinjam", text="Tanggal Pinjam")

        # Ambil data peminjaman dari database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM peminjaman")
        borrowers = cursor.fetchall()
        cursor.close()
        conn.close()

        # Menampilkan data peminjaman
        for borrower in borrowers:
            tree_borrowers.insert("", tk.END, values=borrower)

        # Fungsi untuk menutup jendela peminjaman dan menampilkan kembali jendela admin
        def close_borrower_window():
            borrower_window.destroy()
            root.deiconify()  # Menampilkan kembali jendela admin

        # Tombol untuk menutup jendela peminjaman
        btn_close = tk.Button(borrower_window, text="Tutup", command=close_borrower_window)
        btn_close.pack(pady=10)

    def on_view_users():
        # Menyembunyikan jendela admin dan membuka jendela pengelolaan user
        root.withdraw()

        # Membuka jendela baru untuk menampilkan user
        user_window = tk.Toplevel(root)
        user_window.title("Daftar User")

        # Menampilkan data user dalam Treeview
        tree_users = ttk.Treeview(user_window, columns=("ID User", "Nama User", "Status"), show="headings")
        tree_users.pack(padx=10, pady=10)

        # Definisikan kolom
        tree_users.heading("ID User", text="ID User")
        tree_users.heading("Nama User", text="Nama User")
        tree_users.heading("Status", text="Status")

        # Ambil data user dari database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nama_user, 
                CASE 
                    WHEN p.id_user IS NOT NULL THEN 'Meminjam Buku'
                    ELSE 'Tidak Meminjam Buku' 
                END AS status
            FROM user u
            LEFT JOIN peminjaman p ON u.id = p.id_user
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        # Menampilkan data user
        for user in users:
            tree_users.insert("", tk.END, values=user)

        # Fungsi untuk menutup jendela user dan menampilkan kembali jendela admin
        def close_user_window():
            user_window.destroy()
            root.deiconify()  # Menampilkan kembali jendela admin

        # Tombol untuk menutup jendela user
        btn_close_user = tk.Button(user_window, text="Tutup", command=close_user_window)
        btn_close_user.pack(pady=10)

        # Fungsi untuk menghapus user
        def on_delete_user():
            selected_user = tree_users.selection()
            if selected_user:
                item = tree_users.item(selected_user)
                values = item["values"]
                user_name = values[1]

                if values[2] == 'Tidak Meminjam Buku':
                    delete_user(user_name)
                    tree_users.delete(selected_user)
                else:
                    messagebox.showwarning("Error", f"User '{user_name}' sedang meminjam buku dan tidak dapat dihapus.")

        # Tombol untuk menghapus user
        btn_delete_user = tk.Button(user_window, text="Hapus User", command=on_delete_user)
        btn_delete_user.pack(pady=10)

    btn_add = tk.Button(frame_buttons, text="Tambah", command=on_add)
    btn_add.grid(row=0, column=0, padx=10)

    btn_update = tk.Button(frame_buttons, text="Update", command=on_update)
    btn_update.grid(row=0, column=1, padx=10)

    btn_delete = tk.Button(frame_buttons, text="Hapus", command=on_delete)
    btn_delete.grid(row=0, column=2, padx=10)

    btn_clear = tk.Button(frame_buttons, text="Clear", command=clear_entries)
    btn_clear.grid(row=0, column=3, padx=10)

    # Tombol untuk melihat bagian peminjaman
    btn_loan = tk.Button(frame_buttons, text="Lihat Peminjaman", command=on_view_borrowers)
    btn_loan.grid(row=0, column=4, padx=10)

    # Tombol untuk melihat dan menghapus user
    btn_delete_user = tk.Button(frame_buttons, text="Lihat & Hapus User", command=on_view_users)
    btn_delete_user.grid(row=0, column=5, padx=10)

    # Treeview untuk menampilkan daftar buku
    frame_books = tk.Frame(root)
    frame_books.pack(pady=10)

    columns = ("ID", "Judul Buku", "Pengarang", "Stok")
    tree = ttk.Treeview(frame_books, columns=columns, show="headings")
    tree.pack()

    # Definisikan kolom
    tree.heading("ID", text="ID")
    tree.heading("Judul Buku", text="Judul Buku")
    tree.heading("Pengarang", text="Pengarang")
    tree.heading("Stok", text="Stok")

    load_books()  # Muat buku pada awalnya

    # Menangani klik pada baris di Treeview
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Menjalankan GUI
    root.mainloop()

def user_menu():
    root = tk.Tk()
    root.title("Menu User Perpustakaan")

    # Frame untuk inputan user dan judul buku
    frame_input = tk.Frame(root)
    frame_input.pack(pady=10, anchor="w") 

    tk.Label(frame_input, text="Nama User:").grid(row=0, column=0, sticky="w") 
    entry_user_name = tk.Entry(frame_input, width=30) 
    entry_user_name.grid(row=0, column=1)

    selected_book_title = tk.StringVar()

    tk.Label(frame_input, text="Judul Buku:").grid(row=1, column=0, sticky="w") 
    entry_book_title = tk.Entry(frame_input, textvariable=selected_book_title, state="readonly", width=30) 
    entry_book_title.grid(row=1, column=1)

    # Tombol untuk pinjam buku
    btn_pinjam = tk.Button(frame_input, text="Pinjam Buku", command=lambda: on_pinjam(entry_user_name.get(), selected_book_title.get()))
    btn_pinjam.grid(row=2, column=0, columnspan=2, pady=10, sticky="w") 

    # Tombol untuk kembalikan buku
    btn_kembalikan = tk.Button(frame_input, text="Kembalikan Buku", command=lambda: on_kembalikan(entry_user_name.get(), selected_book_title.get()))
    btn_kembalikan.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

    # Frame untuk daftar buku
    frame_books = tk.Frame(root)
    frame_books.pack(pady=10)

    columns = ("ID", "Judul Buku", "Pengarang", "Stok")
    tree = ttk.Treeview(frame_books, columns=columns, show="headings")
    tree.pack()

    # Definisikan kolom
    tree.heading("ID", text="ID")
    tree.heading("Judul Buku", text="Judul Buku")
    tree.heading("Pengarang", text="Pengarang")
    tree.heading("Stok", text="Stok")

    # Fungsi untuk memuat buku dari database
    def load_books():
        for row in tree.get_children():
            tree.delete(row)

        books = view_books()
        for book in books:
            tree.insert("", tk.END, values=(book[0], book[1], book[2], book[3]))

    load_books()

    # Fungsi untuk memilih buku dari Treeview dan memasukkan judul buku ke input
    def on_select_book(event):
        selected_item = tree.selection()[0]  # Mendapatkan item yang dipilih
        book_title = tree.item(selected_item, "values")[1]  # Mengambil judul buku dari kolom Treeview
        selected_book_title.set(book_title)  # Set judul buku ke StringVar

    tree.bind("<ButtonRelease-1>", on_select_book)  # Mengaitkan event saat buku dipilih

    # Fungsi untuk pinjam buku
    def on_pinjam(user_name, book_title):
        if user_name and book_title:
            borrow_book(user_name, book_title) 
            load_books()

    # Fungsi untuk mengembalikan buku
    def on_kembalikan(user_name, book_title):
        if user_name and book_title:
            return_book(user_name, book_title) 
            load_books()

    root.mainloop()

def main():
    while True:
        print("\n--- Menu Utama ---")
        print("1. Masuk sebagai Admin")
        print("2. Masuk sebagai User")
        print("3. Keluar")
        
        choice = input("Pilih opsi: ")

        if choice == '1':
            admin_menu()
        elif choice == '2':
            user_menu()
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()