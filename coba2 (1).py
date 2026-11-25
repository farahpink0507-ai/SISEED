
import os
import time
import shutil
import pyfiglet
import psycopg2
import pandas as pd
from colorama import Fore, Style, init

# Mengaktifkan warna
init(autoreset=True)


# ================= HEADER SISEED =================

def bersihkan_layar():
    os.system('cls' if os.name == 'nt' else 'clear')


def tampilkan_header():
    lebar_layar = shutil.get_terminal_size((80, 20)).columns
    panjang_garis_atas = lebar_layar - 6
    print(Fore.YELLOW + "୨୧ " + "─" * panjang_garis_atas + " ୨୧\n")

    banner = pyfiglet.figlet_format("SiSeed", font="ansi_shadow")

    for baris in banner.splitlines():
        print(Fore.GREEN + Style.BRIGHT + baris.center(lebar_layar))

    panjang_garis_bawah = int(lebar_layar * 0.7)
    garis_bawah = "୨୧ " + "─" * panjang_garis_bawah + " ୨୧"

    print(Fore.YELLOW + garis_bawah.center(lebar_layar))

    subjudul = "SISTEM INFORMASI PENGELOLAAN DATA BIBIT TANAMAN"
    print(Fore.LIGHTGREEN_EX + subjudul.center(lebar_layar) + "\n")


# ================= KONEKSI DATABASE =================

def connectDB():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="1105_Ananda",
            dbname="db_siseed"
        )

        cur = conn.cursor()

        return conn, cur

    except Exception as error:
        print("Koneksi database gagal:", error)
        return None, None


conn, cur = connectDB()

if conn is not None:
    print("Berhasil terhubung ke PostgreSQL!")

else:
    print("Gagal terhubung ke database.")


# ================= REGISTRASI =================

def pilih_dari_daftar(judul, daftar, boleh_baru=False):
    print(f"\n{judul}")
    for d in daftar:
        print(f"{d[0]}. {d[1]}")
    if boleh_baru:
        print("0. Tidak ada di daftar (tambah baru)")

    valid = {str(d[0]) for d in daftar}
    if boleh_baru:
        valid.add("0")

    while True:
        pilihan = input("Pilihan: ").strip()
        if pilihan in valid:
            return int(pilihan)
        print(Fore.RED + "Pilihan tidak valid!")
def register():
    tampilkan_header()
    print("\n======== REGISTRASI AKUN SISEED =======")

    nama = input("Nama Lengkap: ")
    username = input("Username: ")
    password = input("Password: ")
    no_telp = input("No. Telp: ")
    email = input("Email: ")

    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT ID_Role FROM Role WHERE Nama_Role = 'Pelanggan'"
        )
        role = cursor.fetchone()

        if not role:
            print("\nRole Pelanggan tidak ditemukan!")
            return

        # ---- Pilih Kabupaten ----
        cursor.execute(
            "SELECT ID_Kabupaten, Nama_Kabupaten FROM Kabupaten ORDER BY 1"
        )
        id_kab = pilih_dari_daftar("Pilih Kabupaten:", cursor.fetchall())

        # ---- Pilih Kecamatan (sesuai kabupaten) ----
        cursor.execute("""
            SELECT ID_Kecamatan, Nama_Kecamatan
            FROM Kecamatan WHERE ID_Kabupaten = %s ORDER BY 1
        """, (id_kab,))
        daftar_kec = cursor.fetchall()

        if not daftar_kec:
            print(Fore.RED + "\nBelum ada data kecamatan untuk kabupaten ini.")
            time.sleep(2)
            return

        id_kec = pilih_dari_daftar("Pilih Kecamatan:", daftar_kec)

        # ---- Pilih Alamat Jalan (sesuai kecamatan) ----
        cursor.execute("""
            SELECT ID_AlamatJalan, Nama_AlamatJalan
            FROM Alamatjalan WHERE ID_Kecamatan = %s ORDER BY 1
        """, (id_kec,))
        daftar_jalan = cursor.fetchall()

        if daftar_jalan:
            id_jalan = pilih_dari_daftar(
                "Pilih Alamat Jalan:", daftar_jalan, boleh_baru=True
            )
        else:
            print("\nBelum ada alamat jalan untuk kecamatan ini.")
            id_jalan = 0

        if id_jalan == 0:
            nama_jalan = ""
            while not nama_jalan:
                nama_jalan = input("Masukkan nama jalan: ").strip()
            cursor.execute("""
                INSERT INTO Alamatjalan (Nama_AlamatJalan, ID_Kecamatan)
                VALUES (%s, %s) RETURNING ID_AlamatJalan
            """, (nama_jalan, id_kec))
            id_jalan = cursor.fetchone()[0]

        # ---- Simpan user ----
        cursor.execute("""
            INSERT INTO Users
            (Nama_Users, Username, Password, No_Telp, Email,
             ID_Role, ID_Kabupaten, ID_AlamatJalan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nama, username, password, no_telp, email,
              role[0], id_kab, id_jalan))

        conn.commit()
        print(Fore.GREEN + "\nRegistrasi Akun Berhasil!")
        time.sleep(1.5)

    except psycopg2.Error as error:
        conn.rollback()
        print(Fore.RED + "\nRegistrasi Gagal:", error)
        time.sleep(2.5)

    finally:
        cursor.close()

# ================= LOGIN =================

def login():
    tampilkan_header()
    print("======= LOGIN SISEED =======")

    username = input("Username: ")
    password = input("Password: ")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT Users.ID_Users, Users.Nama_Users, Role.Nama_Role
        FROM Users
        JOIN Role ON Users.ID_Role = Role.ID_Role
        WHERE Users.Username = %s AND Users.Password = %s
    """, (username, password))

    data = cursor.fetchone()

    if data:
        print("\nLogin Berhasil!")
        print("Selamat Datang di SISEED", data[1])
        menu_utama(data[0], data[1], data[2])
    else:
        print("\nUsername atau Password Salah!, Silahkan coba lagi!")

    cursor.close()


