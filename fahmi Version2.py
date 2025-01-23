
from instagrapi import Client

# Masukkan kredensial Instagram Anda di sini
username = input("Masukkan username instagram... : ")
password = input("Masukkan password instagram... : ")

def request_otp(challenge):
    """
    Menangani OTP dari Instagram saat login.
    """
    if challenge["step_name"] == "submit_phone":
        print("Mengirimkan kode OTP ke nomor ponsel Anda...")
        client.challenge_send_code(choice="0")  # Kirim OTP ke ponsel
    elif challenge["step_name"] == "select_verify_method":
        print("Memilih metode verifikasi...")
        client.challenge_send_code(choice="0")  # Pilih metode verifikasi pertama (biasanya SMS)
    else:
        raise Exception(f"Step tidak diketahui: {challenge['step_name']}")

    while True:
        otp = input("Masukkan kode OTP yang Anda terima: ")
        try:
            if client.challenge_resolve(otp):
                print("Berhasil memverifikasi kode OTP.")
                break
        except Exception as e:
            print(f"Kode OTP salah atau verifikasi gagal: {e}. Coba lagi.")

def get_followers():
    """
    Mengambil daftar followers.
    """
    print("Mengambil daftar followers...")
    followers = client.user_followers(user_id)
    print(f"Ditemukan {len(followers)} followers.")
    return [follower.username for follower in followers.values()]

def get_following():
    """
    Mengambil daftar following.
    """
    print("Mengambil daftar following...")
    following = client.user_following(user_id)
    print(f"Ditemukan {len(following)} following.")
    return [follower.username for follower in following.values()]

def saring_yang_mau_di_unfollow(not_following_back):
    

    # # Kurasi daftar berdasarkan input pengguna
    print("Semua Akan Diunfollow, Masukkan nomor urutan pengguna yang ingin Anda pertahankan (pisahkan dengan koma), atau tekan Enter untuk lanjut:")
    retained_indices = input()
    retained_users = []

    if retained_indices.strip():
        indices = map(int, retained_indices.split(","))
        retained_users = [not_following_back[i - 1] for i in indices]

    not_following_back = [user for user in not_following_back if user not in retained_users]

    # Unfollow pengguna yang tidak follow back
    print("Mulai proses unfollow...")
    for user in not_following_back:
        try:
            client.user_unfollow(client.user_id_from_username(user))
            print(f"Unfollow {user}")
        except Exception as e:
            print(f"Gagal unfollow {user}: {e}")

def pilihan_disaring_atau_tidak(not_following_back):
    while True:
        # Tampilkan pilihan
        print("Pilih:")
        print("1. Jalankan fungsi saring_yang_mau_di_unfollow")
        print("2. Skip")

        pilihan = input("Masukkan pilihan (1/2): ")

        if pilihan == "1":
            saring_yang_mau_di_unfollow(not_following_back)  # Panggil fungsi jika pilih 1
            break  # Keluar dari loop setelah fungsi dijalankan
        elif pilihan == "2":
            print("Anda memilih untuk skip.")
            break  # Keluar dari loop jika pilih 2
        else:
            print("Input tidak valid. Harap masukkan 1 atau 2.")
            continue  # Ulangi perulangan jika input tidak valid
    

if __name__ == "__main__":
    client = Client()
    client.delay_range = [1, 3]  # jeda antara permintaan untuk terlihat lebih alami

    print("Mencoba login...")
    try:
        client.login(username, password)
    except Exception as e:
        print(f"Gagal login: {e}")
        challenge = client.last_json.get("challenge", {})
        if challenge:
            request_otp(challenge)
        else:
            print("Challenge tidak ditemukan. Pastikan akun Anda tidak terkunci.")
            exit()

    print("Berhasil login.")

    # Ambil user_id untuk akun yang login
    user_id = client.user_id

    # Ambil daftar followers dan following
    follower_usernames = get_followers()
    following_usernames = get_following()

    # Temukan pengguna yang Anda follow tapi tidak follow back
    not_following_back = [user for user in following_usernames if user not in follower_usernames]
    print(f"Ada {len(not_following_back)} pengguna yang tidak follow back.")

    # # Tampilkan daftar untuk dikurasi manual
    print("Daftar pengguna yang tidak follow back:")
    for i, user in enumerate(not_following_back):
        print(f"{i + 1}. {user}")

    pilihan_disaring_atau_tidak(not_following_back)

    # Logout dari akun Instagram
    client.logout()
    print("Proses selesai dan akun telah logout.")
    
    
############ SKRIP INI DIBUAT OLEH LORD MAJESTY FAHMOY ARDIANSYAH N RONAN ############
