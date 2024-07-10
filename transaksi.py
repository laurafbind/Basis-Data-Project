import psycopg2
from datetime import datetime
import os

def create_connection():
    return psycopg2.connect(
        dbname="kopu2", user="postgres", password="12345", host="localhost", port=5432)

def read_unpaid_transaksi(cursor, username):
    sql = '''
    SELECT t.transaksi_id, t.waktu_transaksi, r.rsv_tempat_id, r.tanggal_kedatangan, r.waktu_kedatangan, p.username, r.nama_acara, m.nomer_meja, d.detail_rsv_id, me.nama_menu, d.jumlah_pesanan, SUM(d.jumlah_pesanan * me.harga) AS total_biaya
    FROM rsv_tempat r
    JOIN pelanggan p ON r.pelanggan_id = p.pelanggan_id
    LEFT JOIN meja m ON r.meja_id = m.meja_id
    LEFT JOIN detail_rsv d ON r.rsv_tempat_id = d.rsv_tempat_id
    LEFT JOIN menu me ON d.menu_id = me.menu_id
    LEFT JOIN transaksi t ON r.rsv_tempat_id = t.rsv_tempat_id
    WHERE p.username = %s AND t.transaksi_id IS NULL
    GROUP BY 
        r.rsv_tempat_id,
        r.tanggal_kedatangan,
        r.waktu_kedatangan,
        p.username,
        r.nama_acara,
        m.nomer_meja,
        d.detail_rsv_id,
        me.nama_menu,
        d.jumlah_pesanan,
        t.transaksi_id,
        t.waktu_transaksi
    ORDER BY r.rsv_tempat_id, d.detail_rsv_id
    '''
    cursor.execute(sql, (username,))
    data = cursor.fetchall()
    
    if data:
        current_rsv_id = None
        print("Daftar Detail Reservasi yang Belum Dibayar:\n\n")
        
        for row in data:
            transaksi_id, waktu_transaksi,rsv_tempat_id, tanggal_kedatangan, waktu_kedatangan, username, nama_acara, nomer_meja, detail_rsv_id, nama_menu, jumlah_pesanan, total_biaya= row
            if waktu_transaksi:
                waktu_transaksi = waktu_transaksi.strftime("%Y-%m-%d %H:%M")
            if rsv_tempat_id != current_rsv_id:
                if current_rsv_id is not None:
                    print(("_") * 60, "\n\n\n")
                current_rsv_id = rsv_tempat_id
                print(("_") * 60)
                print(f"ID Transaksi: {transaksi_id if transaksi_id else 'None'}")
                print(f"Waktu Transaksi: {waktu_transaksi if waktu_transaksi else 'None'}")
                print(f"ID Reservasi: {rsv_tempat_id}")
                print(f"Tanggal Kedatangan: {tanggal_kedatangan}")
                print(f"Waktu Kedatangan: {waktu_kedatangan}")
                print(f"Pelanggan: {username}")
                print(f"Nama Acara: {nama_acara}")
                print(f"Nomer Meja: {nomer_meja if nomer_meja else 'None'}")
                print(f"Total Biaya: {total_biaya}")
                print("-" * 60)
                print(f"{'Detail ID':<13}{'Nama Menu':<20}{'Jumlah Pesanan':<15}")
                print("-" * 60)
            print(f"{detail_rsv_id:<13}{nama_menu:<20}{jumlah_pesanan:<15}")
        print("_" * 60)
        print(f"=============ID reservasi terakhir Anda: {rsv_tempat_id}=============\n\n")
    else:
        print("Anda belum memiliki reservasi yang belum dibayar.")


