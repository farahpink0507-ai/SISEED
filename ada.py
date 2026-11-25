
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
            dbname="SISEED_Projek"
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


# =====================================================================
# BAGIAN PELANGGAN (11 informasi bibit, 12 pemesanan, 13 riwayat pembelian)
# Diletakkan SEBELUM halaman_awal() supaya sudah terdefinisi saat program jalan
# =====================================================================

METODE_PEMBAYARAN = ["Tunai", "Transfer Bank", "QRIS", "E-Wallet"]


# ================= FUNGSI BANTU =================

def rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")


def tekan_enter():
    input(Fore.WHITE + "\nTekan Enter untuk kembali...")


def baca_angka(pesan):
    """Baca angka bulat. Kosong -> None. Bukan angka -> minta ulang."""
    while True:
        teks = input(pesan).strip()

        if teks == "":
            return None

        if teks.isdigit():
            return int(teks)

        print(Fore.RED + "Masukkan angka yang valid!")


# ================= INFORMASI DATA BIBIT =================

def ambil_bibit():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ID_Bibit, Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok
        FROM Bibit
        ORDER BY ID_Bibit
    """)

    data = cursor.fetchall()
    conn.commit()
    cursor.close()

    return data


def cetak_tabel_bibit(data):
    df = pd.DataFrame(data, columns=["ID", "Nama Bibit", "Jenis", "Harga", "Stok"])
    df["Harga"] = df["Harga"].apply(rupiah)
    df["Stok"] = df["Stok"].apply(lambda s: str(s) if s > 0 else "Habis")

    print(df.to_string(index=False))


def informasi_bibit():
    tampilkan_header()
    print("\n======== INFORMASI DATA BIBIT ========\n")

    data = ambil_bibit()

    if not data:
        print("Belum ada data bibit.")
    else:
        cetak_tabel_bibit(data)

    tekan_enter()


# ================= PEMESANAN =================

def pemesanan(id_users):
    tampilkan_header()
    print("\n======== PEMESANAN BIBIT ========\n")

    data = ambil_bibit()

    if not data:
        print("Belum ada data bibit.")
        tekan_enter()
        return

    cetak_tabel_bibit(data)

    # {id_bibit: (nama, harga_jual, stok)}
    bibit = {b[0]: (b[1], b[3], b[4]) for b in data}
    keranjang = {}

    while True:
        id_bibit = baca_angka("\nID bibit yang dipesan (kosongkan jika selesai): ")

        if id_bibit is None:
            break

        if id_bibit not in bibit:
            print(Fore.RED + "ID bibit tidak ditemukan!")
            continue

        nama_bibit, harga, stok = bibit[id_bibit]
        tersisa = stok - keranjang.get(id_bibit, 0)

        if tersisa <= 0:
            print(Fore.RED + f"Stok {nama_bibit} tidak tersedia!")
            continue

        jumlah = baca_angka(f"Jumlah {nama_bibit} (maks {tersisa}): ")

        if jumlah is None or jumlah < 1 or jumlah > tersisa:
            print(Fore.RED + f"Jumlah tidak valid! Isi antara 1 sampai {tersisa}.")
            continue

        keranjang[id_bibit] = keranjang.get(id_bibit, 0) + jumlah
        print(Fore.GREEN + f"Ditambahkan: {jumlah} x {nama_bibit}")

    if not keranjang:
        print("\nTidak ada bibit yang dipesan.")
        tekan_enter()
        return

    # Ringkasan pesanan
    print("\n------ RINGKASAN PESANAN ------")
    perkiraan_total = 0

    for id_b, qty in keranjang.items():
        nama_bibit, harga, _ = bibit[id_b]
        subtotal = harga * qty
        perkiraan_total += subtotal
        print(f"{nama_bibit:<22}{qty:>3} x {rupiah(harga):<12} = {rupiah(subtotal)}")

    print(f"\nTOTAL : {rupiah(perkiraan_total)}")

    print("\nMetode Pembayaran:")
    for i, metode in enumerate(METODE_PEMBAYARAN, start=1):
        print(f"  {i}. {metode}")

    pilihan = baca_angka("Pilih metode (1-" + str(len(METODE_PEMBAYARAN)) + "): ")

    if pilihan is None or pilihan < 1 or pilihan > len(METODE_PEMBAYARAN):
        print(Fore.RED + "\nMetode pembayaran tidak valid, pemesanan dibatalkan!")
        tekan_enter()
        return

    metode = METODE_PEMBAYARAN[pilihan - 1]

    konfirmasi = input("\nKonfirmasi pesanan? (y/t): ")

    if konfirmasi != "y":
        print("\nPemesanan dibatalkan.")
        tekan_enter()
        return

    # Semua langkah disimpan dalam satu transaksi
    cursor = conn.cursor()

    try:
        total = 0
        jumlah_total = 0
        rincian = []

        # Kunci baris bibit (urut ID) lalu cek ulang stok terbaru
        for id_b in sorted(keranjang):
            qty = keranjang[id_b]

            cursor.execute("""
                SELECT Nama_Bibit, Harga_Jual, Stok
                FROM Bibit
                WHERE ID_Bibit = %s
                FOR UPDATE
            """, (id_b,))

            nama_bibit, harga, stok = cursor.fetchone()

            if stok < qty:
                raise ValueError(f"Stok {nama_bibit} tidak cukup (tersisa {stok})!")

            rincian.append((id_b, nama_bibit, harga, qty))
            total += harga * qty
            jumlah_total += qty

        cursor.execute("""
            INSERT INTO Penjualan
            (Tanggal_Penjualan, Total_Penjualan, Metode_Pembayaran, Jumlah, ID_Users)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
            RETURNING ID_Penjualan, Tanggal_Penjualan
        """, (total, metode, jumlah_total, id_users))

        id_penjualan, tanggal = cursor.fetchone()

        for id_b, nama_bibit, harga, qty in rincian:
            cursor.execute("""
                INSERT INTO Detail_Penjualan
                (Jumlah_Bibit, Harga_Jual, ID_Penjualan, ID_Bibit)
                VALUES (%s, %s, %s, %s)
            """, (qty, harga, id_penjualan, id_b))

            cursor.execute(
                "UPDATE Bibit SET Stok = Stok - %s WHERE ID_Bibit = %s",
                (qty, id_b)
            )

        conn.commit()

        print(Fore.GREEN + "\n======== PEMESANAN BERHASIL ========")
        print("No. Transaksi :", id_penjualan)
        print("Tanggal       :", tanggal)

        for _, nama_bibit, harga, qty in rincian:
            print(f"  {nama_bibit:<22}{qty:>3} x {rupiah(harga)}")

        print("Total         :", rupiah(total))
        print("Pembayaran    :", metode)

    except ValueError as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan Gagal:", error, "Silahkan pesan ulang!")

    except psycopg2.Error as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan Gagal:", error)

    finally:
        cursor.close()

    tekan_enter()


# ================= RIWAYAT PEMBELIAN =================

def riwayat_pembelian(id_users):
    tampilkan_header()
    print("\n======== RIWAYAT PEMBELIAN ========")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.ID_Penjualan, p.Tanggal_Penjualan, p.Metode_Pembayaran,
               p.Total_Penjualan, b.Nama_Bibit, d.Jumlah_Bibit, d.Harga_Jual
        FROM Penjualan p
        JOIN Detail_Penjualan d ON d.ID_Penjualan = p.ID_Penjualan
        JOIN Bibit b ON b.ID_Bibit = d.ID_Bibit
        WHERE p.ID_Users = %s
        ORDER BY p.Tanggal_Penjualan DESC, p.ID_Penjualan DESC, d.ID_DetailPenjualan
    """, (id_users,))

    data = cursor.fetchall()
    conn.commit()
    cursor.close()

    if not data:
        print("\nBelum ada riwayat pembelian.")
        tekan_enter()
        return

    # Kelompokkan baris per transaksi (urutan terbaru tetap terjaga)
    transaksi = {}

    for id_p, tanggal, metode, total, nama_bibit, qty, harga in data:
        if id_p not in transaksi:
            transaksi[id_p] = {
                "tanggal": tanggal,
                "metode": metode,
                "total": total,
                "item": []
            }

        transaksi[id_p]["item"].append((nama_bibit, qty, harga, qty * harga))

    for id_p, t in transaksi.items():
        print(Fore.YELLOW + f"\nTransaksi #{id_p} | {t['tanggal']} | {t['metode']}")

        df = pd.DataFrame(t["item"], columns=["Nama Bibit", "Jumlah", "Harga", "Subtotal"])
        df["Harga"] = df["Harga"].apply(rupiah)
        df["Subtotal"] = df["Subtotal"].apply(rupiah)

        print(df.to_string(index=False))
        print("Total :", rupiah(t["total"]))

    tekan_enter()


