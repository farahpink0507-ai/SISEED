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
            password="1105_Ananda",
            dbname="db_siseed"
        )

        cur = conn.cursor()

        return conn, cur

    except Exception as error:
        print("Koneksi database gagal:", error)
        return None, None

#fungsi bantu

#memilih data wilayah dari daftar, atau menambah data baru jika tidak ada di daftar
def pilih_atau_tambah(cur, label, tabel, kolom_id, kolom_nama, kolom_induk, id_induk):
    conn, cur = connectDB()
    cur.execute(
        f"SELECT {kolom_id}, {kolom_nama} FROM {tabel} "
        f"WHERE {kolom_induk} = %s ORDER BY {kolom_id}",
        (id_induk,)
    )
    daftar = cur.fetchall()

    print(f"\nPilih {label}:")
    for id_data, nama_data in daftar:
        print(f"{id_data}. {nama_data}")
    print(f"0. Tambah {label} baru")

    id_valid = [d[0] for d in daftar]
    while True:
        pilihan = input_angka(f"{label} (masukkan nomor): ")

        if pilihan in id_valid:
            return pilihan

        if pilihan == 0:
            nama_baru = input(f"Nama {label} baru: ").strip()
            if not nama_baru:
                print("Nama tidak boleh kosong!")
                continue
            cur.execute(
                f"INSERT INTO {tabel} ({kolom_nama}, {kolom_induk}) "
                f"VALUES (%s, %s) RETURNING {kolom_id}",
                (nama_baru, id_induk)
            )
            return cur.fetchone()[0]

        print("Nomor tidak tersedia!")

