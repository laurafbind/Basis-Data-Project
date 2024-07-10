CREATE DATABASE kopus2

CREATE TABLE rsv_tempat (
    rsv_tempat_id      SERIAL NOT NULL,
    tanggal_kedatangan DATE NOT NULL,
    waktu_kedatangan   TIME NOT NULL,
    jumlah_orang       INTEGER NOT NULL,
    nama_acara         VARCHAR(64) NOT NULL,
    pelanggan_id       INTEGER NOT NULL,
	meja_id            INTEGER,
	FOREIGN KEY (meja_id) REFERENCES meja(meja_id) ON DELETE CASCADE
);
ALTER TABLE rsv_tempat ADD CONSTRAINT rsv_tempat_pk PRIMARY KEY (rsv_tempat_id);

CREATE TABLE detail_rsv (
    detail_rsv_id            SERIAL NOT NULL,
    rsv_tempat_id            INTEGER NOT NULL,
    jumlah_pesanan           INTEGER NOT NULL,
    menu_id                  INTEGER NOT NULL,
	FOREIGN KEY (rsv_tempat_id) REFERENCES rsv_tempat(rsv_tempat_id) ON DELETE CASCADE
);
ALTER TABLE detail_rsv ADD CONSTRAINT detail_rsv_pk PRIMARY KEY (detail_rsv_id);

CREATE TABLE jenis (
    jenis_id   SERIAL NOT NULL,
    jenis_menu VARCHAR(20) NOT NULL
);
ALTER TABLE jenis ADD CONSTRAINT jenis_pk PRIMARY KEY (jenis_id);

CREATE TABLE kota (
    kota_id   SERIAL NOT NULL,
    nama_kota VARCHAR(64) NOT NULL
);
ALTER TABLE kota ADD CONSTRAINT kota_pk PRIMARY KEY (kota_id);

CREATE TABLE meja (
    meja_id    SERIAL NOT NULL,
    nomer_meja VARCHAR(3) NOT NULL,
    status     VARCHAR(10) 
);
ALTER TABLE meja ADD CONSTRAINT meja_pk PRIMARY KEY (meja_id);

CREATE TABLE menu (
    menu_id        SERIAL NOT NULL,
    nama_menu      VARCHAR(64) NOT NULL,
    harga          INTEGER NOT NULL,
    deskripsi      VARCHAR(128) NOT NULL,
    jenis_id        INTEGER NOT NULL
);
ALTER TABLE menu ADD CONSTRAINT menu_pk PRIMARY KEY (menu_id);

CREATE TABLE pegawai (
    pegawai_id SERIAL NOT NULL,
    nama       VARCHAR(64) NOT NULL,
    username   VARCHAR(8) NOT NULL,
    password   VARCHAR(8) NOT NULL,
    email      VARCHAR(20) NOT NULL,
    alamat     VARCHAR(64) NOT NULL,
    no_telp    BIGINT NOT NULL,
    kota_id    INTEGER NOT NULL
);
ALTER TABLE pegawai ADD CONSTRAINT pegawai_pk PRIMARY KEY (pegawai_id);
ALTER TABLE pegawai ADD CONSTRAINT pegawai_email_un UNIQUE (email);
ALTER TABLE pegawai ADD CONSTRAINT pegawai_no_telp_un UNIQUE (no_telp);
ALTER TABLE pegawai ADD CONSTRAINT pegawai_username_un UNIQUE (username);

CREATE TABLE pelanggan (
    pelanggan_id SERIAL NOT NULL,
    nama         VARCHAR(64) NOT NULL,
    username     VARCHAR(8) NOT NULL,
    password     VARCHAR(8) NOT NULL,
    no_telp      BIGINT NOT NULL,
    email        VARCHAR(20) NOT NULL
);
ALTER TABLE pelanggan ADD CONSTRAINT pelanggan_pk PRIMARY KEY (pelanggan_id);
ALTER TABLE pelanggan ADD CONSTRAINT pelanggan_username_un UNIQUE (username);
ALTER TABLE pelanggan ADD CONSTRAINT pelanggan_email_un UNIQUE (email);
ALTER TABLE pelanggan ADD CONSTRAINT pelanggan_no_telp_un UNIQUE (no_telp);

