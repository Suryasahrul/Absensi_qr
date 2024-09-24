const video = document.getElementById('video');
const qrResult = document.getElementById('qr-result');
const qrContent = document.getElementById('qr-content');
const qrImage = document.getElementById('qr-image');
const attendanceData = document.getElementById('attendance-data');
const scannedNISNs = {};  // Menyimpan data NISN yang sudah discan dalam sehari

// Menginisialisasi webcam untuk pemindaian QR code
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function(stream) {
    video.srcObject = stream;
    video.setAttribute("playsinline", true); // for iOS devices
    video.play();
    requestAnimationFrame(tick);
});

function tick() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const qrCode = jsQR(imageData.data, canvas.width, canvas.height, {
            inversionAttempts: "dontInvert",
        });

        if (qrCode) {
            qrResult.style.display = "block";
            qrContent.innerText = qrCode.data;
            processAttendance(qrCode.data);
        }
    }
    requestAnimationFrame(tick);
}

// Fungsi untuk mengenerate QR code berdasarkan NISN
function generateQRCode() {
    const nisn = document.getElementById('nisn').value;
    if (nisn) {
        const qrCodeURL = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + nisn;
        qrImage.src = qrCodeURL;
        qrImage.style.display = 'block';
    } else {
        alert('Masukkan NISN terlebih dahulu!');
    }
}

// Fungsi untuk memproses kehadiran siswa
function processAttendance(nisn) {
    const name = document.getElementById('name').value;
    const studentClass = document.getElementById('class').value;
    const currentTime = new Date().toLocaleTimeString();
    const currentDate = new Date().toLocaleDateString();
    const status = checkAttendanceStatus(currentTime);

    // Cek apakah NISN ini sudah discan hari ini
    if (scannedNISNs[nisn] === currentDate) {
        alert("Siswa dengan NISN ini sudah tercatat hadir hari ini.");
        return;
    }

    // Simpan NISN yang sudah discan pada tanggal ini
    scannedNISNs[nisn] = currentDate;

    // Tambahkan data kehadiran ke tabel
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${name}</td>
        <td>${nisn}</td>
        <td>${studentClass}</td>
        <td>${currentDate}</td>
        <td>${currentTime}</td>
        <td>${status}</td>
    `;
    attendanceData.appendChild(newRow);
}

// Fungsi untuk memeriksa status kehadiran berdasarkan waktu
function checkAttendanceStatus(time) {
    const limitTime = "07:05";
    return time <= limitTime ? "Tepat Waktu" : "Terlambat";
}

// Fungsi untuk mengunduh data kehadiran dalam format Excel
function downloadExcel() {
    const data = [];
    const rows = document.querySelectorAll("#attendance-data tr");
    
    // Buat header
    const header = ["Nama", "NIS", "Kelas", "Tanggal Kehadiran", "Waktu Kehadiran", "Status"];
    data.push(header);

    // Ambil data dari tabel
    rows.forEach(row => {
        const rowData = [];
        row.querySelectorAll("td").forEach(td => {
            rowData.push(td.innerText);
        });
        data.push(rowData);
    });

    // Buat workbook dan worksheet
    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Data Kehadiran");

    // Ekspor file Excel
    XLSX.writeFile(workbook, `data_kehadiran_${new Date().toLocaleDateString()}.xlsx`);
}
