# WIRA NUSA — rebuild berbasis Draft Wira Nusa

Versi ini dibuat ulang dari file `main.py` sumber yang tersedia, isi Draft Wira Nusa, gambar map desa yang tertanam di Draft, dan ZIP `Asset karakter.zip` yang baru diunggah.

## Menjalankan
1. Extract ZIP ke folder baru.
2. Buka folder `WiraNusa_REBUILD` di VS Code.
3. Jalankan terminal di folder tersebut.
4. Install dependency: `python -m pip install pygame-ce`
5. Jalankan: `python main.py`

## Kontrol
- Dialog: `ENTER`, `SPACE`, atau `Z`; mouse klik juga lanjut.
- Pilihan: `W/UP`, `S/DOWN`, `ENTER`.
- Map: tahan `W/A/S/D` atau arrow keys untuk berjalan.
- Choice 1 opsi 3: dekat kentongan tekan `E`; setelah ditemukan tekan `ENTER`.
- Battle 5 map: kumpulkan 3 paket obat; hindari pengejar; setelah 3/3 tekan `ENTER`.
- Battle map hanya membatasi kaki player pada road mask `assets/walkable_mask.png`.

## Revisi utama
- Battle 5 dan kentongan memakai panorama sepia landscape yang diberikan pengguna (2048×682).
- Player dan musuh alpha-trim per cell agar padding transparan tidak membuat sprite kecil; target player 74×98 dan enemy 68×92, aspect ratio dipertahankan.
- Battle 5 musuh bergerak acak pada waypoint jalan, tidak mengejar; saat tersentuh, player, 3 paket obat, dan patrol musuh reset ke awal misi.
- Walkable mask 2048×682 mengikuti jalan horizontal, akses tangga, jalur diagonal, pendekatan jembatan, dan bypass di bawah area kios; titik kaki player dibatasi mask.
- Sprite Budi, Sari, dan perwira Belanda memakai sprite sheet transparan dari `Asset karakter.zip`.
- Crop sprite tidak memakai color-key hitam dan tidak memakai API Mask `get_bounding_rect`.
- Map desa top-down dari Draft menjadi world map yang bisa di-scroll oleh kamera.
- Player bergerak kontinu dan dibatasi road mask.
- Choice 1 opsi 3: Budi mencari kentongan, interaksi `E`.
- Battle 5: Sari mencari 3 paket obat di map sambil dikejar satu NPC perwira; collision memberi damage cooldown dan dapat retry.
- Scene dialog berada di kotak kecil di bagian atas.
- Portrait karakter berada di dalam kotak dialog bagian bawah; teks berada di sebelah portrait.
- Dialog/flow cerita mengikuti Draft Wira Nusa. Bagian yang tidak ada di Draft tetap ditandai belum tersedia, tidak ditambahkan cerita baru.

## Pemeriksaan
- `main.py` berhasil `py_compile`.
- Semua referensi asset pada kode tersedia.
- ZIP integrity diperiksa.
- Transparansi alpha sprite sheet Budi/Sari/Belanda/Jepang diperiksa.
- Road mask dibuat dari warna jalan pada map dan dibatasi koridor jalan.
- Connectivity grid-step test berhasil dari titik awal ke kentongan dan ketiga item obat.
- Runtime Pygame tidak dapat diuji di lingkungan pembuat karena paket Pygame tidak dapat diinstal di sini; tes runtime tetap perlu dilakukan di Windows pengguna.