#Registrasi akun
def register():
    tampilkan_header()
    print("\n======== REGISTRASI AKUN SISEED =======")

    conn, cur = connectDB()

    try:
        #mengambil daftar kabupaten dari database untuk dipilih pengguna
        cur.execute("SELECT ID_Kabupaten, Nama_Kabupaten FROM Kabupaten ORDER BY ID_Kabupaten")
        daftar_kabupaten = cur.fetchall()

        if not daftar_kabupaten:
            print("\nData kabupaten kosong! Isi tabel Kabupaten terlebih dahulu.")
            return

        #meminta pengguna memasukkan data untuk register akun
        nama = input("Nama Lengkap: ")
        username = input("Username: ")
        password = input("Password: ")
        no_telp = input("No. Telp: ")
        email = input("Email: ")

        #kabupaten
        print("\nPilih Kabupaten:")
        for id_kab, nama_kab in daftar_kabupaten:
            print(f"{id_kab}. {nama_kab}")

        id_valid = [k[0] for k in daftar_kabupaten]
        while True:
            id_kabupaten = input_angka("Kabupaten (masukkan nomor): ")
            if id_kabupaten in id_valid:
                break
            print("Nomor kabupaten tidak tersedia!")

        #kecamatan (sesuai kabupaten yang dipilih)
        id_kecamatan = pilih_atau_tambah(
            cur, "Kecamatan", "Kecamatan",
            "ID_Kecamatan", "Nama_Kecamatan", "ID_Kabupaten", id_kabupaten
        )

        #alamat jalan (sesuai kecamatan yang dipilih)
        id_alamat = pilih_atau_tambah(
            cur, "Alamat Jalan", "AlamatJalan",
            "ID_AlamatJalan", "Nama_AlamatJalan", "ID_Kecamatan", id_kecamatan
        )

        #mengambil id_role yang berdasarkan nama role nya pelanggan
        cur.execute(
            "SELECT ID_Role FROM Role WHERE Nama_Role = 'Pelanggan'"
        )
        role = cur.fetchone()

        if role:
            #menambahkan data akun ke tabel users di database
            cur.execute("""
                INSERT INTO Users
                (Nama_Users, Username, Password, No_Telp, Email, ID_Role, ID_Kabupaten, ID_AlamatJalan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nama, username, password, no_telp, email, role[0], id_kabupaten, id_alamat))

            conn.commit()
            print("\nRegistrasi Akun Berhasil!")

        else:
            print("\nRole Pelanggan tidak ditemukan!")

    except psycopg2.Error as error:
        #membatalkan perubahan jika terjadi kesalahan pada database
        conn.rollback()
        print("\nRegistrasi Gagal:", error)

    finally:
        cur.close()
        input("\nTekan Enter untuk kembali...")

#login
def login():
    tampilkan_header()
    print("======= LOGIN SISEED =======")

    username = input("Username: ")
    password = input("Password: ")

    conn , cur = connectDB()
    #mencari akun pengguna yang sudah registrasi berdasarkan username dan password
    cur.execute("""
        SELECT Users.ID_Users, Users.Nama_Users, Role.Nama_Role
        FROM Users
        JOIN Role ON Users.ID_Role = Role.ID_Role
        WHERE Users.Username = %s AND Users.Password = %s
    """, (username, password))
    #mengambil hanya satu data pengguna dari hassil pencarian
    data = cur.fetchone()

    if data:
        print("\nLogin Berhasil!")
        print("Selamat Datang di SISEED", data[1])
        #memanggil menu utama yang sesuai dengan id users, nama serta role nya
        menu_utama(data[0], data[1], data[2])
    else:
        print("\nUsername atau Password Salah!, Silahkan coba lagi!")

    cur.close()

# =====================================================================
#  FITUR PELANGGAN
# =====================================================================

#mengubah angka menjadi format rupiah, contoh: 24000 -> Rp 24.000
def rupiah(angka):
    return "Rp " + f"{angka:,}".replace(",", ".")

#meminta input angka bulat, mengulang terus sampai pengguna mengisi angka yang valid
def input_angka(pesan):
    while True:
        nilai = input(pesan).strip()
        if nilai.lstrip("-").isdigit():
            return int(nilai)
        print(Fore.RED + "Masukkan angka yang valid!")

#mengambil data bibit dari database (harga beli sengaja tidak diambil karena bukan konsumsi pelanggan)

def memasukkan_bibit(Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok):
    conn, cur = connectDB()
    try:
        query = """
            insert into bibit 
            (Nama_Bibit, Jenis_Bibit, Harga_Jual, Stok)
            VALUES (%s, %s, %s, %s)
        """
        

        cur.execute(query, (
            Nama_Bibit,
            Jenis_Bibit, 
            Harga_Jual, 
            Stok
        ))
        conn.commit()
        print("Data bahan berhasil ditambahkan!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan data:", error)

    finally:
        cur.close()
        conn.close()

def membaca_bibit():

    conn, cur = connectDB()

    try:
        query_select = """
            SELECT * FROM bibit
            ORDER BY id_bibit
        """

        cur.execute(query_select)

        data = cur.fetchall()

        data = pd.DataFrame(data, columns=[
            "id_bibit",
            "Nama_bibit",
            "jenis_bibit",
            "harga_beli",
            "harga_jual",
            "stok"
        ])

        data.index += 1

        return data

    finally:
        cur.close()
        conn.close()
            
        

#menampilkan daftar bibit dalam bentuk tabel
def cetak_tabel_bibit(data):
    if data.empty:
        print(Fore.RED + "\nData bibit tidak ditemukan!")
        return
    
     #hanya kolom yang boleh dilihat pelanggan (harga_beli tidak ditampilkan)
    data = data[["id_bibit", "Nama_bibit", "jenis_bibit", "harga_jual", "stok"]]

    print("\n" + "─" * 70)
    print(f"{'ID':<5}{'Nama Bibit':<25}{'Jenis':<18}{'Harga':>12}{'Stok':>10}")
    print("─" * 70)
    for id_bibit, nama, jenis, harga, stok in data.itertuples(index=False):
        teks_stok = str(stok) if stok > 0 else "Habis"
        print(f"{id_bibit:<5}{nama:<25}{jenis:<18}{rupiah(int(harga)):>12}{teks_stok:>10}")
    print("─" * 70)

#================ 1. INFORMASI DATA BIBIT ================
def informasi_data_bibit():
    while True:
        tampilkan_header()
        print("===== INFORMASI DATA BIBIT =====")
        print("1. Lihat Semua Bibit")
        print("2. Cari Bibit Berdasarkan Nama")
        print("3. Filter Bibit Berdasarkan Jenis")
        print("0. Kembali")

        pilihan = input("\nPilih Menu: ")

        try:
            if pilihan == "1":
                cetak_tabel_bibit(membaca_bibit())
                input("\nTekan Enter untuk kembali...")

            elif pilihan == "2":
                kata_kunci = input("\nMasukkan nama bibit: ").strip()
                #ILIKE agar pencarian tidak membedakan huruf besar/kecil
                data = membaca_bibit("WHERE Nama_Bibit ILIKE %s", (f"%{kata_kunci}%",))
                cetak_tabel_bibit(data)
                input("\nTekan Enter untuk kembali...")

            elif pilihan == "3":
                #menampilkan jenis yang ada di database supaya pelanggan tidak menebak-nebak
                conn, cur = connectDB()
                cur.execute("SELECT DISTINCT Jenis_Bibit FROM Bibit ORDER BY Jenis_Bibit")
                daftar_jenis = [baris[0] for baris in cur.fetchall()]
                cur.close()

                print("\nJenis bibit yang tersedia:")
                for i, jenis in enumerate(daftar_jenis, start=1):
                    print(f"{i}. {jenis}")

                nomor = input_angka("\nPilih nomor jenis: ")
                if 1 <= nomor <= len(daftar_jenis):
                    data = membaca_bibit("WHERE Jenis_Bibit = %s", (daftar_jenis[nomor - 1],))
                    cetak_tabel_bibit(data)
                else:
                    print(Fore.RED + "\nNomor jenis tidak tersedia!")
                input("\nTekan Enter untuk kembali...")

            elif pilihan == "0":
                break

            else:
                print(Fore.RED + "\nPilihan tidak tersedia!")
                input("\nTekan Enter untuk kembali...")

        except Exception as error:
            conn.rollback()
            print(Fore.RED + "\nTerjadi kesalahan pada database:", error)
            input("\nTekan Enter untuk kembali...")

#================ BUKTI TRANSAKSI (dipakai pemesanan & riwayat) ================
def cetak_struk(id_penjualan, id_users):
    conn, cur = connectDB()
    try:
        #kondisi ID_Users memastikan pelanggan hanya bisa melihat transaksinya sendiri
        cur.execute("""
            SELECT ID_Penjualan, Tanggal_Penjualan, Total_Penjualan, Metode_Pembayaran
            FROM Penjualan
            WHERE ID_Penjualan = %s AND ID_Users = %s
        """, (id_penjualan, id_users))
        header = cur.fetchone()

        if not header:
            print(Fore.RED + "\nTransaksi tidak ditemukan!")
            return

        cur.execute("""
            SELECT Bibit.Nama_Bibit, Detail_Penjualan.Jumlah_Bibit, Detail_Penjualan.Harga_Jual
            FROM Detail_Penjualan
            JOIN Bibit ON Detail_Penjualan.ID_Bibit = Bibit.ID_Bibit
            WHERE Detail_Penjualan.ID_Penjualan = %s
            ORDER BY Detail_Penjualan.ID_DetailPenjualan
        """, (id_penjualan,))
        detail = cur.fetchall()

        print("\n" + "=" * 60)
        print("BUKTI TRANSAKSI SISEED".center(60))
        print("=" * 60)
        print(f"No. Transaksi : {header[0]}")
        print(f"Tanggal       : {header[1]}")
        print(f"Pembayaran    : {header[3]}")
        print("-" * 60)
        print(f"{'Nama Bibit':<25}{'Jumlah':>8}{'Harga':>12}{'Subtotal':>15}")
        print("-" * 60)
        for nama, jumlah, harga in detail:
            print(f"{nama:<25}{jumlah:>8}{rupiah(harga):>12}{rupiah(jumlah * harga):>15}")
        print("-" * 60)
        print(f"{'TOTAL':<45}{rupiah(header[2]):>15}")
        print("=" * 60)

    except psycopg2.Error as error:
        conn.rollback()
        print(Fore.RED + "\nGagal menampilkan bukti transaksi:", error)

    finally:
        cur.close()

#================ 2. PEMESANAN ================
METODE_PEMBAYARAN = ["Tunai", "Transfer Bank", "QRIS", "E-Wallet"]

def pemesanan(id_users):
    #keranjang berbentuk {id_bibit: {"nama":..., "harga":..., "jumlah":...}}
    keranjang = {}

    #tahap 1: pelanggan memilih bibit dan jumlah
    while True:
        tampilkan_header()
        print("===== PEMESANAN BIBIT =====")

        daftar_bibit = membaca_bibit()
        cetak_tabel_bibit(daftar_bibit)

        if keranjang:
            print(Fore.YELLOW + "\nKeranjang Anda:")
            for item in keranjang.values():
                print(f"- {item['nama']} x{item['jumlah']} = {rupiah(item['harga'] * item['jumlah'])}")

        print("\nMasukkan ID bibit yang ingin dipesan")
        print("(0 = selesai & lanjut pembayaran, 99 = batalkan pesanan)")
        id_pilih = input_angka("ID Bibit: ")

        if id_pilih == 0:
            break

        if id_pilih == 99:
            print(Fore.YELLOW + "\nPesanan dibatalkan.")
            input("\nTekan Enter untuk kembali...")
            return

        #mencari bibit yang dipilih dengan filtering DataFrame
        baris = daftar_bibit[daftar_bibit["id_bibit"] == id_pilih]
        if baris.empty:
            print(Fore.RED + "\nID bibit tidak ditemukan!")
            input("\nTekan Enter untuk lanjut...")
            continue

        #int() agar tipe numpy diubah ke int biasa (psycopg2 tidak bisa menyimpan numpy.int64)
        nama = baris.iloc[0]["Nama_bibit"]
        harga = int(baris.iloc[0]["harga_jual"])
        stok = int(baris.iloc[0]["stok"])

        sudah_di_keranjang = keranjang[id_pilih]["jumlah"] if id_pilih in keranjang else 0
        stok_tersedia = stok - sudah_di_keranjang

        if stok_tersedia <= 0:
            print(Fore.RED + f"\nStok {nama} tidak tersedia!")
            input("\nTekan Enter untuk lanjut...")
            continue

        jumlah = input_angka(f"Jumlah {nama} (maks {stok_tersedia}): ")

        if jumlah <= 0:
            print(Fore.RED + "\nJumlah harus lebih dari 0!")
        elif jumlah > stok_tersedia:
            print(Fore.RED + f"\nStok tidak mencukupi! Tersisa {stok_tersedia}.")
        else:
            if id_pilih in keranjang:
                keranjang[id_pilih]["jumlah"] += jumlah
            else:
                keranjang[id_pilih] = {"nama": nama, "harga": harga, "jumlah": jumlah}
            print(Fore.GREEN + f"\n{nama} x{jumlah} masuk ke keranjang.")

        input("\nTekan Enter untuk lanjut...")


    if not keranjang:
        print(Fore.YELLOW + "\nKeranjang kosong, pesanan tidak dibuat.")
        input("\nTekan Enter untuk kembali...")
        return

    #tahap 2: ringkasan pesanan dan pilih metode pembayaran
    tampilkan_header()
    print("===== RINGKASAN PESANAN =====\n")
    total_perkiraan = 0
    for item in keranjang.values():
        subtotal = item["harga"] * item["jumlah"]
        total_perkiraan += subtotal
        print(f"- {item['nama']:<22} {item['jumlah']:>3} x {rupiah(item['harga']):>11} = {rupiah(subtotal):>12}")
    print(f"\nTotal : {rupiah(total_perkiraan)}")

    print("\nMetode Pembayaran:")
    for i, metode in enumerate(METODE_PEMBAYARAN, start=1):
        print(f"{i}. {metode}")

    while True:
        nomor = input_angka("Pilih metode pembayaran: ")
        if 1 <= nomor <= len(METODE_PEMBAYARAN):
            metode_bayar = METODE_PEMBAYARAN[nomor - 1]
            break
        print(Fore.RED + "Pilihan metode tidak tersedia!")

    konfirmasi = input("\nKonfirmasi pesanan? (y/t): ").strip().lower()
    if konfirmasi != "y":
        print(Fore.YELLOW + "\nPesanan dibatalkan.")
        input("\nTekan Enter untuk kembali...")
        return

    #tahap 3: simpan ke database dalam satu transaksi
    conn, cur = connectDB()
    try:
        total = 0
        total_jumlah = 0
        baris_detail = []

        #id diurutkan supaya urutan penguncian baris konsisten (menghindari deadlock)
        for id_bibit in sorted(keranjang):
            item = keranjang[id_bibit]
            #FOR UPDATE mengunci baris bibit agar stok tidak dipesan ganda oleh pengguna lain
            cur.execute(
                "SELECT Stok, Harga_Jual FROM Bibit WHERE ID_Bibit = %s FOR UPDATE",
                (id_bibit,)
            )
            stok_terbaru, harga_terbaru = cur.fetchone()

            if stok_terbaru < item["jumlah"]:
                raise ValueError(
                    f"Stok {item['nama']} tidak mencukupi (tersisa {stok_terbaru})."
                )

            total += harga_terbaru * item["jumlah"]
            total_jumlah += item["jumlah"]
            baris_detail.append((id_bibit, item["jumlah"], harga_terbaru))

        #menyimpan data transaksi penjualan
        cur.execute("""
            INSERT INTO Penjualan
            (Tanggal_Penjualan, Total_Penjualan, Metode_Pembayaran, Jumlah, ID_Users)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
            RETURNING ID_Penjualan
        """, (total, metode_bayar, total_jumlah, id_users))
        id_penjualan = cur.fetchone()[0]

        #menyimpan rincian bibit dan mengurangi stok
        for id_bibit, jumlah, harga in baris_detail:
            cur.execute("""
                INSERT INTO Detail_Penjualan
                (Jumlah_Bibit, Harga_Jual, ID_Penjualan, ID_Bibit)
                VALUES (%s, %s, %s, %s)
            """, (jumlah, harga, id_penjualan, id_bibit))

            cur.execute(
                "UPDATE Bibit SET Stok = Stok - %s WHERE ID_Bibit = %s",
                (jumlah, id_bibit)
            )

        conn.commit()
        print(Fore.GREEN + "\nPemesanan berhasil!")
        cur.close()
        cetak_struk(id_penjualan, id_users)

    except ValueError as error:
        #stok berubah sejak pelanggan memilih bibit
        conn.rollback()
        print(Fore.RED + "\nPemesanan gagal:", error)
        cur.close()

    except psycopg2.Error as error:
        conn.rollback()
        print(Fore.RED + "\nPemesanan gagal:", error)
        cur.close()

    input("\nTekan Enter untuk kembali...")

#================ 3. RIWAYAT PEMBELIAN ================
def riwayat_pembelian(id_users):
    while True:
        tampilkan_header()
        print("===== RIWAYAT PEMBELIAN =====")

        conn, cur = connectDB()
        try:
            cur.execute("""
                SELECT ID_Penjualan, Tanggal_Penjualan, Jumlah, Total_Penjualan, Metode_Pembayaran
                FROM Penjualan
                WHERE ID_Users = %s
                ORDER BY Tanggal_Penjualan DESC, ID_Penjualan DESC
            """, (id_users,))
            riwayat = cur.fetchall()
        except psycopg2.Error as error:
            conn.rollback()
            print(Fore.RED + "\nGagal mengambil riwayat:", error)
            input("\nTekan Enter untuk kembali...")
            return
        finally:
            cur.close()

        if not riwayat:
            print(Fore.YELLOW + "\nAnda belum memiliki riwayat pembelian.")
            input("\nTekan Enter untuk kembali...")
            return

        print("\n" + "─" * 72)
        print(f"{'No.Transaksi':<14}{'Tanggal':<14}{'Jumlah':>8}{'Total':>16}  {'Pembayaran'}")
        print("─" * 72)
        for id_jual, tanggal, jumlah, total, metode in riwayat:
            print(f"{id_jual:<14}{str(tanggal):<14}{jumlah:>8}{rupiah(total):>16}  {metode}")
        print("─" * 72)

        id_pilih = input_angka("\nMasukkan No. Transaksi untuk lihat bukti (0 = kembali): ")

        if id_pilih == 0:
            return

        cetak_struk(id_pilih, id_users)
        input("\nTekan Enter untuk kembali...")


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
                print("\nPengelolaan Data Bibit")

            elif pilihan == "2":
                print("\nPengelolaan Akun")

            elif pilihan == "3":
                print("\nPengelolaan Data Pemasok")

            elif pilihan == "4":
                print("\nTransaksi Pembelian")

            elif pilihan == "5":
                print("\nLaporan Toko")

            else:
                print(Fore.RED + "\nPilihan tidak tersedia!")

        # pilihan menu untuk kasir
        elif role.lower() == "kasir":
            if pilihan == "1":
                print("\nTransaksi Penjualan")

            else:
                print(Fore.RED + "\nPilihan tidak tersedia!")

        #pilihan menu untuk pelanggan
        elif role.lower() == "pelanggan":
            if pilihan == "1":
                print("\nInformasi Data Bibit")
                print(membaca_bibit())
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
                
#logout
def logout():
    print(Fore.GREEN + "\nAnda berhasil logout! Sampai jumpa!")

#halaman logout
def logout():
    pilihan = input("\nApakah anda yakin ingin logout? (y/t): ")

    if pilihan == "y":
        tampilkan_header()
        print("\n Anda berhasil logout! Sampai jumpa!")
    #menampilkan ini jika pelanggan membatalkan 
    else:
        print("\n Anda tetap berada di SISEED!")

#halaman awal
def halaman_awal():
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

#menjalankan halaman awal program
halaman_awal()
