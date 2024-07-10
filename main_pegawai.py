import psycopg2
import os
import datetime

def get_db_connection():
    connection = psycopg2.connect(dbname="kopus2", user="postgres", password="12345", host="localhost", port=5432)
    return connection


#------------------MENU-------------------
def create_menu(cursor, connection):
    nama_menu = input("Masukkan menu: ")
    harga = int(input("harga: "))
    deskripsi = input("deskripsi: ")
    jenis_id = int(input("1. Makanan\n2. Minuman\n3. Cemilan\nPilih Kategori ID: "))

    insert_query = """
    INSERT INTO menu (nama_menu, harga, deskripsi, jenis_id)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_query, (nama_menu, harga, deskripsi, jenis_id))
    connection.commit()
    print("Menu berhasil ditambahkan.")

def read_menu(cursor):
    cursor.execute(
        """SELECT m.menu_id, m.nama_menu, m.harga,  m.deskripsi, j.jenis_menu 
        FROM menu m 
        JOIN jenis j ON (m.jenis_id = j.jenis_id)"""
    )
    menu = cursor.fetchall()
    print("Daftar menu :")
    print("_" * 10)
    for row in menu:
        menu_id, nama_menu, harga,  deskripsi, jenis_menu = row
        print("Menu ID:\t", menu_id)
        print("Nama Menu:\t", nama_menu)
        print("Harga:\t\t", harga)
        print("Deskripsi:\t", deskripsi)
        print("Jenis Menu:\t", jenis_menu)
        print("-" * 10)

def update_menu(cursor, connection, harga: int, id: int) -> bool:
    sql = f"UPDATE menu SET harga = %s WHERE menu_id = %s"
    cursor.execute(sql, ( harga, id))
    connection.commit()
    return cursor.rowcount > 0

#---------------MAIN MENU-----------------
def main_menu(cursor, connection): 
    while True:
        os.system("cls")
        print("\nMenu:")
        print("="*6)
        print("1. Tambahkan menu")
        print("2. Edit menu")
        print("3. Exit")

        choice = input("Pilih: ")
        if choice == '1':
            os.system("cls")
            create_menu(cursor, connection)
            input("\nTekan Enter untuk kembali.")
        elif choice == '2':
            os.system("cls")
            read_menu(cursor)
            id = int(input("Masukkan ID menu yang akan diupdate: "))
            harga = int(input("Masukkan harga baru: "))
            if update_menu(cursor, connection, harga, id):
                print("Menu berhasil diupdate.")
            else:
                print("Menu tidak ditemukan atau update gagal.")
            input("\nTekan Enter untuk kembali.")
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

#------------------MEJA---------------------
def read_meja(cursor):
    sql = """SELECT m.meja_id, m.nomer_meja, m.status, r.rsv_tempat_id 
        FROM meja m 
        LEFT JOIN rsv_tempat r 
        ON r.meja_id = m.meja_id"""
    cursor.execute(sql)
    meja = cursor.fetchall()
    if not meja:
        print("Tidak ada data meja yang ditemukan.")
        return
    print("Status meja:\n")
    print("|id | \tnomer\t | status  | rsv_id |")
    print("------------------------------------")
    for row in meja:
        meja_id, nomer_meja, status, rsv_tempat_id = row
        print(f"|{meja_id} | \t{nomer_meja} | \t{status}\t | \t{rsv_tempat_id} |")


def update_meja(cursor, connection, status: str, meja_id: int) -> bool: 
    read_meja(cursor)
    os.system("cls")
    if status is None or status == '':
        sql = "UPDATE meja SET status = NULL WHERE meja_id = %s"
        cursor.execute(sql, (meja_id,))
    else:
        sql = "UPDATE meja SET status = %s WHERE meja_id = %s"
        cursor.execute(sql, (status, meja_id))
    connection.commit()
    return cursor.rowcount > 0

#---------------------MAIN MEJA-------------------------

def read_update_meja(cursor, connection):
    os.system("cls")
    print("\nKelola status nomor meja")
    read_meja(cursor)
    meja_id = input("Masukkan ID meja yang akan diupdate: ")
    if not meja_id.isdigit():
        print("Inputan tidak tepat. ID meja harus berupa angka.")
    meja_id = int(meja_id)
    status = input("Status (reserved/kosongkan jika tidak ada): ")
    if status == '':
        status = None
        if update_meja(cursor, connection, status, meja_id):
                print("\nData meja berhasil diupdate.")
        else:
                print("Gagal update data meja.")
    input("\nTekan Enter untuk kembali.")


#-------------------- TRANSAKSI----------------------

def read_pg_transaksi(cursor):
    cursor.execute(
        '''SELECT pegawai_id, nama 
        FROM pegawai  
        ORDER BY pegawai_id''')
    pegawai = cursor.fetchall()
    print("Daftar akun pegawai :")
    for row in pegawai:
        pegawai_id, nama = row
        print("Pegawai ID:\t\t", pegawai_id)
        print("Nama:\t\t", nama)
        print("-" * 10)

def read_transaksi(cursor):
    sql= '''
    SELECT t.transaksi_id, t.waktu_transaksi, r.rsv_tempat_id, r.tanggal_kedatangan, r.waktu_kedatangan, p.username, 
    r.nama_acara, m.nomer_meja, d.detail_rsv_id, me.nama_menu, d.jumlah_pesanan, t.transaksi_id, p2.nama as pegawai,
    SUM(d.jumlah_pesanan * me.harga ) AS total_biaya
    FROM rsv_tempat r
    JOIN pelanggan p ON r.pelanggan_id = p.pelanggan_id
    LEFT JOIN meja m ON r.meja_id = m.meja_id
    LEFT JOIN detail_rsv d ON r.rsv_tempat_id = d.rsv_tempat_id
    JOIN transaksi t ON r.rsv_tempat_id = t.rsv_tempat_id
    LEFT JOIN pegawai p2 ON t.pegawai_id = p2.pegawai_id
    LEFT JOIN menu me ON d.menu_id = me.menu_id
    WHERE d.detail_rsv_id IS NOT NULL
    GROUP BY 
        t.transaksi_id,
        r.rsv_tempat_id,
        d.detail_rsv_id,
        m.nomer_meja,
        me.nama_menu,
        p.username,
        p2.nama
    ORDER BY r.rsv_tempat_id, d.detail_rsv_id
    '''
    cursor.execute(sql,)
    data = cursor.fetchall()
    
    if data:
        current_rsv_id = None
        print("Daftar Detail Reservasi Pelanggan:\n\n")
        
        for row in data:
            transaksi_id, waktu_transaksi, rsv_tempat_id, tanggal_kedatangan, waktu_kedatangan, username, nama_acara, nomer_meja, detail_rsv_id, nama_menu, jumlah_pesanan, transaksi_id, pegawai, total_biaya = row
            
            if rsv_tempat_id != current_rsv_id:
                if current_rsv_id is not None:
                    print(("_") * 60,"\n\n\n")
                current_rsv_id = rsv_tempat_id
                print(("_") * 60)
                print(f"ID Transaksi: {transaksi_id}")
                print(f"Waktu Transaksi: {waktu_transaksi}")
                print(f"ID Reservasi: {rsv_tempat_id}")
                print(f"Tanggal Kedatangan: {tanggal_kedatangan}")
                print(f"Waktu Kedatangan: {waktu_kedatangan}")
                print(f"Pelanggan: {username}")
                print(f"Nama Acara: {nama_acara}")
                print(f"Nomer Meja: {nomer_meja if nomer_meja else 'None'}")
                print(f"Pegawai: {pegawai if pegawai else 'None'}")
                print(f"Total Biaya: {total_biaya}")
                print("-" * 60)
                print(f"{'Detail ID':<13}{'Nama Menu':<20}{'Jumlah Pesanan':<15}")
                print("-" * 60)
            print(f"{detail_rsv_id:<13}{nama_menu:<20}{jumlah_pesanan:<15}")
        print("_" * 60)
    else:
        print("Tidak ada yang memiliki detail reservasi.")

def update_transaksi(cursor, connection, pegawai_id: int, transaksi_id: int) -> bool:
    sql = "UPDATE transaksi SET pegawai_id = %s WHERE transaksi_id = %s"
    cursor.execute(sql, (pegawai_id, transaksi_id))
    connection.commit()
    return cursor.rowcount > 0

# ---------------KONFIRMASI TRANSAKSI OLEH PEGAWAI----------------------

def update_pg_transaksi(cursor, connection):
    read_transaksi(cursor)
    transaksi_id = int(input("Masukkan ID transaksi yang ingin diperbarui: "))
    os.system("cls")
    read_pg_transaksi(cursor)
    pegawai_id = input("Masukkan ID pegawai (kosongkan): ")
    if pegawai_id.strip() == '':
        pegawai_id = None
    else:
        pegawai_id = int(pegawai_id)
    if update_transaksi(cursor, connection, pegawai_id, transaksi_id):
        
        print("Transaksi berhasil diperbarui.")
    else:
        print("Transaksi tidak ditemukan atau tidak ada perubahan.")



#--------------------PEGAWAI----------------------

def create_pegawai(cursor, connection):
    print("Tambah data pegawai:\n")
    nama = input("Masukkan nama: ")
    username = input("Masukkan username: ")
    password = input("Masukkan password: ")
    email = input("Masukkan email: ")
    no_telp = input("Masukkan no telp: ")
    alamat = input("Masukkan alamat: ")
    kota_id = input("\n1. Jember \n2. Banyuwangi\n3. Bondowoso\nMasukkan id kota: ")

    sql = """
    INSERT INTO pegawai (nama, username, password, email, no_telp, alamat, kota_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (nama, username, password, email, no_telp, alamat, kota_id))
    connection.commit() 
    print("\nPegawai berhasil ditambahkan.")

