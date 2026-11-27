import pygame, os, sys, random, math

pygame.init()
W,H = 640,480
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("WIRA NUSA — 10 NOVEMBER")
clock=pygame.time.Clock()
BASE=os.path.dirname(os.path.abspath(__file__))
AS=os.path.join(BASE,"assets")
BLACK=(0,0,0); WHITE=(245,245,245); RED=(230,55,65); GOLD=(255,210,80)
GREEN=(70,180,95); CYAN=(100,220,230); GRAY=(130,130,130)
FONT=pygame.font.SysFont("Courier New",16,bold=True)
SMALL=pygame.font.SysFont("Courier New",13,bold=True)
TITLE=pygame.font.SysFont("Courier New",32,bold=True)
BIG=pygame.font.SysFont("Courier New",23,bold=True)

def asset(name):
    p=os.path.join(AS,name)
    try:
        im=pygame.image.load(p).convert_alpha()
        return im
    except Exception:
        return None

def fit(img,size, smooth=False):
    if img is None: return pygame.Surface(size)
    return pygame.transform.smoothscale(img,size) if smooth else pygame.transform.scale(img,size)

def blit_center(img, x, y):
    screen.blit(img,(int(x-img.get_width()/2),int(y-img.get_height()/2)))

def text(txt, font=FONT, color=WHITE):
    return font.render(str(txt),True,color)

def wrap(txt,font,maxw):
    out=[]; cur=""
    for word in txt.split():
        test=(cur+" "+word).strip()
        if font.size(test)[0] <= maxw: cur=test
        else:
            if cur: out.append(cur)
            cur=word
    if cur: out.append(cur)
    return out

def draw_wrapped(txt,x,y,maxw,font=FONT,color=WHITE,leading=4):
    lines=wrap(txt,font,maxw)
    for i,line in enumerate(lines):
        screen.blit(text(line,font,color),(x,y+i*(font.get_height()+leading)))
    return len(lines)

def panel(rect, fill=BLACK, border=WHITE, width=3):
    pygame.draw.rect(screen,fill,rect)
    pygame.draw.rect(screen,border,rect,width)

def image_background(img, tint=None):
    if img:
        screen.blit(fit(img,(W,H)),(0,0))
    else:
        screen.fill((22,18,16))
    if tint:
        overlay=pygame.Surface((W,H),pygame.SRCALPHA); overlay.fill(tint); screen.blit(overlay,(0,0))

# Load backgrounds and source composites
map_img=asset("village_map.jpg")
map_world=asset("map_panorama.png")
intro_peace_bg=asset("intro_peace.jpg")
intro_conflict_bg=asset("intro_conflict.jpg")
frontline_bg=asset("frontline.jpg")
kentongan_scene=asset("kentongan_scene.jpg")
kentongan_sheet=asset("Pixel Art Kentongan Village Asset Sheet.png")
budi_dialog_asset=asset("Pixel Soldier Budi Character Sheet (1).png")
sari_dialog_asset=asset("Sari’s Defiant Pixel Dialogue.png")
dutch_dialog_asset=asset("Dutch Officer’s Defiant Ultimatum.png")
japan_dialog_asset=asset("Japanese Soldier Pixel Art Sprite Sheet.png")
budi_sheet=asset("Budi’s Independence Fighter Sprite Sheet.png")
ind_fighter_sheet=asset("Indonesian Freedom Fighter Sprite Sheet.png")
dutch_sheet=asset("Dutch Officer Pixel Sprite Sheet.png")
dutch_sheet2=asset("Dutch Colonial Officer Sprite Sheet (1).png")
japan_sheet=asset("Japanese Soldier Pixel Sprite Sheet.png")
budi_sheet2=asset("Pixel Soldier Budi Character Sheet (1).png")

# Transparent sprite sheets: keep the original alpha channel; NEVER color-key black.
# The uploaded sheets are 4x4 directional grids (rows: front/right/back/left).
def crop_sprite(sheet, col, row, cols=4, rows=4, pad=2):
    """Crop a directional frame and trim only transparent padding."""
    if sheet is None:
        return None
    sw, sh = sheet.get_width(), sheet.get_height()
    x0 = round(col * sw / cols); x1 = round((col + 1) * sw / cols)
    y0 = round(row * sh / rows); y1 = round((row + 1) * sh / rows)
    cell = sheet.subsurface((x0, y0, max(1, x1-x0), max(1, y1-y0))).copy().convert_alpha()
    # Pygame Surface has no PIL-style getchannel(). Scan alpha directly.
    min_x, min_y = cell.get_width(), cell.get_height()
    max_x, max_y = -1, -1
    for yy in range(cell.get_height()):
        for xx in range(cell.get_width()):
            if cell.get_at((xx,yy)).a > 0:
                if xx < min_x: min_x = xx
                if yy < min_y: min_y = yy
                if xx > max_x: max_x = xx
                if yy > max_y: max_y = yy
    if max_x >= min_x and max_y >= min_y:
        left=max(0,min_x-pad); top=max(0,min_y-pad)
        right=min(cell.get_width(),max_x+1+pad); bottom=min(cell.get_height(),max_y+1+pad)
        cell=cell.subsurface((left,top,max(1,right-left),max(1,bottom-top))).copy()
    return cell

budi_frames = [crop_sprite(budi_sheet,c,r,4,4) for r in range(4) for c in range(4)]
sari_frames = [crop_sprite(ind_fighter_sheet,c,r,4,4) for r in range(4) for c in range(4)]
dutch_frames = [crop_sprite(dutch_sheet,c,r,4,4) for r in range(4) for c in range(4)]
japan_frames = [crop_sprite(japan_sheet,c,r,4,4) for r in range(4) for c in range(4)]

