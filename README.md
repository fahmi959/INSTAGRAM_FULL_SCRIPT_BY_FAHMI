# INSTAGRAM_FULL_SCRIPT_BY_FAHMI

API ini menyediakan berbagai layanan otomatisasi untuk akun Instagram menggunakan Instagram Private API. Fungsionalitas utamanya mencakup login, pengambilan data profil, followers, following, serta menganalisis akun yang tidak mengikuti kembali (Don't Follow Back) dan mengambil followers dari akun target tertentu.

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