def read_rsv_pelanggan(cursor, username):
    sql= '''
    SELECT t.transaksi_id, t.waktu_transaksi, r.rsv_tempat_id, r.tanggal_kedatangan, r.waktu_kedatangan, p.username, r.nama_acara, m.nomer_meja, d.detail_rsv_id, me.nama_menu, d.jumlah_pesanan, t.transaksi_id, p2.nama as pegawai,
    SUM(d.jumlah_pesanan * me.harga ) AS total_biaya
    FROM rsv_tempat r
    JOIN pelanggan p ON r.pelanggan_id = p.pelanggan_id
    LEFT JOIN meja m ON r.meja_id = m.meja_id
    LEFT JOIN detail_rsv d ON r.rsv_tempat_id = d.rsv_tempat_id
    JOIN transaksi t ON r.rsv_tempat_id = t.rsv_tempat_id
    LEFT JOIN pegawai p2 ON t.pegawai_id = p2.pegawai_id
    LEFT JOIN menu me ON d.menu_id = me.menu_id
    WHERE p.username = %s AND d.detail_rsv_id IS NOT NULL
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
    cursor.execute(sql, (username,))
    data = cursor.fetchall()
    
    if data:
        current_rsv_id = None
        print("Daftar Detail Reservasi:\n\n")
        
        for row in data:
            transaksi_id, waktu_transaksi, rsv_tempat_id, tanggal_kedatangan, waktu_kedatangan, username, nama_acara, nomer_meja, detail_rsv_id, nama_menu, jumlah_pesanan, transaksi_id, pegawai, total_biaya = row
            waktu_transaksi = waktu_transaksi.strftime("%Y-%m-%d %H:%M")
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
        print(f"=============ID transaksi terakhir Anda: {transaksi_id}=============\n\n")
    else:
        print("Anda belum memiliki detail transaksi.")

def create_transaksi(cursor, connection, rsv_tempat_id):
    cursor.execute(
        '''
        INSERT INTO transaksi (rsv_tempat_id, pegawai_id)
        VALUES (%s, NULL) RETURNING transaksi_id
        ''',
        (rsv_tempat_id,)
    )
    transaksi_id = cursor.fetchone()[0]
    connection.commit()
    # print(f"Transaksi berhasil ditambahkan dengan ID {transaksi_id}")
    return transaksi_id

def update_payment_method(cursor, connection, transaksi_id, payment_method, payment_details):
    if payment_method == 'cash':
        cursor.execute(
            '''
            INSERT INTO cash (transaksi_id)
            VALUES (%s)''',
            (transaksi_id,)
        )
        connection.commit()
        print(f"Transaksi cash berhasil diperbarui dengan ID {transaksi_id}")
    elif payment_method == 'transfer':
        cursor.execute(
            '''
            INSERT INTO transfer (transaksi_id, no_rek, nama)
            VALUES (%s, %s, %s)''',
            (transaksi_id, payment_details['no_rek'], payment_details['nama'])
        )
        connection.commit()
        # print(f"Transaksi transfer berhasil diperbarui dengan ID {transaksi_id}")

def process_payment(cursor, connection, username):
    read_unpaid_transaksi(cursor, username)
    # rsv_tempat_id = int(input("Masukkan ID reservasi yang ingin dibayar: "))
    while True:
        try:
            rsv_tempat_id = int(input("Masukkan ID reservasi yang ingin dibayar: "))
            if rsv_tempat_id <= 0:
                raise ValueError("ID reservasi harus berupa angka positif.")
            break
        except ValueError as e:
            print(input(f"Input tidak valid: {e}. \nMasukkan ID reservasi dengan benar."))
            return
    transaksi_id = create_transaksi(cursor, connection, rsv_tempat_id)
    payment_method = input("\nMasukkan metode pembayaran (cash/transfer): ").lower()
    if payment_method == 'cash':
        update_payment_method(cursor, connection, transaksi_id, payment_method='cash', payment_details={})
    elif payment_method == 'transfer':
        no_rek = input("Masukkan nomor rekening: ")
        nama = input("Masukkan nama pemilik rekening: ")
        update_payment_method(cursor, connection, transaksi_id, payment_method='transfer', payment_details={'no_rek': no_rek, 'nama': nama})
    else:
        print("Metode pembayaran tidak valid.")
        return
    print(f"\nTransaksi dengan ID {transaksi_id} berhasil dibayar dengan metode {payment_method}.")
    input("Tekan enter untuk kembali")