def read_pegawai(cursor):
    cursor.execute(
        '''SELECT p.pegawai_id, p.nama, p.no_telp, p.email, p.alamat || ',' || k.nama_kota AS asal
        FROM pegawai p
        JOIN kota k ON p.kota_id = k.kota_id 
        ORDER BY pegawai_id;''')
    pegawai = cursor.fetchall()
    print("Daftar akun pegawai :")
    for row in pegawai:
        pegawai_id, nama, no_telp, email, asal = row
        print("Pegawai ID:\t\t", pegawai_id)
        print("Nama:\t\t", nama)
        print("Nomer telepon:\t", no_telp)
        print("Email:\t\t", email)
        print("Asal:\t\t", asal)
        print("-" * 10)

def update_pegawai(cursor, connection, alamat: str, password: str, id: int) -> bool:
    sql = f"UPDATE pegawai SET alamat = %s, password = %s WHERE pegawai_id = %s"
    cursor.execute(sql, (alamat, password, id))
    connection.commit()
    return cursor.rowcount > 0

#-------------------MAIN AKUN PEGAWAI-----------------------
def read_update_pegawai(cursor, connection): 
    while True:
        os.system("cls")
        print("\nLihat dan kelola akun pegawai:")
        print("1. Lihat akun pegawai")
        print("2. Menambahkan akun pegawai")
        print("3. Ubah akun pegawai")
        print("4. Exit")
        choice = input("\nPilih: ")
        if choice == '1':
            os.system("cls")
            read_pegawai(cursor)
            input("\nTekan Enter untuk kembali.")
        elif choice == '2':
            os.system("cls")
            create_pegawai(cursor, connection)
            input("\nTekan Enter untuk kembali.")
        elif choice == '3':
            os.system("cls")
            read_pegawai(cursor)
            id = int(input("Masukkan ID akun yang akan diubah: "))
            alamat = input("Masukkan alamat baru: ")
            password = input("Masukkan password baru: ")
            if update_pegawai(cursor, connection, alamat, password, id):
                print("\nAkun pegawai berhasil diupdate.")
            else:
                print("Gagal mengupdate akun pegawai.")
            input("Tekan Enter untuk kembali.")
        elif choice == '4':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")


