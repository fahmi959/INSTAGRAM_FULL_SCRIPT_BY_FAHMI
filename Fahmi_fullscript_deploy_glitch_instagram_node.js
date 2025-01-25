// LOGIKA BULL ATAU ANTRIAN PROSES

const { Queue, Worker } = require('bull');
const loginQueue = new Queue('loginQueue');
const profileQueue = new Queue('profileQueue');
const followersQueue = new Queue('followersQueue');
const followingQueue = new Queue('followingQueue');
const dontFollowBackQueue = new Queue('dontFollowBackQueue');
const followersTargetQueue = new Queue('followersTargetQueue');

// Fungsi untuk menambahkan pekerjaan ke antrian
const addToQueue = async (type, data) => {
    switch (type) {
        case 'login':
            await loginQueue.add(data);
            break;
        case 'profile':
            await profileQueue.add(data);
            break;
        case 'followers':
            await followersQueue.add(data);
            break;
        case 'following':
            await followingQueue.add(data);
            break;
        case 'dontFollowBack':
            await dontFollowBackQueue.add(data);
            break;
        case 'followersTarget':
            await followersTargetQueue.add(data);
            break;
        default:
            console.error('Jenis pekerjaan tidak dikenali!');
    }
};

// Worker untuk menangani login
new Worker('loginQueue', async (job) => {
    const { username, password } = job.data;
    await login(username, password);
}, { concurrency: 5 });

// Worker untuk menangani profil
new Worker('profileQueue', async (job) => {
    const { username } = job.data;
    await ensureSession(username); // pastikan sesi valid
    const user = await ig.account.currentUser();
    // Kirimkan data profil ke client (misalnya response API)
}, { concurrency: 5 });

// Worker untuk menangani followers
new Worker('followersQueue', async (job) => {
    const { username } = job.data;
    await ensureSession(username); // pastikan sesi valid
    const user = await ig.account.currentUser();
    const followersFeed = ig.feed.accountFollowers(user.pk);
    let followers = [];
    let nextFollowers = await followersFeed.items();
    followers = followers.concat(nextFollowers);

    while (followersFeed.isMoreAvailable()) {
        nextFollowers = await followersFeed.items();
        followers = followers.concat(nextFollowers);
    }

    // Kirim data followers ke client
}, { concurrency: 5 });

// Worker untuk menangani following
new Worker('followingQueue', async (job) => {
    const { username } = job.data;
    await ensureSession(username); // pastikan sesi valid
    const user = await ig.account.currentUser();
    const followingFeed = ig.feed.accountFollowing(user.pk);
    let following = [];
    let nextFollowing = await followingFeed.items();
    following = following.concat(nextFollowing);

    while (followingFeed.isMoreAvailable()) {
        nextFollowing = await followingFeed.items();
        following = following.concat(nextFollowing);
    }

    // Kirim data following ke client
}, { concurrency: 5 });

// Worker untuk menangani dontFollowBack
new Worker('dontFollowBackQueue', async (job) => {
    const { username } = job.data;
    await ensureSession(username);

    const user = await ig.account.currentUser();
    const followersFeed = ig.feed.accountFollowers(user.pk);
    let followers = [];
    let nextFollowers = await followersFeed.items();
    followers = followers.concat(nextFollowers);

    while (followersFeed.isMoreAvailable()) {
        nextFollowers = await followersFeed.items();
        followers = followers.concat(nextFollowers);
    }

    const followingFeed = ig.feed.accountFollowing(user.pk);
    let following = [];
    let nextFollowing = await followingFeed.items();
    following = following.concat(nextFollowing);

    while (followingFeed.isMoreAvailable()) {
        nextFollowing = await followingFeed.items();
        following = following.concat(nextFollowing);
    }

    const dontFollowBack = getNonFollowers(followers, following);
    // Kirim hasil dontFollowBack ke client
}, { concurrency: 5 });

// Worker untuk mengambil followers dari target
new Worker('followersTargetQueue', async (job) => {
    const { username, target } = job.data;
    await ensureSession(username);

    const targetUser = await ig.user.searchExact(target);
    const followersFeed = ig.feed.accountFollowers(targetUser.pk);
    let followers = [];
    let nextFollowers = await followersFeed.items();
    followers = followers.concat(nextFollowers);

    while (followersFeed.isMoreAvailable()) {
        nextFollowers = await followersFeed.items();
        followers = followers.concat(nextFollowers);
    }

    // Kirim followers target ke client
}, { concurrency: 5 });