# ================= REGISTRASI =================

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

        if role:
            cursor.execute(
                "SELECT ID_Kabupaten, Nama_Kabupaten FROM Kabupaten ORDER BY ID_Kabupaten"
            )

            print("\nPilih Kabupaten:")
            for id_kab, nama_kab in cursor.fetchall():
                print(f"  {id_kab}. {nama_kab}")

            id_kabupaten = input("ID Kabupaten: ")

            cursor.execute("""
                INSERT INTO Users
                (Nama_Users, Username, Password, No_Telp, Email, ID_Role, ID_Kabupaten)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nama, username, password, no_telp, email, role[0], id_kabupaten))

            conn.commit()
            print("\nRegistrasi Akun Berhasil!")

        else:
            print("\nRole Pelanggan tidak ditemukan!")

    except psycopg2.Error as error:
        conn.rollback()
        print("\nRegistrasi Gagal:", error)

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


halaman_awal()

cur.close()
conn.close()




# ================= FUNGSI BANTU =================

def rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")


def tekan_enter():
    input(Fore.WHITE + "\nTekan Enter untuk kembali...")


def baca_angka(pesan):
    """Baca angka bulat. Kosong -> None. Bukan angka -> minta ulang."""
    while True:
        teks = input(pesan).strip()

        if teks == "":
            return None

        if teks.isdigit():
            return int(teks)

        print(Fore.RED + "Masukkan angka yang valid!")


# ================= INFORMASI DATA BIBIT =================

def ambil_bibit():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ID_Bibit, Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok
        FROM Bibit
        ORDER BY ID_Bibit
    """)

    data = cursor.fetchall()
    conn.commit()
    cursor.close()

    return data


