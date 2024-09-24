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

# Membaca QR code menggunakan kamera secara berkelanjutan
def continuous_qr_scan():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    st.write("Menunggu scan QR code... Tekan 'q' di jendela kamera untuk berhenti.")

    while True:
        ret, img = cap.read()

        if not ret:
            st.error("Gagal mengambil gambar dari kamera. Pastikan kamera berfungsi dengan baik.")
            break

        data, _, _ = detector.detectAndDecode(img)

        if data:
            st.write(f"QR code terdeteksi: {data}")
            yield data

        cv2.imshow("QR Code Scanner", img)

        if cv2.waitKey(1) == ord("q"):  # Tekan 'q' untuk keluar
            break

    cap.release()
    cv2.destroyAllWindows()

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

if st.button("Mulai Scan QR Code"):
    scanned_data = continuous_qr_scan()

    for scanned_nis in scanned_data:
        # Dapatkan waktu dan tanggal saat ini
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.today().strftime("%Y-%m-%d")
        status = validate_attendance(datetime.strptime(current_time, "%H:%M:%S").time())

        # Simpan data ke Excel berdasarkan tanggal
        df = load_data(current_date)

        # Cek apakah barcode sudah dipindai hari ini
        if not df[df['NIS'] == scanned_nis].empty:
            st.warning(f"Siswa dengan NIS {scanned_nis} sudah tercatat hari ini.")
        else:
            if nama and kelas:  # Pastikan data Nama dan Kelas terisi
                # Buat DataFrame untuk data baru
                new_data = {
                    "Nama": nama,
                    "NIS": scanned_nis,
                    "Kelas": kelas,
                    "Waktu Kehadiran": current_time,
                    "Status": status
                }
                new_data_df = pd.DataFrame([new_data])

                # Gabungkan data lama dengan data baru
                df = pd.concat([df, new_data_df], ignore_index=True)
                save_data(df, current_date)

                st.success(f"Kehadiran tercatat untuk NIS: {scanned_nis} ({status})")
            else:
                st.error("Nama dan kelas tidak boleh kosong!")

# Membaca QR code menggunakan kamera secara berkelanjutan dengan DirectShow sebagai backend
def continuous_qr_scan():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Menggunakan backend DirectShow
    detector = cv2.QRCodeDetector()

    st.write("Menunggu scan QR code... Tekan 'q' di jendela kamera untuk berhenti.")

    while True:
        ret, img = cap.read()

        if not ret:
            st.error("Gagal mengambil gambar dari kamera. Pastikan kamera berfungsi dengan baik.")
            break

        data, _, _ = detector.detectAndDecode(img)

        if data:
            st.write(f"QR code terdeteksi: {data}")
            yield data

        cv2.imshow("QR Code Scanner", img)

        if cv2.waitKey(1) == ord("q"):  # Tekan 'q' untuk keluar
            break

    cap.release()
    cv2.destroyAllWindows()


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