// LOGIKA UTAMA APLIKASI NYA

const { IgApiClient } = require('instagram-private-api');
const express = require('express');
const router = express.Router();
const db = require('../config/firebase');  // Mengimpor konfigurasi Firestore
const ig = new IgApiClient();

// Fungsi untuk login dan menyimpan sesi
const login = async (username, password) => {
    console.log('Memulai proses login untuk', username);
    ig.state.generateDevice(username);

    try {
        await ig.account.login(username, password);
        console.log('Login berhasil untuk', username);

        const sessionData = await ig.state.serialize();
        console.log('Data sesi:', sessionData);

        if (sessionData && sessionData.cookies) {
            console.log('Cookies ditemukan:', sessionData.cookies);
        } else {
            console.error('Cookies tidak ditemukan dalam sesi');
        }

        if (!sessionData || !sessionData.cookies) {
            throw new Error('Data sesi tidak lengkap: cookies tidak ditemukan');
        }

        await saveSessionToFirestore(username, sessionData);
    } catch (error) {
        console.error('Login gagal untuk', username, error);
        throw new Error('Login gagal: ' + error.message);
    }
};

// Fungsi untuk menyimpan sesi ke Firestore
const saveSessionToFirestore = async (username, sessionData) => {
    try {
        const simplifiedSessionData = {
            cookies: sessionData.cookies || null,
            userAgent: sessionData.userAgent || null,
        };

        const sessionRef = db.collection('sessions').doc(username);
        const sessionDoc = await sessionRef.get();

        if (sessionDoc.exists) {
            await sessionRef.update({ session_data: simplifiedSessionData });
        } else {
            await sessionRef.set({ username, session_data: simplifiedSessionData });
        }

        console.log('Sesi berhasil disimpan untuk', username);
    } catch (error) {
        console.error('Gagal menyimpan sesi ke Firestore:', error);
        throw error;
    }
};

// Fungsi untuk memuat sesi dari Firestore
const loadSessionFromFirestore = async (username) => {
    try {
        const sessionRef = db.collection('sessions').doc(username);
        const sessionDoc = await sessionRef.get();

        if (sessionDoc.exists) {
            console.log('Sesi ditemukan untuk', username);
            return sessionDoc.data().session_data;  // Mengembalikan data sesi
        } else {
            console.log('Sesi tidak ditemukan untuk', username);
            return null;
        }
    } catch (error) {
        console.error('Gagal memuat sesi dari Firestore:', error);
        throw error;
    }
};

// Fungsi untuk memastikan sesi aktif sebelum mengambil data
const ensureSession = async (username) => {
    const session = await loadSessionFromFirestore(username);
    if (!session) {
        throw new Error('Pengguna harus login terlebih dahulu');
    }

    ig.state.deserialize(session);
    try {
        await ig.account.currentUser();
        console.log('Sesi valid untuk', username);
    } catch (error) {
        console.log('Sesi kadaluarsa untuk', username);
        throw new Error('Sesi kadaluarsa, harap login ulang');
    }
};

// Endpoint login
router.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) {
            return res.status(400).send('Username dan password diperlukan!');
        }

        await login(username, password);
        res.status(200).send('Login berhasil');
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).send('Login gagal: ' + error.message);
    }
});

// Endpoint untuk mengambil profil
router.get('/profile', async (req, res) => {
    try {
        const { username } = req.query;
        if (!username) {
            return res.status(400).send('Username diperlukan!');
        }

        await ensureSession(username);

        const user = await ig.account.currentUser();
        res.json({
            username: user.username,
            full_name: user.full_name,
            biography: user.biography,
            followers_count: user.follower_count,
            following_count: user.following_count,
            profile_picture_url: user.profile_pic_url,
        });
    } catch (error) {
        console.error('Error fetching profile:', error);
        res.status(500).send(error.message);
    }
});

