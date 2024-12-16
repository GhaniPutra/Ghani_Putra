import mysql.connector
from prettytable import PrettyTable
import random
import tkinter as tk
from tkinter import messagebox

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
def add_book(title, author, stock):
    conn = create_connection()
    cursor = conn.cursor()
    book_id = generate_random_id()
    cursor.execute("INSERT INTO buku (id, judul_buku, pengarang, stok) VALUES (%s, %s, %s, %s)", (book_id, title, author, stock))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Buku '{title}' berhasil ditambahkan.")

# Fungsi untuk mengecek semua buku (Admin)
def view_books():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buku")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    
    table = PrettyTable()
    table.field_names = ["ID", "Judul Buku", "Pengarang", "Stok"]
    for book in books:
        table.add_row(book)
    print(table)

# Fungsi untuk melihat user yang meminjam buku (Admin)
def view_borrowers():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM peminjaman")
    borrowers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    table = PrettyTable()
    table.field_names = ["ID", "ID User", "Nama User", "ID Buku", "Judul Buku", "Tanggal Pinjam"]
    for borrower in borrowers:
        table.add_row(borrower)
    print(table)

# Fungsi untuk menghapus buku (Admin) menggunakan judul buku
def delete_book_by_title(title):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Cek apakah buku sedang dipinjam
    cursor.execute("SELECT * FROM peminjaman WHERE judul_buku = %s", (title,))
    borrowing = cursor.fetchall()
    
    if borrowing:
        print(f"Buku '{title}' tidak bisa dihapus karena sedang dipinjam.")
    else:
        cursor.execute("DELETE FROM buku WHERE judul_buku = %s", (title,))
        if cursor.rowcount > 0:
            print(f"Buku '{title}' berhasil dihapus.")
        else:
            print(f"Buku '{title}' tidak ditemukan.")
    
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk mengupdate stok buku (Admin) menggunakan nama buku
def update_stock_by_title(title, new_stock):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE buku SET stok = %s WHERE judul_buku = %s", (new_stock, title))
    if cursor.rowcount > 0:
        print(f"Stok buku '{title}' berhasil diperbarui menjadi {new_stock}.")
    else:
        print(f"Buku dengan judul '{title}' tidak ditemukan.")
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk menghapus user (Admin) menggunakan nama user
def delete_user(name):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Cek apakah user sedang meminjam buku
    cursor.execute("SELECT * FROM peminjaman WHERE nama_user = %s", (name,))
    borrowing = cursor.fetchall()
    
    if borrowing:
        print(f"User '{name}' tidak bisa dihapus karena sedang meminjam buku.")
    else:
        cursor.execute("DELETE FROM user WHERE nama_user = %s", (name,))
        if cursor.rowcount > 0:
            print(f"User '{name}' berhasil dihapus.")
        else:
            print(f"User '{name}' tidak ditemukan.")
    
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk meminjam buku (User)
def borrow_book(user_name, book_title):
    conn = create_connection()
    cursor = conn.cursor()

    # Cek apakah user sudah ada di database
    cursor.execute("SELECT id FROM user WHERE nama_user = %s", (user_name,))
    user_result = cursor.fetchone()

    # Jika user belum ada, tambahkan ke database
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
            # Catat peminjaman buku jika tersedia
            cursor.execute("INSERT INTO peminjaman (id_user, id_buku, nama_user, judul_buku, tgl_pinjam) VALUES (%s, %s, %s, %s, CURDATE())",
                           (user_id, book_id, user_name, book_title))
            cursor.execute("UPDATE buku SET stok = stok - 1 WHERE id = %s", (book_id,))
            conn.commit()
            print(f"User '{user_name}' berhasil meminjam buku '{book_title}'.")
        else:
            print(f"Buku '{book_title}' sedang dipinjam.")
    else:
        print(f"Buku '{book_title}' tidak ditemukan.")
    
    cursor.close()
    conn.close()

