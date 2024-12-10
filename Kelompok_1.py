# Import library yang diperlukan
import mysql.connector  # Untuk koneksi dengan database MySQL
from tkinter import *  # Untuk GUI dasar
from tkinter import ttk, messagebox  # ttk untuk widget modern, messagebox untuk notifikasi
import random  # Untuk menghasilkan ID acak

# Fungsi untuk koneksi ke database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Username MySQL
        password="",  # Password MySQL
        database="absensi_kelas"  # Nama database
    )

# Fungsi untuk mengambil data dari database dan menampilkannya di tabel GUI
def fetch_data():
    try:
        conn = connect_db()  # Membuka koneksi ke database
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")  # Mengambil semua data dari tabel `students`
        rows = cursor.fetchall()  # Ambil hasil query
        if len(rows) > 0:
            table.delete(*table.get_children())  # Bersihkan tabel GUI
            for row in rows:
                table.insert("", END, values=row)  # Tambahkan data ke tabel GUI
        conn.close()  # Tutup koneksi database
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")  # Tampilkan error jika terjadi masalah

# Fungsi untuk menambahkan data baru ke database
def add_data():
    if name_var.get() == "" or nis_var.get() == "":  # Validasi input
        messagebox.showwarning("Input Error", "All fields are required")
        return

    # Generate ID dengan 5 angka random
    generated_id = random.randint(10000, 99999)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Periksa jika ID sudah ada di database
        cursor.execute("SELECT id FROM students WHERE id = %s", (generated_id,))
        while cursor.fetchone():  # Jika ID ditemukan, buat ID baru
            generated_id = random.randint(10000, 99999)

        # Masukkan data baru ke database
        cursor.execute(
            "INSERT INTO students (id, name, nis, status) VALUES (%s, %s, %s, %s)",
            (generated_id, name_var.get(), nis_var.get(), status_var.get())
        )
        conn.commit()  # Simpan perubahan
        conn.close()  # Tutup koneksi

        fetch_data()  # Refresh tabel GUI
        clear_data()  # Bersihkan input
        messagebox.showinfo("Success", f"Student with ID {generated_id} added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error adding data: {e}")  # Tampilkan error jika gagal

# Fungsi untuk memperbarui data yang dipilih di database
def update_data():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name=%s, nis=%s, status=%s WHERE id=%s",
            (name_var.get(), nis_var.get(), status_var.get(), id_var.get())
        )
        conn.commit()  # Simpan perubahan
        conn.close()  # Tutup koneksi
        fetch_data()  # Refresh tabel GUI
        clear_data()  # Bersihkan input
    except Exception as e:
        messagebox.showerror("Error", f"Error updating data: {e}")  # Tampilkan error jika gagal

# Fungsi untuk menghapus data mahasiswa berdasarkan ID
def delete_student():
    selected_student = table.focus()  # Mendapatkan data yang dipilih dari tabel
    if selected_student:
        student_info = table.item(selected_student, "values")  # Mendapatkan data dari baris yang dipilih
        student_id = student_info[0]  # Mengambil ID dari data tersebut

        # Konfirmasi penghapusan
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student with ID {student_id}?")
        if confirm:
            try:
                connection = connect_db()
                cursor = connection.cursor()
                query = "DELETE FROM students WHERE id = %s"
                cursor.execute(query, (student_id,))
                connection.commit()
                cursor.close()
                connection.close()

                # Hapus data dari tabel GUI
                table.delete(selected_student)
                messagebox.showinfo("Success", f"Student with ID {student_id} deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting student: {e}")  # Tampilkan error jika gagal
    else:
        messagebox.showwarning("Selection Error", "Please select a student to delete.")  # Jika tidak ada data yang dipilih

# Fungsi untuk membersihkan input di form
def clear_data():
    id_var.set("")  # Bersihkan ID
    name_var.set("")  # Bersihkan Nama
    nis_var.set("")  # Bersihkan NIS
    status_var.set("Hadir")  # Set status default ke "Hadir"

# Fungsi untuk memilih data dari tabel
def select_data(event):
    selected_row = table.focus()  # Mendapatkan data yang dipilih
    data = table.item(selected_row, "values")  # Mengambil nilai data
    if data:
        id_var.set(data[0])  # Isi ID
        name_var.set(data[1])  # Isi Nama
        nis_var.set(data[2])  # Isi NIS
        status_var.set(data[3])  # Isi Status

# GUI Utama
app = Tk()
app.title("Aplikasi Absensi Kelas")  # Judul aplikasi
app.geometry("800x500")  # Ukuran jendela aplikasi

# Variabel untuk menyimpan input
id_var = StringVar()
name_var = StringVar()
nis_var = StringVar()
status_var = StringVar(value="Hadir")

# Frame Input untuk memasukkan data
frame_input = Frame(app, pady=10)
frame_input.pack(fill=X)

# Input Nama
Label(frame_input, text="Nama:").grid(row=0, column=0, padx=10, pady=5)
Entry(frame_input, textvariable=name_var, width=30).grid(row=0, column=1, padx=10)

# Input NIS
Label(frame_input, text="NIS:").grid(row=1, column=0, padx=10, pady=5)
Entry(frame_input, textvariable=nis_var, width=30).grid(row=1, column=1, padx=10)

# Dropdown Status
Label(frame_input, text="Status:").grid(row=2, column=0, padx=10, pady=5)
ttk.Combobox(frame_input, textvariable=status_var, values=("Hadir", "Izin", "Alpha"), width=27).grid(row=2, column=1, padx=10)

# Tombol untuk operasi CRUD
Button(frame_input, text="Tambah", command=add_data, width=10, bg="green", fg="white").grid(row=3, column=0, padx=10, pady=10)
Button(frame_input, text="Update", command=update_data, width=10, bg="blue", fg="white").grid(row=3, column=1, padx=10)
Button(frame_input, text="Hapus", command=delete_student, width=10, bg="red", fg="white").grid(row=3, column=2, padx=10)
Button(frame_input, text="Clear", command=clear_data, width=10, bg="yellow", fg="black").grid(row=3, column=3, padx=10)

# Frame Tabel untuk menampilkan data
frame_table = Frame(app)
frame_table.pack(fill=BOTH, expand=True)

# Tabel untuk menampilkan data
table = ttk.Treeview(frame_table, columns=("ID", "Nama", "NIS", "Status"), show="headings")
table.heading("ID", text="ID")  # Header kolom ID
table.heading("Nama", text="Nama")  # Header kolom Nama
table.heading("NIS", text="NIS")  # Header kolom NIS
table.heading("Status", text="Status")  # Header kolom Status

table.column("ID", width=50)  # Lebar kolom ID
table.column("Nama", width=200)  # Lebar kolom Nama
table.column("NIS", width=100)  # Lebar kolom NIS
table.column("Status", width=100)  # Lebar kolom Status

table.pack(fill=BOTH, expand=True)  # Buat tabel memenuhi frame
table.bind("<ButtonRelease-1>", select_data)  # Bind klik tabel untuk memilih data

# Jalankan Data Awal
fetch_data()  # Ambil data dari database dan tampilkan di tabel

# Jalankan Aplikasi
app.mainloop()  # Jalankan aplikasi
