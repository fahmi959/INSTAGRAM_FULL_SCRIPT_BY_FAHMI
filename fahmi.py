import os
from instagrapi import Client

# 0. Masukkan kredensial Instagram Anda di sini
username = "oleole.45"
password = "Amanah123"

def check_if_cached_exists(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return f.read().splitlines()
    else:
        return None

def get_followers() -> list:
    if follower_list := check_if_cached_exists("followers.txt") is not None:
        print("Menggunakan daftar followers yang sudah ada. Hapus followers.txt dan jalankan ulang jika ingin memperbarui.")
    else:
        print("Mengambil daftar followers...")
        followers = client.user_followers(user_id)
        print(f"Ditemukan {len(followers)} followers.")
        follower_list = []
        for ig_id, follower in followers.items():
            try:
                # Kadang user tidak memiliki username, kemungkinan karena mereka privat atau dibanned
                follower_list.append(follower.username)
            except AttributeError as e:
                print(f"User {ig_id} tidak memiliki username, dilewati.")
                continue

        # Simpan daftar followers ke file
        with open("followers.txt", "w") as followers_file:
            followers_file.write("\n".join(follower_list))
    return follower_list

def get_following() -> list:
    if following_list := check_if_cached_exists("following.txt") is not None:
        print("Menggunakan daftar following yang sudah ada. Hapus following.txt dan jalankan ulang jika ingin memperbarui.")
    else:
        print("Mengambil daftar following...")
        following = client.user_following(user_id)
        print(f"Ditemukan {len(following)} following.")
        following_list = []
        for ig_id, follower in following.items():
            try:
                following_list.append(follower.username)
            except AttributeError as e:
                print(f"User {ig_id} tidak memiliki username, dilewati.")
                continue

        # Simpan daftar following ke file
        with open("following.txt", "w") as following_file:
            following_file.write("\n".join(following_list))
    return following_list

if __name__ == '__main__':
    # 1. Login ke Instagram
    client = Client()
    client.delay_range = [1, 3]  # jeda antara permintaan untuk terlihat lebih alami

    print("Mencoba login...")
    client.login(username, password)
    user_id = str(client.user_id)
    print("Berhasil login.")

    # 2. Ambil daftar followers
    follower_usernames = get_followers()

    # 3. Ambil daftar users yang Anda follow
    following_usernames = get_following()

    # 4. Temukan pengguna yang Anda follow tapi tidak follow back
    not_following_back = [user for user in following_usernames if user not in follower_usernames]

    # Simpan daftar users yang tidak follow back ke file
    if os.path.exists("not_following_back.txt"):
        os.remove("not_following_back.txt")
    with open("not_following_back.txt", "w") as file:
        file.write("\n".join(not_following_back))

    # 5. Meminta pengguna untuk mengedit daftar unfollow (misalnya untuk menghapus selebriti atau orang yang ingin dipertahankan)
    input("Buka not_following_back.txt dan kurasi daftar (hapus orang yang ingin Anda pertahankan). "
          "Jangan biarkan baris kosong. Ingat untuk menyimpan. Tekan enter di terminal ini ketika selesai.")

    # 6. Unfollow users yang tidak follow back
    with open("not_following_back.txt", "r") as file:
        curated_unfollow_list = file.read().splitlines()

    for user in curated_unfollow_list:
        print(f"Unfollow {user}")
        client.user_unfollow(client.user_id_from_username(user))

    # 7. Logout dari akun Instagram
    client.logout()
