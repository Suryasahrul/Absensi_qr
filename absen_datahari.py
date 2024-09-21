import streamlit as st
import pandas as pd
import qrcode
import cv2
from datetime import datetime
import os

# Membuat DataFrame untuk menyimpan kehadiran siswa berdasarkan tanggal
def load_data(date):
    file_name = f"data_absensi_{date}.xlsx"
    if os.path.exists(file_name):
        df = pd.read_excel(file_name, dtype={"NIS": str})  # Pastikan NIS dibaca sebagai string
    else:
        df = pd.DataFrame(columns=["Nama", "NIS", "Kelas", "Waktu Kehadiran", "Status"])
    return df

def save_data(df, date):
    file_name = f"data_absensi_{date}.xlsx"
    df.to_excel(file_name, index=False)

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
nis = st.text_input("NISN")  # Pastikan NISN dimasukkan sebagai teks/string
kelas = st.text_input("Kelas")  # Input baru untuk kelas siswa

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
        # Dapatkan waktu dan tanggal saat ini
        current_time = datetime.now().time()
        current_date = datetime.today().strftime("%Y-%m-%d")
        status = validate_attendance(current_time)

        # Simpan data ke Excel berdasarkan tanggal
        df = load_data(current_date)
        
        # Buat DataFrame untuk data baru
        new_data = {
            "Nama": nama, 
            "NIS": scanned_nis,  # NIS tetap sebagai string
            "Kelas": kelas,  # Tambahkan data kelas
            "Waktu Kehadiran": current_time.strftime("%H:%M:%S"), 
            "Status": status
        }
        new_data_df = pd.DataFrame([new_data])  # Buat DataFrame dari new_data

        # Gabungkan data lama dengan data baru
        df = pd.concat([df, new_data_df], ignore_index=True)
        save_data(df, current_date)
        
        st.success(f"Kehadiran tercatat untuk NIS: {scanned_nis} ({status})")
    else:
        st.warning("Tidak ada QR code yang terdeteksi!")

# Menampilkan data absensi yang sudah tercatat
st.header("Data Kehadiran Siswa")

# Pilih tanggal untuk melihat atau mengunduh data
selected_date = st.date_input("Pilih tanggal untuk melihat data:", datetime.today())
selected_date_str = selected_date.strftime("%Y-%m-%d")

# Menampilkan data sesuai dengan tanggal yang dipilih
df = load_data(selected_date_str)
st.dataframe(df)

# Mengunduh data sesuai tanggal yang dipilih
if st.button("Download Data"):
    df.to_excel(f"data_absensi_{selected_date_str}.xlsx", index=False)
    st.write(f"Data berhasil diunduh untuk tanggal {selected_date_str}.")
