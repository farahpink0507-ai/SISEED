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