# ================= MENU UTAMA =================

def menu_utama(id_users, nama, role):
    tampilkan_header()

    print("\n===== MENU UTAMA SISEED =====")
    print("Nama Pengguna :", nama)
    print("Role          :", role)

    print("\nSelamat Berbelanja di SISEED!")
    logout()


# ================= LOGOUT =================

def logout():
    pilihan = input("\nApakah anda yakin ingin logout? (y/t): ")

    if pilihan == "y":
        tampilkan_header()
        print("\n Anda berhasil logout! Sampai jumpa!")

    else:
        print("\n Anda tetap berada di SISEED!")


# ================= HALAMAN AWAL =================

def halaman_awal():
    while True:
        tampilkan_header()

        print(Fore.WHITE + "1. Login")
        print(Fore.WHITE + "2. Register")
        print(Fore.WHITE + "3. Keluar")

        pilihan = input(Fore.WHITE + "\nPilih menu (1-3): ")

        if pilihan == "1":
            login()

        elif pilihan == "2":
            register()

        elif pilihan == "3":
            print(Fore.YELLOW + "\nTerima kasih telah mengunjungi SISEED!")
            break

        else:
            print(Fore.RED + "\nPilihan tidak tersedia, silahkan pilih menu ulang!")
            time.sleep(1.2)
def logout():
    pilihan = input("\nApakah anda yakin ingin logout? (y/t): ").lower()

    if pilihan == "y":
        tampilkan_header()
        print("\n Anda berhasil logout!")
        time.sleep(1.2)
        return True
    else:
        print("\n Anda tetap berada di SISEED!")
        time.sleep(1.2)
        return False


def menu_utama(id_users, nama, role):
    if role == "Pelanggan":
        menu_pelanggan(id_users, nama)
    else:
        # Role Pemilik Toko & Kasir belum dibuat
        tampilkan_header()
        print(f"\nMenu untuk role {role} belum tersedia.")
        logout()

# ================= FITUR PELANGGAN =================

def rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")


def menu_pelanggan(id_users, nama):
    while True:
        tampilkan_header()
        print("\n===== MENU PELANGGAN =====")
        print("Selamat datang,", nama)
        print("\n1. Informasi Data Bibit")
        print("2. Pemesanan Bibit")
        print("3. Riwayat Pembelian")
        print("4. Logout")

        pilihan = input("\nPilih menu (1-4): ")

        if pilihan == "1":
            lihat_data_bibit()
        elif pilihan == "2":
            pemesanan(id_users)
        elif pilihan == "3":
            riwayat_pembelian(id_users)
        elif pilihan == "4":
            if logout():
                break
        else:
            print(Fore.RED + "\nPilihan tidak tersedia!")
            time.sleep(1.2)


