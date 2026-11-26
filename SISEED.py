import os
import shutil
import pyfiglet
from colorama import Fore, init
import psycopg2
import pandas as pd

# Mengaktifkan warna
init(autoreset=True)

#header
def tampilkan_header():
    os.system('cls')
    #mengambil lebar terminal
    lebar_layar = shutil.get_terminal_size((80, 20)).columns
    panjang_garis_atas = lebar_layar - 6
    print(Fore.YELLOW + "୨୧ " + "─" * panjang_garis_atas + " ୨୧\n")
    #membuat tulisan SISEED memakai font dari ASCII yang ansi reguler
    banner = pyfiglet.figlet_format("SiSeed", font="ansi_regular")
    #menampilkan setiap baris tulisan SISEED di tengah
    for baris in banner.splitlines():
        print(Fore.GREEN + baris.center(lebar_layar))

    panjang_garis_bawah = lebar_layar - 6
    garis_bawah = "୨୧ " + "─" * panjang_garis_bawah + " ୨୧"
    print(Fore.YELLOW + garis_bawah.center(lebar_layar))
    #untuk menampilkan deskripsi singkat di bagian tengah
    subjudul = "SISTEM INFORMASI PENGELOLAAN DATA BIBIT TANAMAN"
    print(Fore.LIGHTGREEN_EX + subjudul.center(lebar_layar) + "\n")

#koneksi ke  database
def connectDB():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="160707",
            dbname="db_project"
        )

        cur = conn.cursor()

        return conn, cur

    except Exception as error:
        print("Koneksi database gagal:", error)
        return None, None

def login():
    tampilkan_header()
    print("======= LOGIN SISEED =======")

    username = input("Username: ")
    password = input("Password: ")

    conn , cur = connectDB()

    cur.execute("""
        SELECT Users.ID_Users, Users.Nama_Users, Role.Nama_Role
        FROM Users
        JOIN Role ON Users.ID_Role = Role.ID_Role
        WHERE Users.Username = %s AND Users.Password = %s
    """, (username, password))
    data = cur.fetchone()

    if data:
        print("\nLogin Berhasil!")
        print("Selamat Datang di SISEED", data[1])
    
        menu_utama(data[0], data[1], data[2])
    else:
        print("\nUsername atau Password Salah!, Silahkan coba lagi!")

    cur.close()
    
#menu utama
def menu_utama(id_users, nama, role):
    while True:
        tampilkan_header()

        print("\n ===== MENU UTAMA SISEED =====")
        print("Nama Pengguna :", nama)
        print("Role          :", role)

        #menu untuk pemilik toko
        if role.lower() == "pemilik toko":
            print(Fore.YELLOW + "\n===== MENU PEMILIK TOKO =====")
            print("1. Pengelolaan Data Bibit")
            print("2. Pengelolaan Akun")
            print("3. Pengelolaan Data Pemasok")
            print("4. Transaksi Pembelian")
            print("5. Laporan Toko")
            print("0. Logout")

        #menu untuk kasir
        elif role.lower() == "kasir":
            print(Fore.YELLOW + "\n===== MENU KASIR =====")
            print("1. Transaksi Penjualan")
            print("0. Logout")

        #menu untuk pelanggan
        elif role.lower() == "pelanggan":
            print(Fore.YELLOW + "\n===== MENU PELANGGAN =====")
            print("1. Informasi Data Bibit")
            print("2. Pemesanan")
            print("3. Riwayat Pembelian")
            print("0. Logout")

        else:
            print(Fore.RED + "\nRole tidak tersedia!")
            break

        pilihan = input("\nPilih Menu: ")

        if pilihan == "0":
            logout()
            break

        #pilihan menu pemilik toko
        elif role.lower() == "pemilik toko":
            if pilihan == "1":
                menuPengelolaanBibit()

            elif pilihan == "2":
                menuPengelolaanAkun()

            elif pilihan == "3":
                menuPengelolaanDataPemasok()

            elif pilihan == "4":
                transaksi_pembelian_bibit(id_users)

            elif pilihan == "5":
                laporan_toko()

            else:
                print(Fore.RED + "\nPilihan tidak tersedia!")

        # pilihan menu untuk kasir
        elif role.lower() == "kasir":
            if pilihan == "1":
                transaksi_penjualan_bibit(id_users)

            else:
                print(Fore.RED + "\nPilihan tidak tersedia!")

        #pilihan menu untuk pelanggan
        elif role.lower() == "pelanggan":
            if pilihan == "1":
                informasi_data_bibit()
                input ("enter untuk melanjutkan")

            elif pilihan == "2":
                print("\nPemesanan")
                pemesanan(id_users)
                input ("enter untuk melanjutkan")
                
            elif pilihan == "3":
                print("\nRiwayat Pembelian")
                riwayat_pembelian(id_users)
            #menghentikan menu jika role tidak dapat dikenali
            else:
                print(Fore.RED + "\nPilihan tidak tersedia!")
                input("\nTekan Enter untuk kembali...")

