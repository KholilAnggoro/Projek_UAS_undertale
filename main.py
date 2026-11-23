import pygame
import random
import math
import os
import sys
#tes2
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LEGASI SATRIA NUSANTARA")
clock = pygame.time.Clock()

# Warna & Font
BLACK, WHITE, RED = (0, 0, 0), (255, 255, 255), (235, 55, 70)
YELLOW, GOLD, PURPLE, CYAN, GRAY = (255, 220, 60), (245, 185, 45), (155, 75, 235), (60, 225, 255), (135, 135, 150)
GREEN_PEACE = (80, 220, 135)
DARK_BG = (18, 12, 32)

font_title = pygame.font.SysFont("Courier New", 36, bold=True)
font_main = pygame.font.SysFont("Courier New", 19, bold=True)
font_small = pygame.font.SysFont("Courier New", 17, bold=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def load_asset(base_name, size, transparent_key=None):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        path = os.path.join(ASSETS_DIR, base_name + ext)
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(img, size)
            if transparent_key is not None:
                img.set_colorkey(transparent_key)
            return img
    fb = pygame.Surface(size)
    fb.fill((38, 22, 55))
    pygame.draw.rect(fb, GOLD, (0, 0, size[0], size[1]), 2)
    return fb


def build_fallback_keris(size=(22, 22)):
    surf = pygame.Surface(size)
    surf.fill(BLACK)
    cx = size[0] // 2
    # Gagang keris emas
    pygame.draw.rect(surf, GOLD, (cx - 2, 2, 4, 5))
    # Ganja / pelindung bilah
    pygame.draw.rect(surf, YELLOW, (cx - 6, 7, 12, 3))
    # Bilah keris berlekuk
    pts = [
        (cx, 10), (cx + 3, 12), (cx - 1, 14),
        (cx + 2, 16), (cx - 1, 18), (cx, size[1] - 1),
        (cx - 2, 17), (cx + 1, 15), (cx - 2, 13), (cx + 1, 11)
    ]
    pygame.draw.polygon(surf, CYAN, pts)
    surf.set_colorkey(BLACK)
    return pygame.transform.smoothscale(surf, size)


# Pemuatan Aset Gambar dari Folder assets/
IMG_PEACE = load_asset("nusantara_damai", (360, 170), None)
IMG_STORY1 = load_asset("nusantara_kawah", (360, 170), None)
IMG_STORY2 = load_asset("nusantara_kawah", (360, 170), None)
IMG_CABANG = load_asset("nusantara_cabang", (360, 170), None)
IMG_HERO = load_asset("bima_hero", (76, 76), (0, 0, 0))
IMG_HERO_MINI = pygame.transform.smoothscale(IMG_HERO, (28, 28))

raw_keris = load_asset("keris_icon", (22, 22), (0, 0, 0))
has_real_keris = any(
    os.path.exists(os.path.join(ASSETS_DIR, "keris_icon" + ext))
    for ext in (".png", ".jpg", ".jpeg", ".webp")
)
IMG_KERIS = raw_keris if has_real_keris else build_fallback_keris((22, 22))
IMG_KERIS_BATTLE = pygame.transform.smoothscale(IMG_KERIS, (20, 20))

ENEMY_SPRITES = {
    "Garuda Bayang": load_asset("garuda_bayang", (105, 105), (255, 255, 255)),
    "Siluman Api Kawah": load_asset("garuda_bayang", (105, 105), (255, 255, 255)),
    "Naga Kegelapan": load_asset("naga_kegelapan", (115, 115), (255, 255, 255)),
}

# Cerita Pembuka
INTRO_SLIDES = [
    ("Jauh di masa lalu, Desa Sinar Pagi hidup tenteram di bawah langit biru dan bukit hijau.", IMG_PEACE),
    ("Warga hidup rukun, dan Bima giat berlatih pencak silat serta kebijaksanaan leluhur.", IMG_PEACE),
    ("Namun suatu senja, kabut ungu pekat turun dari puncak gunung dan menelan cahaya desa.", IMG_STORY1),
    ("Kutukan itu berpusat di Kawah Gelap Bayang—di mana jalan terbagi menuju nasib berbeda.", IMG_CABANG),
]

# Percabangan 1: Di Gerbang Kawah
CHOICE_1 = {
    "title": "PERCABANGAN CERITA 1: ALTAR LELUHUR",
    "prompt": "Di gerbang Kawah Gelap Bayang, Bima menatap dua pusaka leluhur. Jalan mana yang dipilih?",
    "img": IMG_STORY2,
    "options": [
        {
            "label": "Cabut Keris Pusaka (+6 ATK | Jalur Satria)",
            "path": "PUSAKA",
            "result": "Keris emas menyala terang! Kekuatan serangan Bima bertambah (+6 ATK)."
        },
        {
            "label": "Ambil Tirta Kidung (+10 Max HP | Jalur Harmoni)",
            "path": "HARMONI",
            "result": "Tirta suci menenangkan batin Bima! Max HP & HP pulih (+10 Max HP)."
        }
    ]
}

# Percabangan 2: Persimpangan Hutan Kawah (Mengubah Alur Lawan!)
CHOICE_2 = {
    "title": "PERCABANGAN CERITA 2: PERSIMPANGAN KAWAH",
    "prompt": "Garuda Bayang tumbang. Di depan ada Jurang Api (penuh musuh) dan Sungai Cahaya (lebih singkat).",
    "img": IMG_CABANG,
    "options": [
        {
            "label": "Masuk Jurang Api (Lawan Siluman Api + Bonus EXP)",
            "path": "JURANG_API",
            "result": "Bima menuruni Jurang Api! Siluman Api Kawah menghadang di tengah jalan."
        },
        {
            "label": "Lewati Sungai Cahaya (Langsung ke Naga + Pulih 15 HP)",
            "path": "SUNGAI_CAHAYA",
            "result": "Air sungai sejernih embun memulihkan tenaga Bima (+15 HP) menuju sarang Naga!"
        }
    ]
}

FOE_GARUDA = {
    "name": "Garuda Bayang", "atk": 2, "def": 0,
    "pre_dialog": [
        "GARUDA BAYANG: 'Kau berani masuk ke sarang bayangan, manusia muda?'",
        "BIMA: 'Desaku dulu damai sebelum kabutmu datang! Kembalikan cahayanya!'",
        "GARUDA BAYANG: 'Angin gelapku akan menguji nyalimu!'"
    ],
    "desc": "GARUDA BAYANG - ATK 2 DEF 0. Roh penjaga gerbang berkabut.",
    "acts": ["Telaah", "Seru Semangat", "Ejek Bayangan"], "purify_act": "Seru Semangat",
    "resp": {
        "Seru Semangat": "* Suara lantang Bima mengguncang kabut! Garuda Bayang siap disucikan!",
        "Ejek Bayangan": "* Garuda Bayang murka dan mengepakkan sayap gelap lebih kencang!"
    }
}

FOE_SILUMAN_API = {
    "name": "Siluman Api Kawah", "atk": 3, "def": 0,
    "pre_dialog": [
        "SILUMAN API: 'Wuss! Jalur Jurang Api ini membara karena dendam kuno!'",
        "BIMA: 'Api kegelapan tidak akan memadamkan semangat Desa Sinar Pagi!'",
        "SILUMAN API: 'Rasakan panas bara di dasar jurang ini!'"
    ],
    "desc": "SILUMAN API KAWAH - ATK 3 DEF 0. Makhluk bara di jalur Jurang Api.",
    "acts": ["Telaah", "Tarik Napas", "Lawan Bara"], "purify_act": "Tarik Napas",
    "resp": {
        "Tarik Napas": "* Napas tenang Bima meredam bara! Siluman Api siap disucikan!",
        "Lawan Bara": "* Bara api memercik tajam dan menambah serangan lawan!"
    }
}

FOE_NAGA = {
    "name": "Naga Kegelapan", "atk": 3, "def": 1,
    "pre_dialog": [
        "NAGA KEGELAPAN: 'Hmph... Bocah dari desa kecil berani menantang penguasa kawah?'",
        "BIMA: 'Aku tidak gentar! Demi rakyatku, kutukan ini berakhir di sini!'",
        "NAGA KEGELAPAN: 'Mari kita lihat apakah tekadmu sekuat legenda leluhurmu!'"
    ],
    "desc": "NAGA KEGELAPAN - ATK 3 DEF 1. Naga kuno yang terbelenggu kutukan.",
    "acts": ["Telaah", "Kidung Damai", "Gertak Satria"], "purify_act": "Kidung Damai",
    "resp": {
        "Kidung Damai": "* Cahaya lembut meredakan api ungu! Naga Kegelapan siap disucikan!",
        "Gertak Satria": "* Naga Kegelapan mengaum keras dan meningkatkan kekuatannya!"
    }
}

TUTORIAL_PAGES = [
    [
        "PANDUAN BERMAIN - BAGIAN 1: KONTROL & PERTARUNGAN",
        "",
        "* Gerakkan KERIS pusaka di kotak battle pakai",
        "  tombol PANAH atau W A S D untuk hindari serangan.",
        "* Pilih menu SERANG / AKSI / JAMU / SEGEL pakai",
        "  PANAH KIRI-KANAN lalu tekan Z / ENTER atau KLIK."
    ],
    [
        "PANDUAN BERMAIN - BAGIAN 2: AKSI, SEGEL & CERITA",
        "",
        "* Pakai AKSI (pilih opsi yang melemahkan musuh),",
        "  lalu pilih SEGEL -> Sucikan untuk menang damai.",
        "* Pakai JAMU kapan saja untuk memulihkan HP Bima.",
        "* Pilihan di PERCABANGAN CERITA mengubah lawan",
        "  yang muncul, stat Bima, serta EPILOG akhir!"
    ]
]

# State: TITLE, TUTORIAL, STORY, CHOICE, PRE_DIALOG, PLAYER, ACT, SEAL, ENEMY, DIALOG, WIN, OVER, EPILOGUE
state = "TITLE"
prev_state_after_tut = "TITLE"
tut_page = 0

sel_title, sel_choice, sel_menu, sel_sub, sel_end = 0, 0, 0, 0, 0

story_idx, story_char = 0, 0.0
active_choice = None
choice_step = 1
choice_feedback = ""
showing_choice_result = False

pre_idx, pre_char = 0, 0.0
ep_idx, ep_char = 0, 0.0
epilogue_lines = []
epilogue_title = ""

# Jalur Cerita & Antrean Lawan
path_pusaka = 0
path_harmoni = 0
chose_jurang_api = False
foe_queue = []
foe_queue_idx = 0

lv, exp, next_exp = 1, 0, 8
max_hp, hp, atk = 36, 36, 15
foe = FOE_GARUDA
e_max_hp, e_hp = 42, 42
purifiable, atk_mod = False, 0
dialog = ""

box = pygame.Rect(220, 230, 200, 150)
keris_hitbox = pygame.Rect(314, 299, 12, 12)
keris_pos = [320.0, 305.0]
keris_speed = 5.5
inv_timer, turn_timer, anim_tick = 0, 0, 0
bullets = []


def draw_keris_pointer(x, y):
    screen.blit(IMG_KERIS, (int(x), int(y)))


def draw_battle_keris(cx, cy):
    # Gambar sprite keris dengan pusat di (cx, cy)
    rect = IMG_KERIS_BATTLE.get_rect(center=(int(cx), int(cy)))
    screen.blit(IMG_KERIS_BATTLE, rect)
    keris_hitbox.center = (int(cx), int(cy))


def wrap_text(txt, max_w):
    if txt == "":
        return [""]
    lines, cur = [], ""
    for w in txt.split(" "):
        if font_main.size(cur + w + " ")[0] <= max_w:
            cur += w + " "
        else:
            lines.append(cur.strip())
            cur = w + " "
    if cur:
        lines.append(cur.strip())
    return lines


def reset_all_stats():
    global lv, exp, next_exp, max_hp, hp, atk
    global path_pusaka, path_harmoni, chose_jurang_api, foe_queue, foe_queue_idx
    lv, exp, next_exp = 1, 0, 8
    max_hp, hp, atk = 36, 36, 15
    path_pusaka = 0
    path_harmoni = 0
    chose_jurang_api = False
    foe_queue = []
    foe_queue_idx = 0


def start_new_story():
    global state, story_idx, story_char, choice_step, showing_choice_result
    reset_all_stats()
    story_idx = 0
    story_char = 0.0
    choice_step = 1
    showing_choice_result = False
    state = "STORY"


def open_choice(step_num):
    global state, active_choice, sel_choice, choice_step, showing_choice_result
    choice_step = step_num
    active_choice = CHOICE_1 if step_num == 1 else CHOICE_2
    sel_choice = 0
    showing_choice_result = False
    state = "CHOICE"


def apply_choice():
    global max_hp, hp, atk, path_pusaka, path_harmoni, chose_jurang_api
    global foe_queue, foe_queue_idx, choice_feedback, showing_choice_result

    opt = active_choice["options"][sel_choice]
    if choice_step == 1:
        if opt["path"] == "PUSAKA":
            path_pusaka += 1
            atk += 6
        else:
            path_harmoni += 1
            max_hp += 10
            hp = max_hp
        foe_queue = [FOE_GARUDA]
        foe_queue_idx = 0
    else:
        if opt["path"] == "JURANG_API":
            chose_jurang_api = True
            foe_queue = [FOE_SILUMAN_API, FOE_NAGA]
            foe_queue_idx = 0
        else:
            chose_jurang_api = False
            hp = min(max_hp, hp + 15)
            foe_queue = [FOE_NAGA]
            foe_queue_idx = 0

    choice_feedback = opt["result"]
    showing_choice_result = True


def continue_after_choice():
    global showing_choice_result
    showing_choice_result = False
    start_foe_at_index(foe_queue_idx)


def start_foe_at_index(idx):
    global foe, e_max_hp, e_hp, purifiable, atk_mod, state, sel_menu, pre_idx, pre_char
    foe = foe_queue[idx]
    if foe["name"] == "Garuda Bayang":
        e_max_hp = 40
    elif foe["name"] == "Siluman Api Kawah":
        e_max_hp = 44
    else:
        e_max_hp = 54
    e_hp = e_max_hp
    purifiable = (foe["name"] == "Naga Kegelapan" and path_harmoni >= 1)
    atk_mod = 0
    sel_menu = 0
    pre_idx = 0
    pre_char = 0.0
    state = "PRE_DIALOG"


def build_epilogue(mode):
    global state, epilogue_title, epilogue_lines, ep_idx, ep_char, sel_end
    ep_idx = 0
    ep_char = 0.0
    sel_end = 0

    if mode == "SUCIKAN" or path_harmoni > path_pusaka:
        epilogue_title = "ENDING: PENJAGA HARMONI"
        epilogue_lines = [
            "Tirta kidung dan doa leluhur menyucikan kutukan di Kawah Gelap Bayang.",
            "Naga Kegelapan kembali tenang, sementara kabut ungu perlahan sirna dari langit.",
            "Desa Sinar Pagi menyambut Bima sebagai pahlawan penjaga keseimbangan alam.",
            "EPILOG TAMAT - Damai abadi kembali ke Nusantara."
        ]
    elif chose_jurang_api and path_pusaka >= 1:
        epilogue_title = "ENDING: PENAKLUK JURANG API"
        epilogue_lines = [
            "Menembus Jurang Api hingga menaklukkan Naga Kegelapan, Bima menepati sumpahnya.",
            "Bilah keris pusaka bersinar membelah sisa kabut kutukan di puncak kawah.",
            "Rakyat Desa Sinar Pagi merayakan kepulangan Bima dengan penuh rasa bangga.",
            "EPILOG TAMAT - Legenda keberanian Bima abadi selamanya."
        ]
    else:
        epilogue_title = "ENDING: SATRIA SUNGAI CAHAYA"
        epilogue_lines = [
            "Dengan langkah pasti dan ketenangan hati, Bima menuntaskan kutukan kawah.",
            "Langit cerah kembali menyinari sawah dan rumah-rumah di Desa Sinar Pagi.",
            "Bima terus berlatih, siap menjaga kedamaian tanah air dari ancaman apa pun.",
            "EPILOG TAMAT - Fajar baru menyinari Nusantara."
        ]
    state = "EPILOGUE"


def start_enemy():
    global state, turn_timer, bullets, keris_pos
    state = "ENEMY"
    turn_timer = 210
    bullets = []
    keris_pos = [float(box.centerx), float(box.centery)]
    keris_hitbox.center = (box.centerx, box.centery)


def main_action():
    global e_hp, hp, dialog, state, sel_sub
    opt = ["SERANG", "AKSI", "JAMU", "SEGEL"][sel_menu]
    if opt == "SERANG":
        dmg = max(5, random.randint(atk, atk + 9) - foe["def"])
        e_hp = max(0, e_hp - dmg)
        dialog = f"* Bima menebaskan keris ke {foe['name']}! ({dmg} DMG)"
        state = "DIALOG"
    elif opt == "AKSI":
        sel_sub = 0
        state = "ACT"
    elif opt == "JAMU":
        heal = 16 + lv * 3
        hp = min(max_hp, hp + heal)
        dialog = f"* Bima meminum Jamu Akar Naga. HP pulih +{heal}!"
        state = "DIALOG"
    elif opt == "SEGEL":
        sel_sub = 0
        state = "SEAL"


def act_action():
    global purifiable, atk_mod, dialog, state
    act = foe["acts"][sel_sub]
    if act == "Telaah":
        dialog = f"* {foe['desc']}"
    else:
        dialog = foe["resp"][act]
        if act == foe["purify_act"]:
            purifiable = True
        else:
            atk_mod = 1
    state = "DIALOG"


def advance_after_foe_cleared():
    global foe_queue_idx, dialog, state
    foe_queue_idx += 1
    if foe_queue_idx < len(foe_queue):
        start_foe_at_index(foe_queue_idx)
    elif foe["name"] == "Garuda Bayang":
        open_choice(2)
    else:
        build_epilogue("KALAHKAN")


def seal_action():
    global dialog, state
    if sel_sub == 0:
        if purifiable:
            if foe["name"] == "Naga Kegelapan":
                build_epilogue("SUCIKAN")
            else:
                dialog = f"* {foe['name']} tersucikan oleh semangat Bima!"
                state = "WIN"
        else:
            dialog = f"* {foe['name']} belum dapat disucikan! Gunakan AKSI yang tepat dulu."
            state = "DIALOG"
    else:
        dialog = "* Bima mundur sejenak mengatur napas."
        state = "WIN"


def check_win():
    global exp, lv, next_exp, max_hp, hp, atk, dialog, state
    if e_hp <= 0:
        if foe["name"] == "Naga Kegelapan":
            build_epilogue("KALAHKAN")
            return
        gain = 16 if foe["name"] == "Siluman Api Kawah" else 14
        exp += gain
        while exp >= next_exp:
            lv += 1
            next_exp += lv * 8
            max_hp += 6
            hp = max_hp
            atk += 4
        dialog = f"* {foe['name']} tumbang! +{gain} EXP. Lanjut ke perjalanan berikutnya!"
        state = "WIN"
    else:
        start_enemy()


running = True
while running:
    anim_tick += 1
    screen.fill(BLACK)

    t_rects = [pygame.Rect(205, 272 + i * 44, 230, 36) for i in range(3)]
    c_rects = [pygame.Rect(75, 295 + i * 46, 490, 38) for i in range(2)]
    m_rects = [pygame.Rect(40 + i * 145, 430, 125, 36) for i in range(4)]
    subs = foe["acts"] if state == "ACT" else ["Sucikan", "Mundur"]
    s_rects = [pygame.Rect(70 + (i % 2) * 260, 255 + (i // 2) * 40, 240, 32) for i in range(len(subs))]
    end_rects = [pygame.Rect(170, 355, 140, 38), pygame.Rect(330, 355, 140, 38)]

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        if ev.type == pygame.MOUSEMOTION:
            if state == "TITLE":
                for i, r in enumerate(t_rects):
                    if r.collidepoint(ev.pos): sel_title = i
            elif state == "CHOICE" and not showing_choice_result:
                for i, r in enumerate(c_rects):
                    if r.collidepoint(ev.pos): sel_choice = i
            elif state == "PLAYER":
                for i, r in enumerate(m_rects):
                    if r.collidepoint(ev.pos): sel_menu = i
            elif state in ("ACT", "SEAL"):
                for i, r in enumerate(s_rects):
                    if r.collidepoint(ev.pos): sel_sub = i
            elif state == "EPILOGUE" and ep_idx >= len(epilogue_lines) - 1:
                for i, r in enumerate(end_rects):
                    if r.collidepoint(ev.pos): sel_end = i

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if state == "TITLE":
                for i, r in enumerate(t_rects):
                    if r.collidepoint(ev.pos):
                        if i == 0:
                            start_new_story()
                        elif i == 1:
                            prev_state_after_tut = "TITLE"
                            tut_page = 0
                            state = "TUTORIAL"
                        else:
                            running = False
            elif state == "TUTORIAL":
                if tut_page < len(TUTORIAL_PAGES) - 1:
                    tut_page += 1
                else:
                    state = prev_state_after_tut
            elif state == "STORY":
                txt_now = INTRO_SLIDES[story_idx][0]
                if story_char < len(txt_now):
                    story_char = float(len(txt_now))
                else:
                    story_idx += 1
                    story_char = 0.0
                    if story_idx >= len(INTRO_SLIDES):
                        open_choice(1)
            elif state == "CHOICE":
                if showing_choice_result:
                    continue_after_choice()
                else:
                    for i, r in enumerate(c_rects):
                        if r.collidepoint(ev.pos):
                            sel_choice = i
                            apply_choice()
            elif state == "PRE_DIALOG":
                cur_p = foe["pre_dialog"][pre_idx]
                if pre_char < len(cur_p):
                    pre_char = float(len(cur_p))
                else:
                    pre_idx += 1
                    pre_char = 0.0
                    if pre_idx >= len(foe["pre_dialog"]):
                        dialog = f"* {foe['name']} menghadang Bima!"
                        state = "PLAYER"
            elif state == "PLAYER":
                for i, r in enumerate(m_rects):
                    if r.collidepoint(ev.pos): sel_menu = i; main_action()
            elif state == "ACT":
                for i, r in enumerate(s_rects):
                    if r.collidepoint(ev.pos): sel_sub = i; act_action()
            elif state == "SEAL":
                for i, r in enumerate(s_rects):
                    if r.collidepoint(ev.pos): sel_sub = i; seal_action()
            elif state == "DIALOG":
                check_win()
            elif state == "WIN":
                advance_after_foe_cleared()
            elif state == "OVER":
                start_new_story()
            elif state == "EPILOGUE":
                cur_ep = epilogue_lines[ep_idx]
                if ep_char < len(cur_ep):
                    ep_char = float(len(cur_ep))
                elif ep_idx < len(epilogue_lines) - 1:
                    ep_idx += 1
                    ep_char = 0.0
                else:
                    for i, r in enumerate(end_rects):
                        if r.collidepoint(ev.pos):
                            if i == 0: state = "TITLE"; sel_title = 0
                            else: running = False

        if ev.type == pygame.KEYDOWN:
            if state == "TITLE":
                if ev.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                    step = 1 if ev.key in (pygame.K_DOWN, pygame.K_s) else -1
                    sel_title = (sel_title + step) % 3
                elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    if sel_title == 0:
                        start_new_story()
                    elif sel_title == 1:
                        prev_state_after_tut = "TITLE"
                        tut_page = 0
                        state = "TUTORIAL"
                    else:
                        running = False
                elif ev.key == pygame.K_t:
                    prev_state_after_tut = "TITLE"
                    tut_page = 0
                    state = "TUTORIAL"
            elif state == "TUTORIAL":
                if ev.key in (pygame.K_x, pygame.K_ESCAPE):
                    state = prev_state_after_tut
                elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT, pygame.K_d):
                    if tut_page < len(TUTORIAL_PAGES) - 1:
                        tut_page += 1
                    else:
                        state = prev_state_after_tut
                elif ev.key in (pygame.K_LEFT, pygame.K_a) and tut_page > 0:
                    tut_page -= 1
            elif state == "STORY":
                if ev.key == pygame.K_x:
                    open_choice(1)
                elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    txt_now = INTRO_SLIDES[story_idx][0]
                    if story_char < len(txt_now):
                        story_char = float(len(txt_now))
                    else:
                        story_idx += 1
                        story_char = 0.0
                        if story_idx >= len(INTRO_SLIDES):
                            open_choice(1)
            elif state == "CHOICE":
                if showing_choice_result:
                    if ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        continue_after_choice()
                else:
                    if ev.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                        sel_choice = (sel_choice + 1) % 2
                    elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        apply_choice()
            elif state == "PRE_DIALOG":
                if ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    cur_p = foe["pre_dialog"][pre_idx]
                    if pre_char < len(cur_p):
                        pre_char = float(len(cur_p))
                    else:
                        pre_idx += 1
                        pre_char = 0.0
                        if pre_idx >= len(foe["pre_dialog"]):
                            dialog = f"* {foe['name']} menghadang Bima!"
                            state = "PLAYER"
            elif state == "PLAYER":
                if ev.key in (pygame.K_LEFT, pygame.K_a): sel_menu = (sel_menu - 1) % 4
                elif ev.key in (pygame.K_RIGHT, pygame.K_d): sel_menu = (sel_menu + 1) % 4
                elif ev.key == pygame.K_t:
                    prev_state_after_tut = "PLAYER"
                    tut_page = 0
                    state = "TUTORIAL"
                elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE): main_action()
            elif state in ("ACT", "SEAL"):
                if ev.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                    sel_sub = (sel_sub - 1) % len(subs)
                elif ev.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d, pygame.K_s):
                    sel_sub = (sel_sub + 1) % len(subs)
                elif ev.key in (pygame.K_x, pygame.K_ESCAPE): state = "PLAYER"
                elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    act_action() if state == "ACT" else seal_action()
            elif state == "DIALOG" and ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                check_win()
            elif state == "WIN" and ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                advance_after_foe_cleared()
            elif state == "OVER" and ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                start_new_story()
            elif state == "EPILOGUE":
                cur_ep = epilogue_lines[ep_idx]
                if ep_char < len(cur_ep):
                    ep_char = float(len(cur_ep))
                elif ep_idx < len(epilogue_lines) - 1:
                    if ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        ep_idx += 1
                        ep_char = 0.0
                else:
                    if ev.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                        sel_end = (sel_end + 1) % 2
                    elif ev.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        if sel_end == 0: state = "TITLE"; sel_title = 0
                        else: running = False

    # --- RENDER LAYAR ---
    if state == "TITLE":
        screen.fill(DARK_BG)
        t1 = font_title.render("LEGASI SATRIA NUSANTARA", True, GOLD)
        t2 = font_small.render("DONGENG BIMA & KAWAH GELAP BAYANG", True, CYAN)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 48))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 96))
        screen.blit(IMG_HERO, (WIDTH // 2 - IMG_HERO.get_width() // 2, 142))
        for i, txt in enumerate(["MULAI CERITA", "TUTORIAL", "KELUAR"]):
            c = CYAN if i == sel_title else WHITE
            screen.blit(font_main.render(txt, True, c), (255, 278 + i * 44))
            if i == sel_title:
                draw_keris_pointer(222, 275 + i * 44)
        h = font_small.render("[Panah / Mouse & Z / Enter | Tekan T untuk Tutorial]", True, GRAY)
        screen.blit(h, (WIDTH // 2 - h.get_width() // 2, 424))

    elif state == "TUTORIAL":
        screen.fill(DARK_BG)
        pygame.draw.rect(screen, GOLD, (45, 38, WIDTH - 90, 365), 3)
        lines = TUTORIAL_PAGES[tut_page]
        for idx, ln in enumerate(lines):
            col = GOLD if idx == 0 else (CYAN if ln.startswith("*") else WHITE)
            fnt = font_main if idx == 0 else font_small
            screen.blit(fnt.render(ln, True, col), (68, 62 + idx * 44))
        nav = font_small.render(
            f"[Halaman {tut_page+1}/{len(TUTORIAL_PAGES)}] [Klik / Z: Lanjut] [X / ESC: Kembali]",
            True, CYAN
        )
        screen.blit(nav, (WIDTH // 2 - nav.get_width() // 2, 424))

    elif state == "STORY":
        screen.fill(DARK_BG)
        cur_s, cur_img = INTRO_SLIDES[story_idx]
        if story_char < len(cur_s): story_char += 0.75
        screen.blit(cur_img, (140, 40))
        pygame.draw.rect(screen, GOLD, (140, 40, 360, 170), 3)
        for i, ln in enumerate(wrap_text(cur_s[:int(story_char)], WIDTH - 140)):
            screen.blit(font_main.render(ln, True, WHITE), (70, 240 + i * 30))
        nav = font_small.render(f"[{story_idx+1}/{len(INTRO_SLIDES)}] [Klik / Z: Lanjut] [X: Ke Percabangan]", True, CYAN)
        screen.blit(nav, (WIDTH // 2 - nav.get_width() // 2, 425))

    elif state == "CHOICE":
        screen.fill(DARK_BG)
        hdr = font_small.render(active_choice["title"], True, GOLD)
        screen.blit(hdr, (WIDTH // 2 - hdr.get_width() // 2, 12))
        screen.blit(active_choice["img"], (140, 36))
        pygame.draw.rect(screen, PURPLE, (140, 36, 360, 170), 3)

        if showing_choice_result:
            for i, ln in enumerate(wrap_text(choice_feedback, WIDTH - 120)):
                screen.blit(font_main.render(ln, True, YELLOW), (60, 242 + i * 30))
            screen.blit(font_small.render("[Klik / Z untuk melanjutkan cerita]", True, CYAN), (60, 365))
        else:
            for i, ln in enumerate(wrap_text(active_choice["prompt"], WIDTH - 120)):
                screen.blit(font_main.render(ln, True, WHITE), (60, 220 + i * 26))
            for i, opt in enumerate(active_choice["options"]):
                r = c_rects[i]
                is_s = (i == sel_choice)
                col = CYAN if is_s else WHITE
                pygame.draw.rect(screen, col, r, 2)
                screen.blit(font_small.render(opt["label"], True, col), (r.x + 36, r.y + 9))
                if is_s:
                    draw_keris_pointer(r.x + 8, r.y + 8)

    elif state == "EPILOGUE":
        screen.fill((12, 24, 34))
        t_end = font_title.render(epilogue_title, True, GREEN_PEACE)
        screen.blit(t_end, (WIDTH // 2 - t_end.get_width() // 2, 32))
        pygame.draw.rect(screen, GREEN_PEACE, (140, 88, 360, 125), 2)
        screen.blit(IMG_HERO, (WIDTH // 2 - IMG_HERO.get_width() // 2, 112))

        cur_ep = epilogue_lines[ep_idx]
        if ep_char < len(cur_ep): ep_char += 0.75
        for i, ln in enumerate(wrap_text(cur_ep[:int(ep_char)], WIDTH - 120)):
            screen.blit(font_main.render(ln, True, WHITE), (60, 232 + i * 28))

        info = font_small.render(f"BIMA  LV {lv}   ATK {atk}   HP {hp}/{max_hp}", True, GOLD)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 316))

        if ep_idx >= len(epilogue_lines) - 1 and ep_char >= len(cur_ep):
            for i, lbl in enumerate(["MAIN LAGI", "KELUAR"]):
                r = end_rects[i]
                col = CYAN if i == sel_end else WHITE
                pygame.draw.rect(screen, col, r, 2)
                screen.blit(font_main.render(lbl, True, col), (r.x + 24, r.y + 8))
                if i == sel_end:
                    draw_keris_pointer(r.x + 2, r.y + 8)
        else:
            nxt = font_small.render(f"[{ep_idx+1}/{len(epilogue_lines)}] Klik / Z untuk lanjut", True, CYAN)
            screen.blit(nxt, (WIDTH // 2 - nxt.get_width() // 2, 420))

    else:
        pygame.draw.rect(screen, (14, 6, 26), (0, 0, WIDTH, 225))

        if state == "ENEMY":
            k = pygame.key.get_pressed()
            if (k[pygame.K_LEFT] or k[pygame.K_a]) and keris_pos[0] > box.left + 12:
                keris_pos[0] -= keris_speed
            if (k[pygame.K_RIGHT] or k[pygame.K_d]) and keris_pos[0] < box.right - 12:
                keris_pos[0] += keris_speed
            if (k[pygame.K_UP] or k[pygame.K_w]) and keris_pos[1] > box.top + 12:
                keris_pos[1] -= keris_speed
            if (k[pygame.K_DOWN] or k[pygame.K_s]) and keris_pos[1] < box.bottom - 12:
                keris_pos[1] += keris_speed

            keris_hitbox.center = (int(keris_pos[0]), int(keris_pos[1]))

            if random.randint(1, 18) == 1:
                bullets.append(pygame.Rect(random.randint(box.left + 12, box.right - 12), box.top - 8, 8, 8))

            for b in bullets[:]:
                b.y += 2.6
                if b.top > box.bottom:
                    bullets.remove(b)
                elif keris_hitbox.colliderect(b) and inv_timer == 0:
                    hp = max(0, hp - (foe["atk"] + atk_mod))
                    inv_timer = 75
                    bullets.remove(b)
                    if hp == 0:
                        dialog, state = "* Bima terjatuh... Semangat Nusantara memanggilmu bangkit!", "OVER"
            if inv_timer > 0:
                inv_timer -= 1
            turn_timer -= 1
            if turn_timer <= 0 and state == "ENEMY":
                dialog = f"* {foe['name']} siap disucikan (CYAN)!" if purifiable else f"* {foe['name']} bersiap menyerang lagi!"
                state = "PLAYER"

        ncol = CYAN if purifiable else WHITE
        nsurf = font_small.render(foe["name"], True, ncol)
        screen.blit(nsurf, (WIDTH // 2 - nsurf.get_width() // 2, 14))

        bob_y = int(math.sin(anim_tick * 0.1) * 4)
        f_img = ENEMY_SPRITES[foe["name"]]
        screen.blit(f_img, (WIDTH // 2 - f_img.get_width() // 2, 42 + bob_y))

        pygame.draw.rect(screen, RED, (WIDTH // 2 - 50, 155, 100, 10))
        pygame.draw.rect(screen, GOLD, (WIDTH // 2 - 50, 155, 100 * (e_hp / e_max_hp), 10))

        screen.blit(IMG_HERO_MINI, (40, 390))

        c_box = box if state == "ENEMY" else pygame.Rect(40, 230, WIDTH - 80, 150)
        border_col = CYAN if state == "PRE_DIALOG" else GOLD
        pygame.draw.rect(screen, border_col, c_box, 4)

        if state == "PRE_DIALOG":
            cur_p = foe["pre_dialog"][pre_idx]
            if pre_char < len(cur_p): pre_char += 0.8
            speaker_col = YELLOW if cur_p.startswith("BIMA:") else RED
            for i, ln in enumerate(wrap_text(cur_p[:int(pre_char)], c_box.width - 40)):
                screen.blit(font_main.render(ln, True, speaker_col), (60, 252 + i * 26))
            screen.blit(font_small.render(f"[Dialog {pre_idx+1}/{len(foe['pre_dialog'])} - Klik / Z]", True, CYAN), (60, 345))

        elif state in ("PLAYER", "DIALOG", "OVER", "WIN"):
            for i, ln in enumerate(wrap_text(dialog, c_box.width - 40)):
                screen.blit(font_main.render(ln, True, WHITE), (60, 252 + i * 26))
            if state == "PLAYER":
                screen.blit(font_small.render("[Tekan T untuk Tutorial]", True, GRAY), (60, 345))
            elif state in ("DIALOG", "WIN"):
                screen.blit(font_small.render("[Klik / Z untuk lanjut]", True, CYAN), (60, 345))
            elif state == "OVER":
                screen.blit(font_small.render("[Klik / R untuk ulang]", True, YELLOW), (60, 345))

        elif state in ("ACT", "SEAL"):
            for i, item in enumerate(subs):
                r = s_rects[i]
                ic = CYAN if (state == "SEAL" and item == "Sucikan" and purifiable) else WHITE
                screen.blit(font_main.render(f"> {item}", True, ic), (r.x + 30, r.y + 4))
                if i == sel_sub:
                    draw_keris_pointer(r.x + 2, r.y + 4)
            screen.blit(font_small.render("[X / ESC untuk kembali]", True, GRAY), (60, 345))

        elif state == "ENEMY":
            if inv_timer % 6 < 3:
                draw_battle_keris(keris_pos[0], keris_pos[1])
            for b in bullets:
                pygame.draw.rect(screen, GOLD, b)

        screen.blit(font_small.render(f"BIMA  LV {lv}  HP {hp}/{max_hp}", True, WHITE), (74, 395))
        pygame.draw.rect(screen, RED, (335, 397, 90, 16))
        pygame.draw.rect(screen, CYAN, (335, 397, 90 * (hp / max_hp), 16))
        screen.blit(font_small.render(f"EXP:{exp}/{next_exp}", True, WHITE), (440, 395))

        for i, opt in enumerate(["SERANG", "AKSI", "JAMU", "SEGEL"]):
            r = m_rects[i]
            c = CYAN if (i == sel_menu and state == "PLAYER") else GOLD
            pygame.draw.rect(screen, c, r, 2)
            screen.blit(font_main.render(opt, True, c), (r.x + 28, r.y + 7))
            if i == sel_menu and state == "PLAYER":
                draw_keris_pointer(r.x + 4, r.y + 7)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()