#--------------------------RESERVASI----------------------------

def read_rsv_details(cursor):
    sql = '''
    SELECT r.rsv_tempat_id, r.tanggal_kedatangan, r.waktu_kedatangan, p.username, r.nama_acara, m.nomer_meja, 
    d.detail_rsv_id, me.nama_menu, d.jumlah_pesanan, t.transaksi_id, p2.nama as pegawai,
    SUM(d.jumlah_pesanan * me.harga ) AS total_biaya
    FROM rsv_tempat r
    JOIN pelanggan p ON r.pelanggan_id = p.pelanggan_id
    LEFT JOIN meja m ON r.meja_id = m.meja_id
    LEFT JOIN detail_rsv d ON r.rsv_tempat_id = d.rsv_tempat_id
    LEFT JOIN transaksi t ON r.rsv_tempat_id = t.rsv_tempat_id
    LEFT JOIN pegawai p2 ON t.pegawai_id = p2.pegawai_id
    LEFT JOIN menu me ON d.menu_id = me.menu_id
    WHERE d.detail_rsv_id IS NOT NULL
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
    cursor.execute(sql)
    data = cursor.fetchall()
    
    if data:
        current_rsv_id = None
        print("Daftar Detail Reservasi Pelanggan:\n\n")
        
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
    else:
        print("Tidak ada yang memiliki detail reservasi.")
        

def delete_rsv_tempat(cursor, connection, id: int) -> None:
    sql = "DELETE FROM rsv_tempat WHERE rsv_tempat_id = %s"
    cursor.execute(sql, (id,))
    connection.commit()
    if cursor.rowcount > 0:
        print("Reservasi berhasil dihapus.")
    else:
        print("Reservasi tidak ditemukan atau sudah dihapus.")

def update_reservasi(cursor, connection, meja_id: int, id: int) -> bool:
    if meja_id is None or meja_id == '':
        sql = "UPDATE rsv_tempat SET meja_id = NULL WHERE rsv_tempat_id = %s"
        cursor.execute(sql, (id,))
    else:
        sql = "UPDATE rsv_tempat SET meja_id = %s WHERE rsv_tempat_id = %s"
        cursor.execute(sql, (meja_id, id))
    
    connection.commit()
    return cursor.rowcount > 0

# -----------------------MAIN RESERVASI-------------------

def read_update_rsv(cursor, connection): 
    while True:
        os.system("cls")
        print("\nPilih Kelola Reservasi:")
        print("="*10)
        print("1. Lihat data reservasi")
        print("2. Hapus reservasi")
        print("3. Exit")
        
        choice = input("Pilih: ")
        if choice == '1':
            os.system("cls")
            read_rsv_details(cursor)
            input("\nTekan Enter untuk kembali.")
        elif choice == '2':
            os.system("cls")
            read_rsv_details(cursor)
            id = int(input("Masukkan ID reservasi yang akan dihapus: "))
            delete_rsv_tempat(cursor, connection, id)
            input("\nTekan Enter untuk kembali.")
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

#-------------------MAIN TRANSAKSI-------------------------

def main_transaksi(cursor,connection):
    while True:
        os.system("cls")
        print("\nPilih Kelola Transaksi:")
        print("="*20)
        print("1. Lihat data transaksi")
        print("2. Konfirmasi Transaksi")
        print("3. Exit")
        
        choice = input("Pilih: ")
        if choice == '1':
            os.system("cls")
            read_transaksi(cursor)
            input("\nTekan Enter untuk kembali.")
            os.system("cls")
        elif choice == '2':
            os.system("cls")
            read_transaksi(cursor)
            id = int(input("Masukkan ID reservasi untuk reservasi meja: "))
            os.system("cls")
            read_meja(cursor)
            print(f"ID reservasi terakhir yang dipilih: {id}\n\n")
            meja_id = input("Masukkan ID meja untuk direservasi: ")
            if update_reservasi(cursor, connection, meja_id, id):
                print("Reservasi berhasil diupdate.")
            else:
                print("Reservasi tidak ditemukan atau update gagal.")
            os.system("cls")
            update_pg_transaksi(cursor, connection)
        elif choice == '3':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")


#-------------------BERANDA PEGAWAI-------------------------

def main_pegawai():
    connection = get_db_connection()
    cursor = connection.cursor()
    while True:
        os.system("cls")
        print("\nMenu Utama:")
        print("="*10)
        print("1. Kelola Pegawai")
        print("2. Kelola Menu")
        print("3. Kelola Reservasi")
        print("4. Kelola Transaksi")
        print("5. Kelola Status Meja")
        print("6. Exit")
        
        choice = input("Pilih: ")
        if choice == '1':
            os.system("cls")
            read_update_pegawai(cursor, connection)
        elif choice == '2':
            os.system("cls")
            main_menu(cursor, connection)
        elif choice == '3':
            os.system("cls")
            read_update_rsv(cursor, connection)
        elif choice == '4':
            os.system("cls")
            main_transaksi(cursor,connection)
        elif choice == '5':
            os.system("cls")
            read_update_meja(cursor, connection)
        elif choice == '6':
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main_pegawai()