def cetak_tabel_bibit(data):
    df = pd.DataFrame(data, columns=["ID", "Nama Bibit", "Jenis", "Harga", "Stok"])
    df["Harga"] = df["Harga"].apply(rupiah)
    df["Stok"] = df["Stok"].apply(lambda s: str(s) if s > 0 else "Habis")

    print(df.to_string(index=False))


def informasi_bibit():
    tampilkan_header()
    print("\n======== INFORMASI DATA BIBIT ========\n")

    data = ambil_bibit()

    if not data:
        print("Belum ada data bibit.")
    else:
        cetak_tabel_bibit(data)

    tekan_enter()


# ================= PEMESANAN =================

def pemesanan(id_users):
    tampilkan_header()
    print("\n======== PEMESANAN BIBIT ========\n")

    data = ambil_bibit()

    if not data:
        print("Belum ada data bibit.")
        tekan_enter()
        return

    cetak_tabel_bibit(data)

    # {id_bibit: (nama, harga_jual, stok)}
    bibit = {b[0]: (b[1], b[3], b[4]) for b in data}
    keranjang = {}

    while True:
        id_bibit = baca_angka("\nID bibit yang dipesan (kosongkan jika selesai): ")

        if id_bibit is None:
            break

        if id_bibit not in bibit:
            print(Fore.RED + "ID bibit tidak ditemukan!")
            continue

        nama_bibit, harga, stok = bibit[id_bibit]
        tersisa = stok - keranjang.get(id_bibit, 0)

        if tersisa <= 0:
            print(Fore.RED + f"Stok {nama_bibit} tidak tersedia!")
            continue

        jumlah = baca_angka(f"Jumlah {nama_bibit} (maks {tersisa}): ")

        if jumlah is None or jumlah < 1 or jumlah > tersisa:
            print(Fore.RED + f"Jumlah tidak valid! Isi antara 1 sampai {tersisa}.")
            continue

        keranjang[id_bibit] = keranjang.get(id_bibit, 0) + jumlah
        print(Fore.GREEN + f"Ditambahkan: {jumlah} x {nama_bibit}")

    if not keranjang:
        print("\nTidak ada bibit yang dipesan.")
        tekan_enter()
        return

    # Ringkasan pesanan
    print("\n------ RINGKASAN PESANAN ------")
    perkiraan_total = 0

    for id_b, qty in keranjang.items():
        nama_bibit, harga, _ = bibit[id_b]
        subtotal = harga * qty
        perkiraan_total += subtotal
        print(f"{nama_bibit:<22}{qty:>3} x {rupiah(harga):<12} = {rupiah(subtotal)}")

    print(f"\nTOTAL : {rupiah(perkiraan_total)}")

    print("\nMetode Pembayaran:")
    for i, metode in enumerate(METODE_PEMBAYARAN, start=1):
        print(f"  {i}. {metode}")

    pilihan = baca_angka("Pilih metode (1-" + str(len(METODE_PEMBAYARAN)) + "): ")

    if pilihan is None or pilihan < 1 or pilihan > len(METODE_PEMBAYARAN):
        print(Fore.RED + "\nMetode pembayaran tidak valid, pemesanan dibatalkan!")
        tekan_enter()
        return

    metode = METODE_PEMBAYARAN[pilihan - 1]

    konfirmasi = input("\nKonfirmasi pesanan? (y/t): ")

    if konfirmasi != "y":
        print("\nPemesanan dibatalkan.")
        tekan_enter()
        return

    # Semua langkah disimpan dalam satu transaksi
    cursor = conn.cursor()

    try:
        total = 0
        jumlah_total = 0
        rincian = []

        # Kunci baris bibit (urut ID) lalu cek ulang stok terbaru
        for id_b in sorted(keranjang):
            qty = keranjang[id_b]

            cursor.execute("""
                SELECT Nama_Bibit, Harga_Jual, Stok
                FROM Bibit
                WHERE ID_Bibit = %s
                FOR UPDATE
            """, (id_b,))

            nama_bibit, harga, stok = cursor.fetchone()

            if stok < qty:
                raise ValueError(f"Stok {nama_bibit} tidak cukup (tersisa {stok})!")

            rincian.append((id_b, nama_bibit, harga, qty))
            total += harga * qty
            jumlah_total += qty

        cursor.execute("""
            INSERT INTO Penjualan
            (Tanggal_Penjualan, Total_Penjualan, Metode_Pembayaran, Jumlah, ID_Users)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
            RETURNING ID_Penjualan, Tanggal_Penjualan
        """, (total, metode, jumlah_total, id_users))

        id_penjualan, tanggal = cursor.fetchone()

        for id_b, nama_bibit, harga, qty in rincian:
            cursor.execute("""
                INSERT INTO Detail_Penjualan
                (Jumlah_Bibit, Harga_Jual, ID_Penjualan, ID_Bibit)
                VALUES (%s, %s, %s, %s)
            """, (qty, harga, id_penjualan, id_b))

            cursor.execute(
                "UPDATE Bibit SET Stok = Stok - %s WHERE ID_Bibit = %s",
                (qty, id_b)
            )

        conn.commit()

        print(Fore.GREEN + "\n======== PEMESANAN BERHASIL ========")
        print("No. Transaksi :", id_penjualan)
        print("Tanggal       :", tanggal)

        for _, nama_bibit, harga, qty in rincian:
            print(f"  {nama_bibit:<22}{qty:>3} x {rupiah(harga)}")

        print("Total         :", rupiah(total))
        print("Pembayaran    :", metode)

    except ValueError as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan Gagal:", error, "Silahkan pesan ulang!")

    except psycopg2.Error as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan Gagal:", error)

    finally:
        cursor.close()

    tekan_enter()


