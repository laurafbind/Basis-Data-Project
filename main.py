import psycopg2
import os
from main_pegawai import main_pegawai
from main_pelanggan import main_pelanggan

def get_db_connection():
    connection = psycopg2.connect(dbname="kopus2", user="postgres", password="12345", host="localhost", port=5432)
    return connection

def login_pegawai(cursor):
    print("\nMasukkan data untuk login: ")
    username = input("\nUsername: ")
    password = input("Password: ")
    
    sql = "SELECT * FROM pegawai WHERE username = %s AND password = %s"
    cursor.execute(sql, (username, password))
    result = cursor.fetchone()
    
    if result:
        print("Login berhasil sebagai pegawai.")
        return True
    else:
        print("Username atau password salah.")
        return False   
    
def login_pelanggan(cursor):
    os.system("cls")
    print("\n\n'Masuk sebagai pelanggan'")
    print("_" * 25)
    username = input("Username: ")
    password = input("Password: ")
    
    sql = "SELECT * FROM pelanggan WHERE username = %s AND password = %s"
    cursor.execute(sql, (username, password))
    result = cursor.fetchone()
    
    if result:
        print("Login berhasil sebagai pelanggan.")
        return username  
    else:
        print("Username atau password salah.")
        return None
    
def create_akun_pelanggan(cursor, connection):
    os.system("cls")
    print("\n'Selamat datang pelanggan:'")
    nama = input("Masukkan nama: ")
    username = input("Masukkan username: ")
    password = input("Masukkan password: ")
    email = input("Masukkan email: ")
    no_telp = input("Masukkan no telp: ")

    cursor.execute("SELECT COUNT(*) FROM pelanggan WHERE username = %s", (username,))
    username_exists = cursor.fetchone()[0]
    if username_exists:
        print("Username sudah ada. Tekan Enter untuk kembali ke beranda.")
        input()
        return
    cursor.execute("SELECT COUNT(*) FROM pelanggan WHERE email = %s", (email,))
    email_exists = cursor.fetchone()[0]
    if email_exists:
        print("Email sudah ada. Tekan Enter untuk kembali ke beranda.")
        input()
        return
    sql = """
    INSERT INTO pelanggan (nama, username, password, email, no_telp)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (nama, username, password, email, no_telp))
    connection.commit()
    

def main_utama():
    os.system('cls')
    connection = get_db_connection()
    cursor = connection.cursor()

    while True:
        os.system("cls")
        print("=" * 30)
        print("SELAMAT DATANG DI KOPUS.CO:")
        print("=" * 30 ,'\n')
        print("Masuk sebagai:")
        print("1. Pegawai")
        print("2. Pelanggan")
        choice = input("Pilih menu nomor: ")
        

        if choice == '1':
            os.system('cls')
            print("=" * 22)
            print("\tPegawai")
            print("=" * 22)
            if login_pegawai(cursor):
                    main_pegawai()
            else:
                input("\nTekan enter untuk kembali")

        elif choice == '2':
            os.system('cls')
            print("=" * 22)
            print("\tPelanggan")
            print("=" * 22)
            print("Sudah punya akun?")
            print("1. Login")
            print("2. Register")
            print("ketik 2 apabila belum memiliki akun")
            data = input("Pilih nomor: ")
            if data == "2":
                username = create_akun_pelanggan(cursor, connection)
                print(input("\nBerhasil membuat akun pelanggan."))
                main_pelanggan(username)
            elif data == "1":
                os.system('cls')
                username = login_pelanggan(cursor)
                if username:
                    main_pelanggan(username)
                else:
                    print("Login gagal: nama atau password salah.")
                    input("\nTekan enter untuk kembali")
            cursor.close()
            connection.close()
        else:
            print("Pilihan tidak tersedia, coba lagi!") 
if __name__ == "__main__":
    main_utama()
    os.system('cls')