# ---------- 11. Informasi Data Bibit ----------

def lihat_data_bibit(tunggu=True):
    tampilkan_header()
    print("\n===== INFORMASI DATA BIBIT =====")
    keyword = input("Cari nama/jenis bibit (kosongkan untuk semua): ").strip()

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_Bibit, Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok
            FROM Bibit
            WHERE Nama_Bibit ILIKE %s OR Jenis_Bibit ILIKE %s
            ORDER BY ID_Bibit
        """, (f"%{keyword}%", f"%{keyword}%"))
        data = cursor.fetchall()
    except psycopg2.Error as error:
        conn.rollback()
        print("\nGagal mengambil data bibit:", error)
        data = []
    finally:
        cursor.close()

    if data:
        print("\n" + "-" * 75)
        print(f"{'ID':<5}{'Nama Bibit':<25}{'Jenis':<20}{'Harga':>12}{'Stok':>8}")
        print("-" * 75)
        for b in data:
            print(f"{b[0]:<5}{b[1]:<25}{b[2]:<20}{rupiah(b[3]):>12}{b[4]:>8}")
        print("-" * 75)
    else:
        print("\nBibit tidak ditemukan.")

    if tunggu:
        input("\nTekan Enter untuk kembali...")


# ---------- 12. Pemesanan ----------

def pemesanan(id_users):
    keranjang = {}   # {id_bibit: {"nama":..., "harga":..., "jumlah":...}}

    while True:
        tampilkan_header()
        print("\n===== PEMESANAN BIBIT =====")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_Bibit, Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok
            FROM Bibit WHERE Stok > 0 ORDER BY ID_Bibit
        """)
        daftar = cursor.fetchall()
        cursor.close()

        if not daftar:
            print("\nMaaf, semua bibit sedang habis.")
            input("\nTekan Enter untuk kembali...")
            return

        print("\n" + "-" * 75)
        print(f"{'ID':<5}{'Nama Bibit':<25}{'Jenis':<20}{'Harga':>12}{'Stok':>8}")
        print("-" * 75)
        for b in daftar:
            print(f"{b[0]:<5}{b[1]:<25}{b[2]:<20}{rupiah(b[3]):>12}{b[4]:>8}")
        print("-" * 75)

        if keranjang:
            print("\nKeranjang saat ini:")
            for i, k in keranjang.items():
                print(f"  - {k['nama']} x{k['jumlah']} = {rupiah(k['harga'] * k['jumlah'])}")

        print("\n1. Tambah bibit ke keranjang")
        print("2. Checkout")
        print("3. Batal")
        pilihan = input("\nPilih (1-3): ")

        if pilihan == "1":
            try:
                id_bibit = int(input("ID Bibit : "))
                jumlah = int(input("Jumlah   : "))
            except ValueError:
                print(Fore.RED + "\nInput harus berupa angka!")
                time.sleep(1.2)
                continue

            bibit = next((b for b in daftar if b[0] == id_bibit), None)

            if bibit is None:
                print(Fore.RED + "\nID bibit tidak ditemukan / stok habis!")
            elif jumlah <= 0:
                print(Fore.RED + "\nJumlah harus lebih dari 0!")
            else:
                sudah = keranjang.get(id_bibit, {}).get("jumlah", 0)
                if sudah + jumlah > bibit[4]:
                    print(Fore.RED + f"\nStok tidak cukup! Stok tersedia: {bibit[4]}, di keranjang: {sudah}")
                else:
                    keranjang[id_bibit] = {
                        "nama": bibit[1],
                        "harga": bibit[3],
                        "jumlah": sudah + jumlah
                    }
                    print(Fore.GREEN + "\nBerhasil ditambahkan ke keranjang.")
            time.sleep(1.5)

        elif pilihan == "2":
            if not keranjang:
                print(Fore.RED + "\nKeranjang masih kosong!")
                time.sleep(1.2)
                continue
            if checkout(id_users, keranjang):
                return

        elif pilihan == "3":
            print("\nPemesanan dibatalkan.")
            time.sleep(1.2)
            return

        else:
            print(Fore.RED + "\nPilihan tidak tersedia!")
            time.sleep(1.2)


