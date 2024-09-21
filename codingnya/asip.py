import streamlit as st
import pandas as pd
import qrcode
import cv2
from datetime import datetime
import os

# Membuat DataFrame untuk menyimpan kehadiran siswa
def load_data():
    if os.path.exists("data_absensi.xlsx"):
        df = pd.read_excel("data_absensi.xlsx")
    else:
        df = pd.DataFrame(columns=["Nama", "NIS", "Waktu Kehadiran", "Status"])
    return df

def save_data(df):
    df.to_excel("data_absensi.xlsx", index=False)

# Membuat QR code (contoh sederhana)
def generate_qr(nis):
    folder_path = os.path.join(os.getcwd(), "qr_codes")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    qr_img = qrcode.make(nis)
    qr_code_path = os.path.join(folder_path, f"{nis}.png")
    qr_img.save(qr_code_path)
    return qr_code_path

# Memvalidasi waktu kedatangan
def validate_attendance(time):
    limit_time = datetime.strptime("07:05", "%H:%M").time()
    if time <= limit_time:
        return "Tepat Waktu"
    else:
        return "Terlambat"

# Membaca QR code menggunakan kamera
def read_qr_code():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    
    while True:
        _, img = cap.read()
        data, _, _ = detector.detectAndDecode(img)
        
        if data:
            cap.release()
            cv2.destroyAllWindows()
            return data
        
        cv2.imshow("QR Code Scanner", img)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

# Aplikasi Streamlit
st.title("Sistem Absensi Siswa dengan QR Code")

# Input untuk memasukkan data siswa dan membuat QR code
st.header("Tambah Data Siswa")
nama = st.text_input("Nama Siswa")
nis = st.text_input("NIS")

if st.button("Generate QR Code"):
    if nis:
        generate_qr(nis)
        st.image(f"qr_codes/{nis}.png", caption=f"QR Code untuk {nama}")
    else:
        st.warning("Masukkan NIS untuk generate QR code!")

# Membaca QR code dan mencatat kehadiran
st.header("Scan Kehadiran Siswa")
if st.button("Scan QR Code"):
    scanned_nis = read_qr_code()
    
    if scanned_nis:
        # Dapatkan waktu saat ini
        current_time = datetime.now().time()
        status = validate_attendance(current_time)

        # Simpan data ke Excel
        df = load_data()
        new_data = {"Nama": nama, "NIS": scanned_nis, "Waktu Kehadiran": current_time.strftime("%H:%M:%S"), "Status": status}
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        
        st.success(f"Kehadiran tercatat untuk NIS: {scanned_nis} ({status})")
    else:
        st.warning("Tidak ada QR code yang terdeteksi!")

# Menampilkan data absensi yang sudah tercatat
st.header("Data Kehadiran Siswa")
df = load_data()
st.dataframe(df)

if st.button("Download Data"):
    df.to_excel("data_absensi.xlsx", index=False)
    st.write("Data berhasil diunduh.")

import os
import qrcode

# Membuat QR code dan memastikan folder untuk menyimpan QR ada
def generate_qr(nis):
    # Pastikan folder qr_codes ada, jika tidak buat folder tersebut
    if not os.path.exists("qr_codes"):
        os.makedirs("qr_codes")

    # Generate QR code dan simpan ke folder
    qr_img = qrcode.make(nis)
    qr_img.save(f"qr_codes/{nis}.png")

import os
import qrcode

# Membuat QR code dan memastikan folder untuk menyimpan QR ada
def generate_qr(nis):
    # Pastikan folder qr_codes ada, jika tidak buat folder tersebut
    folder_path = os.path.join(os.getcwd(), "qr_codes")
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Generate QR code dan simpan ke folder
    qr_img = qrcode.make(nis)
    qr_code_path = os.path.join(folder_path, f"{nis}.png")
    qr_img.save(qr_code_path)
    return qr_code_path

import pandas as pd
import streamlit as st

# Misal data awal (data lama)
data = {
    "NIS": [12345, 67890],
    "Nama": ["Siswa A", "Siswa B"],
    "Waktu Kehadiran": ["07:00", "07:10"],
    "Status": ["Tepat Waktu", "Terlambat"]
}

# Membuat DataFrame dari data awal
df = pd.DataFrame(data)

# Data baru yang akan ditambahkan (ini adalah data baru yang ingin kita masukkan)
new_data = {
    "NIS": [11223],
    "Nama": ["Siswa C"],
    "Waktu Kehadiran": ["07:02"],
    "Status": ["Tepat Waktu"]
}

# Membuat DataFrame untuk data baru (ini yang dinamakan new_data_df)
new_data_df = pd.DataFrame(new_data)

# Sekarang kita bisa menggabungkan data lama dengan data baru menggunakan pd.concat()
df = pd.concat([df, new_data_df], ignore_index=True)

# Menampilkan DataFrame hasil penggabungan di Streamlit
st.write(df)

 