# Fungsi untuk mengembalikan buku (User)
def return_book(user_name):
    conn = create_connection()
    cursor = conn.cursor()
    
    while True:
        title = input("Masukkan judul buku yang ingin dikembalikan: ")
        # Cek apakah buku ada berdasarkan judul
        cursor.execute("SELECT id FROM buku WHERE judul_buku = %s", (title,))
        book_result = cursor.fetchone()

        if book_result:
            book_id = book_result[0]
            # Cek apakah buku tersebut benar-benar dipinjam oleh user berdasarkan nama
            cursor.execute("SELECT * FROM peminjaman WHERE id_user = (SELECT id FROM user WHERE nama_user = %s) AND id_buku = %s", (user_name, book_id))
            borrow_results = cursor.fetchall()

            if borrow_results:
                # Jika buku ditemukan, lakukan pengembalian untuk semua entri yang ditemukan
                for borrow_result in borrow_results:
                    cursor.execute("DELETE FROM peminjaman WHERE id_user = (SELECT id FROM user WHERE nama_user = %s) AND id_buku = %s", (user_name, book_id))
                    cursor.execute("UPDATE buku SET stok = stok + 1 WHERE id = %s", (book_id,))
                    conn.commit()
                print(f"Buku '{title}' berhasil dikembalikan oleh user '{user_name}' dan tersedia lagi.")
            else:
                print(f"User '{user_name}' belum meminjam buku '{title}'.")
        else:
            print(f"Buku '{title}' tidak ditemukan.")

        # Tanya apakah ada buku lain yang ingin dikembalikan
        another_return = input("Adakah buku lain yang ingin dikembalikan? (y/n): ")
        if another_return.lower() != 'y':
            print("Terima kasih! Sampai jumpa.")
            break
    
    cursor.close()
    conn.close()

# Fungsi untuk menampilkan buku yang tersedia dan menanyakan peminjaman (User)
def show_available_books(user_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT judul_buku, stok FROM buku WHERE stok > 0")
    available_books = cursor.fetchall()
    cursor.close()
    conn.close()
    
    table = PrettyTable()
    table.field_names = ["Judul Buku", "Stok"]
    for book in available_books:
        table.add_row(book)
    
    if available_books:
        print("\nBuku yang tersedia:")
        print(table)

        while True:
            book_title = input("Masukkan judul buku yang ingin dipinjam: ")
            borrow_book(user_name, book_title)

            # Tanya apakah ada buku lain yang ingin dipinjam
            another_borrow = input("Apakah ada buku lain yang ingin dipinjam? (y/n): ")
            if another_borrow.lower() != 'y':
                break 
    else:
        print("\nTidak ada buku yang tersedia.")

# Menu Admin
def admin_menu():
    while True:
        print("\n--- Menu Admin ---")
        print("1. Tambah Buku")
        print("2. Lihat Semua Buku")
        print("3. Lihat Peminjam")
        print("4. Hapus Buku")
        print("5. Update Stok Buku")
        print("6. Hapus User")
        print("7. Keluar")
        
        choice = input("Pilih opsi: ")

        if choice == '1':
            while True:  # Loop untuk menambahkan beberapa buku
                title = input("Masukkan judul buku: ")
                author = input("Masukkan pengarang: ")
                stock = int(input("Masukkan stok buku: "))
                add_book(title, author, stock)
                
                # Menanyakan apakah ada buku lain yang ingin ditambahkan
                another = input("Apakah ada buku lain yang ingin ditambahkan? (y/n): ")
                if another.lower() != 'y':
                    break
        elif choice == '2':
            view_books()
        elif choice == '3':
            view_borrowers()
        elif choice == '4':
            title = input("Masukkan judul buku yang ingin dihapus: ")
            delete_book_by_title(title)
        elif choice == '5':
            title = input("Masukkan judul buku yang ingin diupdate: ")
            new_stock = int(input("Masukkan stok baru: "))
            update_stock_by_title(title, new_stock)
        elif choice == '6':
            user_name = input("Masukkan nama user yang ingin dihapus: ")
            delete_user(user_name)
        elif choice == '7':
            break
        else:
            print("Pilihan tidak valid.")

# Menu User
def user_menu():
    while True:
        print("\n--- Menu User ---")
        print("1. Pinjam Buku")
        print("2. Kembalikan Buku")
        print("3. Keluar")
        
        choice = input("Pilih opsi: ")

        if choice == '1':
            user_name = input("Masukkan nama user: ")
            show_available_books(user_name) 
        elif choice == '2':
            user_name = input("Masukkan nama user: ") 
            return_book(user_name) 
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid.")

# Menu Utama
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