// Endpoint untuk mengambil followers
router.get('/followers', async (req, res) => {
    try {
        const { username } = req.query;
        if (!username) {
            return res.status(400).send('Username diperlukan!');
        }

        await ensureSession(username);

        const user = await ig.account.currentUser();
        const followersFeed = ig.feed.accountFollowers(user.pk);
        let followers = [];
        let nextFollowers = await followersFeed.items();
        followers = followers.concat(nextFollowers);

        while (followersFeed.isMoreAvailable()) {
            nextFollowers = await followersFeed.items();
            followers = followers.concat(nextFollowers);
        }

        res.json(followers);
    } catch (error) {
        console.error('Error fetching followers:', error);
        res.status(500).send(error.message);
    }
});

// Endpoint untuk mengambil following
router.get('/following', async (req, res) => {
    try {
        const { username } = req.query;
        if (!username) {
            return res.status(400).send('Username diperlukan!');
        }

        await ensureSession(username);

        const user = await ig.account.currentUser();
        const followingFeed = ig.feed.accountFollowing(user.pk);
        let following = [];
        let nextFollowing = await followingFeed.items();
        following = following.concat(nextFollowing);

        while (followingFeed.isMoreAvailable()) {
            nextFollowing = await followingFeed.items();
            following = following.concat(nextFollowing);
        }

        res.json(following);
    } catch (error) {
        console.error('Error fetching following:', error);
        res.status(500).send(error.message);
    }
});

// Fungsi untuk mendapatkan daftar pengguna yang tidak mengikuti kembali
const getNonFollowers = (followers, following) => {
    const followersSet = new Set(followers.map(f => f.username));
    return following.filter(f => !followersSet.has(f.username)).map(f => f.username);
};

// Endpoint untuk mendapatkan pengguna yang tidak mengikuti kembali
router.get('/dontfollowback', async (req, res) => {
    try {
        const { username } = req.query;
        if (!username) {
            return res.status(400).send('Username diperlukan!');
        }

        await ensureSession(username);

        const user = await ig.account.currentUser();
        const followersFeed = ig.feed.accountFollowers(user.pk);
        let followers = [];
        let nextFollowers = await followersFeed.items();
        followers = followers.concat(nextFollowers);

        while (followersFeed.isMoreAvailable()) {
            nextFollowers = await followersFeed.items();
            followers = followers.concat(nextFollowers);
        }

        const followingFeed = ig.feed.accountFollowing(user.pk);
        let following = [];
        let nextFollowing = await followingFeed.items();
        following = following.concat(nextFollowing);

        while (followingFeed.isMoreAvailable()) {
            nextFollowing = await followingFeed.items();
            following = following.concat(nextFollowing);
        }

        const dontFollowBack = getNonFollowers(followers, following);
        res.json(dontFollowBack);
    } catch (error) {
        console.error('Error fetching dontFollowBack:', error);
        res.status(500).send(error.message);
    }
});

// Endpoint untuk mengambil followers dari username target
router.post('/followers_target', async (req, res) => {
    try {
        const { username, target } = req.body;
        if (!username || !target) {
            console.log('Username dan target tidak lengkap');
            return res.status(400).send('Username dan target diperlukan!');
        }

        // Pastikan sesi aktif untuk username
        console.log(`Memastikan sesi aktif untuk username: ${username}`);
        await ensureSession(username);

        // Ambil data user target
        console.log(`Mencari user target: ${target}`);
        const targetUser = await ig.user.searchExact(target);
        console.log('User target ditemukan:', targetUser.username);

        const followersFeed = ig.feed.accountFollowers(targetUser.pk);
        console.log(`Mengambil followers dari target: ${targetUser.username}`);

        let followers = [];
        let nextFollowers = await followersFeed.items();
        console.log(`Fetched first batch of followers: ${nextFollowers.length}`);
        followers = followers.concat(nextFollowers);

        // Ambil semua followers jika masih ada halaman berikutnya
        while (followersFeed.isMoreAvailable()) {
            console.log('Mengambil followers halaman berikutnya...');
            nextFollowers = await followersFeed.items();
            followers = followers.concat(nextFollowers);
        }

        console.log('Total followers fetched:', followers.length);

        // Kirim response dalam format JSON
        res.json({
            target: targetUser.username,
            followers_count: followers.length,
            followers: followers.map(f => ({ username: f.username, full_name: f.full_name, profile_picture: f.profile_pic_url })),
        });
    } catch (error) {
        console.error('Error fetching followers from target:', error);
        res.status(500).send({
            error: error.message,
            stack: error.stack,
        });
    }
});





module.exports = router;
