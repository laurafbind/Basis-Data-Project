
import psycopg2
import datetime
import os
from transaksi import read_rsv_pelanggan,process_payment
import time

def get_db_connection():
    connection = psycopg2.connect(dbname="kopus2", user="postgres", password="12345", host="localhost", port=5432)
    return connection

#----------------------MENU----------------------
def read_menu(cursor):
    cursor.execute(
        """SELECT m.menu_id, m.nama_menu, m.harga, m.deskripsi, j.jenis_menu 
        FROM menu m 
        JOIN jenis j ON (m.jenis_id = j.jenis_id)
        ORDER BY m.menu_id"""
    )
    menu = cursor.fetchall()
    print("Daftar menu :")
    print("_" * 10)
    for row in menu:
        menu_id, nama_menu, harga, deskripsi, jenis_menu = row
        print("Menu ID:\t", menu_id)
        print("Nama Menu:\t", nama_menu)
        print("Harga:\t\t", harga)
        print("Deskripsi:\t", deskripsi)
        print("Jenis Menu:\t", jenis_menu)
        print("-" * 10)

#-------------------------RESERVASI-----------------------------
def create_rsv(cursor, connection, username):
    print("=" * 15)
    print("Buat reservasi:")
    print("=" * 15)
    tanggal_kedatangan = input("Masukkan tanggal kedatangan (YYYY-MM-DD): ")
    waktu_kedatangan = input("Masukkan waktu kedatangan (HH:MM): ")
    jumlah_orang = input("Masukkan jumlah orang: ")
    nama_acara = input("Masukkan nama acara: ")

    cursor.execute("SELECT pelanggan_id FROM pelanggan WHERE username = %s", (username,))
    pelanggan_id_result = cursor.fetchone()
    if pelanggan_id_result is None:
        print(f"Error: Username '{username}' tidak ditemukan.")
        return None
    pelanggan_id = pelanggan_id_result[0]
    sql = '''
    INSERT INTO rsv_tempat (tanggal_kedatangan, waktu_kedatangan, jumlah_orang, nama_acara, pelanggan_id)
    VALUES (%s, %s, %s, %s, %s) RETURNING rsv_tempat_id
    '''
    cursor.execute(sql, (tanggal_kedatangan, waktu_kedatangan, jumlah_orang, nama_acara, pelanggan_id))
    rsv_tempat = cursor.fetchone()[0]
    connection.commit()
    return rsv_tempat


def read_rsv_details(cursor, username):
    sql = '''
    SELECT r.rsv_tempat_id, r.tanggal_kedatangan, r.waktu_kedatangan, p.username, r.nama_acara, m.nomer_meja, d.detail_rsv_id, me.nama_menu, d.jumlah_pesanan, t.transaksi_id, p2.nama as pegawai,
    SUM(d.jumlah_pesanan * me.harga ) AS total_biaya
    FROM rsv_tempat r
    JOIN pelanggan p ON r.pelanggan_id = p.pelanggan_id
    LEFT JOIN meja m ON r.meja_id = m.meja_id
    LEFT JOIN detail_rsv d ON r.rsv_tempat_id = d.rsv_tempat_id
    LEFT JOIN transaksi t ON r.rsv_tempat_id = t.rsv_tempat_id
    LEFT JOIN pegawai p2 ON t.pegawai_id = p2.pegawai_id
    LEFT JOIN menu me ON d.menu_id = me.menu_id
    WHERE p.username = %s AND d.detail_rsv_id IS NOT NULL
    GROUP BY 
        r.rsv_tempat_id,
        d.detail_rsv_id,
        m.nomer_meja,
        me.nama_menu,
        t.transaksi_id,
        p.username,
        p2. nama
    ORDER BY r.rsv_tempat_id, d.detail_rsv_id
    '''
    cursor.execute(sql, (username,))
    data = cursor.fetchall()
    
    if data:
        current_rsv_id = None
        print("Daftar Detail Reservasi Anda:\n\n")
        
        for row in data:
            rsv_tempat_id, tanggal_kedatangan, waktu_kedatangan, username, nama_acara, nomer_meja, detail_rsv_id, nama_menu, jumlah_pesanan, transaksi_id, nama, total_biaya= row
            
            if rsv_tempat_id != current_rsv_id:
                if current_rsv_id is not None:
                    print(("_") * 60,"\n\n\n")
                current_rsv_id = rsv_tempat_id
                print(("_") * 60)
                print(f"ID Reservasi: {rsv_tempat_id}")
                print(f"Tanggal Kedatangan: {tanggal_kedatangan}")
                print(f"Waktu Kedatangan: {waktu_kedatangan}")
                print(f"Pelanggan: {username}")
                print(f"Nama Acara: {nama_acara}")
                print(f"Nomer Meja: {nomer_meja if nomer_meja else 'None'}")
                print(f"ID transaksi: {transaksi_id}")
                print(f"Pegawai: {nama if nama else 'None'}")
                print(f"Total biaya: {total_biaya}")
                print("-" * 60)
                print(f"{'Detail ID':<13}{'Nama Menu':<20}{'Jumlah Pesanan':<15}")
                print("-" * 60)
            print(f"{detail_rsv_id:<13}{nama_menu:<20}{jumlah_pesanan:<15}")
        print("_" * 60)
        print(f"=============ID reservasi terakhir Anda: {rsv_tempat_id}=============\n\n")
    else:
        print("Anda belum memiliki detail reservasi.")