CREATE TABLE cash (
    transaksi_id INTEGER 
);
ALTER TABLE cash ADD CONSTRAINT cash_pk PRIMARY KEY (transaksi_id);

CREATE TABLE transfer (
    transaksi_id INTEGER PRIMARY KEY REFERENCES transaksi(transaksi_id),
    no_rek BIGINT NOT NULL,
    nama VARCHAR(50) NOT NULL
);
ALTER TABLE transfer ADD CONSTRAINT transfer_no_rek_un UNIQUE (no_rek);

CREATE TABLE transaksi (
    transaksi_id             SERIAL NOT NULL,
    waktu_transaksi          TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    pegawai_id               INTEGER,
    rsv_tempat_id            INTEGER NOT NULL
);
CREATE UNIQUE INDEX transaksi_idx ON transaksi (rsv_tempat_id);
ALTER TABLE transaksi ADD CONSTRAINT transaksi_pk PRIMARY KEY (transaksi_id);
ALTER TABLE transaksi 
ALTER COLUMN pegawai_id SET DEFAULT NULL;



ALTER TABLE detail_rsv
    ADD CONSTRAINT detail_rsv_menu_fk FOREIGN KEY (menu_id)
        REFERENCES menu (menu_id);

ALTER TABLE detail_rsv
    ADD CONSTRAINT rsv_tempat_fk FOREIGN KEY (rsv_tempat_id)
        REFERENCES rsv_tempat (rsv_tempat_id) ON DELETE CASCADE;

ALTER TABLE menu
    ADD CONSTRAINT menu_jenis_fk FOREIGN KEY (jenis_id)
        REFERENCES jenis (jenis_id);
		
-- Mengatur default value dari kolom status menjadi NULL
ALTER TABLE meja
    ALTER COLUMN status SET DEFAULT NULL;

-- Mengatur default value dari kolom meja_id menjadi NULL
ALTER TABLE rsv_tempat
    ALTER COLUMN meja_id SET DEFAULT NULL;

ALTER TABLE rsv_tempat
    ADD CONSTRAINT rsv_tempat_meja_fk FOREIGN KEY (meja_id)
        REFERENCES meja (meja_id);

ALTER TABLE pegawai
    ADD CONSTRAINT pegawai_kota_fk FOREIGN KEY (kota_id)
        REFERENCES kota (kota_id);

ALTER TABLE rsv_tempat
    ADD CONSTRAINT rsv_tempat_pelanggan_fk FOREIGN KEY (pelanggan_id)
        REFERENCES pelanggan (pelanggan_id);

ALTER TABLE transaksi
    ADD CONSTRAINT transaksi_pegawai_fk FOREIGN KEY (pegawai_id)
        REFERENCES pegawai (pegawai_id);

ALTER TABLE transaksi
    ADD CONSTRAINT transaksi_rsv_tempat_fk FOREIGN KEY (rsv_tempat_id)
        REFERENCES rsv_tempat (rsv_tempat_id);

ALTER TABLE transaksi
ALTER COLUMN waktu_transaksi SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE transfer
    ADD CONSTRAINT transaksi_fk FOREIGN KEY (transaksi_id)
        REFERENCES transaksi (transaksi_id);


SELECT 
m.menu_id, m.nama_menu, m.harga, 
m.deskripsi, j.jenis_menu 
FROM menu m 
JOIN jenis j ON (m.jenis_id = j.jenis_id)
WHERE m.harga > 10000 
AND j.jenis_menu = 'makanan'
ORDER BY m.menu_id