def sprite_from(frames, index, size=(74,98)):
    fr = frames[index % len(frames)] if frames else None
    if fr is None:
        fallback = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(fallback,(120,70,35),fallback.get_rect())
        return fallback
    target_w, target_h = int(size[0]), int(size[1])
    fw, fh = fr.get_size()
    scale = min(target_h/max(1,fh), target_w/max(1,fw))
    out_w=max(1,int(round(fw*scale))); out_h=max(1,int(round(fh*scale)))
    return pygame.transform.scale(fr,(out_w,out_h))

# Portraits are taken from the transparent front-facing sprite cells, not from
# composite screenshots. This avoids brown/black background pixels and cropping glitches.
budi_portrait = sprite_from(budi_frames,0,(118,118))
sari_portrait = sprite_from(sari_frames,0,(118,118))
dutch_portrait = sprite_from(dutch_frames,0,(118,118))
japan_portrait = sprite_from(japan_frames,0,(118,118))

# Dialogue scene is a small framed panel; portrait and text are integrated
# inside the lower Undertale-style dialogue box to prevent overlap.
def fit_cover(img, size):
    if img is None:
        return pygame.Surface(size)
    iw, ih = img.get_size()
    scale = max(size[0]/iw, size[1]/ih)
    nw, nh = max(size[0],int(round(iw*scale))), max(size[1],int(round(ih*scale)))
    scaled = pygame.transform.scale(img,(nw,nh))
    x = max(0,(nw-size[0])//2); y=max(0,(nh-size[1])//2)
    return scaled.subsurface((x,y,size[0],size[1])).copy()

def draw_dialogue(speaker, message, portrait=None, prompt=True):
    global dialog_page
    box = pygame.Rect(18,292,604,170)
    panel(box,BLACK,WHITE,3)
    namew = max(92,FONT.size(speaker)[0]+24)
    plaque = pygame.Rect(38,278,namew,28)
    panel(plaque,BLACK,WHITE,2)
    screen.blit(text(speaker,SMALL),(plaque.x+10,plaque.y+6))
    if portrait:
        portrait_img = fit(portrait,(112,112))
        screen.blit(portrait_img,(30,326))
        tx=158; maxw=444
    else:
        tx=42; maxw=560
    lines=wrap(message,FONT,maxw)
    max_lines=4
    pages=max(1,math.ceil(len(lines)/max_lines))
    page=dialog_page%pages
    visible=lines[page*max_lines:(page+1)*max_lines]
    for i,line in enumerate(visible):
        screen.blit(text(line,FONT),(tx,326+i*27))
    if pages>1:
        screen.blit(text(f"{page+1}/{pages}",SMALL,GRAY),(555,305))
    if prompt:
        pygame.draw.polygon(screen,WHITE,[(592,443),(602,443),(597,450)])

def draw_header(title,subtitle=""):
    screen.blit(text(title,TITLE),(20,14))
    if subtitle:
        screen.blit(text(subtitle,SMALL),(22,55))

def draw_title():
    screen.fill(BLACK)
    # pixel flags / decorative blocks
    pygame.draw.rect(screen,(160,20,25),(96,100,24,14)); pygame.draw.rect(screen,WHITE,(96,114,24,14))
    pygame.draw.rect(screen,(160,20,25),(520,100,24,14)); pygame.draw.rect(screen,WHITE,(520,114,24,14))
    t=text("WIRA NUSA",TITLE,GOLD); screen.blit(t,(W//2-t.get_width()//2,120))
    t=text("10 NOVEMBER 1945",BIG); screen.blit(t,(W//2-t.get_width()//2,170))
    panel(pygame.Rect(130,230,380,88),BLACK,WHITE,3)
    draw_wrapped("Sebuah kisah perjuangan rakyat Surabaya.",155,250,330,FONT,WHITE)
    draw_wrapped("ENTER / SPACE — MULAI",155,282,330,SMALL,GOLD)
    screen.blit(text("PIXEL STORY RPG • UAS",SMALL,GRAY),(W//2-95,390))

# Story scenes, preserving the wording and order from the uploaded draft.
INTRO=[
("Narator","Setelah Proklamasi Kemerdekaan Indonesia pada 17 Agustus 1945, rakyat di berbagai daerah menyambutnya dengan sukacita.",None,intro_peace_bg),
("Narator","Namun, situasi politik dan keamanan belum stabil. Jepang yang telah kalah dalam Perang Dunia II masih berada di Indonesia sambil menunggu kedatangan Sekutu untuk melucuti senjata mereka.",None,intro_conflict_bg),
("Narator","Dalam perjanjian internasional, Sekutu mendapat tugas untuk mengurus wilayah bekas jajahan Jepang, termasuk Indonesia, dengan mengirim AFNEI yang dipimpin Letnan Jenderal Sir Philip Christison.",None,intro_conflict_bg),
("Narator","Kedatangan pasukan Sekutu ke Indonesia sebenarnya bertujuan melucuti senjata tentara Jepang dan membebaskan tawanan perang.",None,frontline_bg),
("Narator","Namun, di balik misi tersebut, terselip ambisi Belanda yang tergabung dalam NICA untuk kembali menjajah Indonesia.",None,frontline_bg),
("Narator","Hal inilah yang kemudian memicu ketegangan di berbagai daerah, terutama di Surabaya, yang dikenal sebagai kota dengan semangat perlawanan tinggi.",None,frontline_bg),
]
CH1=[
("Budi","Teman-teman, kalian sudah lihat beritanya belum? Sekutu datang ke Indonesia hari ini.",budi_portrait),
("Budi","Mereka bilangnya ingin membebaskan tawanan perang, tapi…",budi_portrait),
("Budi","Aku rasa niat mereka tidak hanya itu saja.",budi_portrait),
("Yanto","Kamu benar, Budi.",None),
("Yanto","Lebih baik kita mempersiapkan diri.",None),
("Budi","Baik, Yanto.",budi_portrait),
("Narator","Budi dan Yanto mempersiapkan perlengkapan mereka sebelum menuju barisan depan.",None),
("Narator","Mereka membawa bambu runcing beserta senjata yang mereka buat sendiri.",None),
("Narator","Membawa semangat membara dan harapan untuk menjaga kemerdekaan Indonesia.",None),
("Narator","Sesuai dengan dugaan mereka, Belanda sebenarnya memiliki niat jahat untuk menguasai Indonesia.",None),
("Narator","Setelah Brigadir Jenderal Mallaby tewas di sekitar Jembatan Merah Surabaya.",None),
("Narator","Sekutu mengancam untuk melancarkan serangan besar-besaran.",None),
("Budi","Kami tidak takut!",budi_portrait),
("Perwira Belanda","Kalau begitu kalian rasakan akibatnya!",dutch_portrait),
]
B1_PRE=[
("Perwira Belanda","Berani-beraninya kalian tidak mematuhi kami!",dutch_portrait),
("Perwira Belanda","Inilah balasannya!",dutch_portrait),
]
B1_POST=[
("Budi","Kami tidak akan mundur!",budi_portrait),
("Yanto","Budi! Ada kawan kita yang terjebak di rumah warga!",None),
("Yanto","Apa yang akan kita lakukan sekarang?",None),
]
CHOICE1=["Tetap di Garis Depan (+Nyali)","Membuka Jalur Evakuasi (+Harapan)","Membuat Taktik Menyerang (+Gema)"]
BRANCH1=[
[
("Perwira Belanda","Kamu masih mau bertahan?",dutch_portrait),
("Perwira Belanda","Hahaha! Coba saja kalau bisa!",dutch_portrait),
("Budi","Akhirnya kita bisa mengalahkan Belanda!",budi_portrait),
("Yanto","Jangan senang dulu, Budi! Masih ada lawan yang harus kita hadapi lagi!",None),
("Budi","Kamu benar, Yanto!",budi_portrait),
("Budi","Ayo kita jaga tanah air tercinta ini!",budi_portrait),
("Narator","Budi beserta temannya pun berjuang untuk melawan Belanda. Bertumpah darah pun tak bisa terelakkan. Bersama, mereka bertarung dan saling menjaga satu sama lain.",None),
],
[
("Budi","Lebih baik kita utamakan teman kita yang masih terjebak, Yanto!",budi_portrait),
("Yanto","Kamu benar!",None),
("Perwira Belanda","Apakah kalian pikir bisa lari dariku?!",dutch_portrait),
("Perwira Belanda","Jangan berani untuk kabur!",dutch_portrait),
("Budi","Teman-teman! Segera pergi lewat sini!",budi_portrait),
("Budi","Saling jaga satu lain!",budi_portrait),
("Narator","Budi dan lainnya pun membuka jalur evakuasi, membantu teman-temannya yang terjebak. Dengan tindakan ini, banyak warga sipil yang terselamatkan.",None),
],
[
("Budi","Kawan-kawanku! Dengarkan aku!",budi_portrait),
("Budi","Aku punya rencana bagus. Tapi aku butuh bantuan dari kalian semua!",budi_portrait),
("Yanto","Apa itu Budi?",None),
("Budi","Kita buat isyarat kentongan ke kawan kita di daerah sebelah, agar kita bisa menyerang secara serentak!",budi_portrait),
("Yanto","Oke!",None),
("Perwira Belanda","Hahaha! Apa kalian pikir bisa melawan kami?!",dutch_portrait),
("Budi","Kawan-kawan! Ini saatnya!",budi_portrait),
("Yanto","Kita menang Budi!",None),
("Budi","Belum saatnya Yanto! Belanda masih belum mundur! Ayo kita bantu kawan lainnya!",budi_portrait),
("Narator","Dengan persatuan rakyat Indonesia, Budi dan kawan-kawan berhasil menyerang balik Belanda. Tetapi ini masih belum berakhir. Masih ada tantangan yang menunggu mereka di masa depan.",None),
]
]
# The Chapter 1 third branch uses the kentongan scene embedded in the draft.
BRANCH1[2]=[(speaker,message,portrait,map_img) if i<5 else (speaker,message,portrait)
            for i,(speaker,message,portrait) in enumerate(BRANCH1[2])]
CH2=[
("Narator","Ketika pertarungan masih memanas dan pertumpah darah terjadi di mana-mana, ada tenaga medis yang ikut berjuang membantu rakyat Indonesia.",None),
("Putri","Sari! Pasokan obat sudah menipis! Tapi masih banyak pejuang yang terluka.",None),
("Putri","Selain itu, rakyat yang terluka mulai kehilangan semangatnya.",None),
("Putri","Apa yang akan kita lakukan sekarang?",None),
("Sari","Tenanglah Sari! Aku pikirkan dulu langkah kita selanjutnya.",sari_portrait),
]
CHOICE2=["Menembus Jalur Berbahaya Demi Obat (+Nyali)","Merawat Semua yang Luka Tanpa Membeda-bedakan (+Harapan)","Menguatkan Semangat Pengungsi (+Gema)"]
BRANCH2=[
[
("Sari","Aku akan mencari obat Putri.",sari_portrait),
("Putri","Apa maksudmu? Di luar sana sangatlah berbahaya!",None),
("Sari","Tidak apa-apa! Aku pasti akan membawakan kalian semua obat.",sari_portrait),
("Narator","Perjalanan Sari dalam mencari obat sangatlah berbahaya. Banyak sekali rintangan yang menghalanginya.",None),
("Perwira Belanda","Hey kamu! Mau ke mana?",dutch_portrait),
("Sari","Jangan halangi aku!",sari_portrait),
("Narator","Sari berhasil membawa obat dan kembali dengan selamat. Kini mereka tidak khawatir kekurangan obat dan menolong banyak pejuang Indonesia.",None),
("Putri","Terima kasih Sari! Berkatmu, banyak nyawa yang terselamatkan.",None),
("Sari","Sama-sama, Putri. Aku senang hati bisa membantu Indonesia untuk ikut berjuang.",sari_portrait),
],
[
("Sari","Kita rawat semua orang yang terluka, Putri.",sari_portrait),
("Putri","Baiklah Sari.",None),
("Putri","Sari! Ada orang yang terluka di luar sana! Bagaimana ini?",None),
("Sari","Aku akan selamatkan mereka, Putri.",sari_portrait),
("Narator","Sari segera pergi ke tempat korban terluka. Walaupun begitu, banyak sekali rintangan yang menghadangnya.",None),
("Perwira Belanda","Hey kamu! Mau ke mana?",dutch_portrait),
("Sari","Jangan halangi aku!",sari_portrait),
("Narator","Sari pun membawa korban yang terluka ke tempat aman. Dengan begitu, Sari bisa menyelamatkan banyak nyawa rakyat Indonesia.",None),
("Korban terluka","Terima kasih telah menyelamatkan nyawa saya.",None),
("Sari","Sama-sama.",sari_portrait),
],
[
("Narator","Pilihan ketiga Chapter 2 — 'Menguatkan Semangat Pengungsi' tercantum pada draft, tetapi dialog dan Battle 7 belum tersedia dalam dokumen yang diunggah.",None),
]
]

# State machine
state="TITLE"
dialog_list=[]; dialog_i=0; dialog_page=0; choice_list=[]; choice_i=0
choice_context=""; values={"Nyali":0,"Harapan":0,"Gema":0}
battle_id=0; battle_mode="dodge"; battle_t=0; player=pygame.Rect(W//2-7,390,14,14); hazards=[]
objective_items=[]; objective_count=0; chaser=pygame.Rect(0,0,28,36)
map_player=pygame.Rect(318,286,18,20); map_obj=None
kentongan_obj_img=None
if kentongan_sheet:
    try:
        kentongan_obj_img=kentongan_sheet.subsurface((390,20,260,980)).copy()
        kentongan_obj_img.set_colorkey((62,44,41))
        kentongan_obj_img=fit(kentongan_obj_img,(24,40))
    except Exception:
        kentongan_obj_img=None
map_active=False; map_message=""; map_found=False
story_bg_idx=0
after_branch=0

def set_dialog(lines,next_state):
    global dialog_list,dialog_i,dialog_page,state,dialog_next
    dialog_list=lines; dialog_i=0; dialog_page=0; dialog_next=next_state; state="DIALOG"

dialog_next=""

def start_battle(number, mode="dodge", after="BATTLE_WIN"):
    global state,battle_id,battle_mode,battle_t,hazards,player,battle_after,objective_items,objective_count,chaser
    battle_id=number; battle_mode=mode; battle_t=0; hazards=[]
    objective_items=[]; objective_count=0
    player.center=(W//2,370); chaser.center=(W//2,125)
    battle_after=after
    state="BATTLE"

battle_after=""

def draw_dialog_state():
    screen.fill((22,16,12))
    if dialog_i < len(dialog_list):
        item=dialog_list[dialog_i]
        speaker,msg,portrait=item[:3]
        bg=item[3] if len(item)>3 and item[3] is not None else map_img
        scene=pygame.Rect(64,42,512,226)
        panel(scene,(18,14,12),WHITE,3)
        if bg:
            screen.blit(fit_cover(bg,(scene.w-8,scene.h-8)),(scene.x+4,scene.y+4))
        # dark translucent overlay keeps scene atmospheric without covering it
        shade=pygame.Surface((scene.w-8,scene.h-8),pygame.SRCALPHA)
        shade.fill((0,0,0,28))
        screen.blit(shade,(scene.x+4,scene.y+4))
        draw_dialogue(speaker,msg,portrait)

def choice_screen():
    screen.fill(BLACK)
    draw_header("PILIHAN",choice_context)
    for i,opt in enumerate(choice_list):
        r=pygame.Rect(40,105+i*95,560,72)
        panel(r,BLACK,GOLD if i==choice_i else WHITE,3)
        prefix="▶ " if i==choice_i else "  "
        draw_wrapped(prefix+opt,r.x+22,r.y+20,r.w-44,FONT,GOLD if i==choice_i else WHITE)
    screen.blit(text("UP/DOWN  •  ENTER",SMALL,GRAY),(20,430))

# Map mission: the player can only walk inside the white road mask.
walk_mask_img = asset("walkable_mask.png")
walk_mask = walk_mask_img if walk_mask_img else None
MAP_W, MAP_H = (map_world.get_size() if map_world else (2048,1024))
map_player = pygame.Rect(0,0,34,28)
map_mode = "kentongan"
map_dir = 0
map_anim = 0
map_found = False
map_message = ""
map_camera_x = 0
map_camera_y = 0
map_medicine_items = []
map_medicine_count = 0
map_hp = 100
map_chaser = pygame.Rect(0,0,34,28)
map_chaser_dir = 3
map_hit_cooldown = 0
map_start_pos = (220,565)
map_target_rect = pygame.Rect(0,0,36,52)
map_reset_flash = 0
map_random_target = (0,0)
map_enemy_walk_timer = 0
kentongan_obj_img = asset("kentongan_object.png")

def on_walkable(x,y):
    if walk_mask is None:
        return 0 <= x <= MAP_W and 490 <= y <= 590
    x=int(x); y=int(y)
    if x<0 or y<0 or x>=walk_mask.get_width() or y>=walk_mask.get_height():
        return False
    return walk_mask.get_at((x,y))[0] > 0

def player_foot_ok(rect):
    return on_walkable(rect.centerx,rect.bottom-3)

def random_road_point():
    # Sample only walkable positions so the patrol never chooses an inaccessible target.
    for _ in range(250):
        x=random.randrange(80,MAP_W-80)
        y=random.randrange(500,580)
        if on_walkable(x,y):
            return (x,y)
    return (580,585)

def start_map(mode="kentongan"):
    global state,map_active,map_message,map_found,map_obj,map_player,map_mode
    global map_medicine_items,map_medicine_count,map_hp,map_chaser,map_start_pos,map_dir,map_anim,map_chaser_dir,map_hit_cooldown
    global map_reset_flash,map_random_target,map_enemy_walk_timer
    state="MAP"; map_active=True; map_mode=mode; map_found=False
    map_medicine_items=[]; map_medicine_count=0; map_hp=100
    map_reset_flash=0; map_enemy_walk_timer=0
    if mode=="kentongan":
        map_message="Cari kentongan di jalan desa. Dekati objek lalu tekan E."
        map_start_pos=(220,545)
        map_obj=pygame.Rect(1500,545,34,42)
    else:
        map_message="Cari 3 paket obat. Musuh bergerak acak—hindari sentuhan!"
        map_start_pos=(180,545)
        map_obj=None
        map_medicine_items=[
            pygame.Rect(520,545,24,24),
            pygame.Rect(1050,545,24,24),
            pygame.Rect(1740,545,24,24),
        ]
        map_chaser.center=(580,545)
        map_chaser_dir=random.randrange(4)
        map_random_target=random_road_point()
    map_player.center=map_start_pos
    map_dir=0; map_anim=0; map_hit_cooldown=0

def draw_medicine_icon(x,y):
    # Small pixel-art medical satchel (no external sprite dependency).
    pygame.draw.rect(screen,(190,55,45),(x-9,y-7,18,15))
    pygame.draw.rect(screen,(235,210,185),(x-5,y-5,10,11))
    pygame.draw.rect(screen,(200,45,45),(x-2,y-4,4,9))
    pygame.draw.rect(screen,(200,45,45),(x-4,y-1,8,3))
    pygame.draw.rect(screen,(90,40,25),(x-9,y-7,18,15),1)

def map_camera():
    view_h=H-88
    cam_x=max(0,min(MAP_W-W,map_player.centerx-W//2))
    cam_y=max(0,min(MAP_H-view_h,map_player.centery-view_h//2))
    return int(cam_x),int(cam_y)

def draw_map():
    screen.fill(BLACK)
    view=pygame.Rect(0,44,W,H-88)
    camx,camy=map_camera()
    if map_world:
        screen.blit(map_world,(view.x-camx,view.y-camy))
    else:
        screen.fill((75,60,40),view)
    # draw objects in world coordinates, then offset by camera
    if map_mode=="kentongan" and not map_found:
        krect=pygame.Rect(map_obj.x-camx,map_obj.y-camy+view.y,map_obj.w,map_obj.h)
        if kentongan_obj_img:
            k=fit(kentongan_obj_img,(44,76))
            screen.blit(k,(krect.x-2,krect.y-8))
        else:
            pygame.draw.rect(screen,(145,85,25),krect)
        screen.blit(text("KENTONGAN",SMALL,GOLD),(krect.x-18,krect.y-22))
    elif map_mode=="medicine":
        for item in map_medicine_items:
            draw_medicine_icon(item.centerx-camx,item.centery-camy+view.y)
        # pursuer sprite uses Dutch transparent sprite sheet
        chaser_frame=map_chaser_dir*4+((map_anim//8)%4)
        enemy=sprite_from(dutch_frames,chaser_frame,(68,92))
        screen.blit(enemy,(map_chaser.centerx-camx-enemy.get_width()//2, map_chaser.bottom-camy+view.y-enemy.get_height()))
    # player frame by direction row, walking column
    frame_col=(map_anim//7)%4
    frame_idx=map_dir*4+frame_col
    player_frames=budi_frames if map_mode=="kentongan" else sari_frames
    p=sprite_from(player_frames,frame_idx,(74,98))
    screen.blit(p,(map_player.centerx-camx-p.get_width()//2,
                   map_player.bottom-camy+view.y-p.get_height()))
    # UI overlays
    panel(pygame.Rect(8,8,624,34),BLACK,WHITE,2)
    title="MISI: TEMUKAN KENTONGAN" if map_mode=="kentongan" else "BATTLE 5: CARI OBAT"
    screen.blit(text(title,SMALL,GOLD),(18,18))
    if map_mode=="medicine":
        screen.blit(text(f"OBAT {map_medicine_count}/3  •  HINDARI MUSUH",SMALL,WHITE),(365,18))
    panel(pygame.Rect(8,405,624,67),BLACK,WHITE,2)
    screen.blit(text(map_message,SMALL),(18,418))
    screen.blit(text("WASD / ARROWS • E INTERACT" if map_mode=="kentongan" else "WASD / ARROWS • AMBIL OBAT • SENTUH MUSUH = RESET",SMALL,GRAY),(18,446))

def draw_battle():
    screen.fill(BLACK)
    draw_header(f"BATTLE {battle_id}", "HINDARI HAZARD • BERTAHAN")
    arena=pygame.Rect(90,100,460,300)
    panel(arena,BLACK,WHITE,4)
    # hazards in simple patterns, all symbolic dots, not realistic projectiles
    for h in hazards:
        pygame.draw.rect(screen,(235,235,235),h)
    for item in objective_items:
        pygame.draw.rect(screen,GOLD if battle_mode=="medicine" else GREEN,item)
        pygame.draw.rect(screen,WHITE,item,1)
    if battle_mode=="medicine":
        enemy=sprite_from(dutch_frames,4,(34,42))
        blit_center(enemy,chaser.centerx,chaser.centery)
    # pixel heart player
    heart_pts=[(player.x+7,player.y+2),(player.x+3,player.y-1),(player.x,player.y+2),(player.x,player.y+6),(player.x+7,player.y+13),(player.x+14,player.y+6),(player.x+14,player.y+2),(player.x+11,player.y-1)]
    pygame.draw.polygon(screen,RED,heart_pts)
    pygame.draw.polygon(screen,WHITE,heart_pts,1)
    screen.blit(text("HP",SMALL),(100,415))
    hpbar=pygame.Rect(130,414,160,12); panel(hpbar,(40,40,40),WHITE,1)
    pygame.draw.rect(screen,(220,70,70),(hpbar.x+1,hpbar.y+1, max(0,int((battle_hp/100)*158)),10))
    screen.blit(text("WASD / ARROW KEYS",SMALL),(340,415))
    screen.blit(text(f"TIME {max(0,6-battle_t//60)}",SMALL,GOLD),(500,78))

def begin_choice(which):
    global choice_context,choice_list,choice_i,state
    choice_context="CHAPTER 1" if which==1 else "CHAPTER 2"
    choice_list=CHOICE1[:] if which==1 else CHOICE2[:]
    choice_i=0; state="CHOICE"; choice_num=which

choice_num=1

def route_choice1(index):
    global values,after_branch
    values[["Nyali","Harapan","Gema"][index]]+=1
    if index==0:
        set_dialog(BRANCH1[0][:2], "B1_BATTLE2")
    elif index==1:
        set_dialog(BRANCH1[1][:3], "B1_BATTLE3")
    else:
        set_dialog(BRANCH1[2][:5], "B1_MAP")

def route_choice2(index):
    global values
    values[["Nyali","Harapan","Gema"][index]]+=1
    if index==0: set_dialog(BRANCH2[0][:6],"B2_MAP5")
    elif index==1: set_dialog(BRANCH2[1][:6],"B2_BATTLE6")
    else: set_dialog(BRANCH2[2],"DRAFT_MISSING")

def next_dialog():
    global dialog_i,dialog_page,state
    item=dialog_list[dialog_i]
    message=item[1]
    portrait=item[2] if len(item)>2 else None
    lines=wrap(message,FONT,444 if portrait else 560)
    pages=max(1,math.ceil(len(lines)/4))
    if dialog_page+1<pages:
        dialog_page+=1
        return
    dialog_page=0
    dialog_i+=1
    if dialog_i>=len(dialog_list):
        state=dialog_next

def show_branch1_after_battle(index):
    if index==0:
        set_dialog(BRANCH1[0][2:],"B1_DONE")
    elif index==1:
        set_dialog(BRANCH1[1][3:],"B1_DONE")
    else:
        set_dialog(BRANCH1[2][6:],"B1_DONE")

def show_branch2_after_battle(index):
    if index==0: set_dialog(BRANCH2[0][6:],"CH2_DONE")
    else: set_dialog(BRANCH2[1][6:],"CH2_DONE")

def choose_battle_result():
    global state
    state="BATTLE_WIN"

# main loop
running=True
while running:
    dt=clock.tick(60)
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        elif event.type==pygame.KEYDOWN:
            if state=="TITLE":
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    set_dialog(INTRO,"CH1_START")
            elif state=="DIALOG":
                if event.key in (pygame.K_z,pygame.K_RETURN,pygame.K_SPACE):
                    next_dialog()
            elif state=="CHOICE":
                if event.key in (pygame.K_UP,pygame.K_w): choice_i=(choice_i-1)%len(choice_list)
                if event.key in (pygame.K_DOWN,pygame.K_s): choice_i=(choice_i+1)%len(choice_list)
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    if choice_context=="CHAPTER 1": route_choice1(choice_i)
                    else: route_choice2(choice_i)
            elif state=="MAP":
                if event.key==pygame.K_e and map_mode=="kentongan":
                    dx=map_player.centerx-map_obj.centerx
                    dy=map_player.centery-map_obj.centery
                    if dx*dx+dy*dy <= 78*78:
                        map_found=True
                        map_message="Kentongan ditemukan! Tekan ENTER untuk melanjutkan."
                    else:
                        map_message="Kentongan belum terlihat. Jelajahi jalan desa."
                if event.key==pygame.K_RETURN:
                    if map_mode=="kentongan" and map_found:
                        set_dialog([BRANCH1[2][5]],"B1_BATTLE4")
                    elif map_mode=="medicine" and map_medicine_count>=3:
                        state="B2_B5_POST"
                if event.key==pygame.K_ESCAPE:
                    map_message="Misi harus diselesaikan untuk melanjutkan cerita."
            elif state=="MAP_LOSE":
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    start_map("medicine")
            elif state=="BATTLE":
                # controls are movement-only; game avoids any real-world weapon depiction
                if event.key in (pygame.K_LEFT,pygame.K_a): player.x-=10
                if event.key in (pygame.K_RIGHT,pygame.K_d): player.x+=10
                if event.key in (pygame.K_UP,pygame.K_w): player.y-=10
                if event.key in (pygame.K_DOWN,pygame.K_s): player.y+=10
                player.clamp_ip(pygame.Rect(95,105,450,290))
            elif state=="BATTLE_WIN":
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    state=battle_after
            elif state=="BATTLE_LOSE":
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    start_battle(battle_id,battle_mode,battle_after)
            elif state=="DRAFT_MISSING":
                if event.key in (pygame.K_RETURN,pygame.K_SPACE): state="TITLE"
            elif state=="END":
                if event.key in (pygame.K_RETURN,pygame.K_SPACE): state="TITLE"
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if state=="DIALOG": next_dialog()
            elif state=="CHOICE":
                y=105
                for i in range(len(choice_list)):
                    if pygame.Rect(40,y+i*95,560,72).collidepoint(event.pos):
                        choice_i=i
                        if choice_context=="CHAPTER 1": route_choice1(i)
                        else: route_choice2(i)
                        break

    # Continuous map movement (WASD and arrow keys) with road-only collision.
    if state=="MAP":
        keys=pygame.key.get_pressed()
        dx=(1 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 0)
        dy=(1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_w] or keys[pygame.K_UP] else 0)
        if dx and dy:
            dx*=0.7071; dy*=0.7071
        move_speed=3.8
        if dx or dy:
            map_anim+=1
            if dx>0: map_dir=1
            elif dx<0: map_dir=3
            elif dy>0: map_dir=0
            elif dy<0: map_dir=2
            # Test movement by the player's feet, keeping each axis independent.
            test=map_player.copy()
            test.x+=int(round(dx*move_speed))
            if player_foot_ok(test):
                map_player.x=test.x
            test=map_player.copy()
            test.y+=int(round(dy*move_speed))
            if player_foot_ok(test):
                map_player.y=test.y
        else:
            map_anim=0
        if map_mode=="medicine":
            for item in map_medicine_items[:]:
                if map_player.colliderect(item.inflate(18,18)):
                    map_medicine_items.remove(item)
                    map_medicine_count+=1
                    map_message=f"Paket obat ditemukan {map_medicine_count}/3."
            # Random waypoint patrol on the road. It does not chase the player.
            map_enemy_walk_timer += 1
            if map_enemy_walk_timer >= random.randint(45,100):
                map_enemy_walk_timer=0
                map_random_target=random_road_point()
            target_x,target_y=map_random_target
            chase_dx=target_x-map_chaser.centerx; chase_dy=target_y-map_chaser.centery
            if abs(chase_dx)>=abs(chase_dy):
                map_chaser_dir=1 if chase_dx>0 else 3
            else:
                map_chaser_dir=0 if chase_dy>0 else 2
            dist=max(1,math.hypot(chase_dx,chase_dy))
            enemy_speed=1.65
            step_x=int(round(chase_dx/dist*enemy_speed)); step_y=int(round(chase_dy/dist*enemy_speed))
            test=map_chaser.copy(); test.x+=step_x
            if player_foot_ok(test): map_chaser.x=test.x
            test=map_chaser.copy(); test.y+=step_y
            if player_foot_ok(test): map_chaser.y=test.y
            if map_chaser.colliderect(map_player):
                map_message="Kena musuh! Misi diulang dari awal."
                map_reset_flash=90
                map_player.center=map_start_pos
                map_medicine_count=0
                map_medicine_items=[pygame.Rect(520,545,24,24),pygame.Rect(1050,545,24,24),pygame.Rect(1740,545,24,24)]
                map_chaser.center=(580,545)
                map_random_target=random_road_point()
                map_enemy_walk_timer=0; map_hit_cooldown=0; map_anim=0
            elif map_reset_flash>0:
                map_reset_flash-=1
                if map_reset_flash==1:
                    map_message="Cari 3 paket obat. Musuh bergerak acak—hindari sentuhan!"
            if map_medicine_count>=3 and state=="MAP":
                map_message="Semua obat ditemukan! Tekan ENTER untuk kembali."

    # state update
    if state=="BATTLE":
        battle_t+=1
        if battle_t%32==0:
            # Hazards are abstract pixel dots in the dodge arena.
            count=2 if battle_mode=="dodge" else 1
            for _ in range(count):
                hazards.append(pygame.Rect(random.randint(105,530),95,7,17))
        if battle_mode in ("medicine","rescue") and battle_t%95==0 and objective_count<3:
            objective_items.append(pygame.Rect(random.randint(115,515),random.randint(125,365),16,16))
        if battle_mode=="medicine":
            # One pursuer follows the player, as requested for Battle 5.
            if chaser.x < player.x: chaser.x += 2
            elif chaser.x > player.x: chaser.x -= 2
            if chaser.y < player.y: chaser.y += 1
            elif chaser.y > player.y: chaser.y -= 1
            if chaser.colliderect(player):
                battle_hp=max(0,battle_hp-1)
                chaser.center=(random.randint(110,530),random.randint(110,180))
        for item in objective_items[:]:
            if item.colliderect(player):
                objective_items.remove(item); objective_count+=1
        for h in hazards[:]:
            h.y+=5
            if h.colliderect(player):
                hazards.remove(h); battle_hp=max(0,battle_hp-8)
            elif h.y>405: hazards.remove(h)
        if battle_mode in ("medicine","rescue") and objective_count>=3:
            state="BATTLE_WIN"
        elif battle_hp<=0:
            state="BATTLE_LOSE"
        elif battle_t>=360:
            state="BATTLE_WIN" if battle_mode=="dodge" else "BATTLE_LOSE"
    if state=="BATTLE_WIN":
        screen.fill(BLACK)
        panel(pygame.Rect(50,120,540,220),BLACK,WHITE,3)
        screen.blit(text("BATTLE SELESAI",BIG,GOLD),(80,155))
        screen.blit(text("Tantangan berhasil dilewati.",FONT),(80,205))
        screen.blit(text("ENTER untuk lanjut.",SMALL),(80,270))
    elif state=="BATTLE_LOSE":
        screen.fill(BLACK)
        panel(pygame.Rect(50,120,540,220),BLACK,WHITE,3)
        screen.blit(text("TANTANGAN GAGAL",BIG,RED),(80,155))
        screen.blit(text("ENTER untuk mencoba lagi.",FONT),(80,205))
        screen.blit(text("ESC tidak digunakan — restart dengan ENTER.",SMALL),(80,270))
    elif state=="MAP_LOSE":
        screen.fill(BLACK)
        panel(pygame.Rect(55,115,530,235),BLACK,WHITE,3)
        screen.blit(text("MISI TERHAMBAT",BIG,GOLD),(90,155))
        draw_wrapped("Sari perlu mencoba jalur pencarian obat sekali lagi.",90,210,460,FONT,WHITE)
        screen.blit(text("ENTER / SPACE — COBA LAGI",SMALL),(90,290))
    elif state=="TITLE": draw_title()
    elif state=="DIALOG": draw_dialog_state()
    elif state=="CHOICE": choice_screen()
    elif state=="MAP": draw_map()
    elif state=="BATTLE": draw_battle()
    elif state=="DRAFT_MISSING":
        screen.fill(BLACK); panel(pygame.Rect(35,85,570,310),BLACK,WHITE,3)
        draw_wrapped("DRAFT BELUM MEMUAT LANJUTAN BAGIAN INI.",60,115,520,BIG,GOLD)
        draw_wrapped("Chapter 2 pilihan 3, Battle 7, Chapter 3, Battle 8-10, dan ending belum terdapat dalam dokumen yang diunggah. Game berhenti di sini agar tidak mengarang cerita.",60,190,520,FONT)
        draw_wrapped("ENTER untuk kembali ke title.",60,340,520,SMALL,WHITE)
    elif state=="END":
        screen.fill(BLACK); draw_wrapped("TERIMA KASIH TELAH BERMAIN WIRA NUSA",90,200,460,BIG,GOLD)
    pygame.display.flip()

    # state transitions after dialogs
    if state=="CH1_START":
        set_dialog(CH1,"B1_PRE")
    elif state=="B1_PRE":
        set_dialog(B1_PRE,"B1_START")
    elif state=="B1_START":
        battle_hp=100; start_battle(1,"dodge","B1_POST")
    elif state=="B1_POST":
        set_dialog(B1_POST,"CHOICE1")
    elif state=="CHOICE1":
        begin_choice(1)
    elif state=="B1_BATTLE2":
        battle_hp=100; start_battle(2,"dodge","B1_B2_POST")
    elif state=="B1_BATTLE3":
        battle_hp=100; start_battle(3,"dodge","B1_B3_POST")
    elif state=="B1_BATTLE4":
        battle_hp=100; start_battle(4,"dodge","B1_B4_POST")
    elif state=="B1_B2_POST":
        show_branch1_after_battle(0)
    elif state=="B1_B3_POST":
        show_branch1_after_battle(1)
    elif state=="B1_B4_POST":
        show_branch1_after_battle(2)
    elif state=="B1_MAP":
        start_map()
    elif state=="B1_MAP_BATTLE":
        battle_hp=100; start_battle(4,"dodge","B1_B4_POST")
    elif state=="B1_DONE":
        set_dialog(CH2,"CHOICE2")
    elif state=="CHOICE2":
        begin_choice(2)
    elif state=="B2_MAP5":
        start_map("medicine")
    elif state=="B2_BATTLE5":
        battle_hp=100; start_battle(5,"medicine","B2_B5_POST")
    elif state=="B2_BATTLE6":
        battle_hp=100; start_battle(6,"rescue","B2_B6_POST")
    elif state=="B2_B5_POST":
        show_branch2_after_battle(0)
    elif state=="B2_B6_POST":
        show_branch2_after_battle(1)
    elif state=="CH2_DONE":
        state="DRAFT_MISSING"
    elif state=="END":
        pass

pygame.quit()
sys.exit()