def checkout(id_users, keranjang):
    tampilkan_header()
    print("\n===== RINGKASAN PESANAN =====")

    total = 0
    total_jumlah = 0
    for k in keranjang.values():
        subtotal = k["harga"] * k["jumlah"]
        total += subtotal
        total_jumlah += k["jumlah"]
        print(f"{k['nama']:<25} {k['jumlah']:>3} x {rupiah(k['harga']):>10} = {rupiah(subtotal):>12}")
    print("-" * 60)
    print(f"{'TOTAL':<45}{rupiah(total):>15}")

    metode_list = {"1": "Tunai", "2": "Transfer Bank", "3": "E-Wallet"}
    print("\nMetode pembayaran:")
    for no, m in metode_list.items():
        print(f"{no}. {m}")
    metode = metode_list.get(input("\nPilih metode (1-3): "))

    if metode is None:
        print(Fore.RED + "\nMetode pembayaran tidak valid!")
        time.sleep(1.5)
        return False

    if input("\nKonfirmasi pesanan? (y/t): ").lower() != "y":
        print("\nPesanan belum dikonfirmasi.")
        time.sleep(1.2)
        return False

    cursor = conn.cursor()
    try:
        # Kunci & cek ulang stok agar tidak minus
        for id_bibit, k in keranjang.items():
            cursor.execute(
                "SELECT Stok FROM Bibit WHERE ID_Bibit = %s FOR UPDATE",
                (id_bibit,)
            )
            stok = cursor.fetchone()[0]
            if stok < k["jumlah"]:
                raise ValueError(f"Stok {k['nama']} tidak cukup (tersisa {stok}).")

        cursor.execute("""
            INSERT INTO Penjualan
            (Tanggal_Penjualan, Total_Penjualan, Metode_Pembayaran, Jumlah, ID_Users)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
            RETURNING ID_Penjualan
        """, (total, metode, total_jumlah, id_users))
        id_penjualan = cursor.fetchone()[0]

        for id_bibit, k in keranjang.items():
            cursor.execute("""
                INSERT INTO Detail_Penjualan
                (Jumlah_Bibit, Harga_Jual, ID_Penjualan, ID_Bibit)
                VALUES (%s, %s, %s, %s)
            """, (k["jumlah"], k["harga"], id_penjualan, id_bibit))

            cursor.execute(
                "UPDATE Bibit SET Stok = Stok - %s WHERE ID_Bibit = %s",
                (k["jumlah"], id_bibit)
            )

        conn.commit()
        print(Fore.GREEN + f"\nPemesanan berhasil! No. Transaksi: {id_penjualan}")
        input("\nTekan Enter untuk kembali...")
        return True

    except (ValueError, psycopg2.Error) as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan gagal:", error)
        input("\nTekan Enter untuk kembali...")
        return False

    finally:
        cursor.close()


# ---------- 13. Riwayat Pembelian ----------

def riwayat_pembelian(id_users):
    tampilkan_header()
    print("\n===== RIWAYAT PEMBELIAN =====")

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.ID_Penjualan, p.Tanggal_Penjualan, p.Metode_Pembayaran,
                   p.Total_Penjualan, b.Nama_Bibit, d.Jumlah_Bibit, d.Harga_Jual
            FROM Penjualan p
            JOIN Detail_Penjualan d ON p.ID_Penjualan = d.ID_Penjualan
            JOIN Bibit b ON d.ID_Bibit = b.ID_Bibit
            WHERE p.ID_Users = %s
            ORDER BY p.Tanggal_Penjualan DESC, p.ID_Penjualan DESC
        """, (id_users,))
        data = cursor.fetchall()
    except psycopg2.Error as error:
        conn.rollback()
        print("\nGagal mengambil riwayat:", error)
        data = []
    finally:
        cursor.close()

    if not data:
        print("\nAnda belum memiliki riwayat pembelian.")
    else:
        id_terakhir = None
        for row in data:
            id_p, tgl, metode, total, nama_bibit, jml, harga = row
            if id_p != id_terakhir:
                if id_terakhir is not None:
                    print()
                print("=" * 60)
                print(f"No. Transaksi : {id_p}")
                print(f"Tanggal       : {tgl}")
                print(f"Pembayaran    : {metode}")
                print("-" * 60)
                print(f"Total         : {rupiah(total)}")
                print("Item:")
                id_terakhir = id_p
            print(f"  - {nama_bibit:<22} {jml:>3} x {rupiah(harga):>10} = {rupiah(jml * harga):>12}")
        print("=" * 60)

    input("\nTekan Enter untuk kembali...")
halaman_awal()

cur.close()
conn.close()