#halaman logout
def logout():
    pilihan = input("\nApakah anda yakin ingin logout? (y/t): ")

    if pilihan == "y":
        tampilkan_header()
        print("\n Anda berhasil logout! Sampai jumpa!")
    #menampilkan ini jika pelanggan membatalkan 
    else:
        print("\n Anda tetap berada di SISEED!")

#menu awal
def menu_awal():
    while True:
        tampilkan_header()

        print("1. Login")
        print("2. Register")
        print("3. Keluar")

        pilihan = input("\nPilih menu (1-3): ")

        if pilihan == "1":
            login()

        elif pilihan == "2":
            register()

        elif pilihan == "3":
            print(Fore.YELLOW + "\nTerima kasih telah mengunjungi SISEED!")
            break

        else:
            #menampilkan pesan dan menunggu pengguna mengklik enter jika pilihan salah dan ingin kembali
            print(Fore.RED + "\nPilihan tidak tersedia!")
            input("\nTekan Enter untuk kembali...")

#menjalankan menu awal program
menu_awal()


#pengelolaan akun oleh pemilik toko 
# ================= PENGELOLAAN DATA BIBIT =================
# Menampilkan seluruh data bibit
def tampilkanBibit():
    conn, cur = connectDB()

    cur.execute("""
        SELECT * FROM bibit
        ORDER BY id_bibit
    """)

    data = cur.fetchall()
    if data:
        print("-" * 95)
        print("| {:<8} | {:<20} | {:<15} | {:<12} | {:<12} | {:<8} |".format(
            "ID", "Nama Bibit", "Jenis Bibit",
            "Harga Beli", "Harga Jual", "Stok"
        ))
        print("-" * 95)

        for bibit in data:
            print("| {:<8} | {:<20} | {:<15} | {:<12} | {:<12} | {:<8} |".format(
                bibit[0], bibit[1], bibit[2],
                bibit[3], bibit[4], bibit[5]
            ))

        print("-" * 95)

    else:
        print("Belum ada data bibit!")

    cur.close()
    conn.close()


# Menambahkan data bibit
def tambahBibit():
    print("\n===== TAMBAH DATA BIBIT =====")

    nama_bibit = input("Masukkan nama bibit: ")
    jenis_bibit = input("Masukkan jenis bibit: ")
    harga_beli = float(input("Masukkan harga beli: "))
    harga_jual = float(input("Masukkan harga jual: "))
    stok = int(input("Masukkan stok bibit: "))

    conn, cur = connectDB()

    cur.execute("""
        INSERT INTO bibit
        (nama_bibit, jenis_bibit, harga_beli, harga_jual, stok)
        VALUES (%s, %s, %s, %s, %s)
    """, (nama_bibit, jenis_bibit, harga_beli,
          harga_jual, stok))

    conn.commit()

    print("\nData bibit berhasil ditambahkan!")

    cur.close()
    conn.close()


# Mengubah data bibit
def ubahBibit():
    print("\n===== UBAH DATA BIBIT =====")

    tampilkanBibit()

    id_bibit = input("\nMasukkan ID bibit yang ingin diubah: ")

    conn, cur = connectDB()

    cur.execute("""
        SELECT * FROM bibit
        WHERE id_bibit = %s
    """, (id_bibit,))

    data = cur.fetchone()

    if data:
        print("\nMasukkan data bibit yang baru!")

        nama_bibit = input("Nama bibit: ")
        jenis_bibit = input("Jenis bibit: ")
        harga_beli = float(input("Harga beli: "))
        harga_jual = float(input("Harga jual: "))
        stok = int(input("Stok: "))

        cur.execute("""
            UPDATE bibit
            SET nama_bibit = %s,
                jenis_bibit = %s,
                harga_beli = %s,
                harga_jual = %s,
                stok = %s
            WHERE id_bibit = %s
        """, (nama_bibit, jenis_bibit, harga_beli,
              harga_jual, stok, id_bibit))

        conn.commit()

        print("\nData bibit berhasil diubah!")

    else:
        print("\nData bibit tidak ditemukan!")

    cur.close()
    conn.close()