#---------------------DETAIL RSV---------------------
def create_detail_rsv(cursor, connection, rsv_tempat_id, menu_id, jumlah_pesanan):
    sql = '''
    INSERT INTO detail_rsv (rsv_tempat_id, menu_id, jumlah_pesanan)
    VALUES (%s, %s, %s) RETURNING detail_rsv_id
    '''
    cursor.execute(sql, (rsv_tempat_id, menu_id, jumlah_pesanan))
    detail_rsv = cursor.fetchone()[0]
    connection.commit()
    print("\nDetail reservasi telah ditambahkan")
    return detail_rsv
# -----------------------------------------------------
def read_update_rsv_pelanggan(cursor, connection, username):
    while True:
        os.system("cls")
        print("Menu Reservasi Pelanggan:")
        print("=" * 25)
        print("1. Lihat Detail Reservasi")
        print("2. Buat Reservasi")
        print("3. Exit")

        choice = input("Pilih: ")
        if choice == '1':
            os.system("cls")
            read_rsv_details(cursor, username)
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == '2':
            os.system("cls")
            rsv_tempat_id = create_rsv(cursor, connection, username)
            if rsv_tempat_id is None:
                input("\nTekan Enter untuk kembali ke menu...")
                continue
            os.system("cls")
            print("\nMenambahkan detail reservasi pesanan:\n")
            print ("-"*20)
            print(f"ID reservasi terakhir Anda: {rsv_tempat_id}\n\n")
            read_menu(cursor)
            print('\n')
            while True:
                menu_id = int(input("Masukkan satu menu ID: "))
                jumlah_pesanan = int(input("Masukkan jumlah pesan: "))
                create_detail_rsv(cursor, connection, rsv_tempat_id, menu_id, jumlah_pesanan)
                more = input("Apakah Anda ingin menambah pesanan lagi? (y/n): ")
                os.system("cls")
                read_menu(cursor)
                if more.lower() != 'y':
                    break
        elif choice == '3':
            break

# ---------------------MAIN TRANSAKSI------------------------

def main_transaksi(username):
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    while True:
        os.system("cls")
        print("Transaksi:")
        print("-" * 10)
        print("1. Lihat Transaksi")
        print("2. Ajukan Transaksi Reservasi")
        print("3. Exit")

        choice = input("Pilih menu nomor: ")
        os.system("cls")

        if choice == '1':
            read_rsv_pelanggan(cursor, username)
            input("\nEnter untuk kembali")
            os.system("cls")
        elif choice == '2':
            process_payment(cursor, connection, username)
            os.system("cls")
        elif choice == '3':
            break
        else:
            print(input("Pilihan tidak valid. Silakan coba lagi."))
            os.system("cls")

# -----------------------------------------------------------

def main_pelanggan(username):
    connection = get_db_connection()
    cursor = connection.cursor()

    while True:
        os.system("cls")
        print("=" * 15)
        print("Menu Pelanggan:")
        print("=" * 15)
        print("1. Lihat Menu")
        print("2. Reservasi")
        print("3. Transaksi")
        print("4. Exit")

        choice = input("Pilih menu nomor: ")
        if choice == '1':
            os.system("cls")
            read_menu(cursor)
            input("\nTekan Enter untuk kembali.")
        elif choice == '2':
            read_update_rsv_pelanggan(cursor, connection, username)
        elif choice == '3':
            main_transaksi(username)
        elif choice == '4': 
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    os.system("cls")
    username = input("username: ")
    main_pelanggan(username)