

# INSTAGRAM FULL SCRIPT BY FAHMI

API Fahmi ini menyediakan berbagai layanan otomatisasi untuk akun Instagram menggunakan Instagram Private API. Fungsionalitas utamanya mencakup login, pengambilan data profil, followers, following, serta menganalisis akun yang tidak mengikuti kembali (Don't Follow Back) dan mengambil followers dari akun target tertentu.

## Fitur

- **Login:** Proses login Instagram menggunakan username dan password.
- **Profile:** Mendapatkan informasi profil pengguna Instagram.
- **Followers:** Mengambil daftar followers pengguna.
- **Following:** Mengambil daftar following pengguna.
- **Don't Follow Back:** Mendapatkan daftar akun yang tidak mengikuti kembali pengguna.
- **Followers Target:** Mengambil daftar followers dari pengguna target tertentu.

## Teknologi yang Digunakan

- **Node.js**: Platform untuk menjalankan API.
- **Bull**: Antrian pekerjaan (job queue) untuk menangani tugas-tugas secara terpisah dan terstruktur.
- **Instagram Private API (IgApiClient)**: Untuk berinteraksi dengan Instagram.
- **Express**: Framework untuk membangun server API.
- **Firestore**: Menyimpan sesi login pengguna secara aman.

## Prasyarat

Sebelum menjalankan API ini, pastikan Anda sudah memenuhi persyaratan berikut:

1. **Node.js** versi 14 atau lebih tinggi.
2. **npm** atau **yarn** untuk manajer paket.
3. Akses ke **Firebase Firestore** untuk menyimpan sesi login.

## Instalasi

1. Clone repositori ini ke mesin lokal Anda:

    ```bash
    git clone https://github.com/username/repository-name.git
    cd repository-name
    ```

2. Install dependensi yang diperlukan:

    ```bash
    npm install
    ```

3. Atur konfigurasi Firebase dengan mengedit file `config/firebase.js` untuk menyertakan kredensial Firebase Anda.

4. Jalankan aplikasi:

    ```bash
    npm start
    ```

API ini akan berjalan pada port default `3000`, dan Anda dapat mengaksesnya melalui `http://localhost:3000`.

## Endpoint

### 1. `/login` (POST)
Endpoint ini digunakan untuk melakukan login ke akun Instagram.

**Request Body:**
```json
{
  "username": "your_instagram_username",
  "password": "your_instagram_password"
}
```

Jika dalam sebuah terminal anda bisa langsung ketik:
```bash
curl -X POST http://localhost:3000/login -H "Content-Type: application/json" -d "{\"username\": \"your_instagram_username\", \"password\": \"your_instagram_password\"}"
```

Penjelasan:
- **`-X POST`**: Menentukan metode HTTP yang digunakan, dalam hal ini adalah POST.
- **`-H "Content-Type: application/json"`**: Menambahkan header yang menunjukkan bahwa data yang dikirimkan adalah dalam format JSON.
- **`-d`**: Digunakan untuk mengirim data (payload) ke server, dalam hal ini adalah body permintaan dengan format JSON.


Dengan contoh di atas, Anda dapat menggunakan perintah cURL untuk mengirimkan request ke endpoint `/login` di API Anda.


### 2. `/profile` (GET)
Endpoint ini digunakan untuk mengambil informasi profil pengguna Instagram yang sedang login.

#### **Query Params:**
- `username`: Nama pengguna Instagram yang ingin diambil profilnya.

**Contoh Request:**
Jika Anda ingin mengambil profil pengguna tertentu, Anda bisa mengirimkan permintaan GET ke endpoint `/profile` dengan menambahkan parameter `username` di URL.

```bash
curl -X GET "http://localhost:3000/profile?username=your_instagram_username"
```

### Penjelasan:
- **`-X GET`**: Menggunakan metode HTTP GET untuk meminta data.
- **`?username=your_instagram_username`**: Parameter `username` dalam query URL yang menunjukkan pengguna yang profilnya ingin diambil.

Sehingga, bagian ini akan memperjelas bagaimana cara mengakses informasi profil pengguna Instagram menggunakan metode **GET** di API Anda.


## ⋆｡‧˚ʚ🧸ɞ˚‧｡⋆🩷 DIBUAT OLEH LORD FAHMI ARDIANSYAH 🩷⋆｡‧˚ʚ🧸ɞ˚‧｡⋆

![License: Fahmoy](https://img.shields.io/badge/License-Fahmoy-yellow.svg)