# Menghapus data bibit
def hapusBibit():
    print("\n===== HAPUS DATA BIBIT =====")

    tampilkanBibit()

    id_bibit = input("\nMasukkan ID bibit yang ingin dihapus: ")

    conn, cur = connectDB()

    cur.execute("""
        SELECT nama_bibit FROM bibit
        WHERE id_bibit = %s
    """, (id_bibit,))

    data = cur.fetchone()

    if data:
        konfirmasi = input(
            "Yakin ingin menghapus bibit " + data[0] + "? (y/t): "
        )

        if konfirmasi.lower() == "y":
            cur.execute("""
                DELETE FROM bibit
                WHERE id_bibit = %s
            """, (id_bibit,))

            conn.commit()

            print("\nData bibit berhasil dihapus!")

        else:
            print("\nPenghapusan dibatalkan!")

    else:
        print("\nData bibit tidak ditemukan!")

    cur.close()
    conn.close()


# Menu pengelolaan data bibit
def menuPengelolaanBibit():
    while True:
        print("\n===== PENGELOLAAN DATA BIBIT =====")
        print("1. Tampilkan Data Bibit")
        print("2. Tambah Data Bibit")
        print("3. Ubah Data Bibit")
        print("4. Hapus Data Bibit")
        print("5. Kembali")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tampilkanBibit()

        elif pilihan == "2":
            tambahBibit()

        elif pilihan == "3":
            ubahBibit()

        elif pilihan == "4":
            hapusBibit()

        elif pilihan == "5":
            break

        else:
            print("\nPilihan tidak tersedia!")

# ================= PENGELOLAAN AKUN KASIR =================


# 1. MELIHAT AKUN KASIR
def lihatAkun():
    conn, cur = connectDB()

    try:
        query_select = """
            SELECT u.id_users, u.nama_users, u.username,
                   u.no_telp, u.email
            FROM users u
            JOIN role r ON u.id_role = r.id_role
            WHERE LOWER(r.nama_role) = 'kasir'
            ORDER BY u.id_users
        """

        cur.execute(query_select)
        data = cur.fetchall()

        print("\n===== DAFTAR AKUN KASIR =====")

        if len(data) == 0:
            print("Belum ada akun Kasir!")

        else:
            for akun in data:
                print("--------------------------------")
                print("ID Akun  :", akun[0])
                print("Nama     :", akun[1])
                print("Username :", akun[2])
                print("No. Telp :", akun[3])
                print("Email    :", akun[4])

    except Exception as error:
        print("Gagal menampilkan akun:", error)

    finally:
        cur.close()
        conn.close()

    input("\nTekan Enter untuk kembali...")