# ================= RIWAYAT PEMBELIAN =================

def riwayat_pembelian(id_users):
    tampilkan_header()
    print("\n======== RIWAYAT PEMBELIAN ========")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.ID_Penjualan, p.Tanggal_Penjualan, p.Metode_Pembayaran,
               p.Total_Penjualan, b.Nama_Bibit, d.Jumlah_Bibit, d.Harga_Jual
        FROM Penjualan p
        JOIN Detail_Penjualan d ON d.ID_Penjualan = p.ID_Penjualan
        JOIN Bibit b ON b.ID_Bibit = d.ID_Bibit
        WHERE p.ID_Users = %s
        ORDER BY p.Tanggal_Penjualan DESC, p.ID_Penjualan DESC, d.ID_DetailPenjualan
    """, (id_users,))

    data = cursor.fetchall()
    conn.commit()
    cursor.close()

    if not data:
        print("\nBelum ada riwayat pembelian.")
        tekan_enter()
        return

    # Kelompokkan baris per transaksi (urutan terbaru tetap terjaga)
    transaksi = {}

    for id_p, tanggal, metode, total, nama_bibit, qty, harga in data:
        if id_p not in transaksi:
            transaksi[id_p] = {
                "tanggal": tanggal,
                "metode": metode,
                "total": total,
                "item": []
            }

        transaksi[id_p]["item"].append((nama_bibit, qty, harga, qty * harga))

    for id_p, t in transaksi.items():
        print(Fore.YELLOW + f"\nTransaksi #{id_p} | {t['tanggal']} | {t['metode']}")

        df = pd.DataFrame(t["item"], columns=["Nama Bibit", "Jumlah", "Harga", "Subtotal"])
        df["Harga"] = df["Harga"].apply(rupiah)
        df["Subtotal"] = df["Subtotal"].apply(rupiah)

        print(df.to_string(index=False))
        print("Total :", rupiah(t["total"]))

    tekan_enter()

METODE_PEMBAYARAN = ["Tunai", "Transfer Bank", "QRIS", "E-Wallet"]


# ================= FUNGSI BANTU =================

def rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")


def tekan_enter():
    input(Fore.WHITE + "\nTekan Enter untuk kembali...")


def baca_angka(pesan):
    """Baca angka bulat. Kosong -> None. Bukan angka -> minta ulang."""
    while True:
        teks = input(pesan).strip()

        if teks == "":
            return None

        if teks.isdigit():
            return int(teks)

        print(Fore.RED + "Masukkan angka yang valid!")


# ================= INFORMASI DATA BIBIT =================

def ambil_bibit():
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ID_Bibit, Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok
        FROM Bibit
        ORDER BY ID_Bibit
    """)

    data = cursor.fetchall()
    conn.commit()
    cursor.close()

    return data


