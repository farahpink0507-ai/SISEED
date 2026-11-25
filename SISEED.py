
import os
import time
import shutil
import pyfiglet
from colorama import Fore, Style, init

# tes
init(autoreset=True)

def bersihkan_layar():
    
    os.system('cls' if os.name == 'nt' else 'clear')

def tampilkan_header():
    bersihkan_layar()
    
    lebar_layar = shutil.get_terminal_size((80, 20)).columns

    panjang_garis_atas = lebar_layar - 6
    print(Fore.YELLOW + "୨୧ " + "─" * panjang_garis_atas + " ୨୧\n")

    banner = pyfiglet.figlet_format("SiSeed", font="ansi_shadow")
    for baris in banner.splitlines():
        print(Fore.GREEN + Style.BRIGHT + baris.center(lebar_layar))

    # --- GARIS BAWAH HIJAU & SUBJUDUL ---
    panjang_garis_bawah = int(lebar_layar * 0.7) 
    garis_bawah = "୨୧ " + "─" * panjang_garis_bawah + " ୨୧"
    print(Fore.YELLOW + garis_bawah.center(lebar_layar))
    
    subjudul = "SISTEM INFORMASI PENGELOLAAN DATA BIBIT TANAMAN"
    print(Fore.LIGHTGREEN_EX + subjudul.center(lebar_layar) + "\n")

def halaman_login():
    tampilkan_header()
    print(Fore.CYAN + Style.BRIGHT + "=== LOGIN PENGGUNA ===\n")
    username = input(Fore.WHITE + "Username : ")
    password = input(Fore.WHITE + "Password : ")
    
    print(Fore.GREEN + f"\n[✓] Login berhasil! Selamat datang, {username}.")
    time.sleep(3)

def halaman_registrasi():
    tampilkan_header()
    print(Fore.CYAN + Style.BRIGHT + "=== REGISTRASI USER BARU ===\n")
    nama_lengkap = input(Fore.WHITE + "Buat Nama Lengkap : ")
    username = input(Fore.WHITE + "Buat Username : ")
    password = input(Fore.WHITE + "Buat Password : ")
    no_telp = int(input(Fore.WHITE + "Buat No.Telp : "))
    alamat = input(Fore.WHITE + "Buat Alamat (opsional) : ")
    
    print(Fore.GREEN + f"\n[✓] Akun '{username}' berhasil didaftarkan!")
    time.sleep(3)

def main():
    while True:
        tampilkan_header()
        
        # Daftar Menu Utama
        print(Fore.WHITE + "1. Login")
        print(Fore.WHITE + "2. Registrasi user baru")
        print(Fore.WHITE + "0. Keluar")
        
        pilihan = input(Fore.WHITE + "Pilih menu: ")

        if pilihan == "1":
            halaman_login()
        elif pilihan == "2":
            halaman_registrasi()
        elif pilihan == "0":
            print(Fore.YELLOW + "\nKeluar dari program. Sampai jumpa!")
            break
        else:
            print(Fore.RED + "\n[!] Pilihan tidak valid. Silakan masukkan 1, 2, atau 0.")
            time.sleep(1.2)

if __name__ == "__main__":
    main()

    jjj