# 2. MENAMBAHKAN AKUN KASIR
def tambahAkun():

    print("\n===== TAMBAH AKUN KASIR =====")

    nama = input("Nama lengkap  : ")
    username = input("Username      : ")
    password = input("Password      : ")
    no_telp = input("Nomor telepon : ")
    email = input("Email         : ")
    id_kabupaten = input("ID Kabupaten  : ")

    conn, cur = connectDB()

    try:
        query_role = """
            SELECT id_role
            FROM role
            WHERE LOWER(nama_role) = 'kasir'
        """

        cur.execute(query_role)
        hasil = cur.fetchone()

        if hasil is None:
            print("Role Kasir tidak ditemukan!")
            return

        id_role = hasil[0]

        query_insert = """
            INSERT INTO users
            (nama_users, username, password, no_telp,
             email, id_role, id_kabupaten)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query_insert, (
            nama,
            username,
            password,
            no_telp,
            email,
            id_role,
            id_kabupaten
        ))

        conn.commit()
        print("Akun Kasir berhasil ditambahkan!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan akun:", error)

    finally:
        cur.close()
        conn.close()

    input("\nTekan Enter untuk kembali...")


# 3. MENGUBAH AKUN KASIR
def ubahAkun():
    conn, cur = connectDB()

    try:
        query_select = """
            SELECT u.id_users, u.nama_users
            FROM users u
            JOIN role r ON u.id_role = r.id_role
            WHERE LOWER(r.nama_role) = 'kasir'
            ORDER BY u.id_users
        """

        cur.execute(query_select)
        data = cur.fetchall()

        print("\n===== UBAH AKUN KASIR =====")

        if len(data) == 0:
            print("Belum ada akun Kasir!")
            return

        for akun in data:
            print("ID:", akun[0], "| Nama:", akun[1])

        id_users = input("\nMasukkan ID akun: ")

        query_cek = """
            SELECT id_users
            FROM users
            WHERE id_users = %s
            AND id_role = (
                SELECT id_role
                FROM role
                WHERE LOWER(nama_role) = 'kasir'
            )
        """

        cur.execute(query_cek, (id_users,))
        hasil = cur.fetchone()

        if hasil is None:
            print("Akun Kasir tidak ditemukan!")
            return

        print("\nMasukkan data akun yang baru")

        nama = input("Nama lengkap  : ")
        username = input("Username      : ")
        password = input("Password      : ")
        no_telp = input("Nomor telepon : ")
        email = input("Email         : ")
        id_kabupaten = input("ID Kabupaten  : ")

        query_update = """
            UPDATE users
            SET nama_users = %s,
                username = %s,
                password = %s,
                no_telp = %s,
                email = %s,
                id_kabupaten = %s
            WHERE id_users = %s
        """

        cur.execute(query_update, (
            nama,
            username,
            password,
            no_telp,
            email,
            id_kabupaten,
            id_users
        ))

        conn.commit()
        print("Akun Kasir berhasil diubah!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah akun:", error)

    finally:
        cur.close()
        conn.close()

    input("\nTekan Enter untuk kembali...")


# 4. MENGHAPUS AKUN KASIR
def hapusAkun():
    conn, cur = connectDB()

    try:
        query_select = """
            SELECT u.id_users, u.nama_users
            FROM users u
            JOIN role r ON u.id_role = r.id_role
            WHERE LOWER(r.nama_role) = 'kasir'
            ORDER BY u.id_users
        """

        cur.execute(query_select)
        data = cur.fetchall()

        print("\n===== HAPUS AKUN KASIR =====")

        if len(data) == 0:
            print("Belum ada akun Kasir!")
            return

        for akun in data:
            print("ID:", akun[0], "| Nama:", akun[1])

        id_users = input("\nMasukkan ID akun: ")

        query_cek = """
            SELECT id_users
            FROM users
            WHERE id_users = %s
            AND id_role = (
                SELECT id_role
                FROM role
                WHERE LOWER(nama_role) = 'kasir'
            )
        """

        cur.execute(query_cek, (id_users,))
        hasil = cur.fetchone()

        if hasil is None:
            print("Akun Kasir tidak ditemukan!")
            return

        konfirmasi = input(
            "Yakin ingin menghapus akun ini? (y/t): "
        )

        if konfirmasi.lower() == "y":

            query_delete = """
                DELETE FROM users
                WHERE id_users = %s
            """

            cur.execute(query_delete, (id_users,))

            conn.commit()
            print("Akun Kasir berhasil dihapus!")

        else:
            print("Penghapusan akun dibatalkan!")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus akun:", error)

    finally:
        cur.close()
        conn.close()

    input("\nTekan Enter untuk kembali...")


# 5. MENU PENGELOLAAN AKUN
def menuPengelolaanAkun():
    while True:
        tampilkan_header()

        print(Fore.YELLOW + "\n===== PENGELOLAAN AKUN =====")
        print("1. Lihat Akun Kasir")
        print("2. Tambah Akun Kasir")
        print("3. Ubah Akun Kasir")
        print("4. Hapus Akun Kasir")
        print("0. Kembali")

        pilihan = input("\nPilih Menu: ")

        if pilihan == "1":
            lihatAkun()

        elif pilihan == "2":
            tambahAkun()

        elif pilihan == "3":
            ubahAkun()

        elif pilihan == "4":
            hapusAkun()

        elif pilihan == "0":
            break

        else:
            print(Fore.RED + "\nPilihan tidak tersedia!")
            input("\nTekan Enter untuk kembali...")


# ==========================================
# PENGELOLAAN DATA PEMASOK
# ==========================================

# Memilih Kabupaten
def pilih_kabupaten(cur):
    cur.execute("""
        SELECT ID_Kabupaten, Nama_Kabupaten
        FROM Kabupaten
        ORDER BY Nama_Kabupaten
    """)

    data = cur.fetchall()

    print("\n===== PILIH KABUPATEN =====")

    for i in range(len(data)):
        print(str(i + 1) + ". " + data[i][1])

    pilihan = input("Pilih kabupaten: ")

    if not pilihan.isdigit():
        print("Pilihan harus berupa angka!")
        return None

    pilihan = int(pilihan)

    if pilihan < 1 or pilihan > len(data):
        print("Pilihan tidak tersedia!")
        return None

    return data[pilihan - 1][0]


# Memilih Kecamatan
def pilih_kecamatan(cur, id_kabupaten):
    cur.execute("""
        SELECT ID_Kecamatan, Nama_Kecamatan
        FROM Kecamatan
        WHERE ID_Kabupaten = %s
        ORDER BY Nama_Kecamatan
    """, (id_kabupaten,))

    data = cur.fetchall()

    if len(data) == 0:
        print("Belum ada kecamatan untuk kabupaten ini!")
        return None

    print("\n===== PILIH KECAMATAN =====")

    for i in range(len(data)):
        print(str(i + 1) + ". " + data[i][1])

    pilihan = input("Pilih kecamatan: ")

    if not pilihan.isdigit():
        print("Pilihan harus berupa angka!")
        return None

    pilihan = int(pilihan)

    if pilihan < 1 or pilihan > len(data):
        print("Pilihan tidak tersedia!")
        return None

    return data[pilihan - 1][0]


# Memilih Alamat Jalan
def pilih_alamat_jalan(cur, id_kecamatan):
    cur.execute("""
        SELECT ID_AlamatJalan, Nama_AlamatJalan
        FROM Alamatjalan
        WHERE ID_Kecamatan = %s
        ORDER BY Nama_AlamatJalan
    """, (id_kecamatan,))

    data = cur.fetchall()

    if len(data) == 0:
        print("Belum ada alamat jalan untuk kecamatan ini!")
        return None

    print("\n===== PILIH ALAMAT JALAN =====")

    for i in range(len(data)):
        print(str(i + 1) + ". " + data[i][1])

    pilihan = input("Pilih alamat jalan: ")

    if not pilihan.isdigit():
        print("Pilihan harus berupa angka!")
        return None

    pilihan = int(pilihan)

    if pilihan < 1 or pilihan > len(data):
        print("Pilihan tidak tersedia!")
        return None

    return data[pilihan - 1][0]


# Menampilkan seluruh data pemasok
def tampilkan_pemasok():
    conn, cur = connectDB()

    cur.execute("""
        SELECT
            p.ID_Pemasok,
            p.Nama_Pemasok,
            p.Nama_Kontak,
            p.No_Kontak,
            a.Nama_AlamatJalan,
            k.Nama_Kecamatan,
            kb.Nama_Kabupaten
        FROM Pemasok p
        JOIN Alamatjalan a
            ON p.ID_AlamatJalan = a.ID_AlamatJalan
        JOIN Kecamatan k
            ON a.ID_Kecamatan = k.ID_Kecamatan
        JOIN Kabupaten kb
            ON k.ID_Kabupaten = kb.ID_Kabupaten
        ORDER BY p.ID_Pemasok
    """)

    data = cur.fetchall()

    print("\n================ DATA PEMASOK ================")

    if len(data) == 0:
        print("Belum ada data pemasok!")
    else:
        print("-" * 115)
        print("{:<5} {:<22} {:<15} {:<16} {:<23} {:<15} {:<15}".format(
            "ID", "Nama Pemasok", "Nama Kontak",
            "No Kontak", "Alamat Jalan", "Kecamatan", "Kabupaten"
        ))
        print("-" * 115)

        for row in data:
            print("{:<5} {:<22} {:<15} {:<16} {:<23} {:<15} {:<15}".format(
                row[0], row[1], row[2], row[3],
                row[4], row[5], row[6]
            ))

        print("-" * 115)

    cur.close()
    conn.close()


# Menambahkan data pemasok
def tambah_pemasok():
    conn, cur = connectDB()

    try:
        print("\n===== TAMBAH DATA PEMASOK =====")

        nama = input("Nama Pemasok : ")
        kontak = input("Nama Kontak  : ")
        no_kontak = input("No Kontak    : ")

        id_kabupaten = pilih_kabupaten(cur)

        if id_kabupaten is None:
            return

        id_kecamatan = pilih_kecamatan(cur, id_kabupaten)

        if id_kecamatan is None:
            return

        id_alamat = pilih_alamat_jalan(cur, id_kecamatan)

        if id_alamat is None:
            return

        cur.execute("""
            INSERT INTO Pemasok
            (Nama_Pemasok, Nama_Kontak, No_Kontak, ID_AlamatJalan)
            VALUES (%s, %s, %s, %s)
        """, (nama, kontak, no_kontak, id_alamat))

        conn.commit()

        print("\nData pemasok berhasil ditambahkan!")

    except Exception as e:
        conn.rollback()
        print("Gagal menambahkan pemasok:", e)

    finally:
        cur.close()
        conn.close()

# Mengubah data pemasok
def ubah_pemasok():
    conn, cur = connectDB()

    try:
        tampilkan_pemasok()

        print("\n===== UBAH DATA PEMASOK =====")

        id_pemasok = input("Masukkan ID Pemasok: ")

        if not id_pemasok.isdigit():
            print("ID harus berupa angka!")
            return

        cur.execute("""
            SELECT ID_Pemasok
            FROM Pemasok
            WHERE ID_Pemasok = %s
        """, (id_pemasok,))

        if cur.fetchone() is None:
            print("Pemasok tidak ditemukan!")
            return

        nama = input("Nama Pemasok baru : ")
        kontak = input("Nama Kontak baru  : ")
        no_kontak = input("No Kontak baru    : ")

        id_kabupaten = pilih_kabupaten(cur)

        if id_kabupaten is None:
            return

        id_kecamatan = pilih_kecamatan(cur, id_kabupaten)

        if id_kecamatan is None:
            return

        id_alamat = pilih_alamat_jalan(cur, id_kecamatan)

        if id_alamat is None:
            return

        cur.execute("""
            UPDATE Pemasok
            SET Nama_Pemasok = %s,
                Nama_Kontak = %s,
                No_Kontak = %s,
                ID_AlamatJalan = %s
            WHERE ID_Pemasok = %s
        """, (nama, kontak, no_kontak, id_alamat, id_pemasok))

        conn.commit()

        print("\nData pemasok berhasil diubah!")

    except Exception as e:
        conn.rollback()
        print("Gagal mengubah pemasok:", e)

    finally:
        cur.close()
        conn.close()

# Menghapus data pemasok
def hapus_pemasok():
    conn, cur = connectDB()

    try:
        tampilkan_pemasok()

        print("\n===== HAPUS DATA PEMASOK =====")

        id_pemasok = input("Masukkan ID Pemasok: ")

        if not id_pemasok.isdigit():
            print("ID harus berupa angka!")
            return

        cur.execute("""
            DELETE FROM Pemasok
            WHERE ID_Pemasok = %s
        """, (id_pemasok,))

        if cur.rowcount == 0:
            print("Pemasok tidak ditemukan!")
        else:
            conn.commit()
            print("Data pemasok berhasil dihapus!")

    except Exception as e:
        conn.rollback()
        print("Gagal menghapus pemasok:", e)

    finally:
        cur.close()
        conn.close()

# Menu pengelolaan data pemasok
def menuPengelolaanDataPemasok():

    while True:
        print("\n===== PENGELOLAAN DATA PEMASOK =====")
        print("1. Tampilkan Data Pemasok")
        print("2. Tambah Data Pemasok")
        print("3. Ubah Data Pemasok")
        print("4. Hapus Data Pemasok")
        print("5. Kembali")

        pilihan = input("Pilih menu: ")
        if pilihan == "1":
            tampilkan_pemasok()
        elif pilihan == "2":
            tambah_pemasok()
        elif pilihan == "3":
            ubah_pemasok()
        elif pilihan == "4":
            hapus_pemasok()
        elif pilihan == "5":
            break
        else:
            print("\nPilihan tidak tersedia!")