def cetak_tabel_bibit(data):
    df = pd.DataFrame(data, columns=["ID", "Nama Bibit", "Jenis", "Harga", "Stok"])
    df["Harga"] = df["Harga"].apply(rupiah)
    df["Stok"] = df["Stok"].apply(lambda s: str(s) if s > 0 else "Habis")

    print(df.to_string(index=False))


def informasi_bibit():
    tampilkan_header()
    print("\n======== INFORMASI DATA BIBIT ========\n")

    data = ambil_bibit()

    if not data:
        print("Belum ada data bibit.")
    else:
        cetak_tabel_bibit(data)

    tekan_enter()


# ================= PEMESANAN =================

def pemesanan(id_users):
    tampilkan_header()
    print("\n======== PEMESANAN BIBIT ========\n")

    data = ambil_bibit()

    if not data:
        print("Belum ada data bibit.")
        tekan_enter()
        return

    cetak_tabel_bibit(data)

    # {id_bibit: (nama, harga_jual, stok)}
    bibit = {b[0]: (b[1], b[3], b[4]) for b in data}
    keranjang = {}

    while True:
        id_bibit = baca_angka("\nID bibit yang dipesan (kosongkan jika selesai): ")

        if id_bibit is None:
            break

        if id_bibit not in bibit:
            print(Fore.RED + "ID bibit tidak ditemukan!")
            continue

        nama_bibit, harga, stok = bibit[id_bibit]
        tersisa = stok - keranjang.get(id_bibit, 0)

        if tersisa <= 0:
            print(Fore.RED + f"Stok {nama_bibit} tidak tersedia!")
            continue

        jumlah = baca_angka(f"Jumlah {nama_bibit} (maks {tersisa}): ")

        if jumlah is None or jumlah < 1 or jumlah > tersisa:
            print(Fore.RED + f"Jumlah tidak valid! Isi antara 1 sampai {tersisa}.")
            continue

        keranjang[id_bibit] = keranjang.get(id_bibit, 0) + jumlah
        print(Fore.GREEN + f"Ditambahkan: {jumlah} x {nama_bibit}")

    if not keranjang:
        print("\nTidak ada bibit yang dipesan.")
        tekan_enter()
        return

    # Ringkasan pesanan
    print("\n------ RINGKASAN PESANAN ------")
    perkiraan_total = 0

    for id_b, qty in keranjang.items():
        nama_bibit, harga, _ = bibit[id_b]
        subtotal = harga * qty
        perkiraan_total += subtotal
        print(f"{nama_bibit:<22}{qty:>3} x {rupiah(harga):<12} = {rupiah(subtotal)}")

    print(f"\nTOTAL : {rupiah(perkiraan_total)}")

    print("\nMetode Pembayaran:")
    for i, metode in enumerate(METODE_PEMBAYARAN, start=1):
        print(f"  {i}. {metode}")

    pilihan = baca_angka("Pilih metode (1-" + str(len(METODE_PEMBAYARAN)) + "): ")

    if pilihan is None or pilihan < 1 or pilihan > len(METODE_PEMBAYARAN):
        print(Fore.RED + "\nMetode pembayaran tidak valid, pemesanan dibatalkan!")
        tekan_enter()
        return

    metode = METODE_PEMBAYARAN[pilihan - 1]

    konfirmasi = input("\nKonfirmasi pesanan? (y/t): ")

    if konfirmasi != "y":
        print("\nPemesanan dibatalkan.")
        tekan_enter()
        return

    # Semua langkah disimpan dalam satu transaksi
    cursor = conn.cursor()

    try:
        total = 0
        jumlah_total = 0
        rincian = []

        # Kunci baris bibit (urut ID) lalu cek ulang stok terbaru
        for id_b in sorted(keranjang):
            qty = keranjang[id_b]

            cursor.execute("""
                SELECT Nama_Bibit, Harga_Jual, Stok
                FROM Bibit
                WHERE ID_Bibit = %s
                FOR UPDATE
            """, (id_b,))

            nama_bibit, harga, stok = cursor.fetchone()

            if stok < qty:
                raise ValueError(f"Stok {nama_bibit} tidak cukup (tersisa {stok})!")

            rincian.append((id_b, nama_bibit, harga, qty))
            total += harga * qty
            jumlah_total += qty

        cursor.execute("""
            INSERT INTO Penjualan
            (Tanggal_Penjualan, Total_Penjualan, Metode_Pembayaran, Jumlah, ID_Users)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
            RETURNING ID_Penjualan, Tanggal_Penjualan
        """, (total, metode, jumlah_total, id_users))

        id_penjualan, tanggal = cursor.fetchone()

        for id_b, nama_bibit, harga, qty in rincian:
            cursor.execute("""
                INSERT INTO Detail_Penjualan
                (Jumlah_Bibit, Harga_Jual, ID_Penjualan, ID_Bibit)
                VALUES (%s, %s, %s, %s)
            """, (qty, harga, id_penjualan, id_b))

            cursor.execute(
                "UPDATE Bibit SET Stok = Stok - %s WHERE ID_Bibit = %s",
                (qty, id_b)
            )

        conn.commit()

        print(Fore.GREEN + "\n======== PEMESANAN BERHASIL ========")
        print("No. Transaksi :", id_penjualan)
        print("Tanggal       :", tanggal)

        for _, nama_bibit, harga, qty in rincian:
            print(f"  {nama_bibit:<22}{qty:>3} x {rupiah(harga)}")

        print("Total         :", rupiah(total))
        print("Pembayaran    :", metode)

    except ValueError as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan Gagal:", error, "Silahkan pesan ulang!")

    except psycopg2.Error as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan Gagal:", error)

    finally:
        cursor.close()

    tekan_enter()


