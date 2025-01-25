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




Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X POST http://localhost:3000/login \
-H "Content-Type: application/json" \
-d '{"username": "your_instagram_username", "password": "your_instagram_password"}'
2. /profile (GET)
Endpoint ini digunakan untuk mengambil data profil pengguna yang sedang login.

Query Parameters:

username: Username dari akun yang ingin diambil datanya.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/profile?username=your_instagram_username"
3. /followers (GET)
Endpoint ini digunakan untuk mengambil daftar followers dari akun yang sedang login.

Query Parameters:

username: Username dari akun yang ingin diambil followers-nya.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/followers?username=your_instagram_username"
4. /following (GET)
Endpoint ini digunakan untuk mengambil daftar following dari akun yang sedang login.

Query Parameters:

username: Username dari akun yang ingin diambil following-nya.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/following?username=your_instagram_username"
5. /dontfollowback (GET)
Endpoint ini digunakan untuk mendapatkan daftar pengguna yang tidak mengikuti kembali.

Query Parameters:

username: Username dari akun yang ingin dianalisis.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/dontfollowback?username=your_instagram_username"
6. /followers_target (POST)
Endpoint ini digunakan untuk mengambil followers dari akun target tertentu.

Request Body:

json

Verify

Open In Editor
Run
Copy code
{
  "username": "your_instagram_username",
  "target": "target_instagram_username"
}
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X POST http://localhost:3000/followers_target \
-H "Content-Type: application/json" \
-d '{"username": "your_instagram_username", "target": "target_instagram_username"}'
Prerequisites
Node.js
Instagram Private API
Firestore untuk menyimpan sesi
Cara Menjalankan
Clone repositori ini.
Install dependensi dengan menjalankan npm install.
Jalankan server dengan node index.js (atau file utama Anda).
Akses API melalui endpoint yang telah disediakan.
Catatan
Pastikan untuk mengganti your_instagram_username dan your_instagram_password dengan informasi akun Instagram Anda yang valid. Gunakan API ini dengan bijak dan sesuai dengan kebijakan penggunaan Instagram.


Verify

Open In Editor
Run
Copy code

Silakan simpan teks di atas ke dalam file `README.md` di repositori Anda. Anda dapat menyesuaikan bagian yang diperlukan sesuai dengan kebutuhan proyek Anda.
You

jadi readme.md secara lengkap gimana jangan dipotong potong masukin ke dalam kode keterangannya

BLACKBOXAI

Berikut adalah isi lengkap untuk file README.md yang dapat Anda gunakan untuk proyek GitHub Anda. Saya telah menyusun semua informasi dalam satu kesatuan tanpa memotong-motong, dan menyertakan format kode yang sesuai untuk memudahkan penyalinan.

markdown

Verify

Open In Editor
Run
Copy code
# INSTAGRAM_FULL_SCRIPT_BY_FAHMI

API ini menyediakan berbagai layanan otomatisasi untuk akun Instagram menggunakan Instagram Private API. Fungsionalitas utamanya mencakup login, pengambilan data profil, followers, following, serta menganalisis akun yang tidak mengikuti kembali (Don't Follow Back) dan mengambil followers dari akun target tertentu.

## Endpoint

### 1. /login (POST)
Endpoint ini digunakan untuk melakukan login ke akun Instagram.

**Request Body:**
```json
{
  "username": "your_instagram_username",
  "password": "your_instagram_password"
}
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X POST http://localhost:3000/login \
-H "Content-Type: application/json" \
-d '{"username": "your_instagram_username", "password": "your_instagram_password"}'
2. /profile (GET)
Endpoint ini digunakan untuk mengambil data profil pengguna yang sedang login.

Query Parameters:

username: Username dari akun yang ingin diambil datanya.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/profile?username=your_instagram_username"
3. /followers (GET)
Endpoint ini digunakan untuk mengambil daftar followers dari akun yang sedang login.

Query Parameters:

username: Username dari akun yang ingin diambil followers-nya.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/followers?username=your_instagram_username"
4. /following (GET)
Endpoint ini digunakan untuk mengambil daftar following dari akun yang sedang login.

Query Parameters:

username: Username dari akun yang ingin diambil following-nya.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/following?username=your_instagram_username"
5. /dontfollowback (GET)
Endpoint ini digunakan untuk mendapatkan daftar pengguna yang tidak mengikuti kembali.

Query Parameters:

username: Username dari akun yang ingin dianalisis.
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X GET "http://localhost:3000/dontfollowback?username=your_instagram_username"
6. /followers_target (POST)
Endpoint ini digunakan untuk mengambil followers dari akun target tertentu.

Request Body:

json

Verify

Open In Editor
Run
Copy code
{
  "username": "your_instagram_username",
  "target": "target_instagram_username"
}
Contoh Penggunaan dengan curl:

bash

Verify

Open In Editor
Run
Copy code
curl -X POST http://localhost:3000/followers_target \
-H "Content-Type: application/json" \
-d '{"username": "your_instagram_username", "target": "target_instagram_username"}'
Prerequisites
Node.js
Instagram Private API
Firestore untuk menyimpan sesi
Cara Menjalankan
Clone repositori ini.
Install dependensi dengan menjalankan npm install.
Jalankan server dengan node index.js (atau file utama Anda).
Akses API melalui endpoint yang telah disediakan.
Catatan
Pastikan untuk mengganti your_instagram_username dan your_instagram_password dengan informasi akun Instagram Anda yang valid. Gunakan API ini dengan bijak dan sesuai dengan kebijakan penggunaan Instagram.