# ================= RIWAYAT PEMBELIAN =================

def riwayat_pembelian(id_users):
    tampilkan_header()
    print("\n======== RIWAYAT PEMBELIAN ========")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.ID_Penjualan, p.Tanggal_Penjualan, p.Metode_Pembayaran,
               p.Total_Penjualan, b.Nama_Bibit, d.Jumlah_Bibit, d.Harga_Jual
        FROM Penjualan p
        JOIN Detail_Penjualan d ON d.ID_Penjualan = p.ID_Penjualan
        JOIN Bibit b ON b.ID_Bibit = d.ID_Bibit
        WHERE p.ID_Users = %s
        ORDER BY p.Tanggal_Penjualan DESC, p.ID_Penjualan DESC, d.ID_DetailPenjualan
    """, (id_users,))

    data = cursor.fetchall()
    conn.commit()
    cursor.close()

    if not data:
        print("\nBelum ada riwayat pembelian.")
        tekan_enter()
        return

    # Kelompokkan baris per transaksi (urutan terbaru tetap terjaga)
    transaksi = {}

    for id_p, tanggal, metode, total, nama_bibit, qty, harga in data:
        if id_p not in transaksi:
            transaksi[id_p] = {
                "tanggal": tanggal,
                "metode": metode,
                "total": total,
                "item": []
            }

        transaksi[id_p]["item"].append((nama_bibit, qty, harga, qty * harga))

    for id_p, t in transaksi.items():
        print(Fore.YELLOW + f"\nTransaksi #{id_p} | {t['tanggal']} | {t['metode']}")

        df = pd.DataFrame(t["item"], columns=["Nama Bibit", "Jumlah", "Harga", "Subtotal"])
        df["Harga"] = df["Harga"].apply(rupiah)
        df["Subtotal"] = df["Subtotal"].apply(rupiah)

        print(df.to_string(index=False))
        print("Total :", rupiah(t["total"]))

    tekan_enter()
    