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
intro_peace_bg=asset("intro_peace.jpg")
intro_conflict_bg=asset("intro_conflict.jpg")
frontline_bg=asset("frontline.jpg")
kentongan_scene=asset("kentongan_scene.jpg")
surabaya_overworld=asset("surabaya_overworld.png")
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

# Sprite sheet crop: auto find non-black pixels inside a cell, then preserve transparent background.
def crop_sprite(sheet, col,row,cols=4,rows=4, pad=3):
    if sheet is None: return None
    cw=sheet.get_width()/cols; ch=sheet.get_height()/rows
    cell=sheet.subsurface((int(col*cw),int(row*ch),max(1,int(cw)),max(1,int(ch)))).copy()
    # black background is transparent; detect visible pixel bounds
    cell.set_colorkey((0,0,0))
    mask=pygame.mask.from_surface(cell)
    # pygame-ce 2.5.x exposes get_bounding_rects(), not get_bounding_rect().
    # Merge all visible mask rectangles into one safe crop rectangle.
    try:
        rects=mask.get_bounding_rects()
    except (AttributeError, TypeError):
        # Safe fallback: leave this frame uncropped instead of crashing.
        return cell
    if not rects: return cell
    # Merge rectangles using coordinates (API-compatible) and CLIP to cell bounds.
    left=min(r.left for r in rects)
    top=min(r.top for r in rects)
    right=max(r.right for r in rects)
    bottom=max(r.bottom for r in rects)
    rect=pygame.Rect(left,top,right-left,bottom-top)
    if rect.width<2 or rect.height<2: return cell
    # Expand crop padding, then intersect with cell bounds. clamp_ip is not
    # suitable for oversized rectangles because it can leave size unchanged.
    rect=rect.inflate(pad*2,pad*2).clip(cell.get_rect())
    if rect.width<=0 or rect.height<=0: return cell
    # Final defensive check before subsurface.
    if rect.left<0 or rect.top<0 or rect.right>cell.get_width() or rect.bottom>cell.get_height():
        return cell
    return cell.subsurface(rect).copy()

# Directional sprite frames (sheet layouts are treated as 4x4; no external dependencies)
budi_frames=[crop_sprite(budi_sheet,c,r,4,4) for r in range(4) for c in range(4)]
sari_frames=[crop_sprite(ind_fighter_sheet,c,r,4,4) for r in range(4) for c in range(4)]
dutch_frames=[crop_sprite(dutch_sheet,c,r,4,4) for r in range(4) for c in range(4)]
japan_frames=[crop_sprite(japan_sheet,c,r,4,4) for r in range(4) for c in range(4)]
# fallbacks if a sheet grid is not aligned: still use any visible crop
def sprite_from(frames,index,size=(42,48)):
    fr=frames[index%len(frames)] if frames else None
    if fr is None: 
        s=pygame.Surface(size); s.fill((90,60,40)); return s
    return fit(fr,size)

# dialogue image portraits crop from left side of composite sheets; these assets intentionally include original character art.
def crop_portrait(img, rect, target=(132,150)):
    if img is None: return None
    safe_rect=pygame.Rect(rect).clip(img.get_rect())
    if safe_rect.width<=0 or safe_rect.height<=0:
        return None
    c=img.subsurface(safe_rect).copy()
    c.set_colorkey((0,0,0))
    # Some dialogue composites use a dark brown backdrop; key that flat backdrop for clean portraits.
    if img is budi_dialog_asset: c.set_colorkey((43,23,17))
    elif img is dutch_dialog_asset: c.set_colorkey((41,22,18))
    return fit(c,target,True)
budi_portrait=crop_portrait(budi_dialog_asset,(0,0,600,724),(145,150))
sari_portrait=crop_portrait(sari_dialog_asset,(0,0,600,887),(145,150))
dutch_portrait=crop_portrait(dutch_dialog_asset,(0,0,600,887),(145,150))
japan_portrait=crop_portrait(japan_dialog_asset,(0,0,500,724),(145,150))

# Asset-specific dialogue box look: black, crisp white border, speaker name tab.
def draw_dialogue(speaker, message, portrait=None, prompt=True):
    global dialog_page
    box=pygame.Rect(20,330,600,132)
    panel(box,BLACK,WHITE,3)
    # name plaque
    namew=max(92,FONT.size(speaker)[0]+24)
    plaque=pygame.Rect(42,315,namew,28)
    panel(plaque,BLACK,WHITE,2)
    screen.blit(text(speaker,SMALL),(plaque.x+10,plaque.y+6))
    tx=190 if portrait else 44
    if portrait:
        # portrait sits outside the box but does not overlap text
        screen.blit(fit(portrait,(145,150),True),(26,176))
    lines=wrap(message,FONT,420 if portrait else 550)
    max_lines=4
    pages=max(1,math.ceil(len(lines)/max_lines))
    page=dialog_page%pages
    visible=lines[page*max_lines:(page+1)*max_lines]
    for i,line in enumerate(visible):
        screen.blit(text(line,FONT),(tx,354+i*24))
    if pages>1:
        screen.blit(text(f"{page+1}/{pages}",SMALL,GRAY),(555,338))
    if prompt:
        pygame.draw.polygon(screen,WHITE,[(592,444),(602,444),(597,451)])

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
BRANCH1[2]=[(speaker,message,portrait,kentongan_scene) if i<5 else (speaker,message,portrait)
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
map_mode="kentongan"; map_camera_x=0; map_scale=0.0; map_items=[]; map_total_items=0; map_scroll_world=0.0
map_sari=False; map_mission_timer=0; map_facing=0; map_anim_frame=0; map_patrol=pygame.Rect(820,495,24,32); map_patrol_dir=1
kentongan_obj_img=None
if kentongan_sheet:
    try:
        # Isolated large kentongan from the supplied sprite sheet; crop safely.
        crop_rect=pygame.Rect(65,35,410,900).clip(kentongan_sheet.get_rect())
        kentongan_obj_img=kentongan_sheet.subsurface(crop_rect).copy()
        kentongan_obj_img.set_colorkey((62,44,41))
        kentongan_obj_img.set_colorkey((44,29,27))
        kentongan_obj_img=fit(kentongan_obj_img,(28,52))
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
    global state,battle_id,battle_mode,battle_t,hazards,player,battle_after,objective_items,objective_count,chaser,battle_hp
    battle_id=number; battle_mode=mode; battle_t=0; hazards=[]
    battle_hp=100
    objective_items=[]; objective_count=0
    player.center=(W//2,370); chaser.center=(W//2,125)
    battle_after=after
    state="BATTLE"

battle_after=""

def draw_dialog_state():
    # story background placeholder uses source-map palette / original images as provided
    screen.fill((30,20,15))
    if map_img:
        bg=fit(map_img,(W,H))
        screen.blit(bg,(0,0))
        overlay=pygame.Surface((W,H),pygame.SRCALPHA); overlay.fill((0,0,0,110)); screen.blit(overlay,(0,0))
    if dialog_i<len(dialog_list):
        item=dialog_list[dialog_i]
        speaker,msg,portrait=item[:3]
        bg=item[3] if len(item)>3 else frontline_bg
        if bg:
            screen.blit(fit(bg,(W,H)),(0,0))
            shade=pygame.Surface((W,H),pygame.SRCALPHA); shade.fill((0,0,0,85)); screen.blit(shade,(0,0))
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

# Overworld collision is defined in the original landscape's pixel coordinates.
# The broad horizontal village road and connecting roads are walkable; fields/buildings are blocked.
MAP_SRC_W, MAP_SRC_H = (surabaya_overworld.get_size() if surabaya_overworld else (2048,682))
MAP_VIEW_H=430
MAP_SCALE=MAP_VIEW_H/MAP_SRC_H
MAP_SCALED_W=int(MAP_SRC_W*MAP_SCALE)
MAP_ROADS=[
    pygame.Rect(0,475,MAP_SRC_W,92),                    # main village road
    pygame.Rect(610,250,150,315),                      # road near central village
    pygame.Rect(1130,235,170,330),                     # road toward fields
    pygame.Rect(1470,500,250,180),                      # bridge/road at right
    pygame.Rect(300,500,340,100),                       # west connecting road
]

def on_walkable(x,y):
    # A point is walkable only on one of the road bands.
    return any(r.collidepoint(int(x),int(y)) for r in MAP_ROADS)

def start_map(mode="kentongan"):
    global state,map_active,map_message,map_found,map_obj,map_player,map_mode,map_camera_x,map_scale,map_items,map_total_items,map_sari,map_mission_timer,map_facing,map_anim_frame,map_patrol,map_patrol_dir
    state="MAP"; map_active=True; map_mode=mode; map_found=False; map_camera_x=0; map_mission_timer=0
    map_scale=MAP_SCALE
    map_message="Cari kentongan. Dekati objek lalu tekan E." if mode=="kentongan" else "Cari 3 paket obat di sepanjang jalan."
    map_player=pygame.Rect(100,495,22,30); map_facing=0; map_anim_frame=0; map_patrol=pygame.Rect(820,495,24,32); map_patrol_dir=1
    if mode=="kentongan":
        map_obj=pygame.Rect(690,500,28,52)
        map_items=[]; map_total_items=0; map_sari=False
    else:
        map_obj=None; map_total_items=3; map_sari=True
        # medicine pickup locations on the main road, spread across the scrolling map
        map_items=[pygame.Rect(350,505,22,22),pygame.Rect(1020,505,22,22),pygame.Rect(1760,505,22,22)]

def map_sprite():
    # Use the supplied character sprite sheet; rows represent facing directions.
    frames=sari_frames if map_sari else budi_frames
    idx=(map_facing*4+map_anim_frame)%len(frames)
    return sprite_from(frames,idx,(30,38))

def draw_map():
    global map_camera_x
    screen.fill(BLACK)
    if surabaya_overworld:
        scaled=pygame.transform.scale(surabaya_overworld,(MAP_SCALED_W,MAP_VIEW_H))
        player_screen_x=map_player.centerx*MAP_SCALE
        # Camera follows horizontally and clamps at both map ends.
        map_camera_x=max(0,min(MAP_SCALED_W-W,player_screen_x-W*0.48))
        screen.blit(scaled,(-int(map_camera_x),24))
    else:
        screen.fill((90,70,45)); map_camera_x=0
    # Kentongan or medicine items are drawn in map/world coordinates and follow camera.
    if map_mode=="kentongan" and not map_found and map_obj:
        ox=int(map_obj.x*MAP_SCALE-map_camera_x); oy=int(map_obj.y*MAP_SCALE+24)
        if -60<ox<W+60:
            if kentongan_obj_img: screen.blit(kentongan_obj_img,(ox,oy-20))
            else: pygame.draw.rect(screen,(180,100,30),(ox,oy,24,40))
        label="KENTONGAN"
        if -80<ox<W+80: screen.blit(text(label,SMALL,GOLD),(ox-8,oy-34))
    if map_mode=="medicine":
        patrol_x=int(map_patrol.centerx*MAP_SCALE-map_camera_x); patrol_y=int(map_patrol.centery*MAP_SCALE+24)
        if -50<patrol_x<W+50:
            blit_center(sprite_from(dutch_frames,4,(26,34)),patrol_x,patrol_y)
        for item in map_items:
            ix=int(item.x*MAP_SCALE-map_camera_x); iy=int(item.y*MAP_SCALE+24)
            if -30<ix<W+30:
                pygame.draw.rect(screen,(230,230,230),(ix,iy,18,18))
                pygame.draw.rect(screen,(180,40,40),(ix+7,iy+3,4,12))
                pygame.draw.rect(screen,(180,40,40),(ix+3,iy+7,12,4))
    # Character sprite on map, positioned by camera; preserve crisp pixel scaling.
    px=int(map_player.centerx*MAP_SCALE-map_camera_x); py=int(map_player.centery*MAP_SCALE+24)
    blit_center(map_sprite(),px,py)
    panel(pygame.Rect(8,8,624,42),BLACK,WHITE,2)
    if map_mode=="kentongan":
        screen.blit(text("MISI: TEMUKAN KENTONGAN",SMALL,GOLD),(18,18))
    else:
        screen.blit(text(f"MISI SARI: OBAT {map_total_items-len(map_items)}/{map_total_items}",SMALL,GOLD),(18,18))
    panel(pygame.Rect(8,425,624,44),BLACK,WHITE,2)
    screen.blit(text(map_message,SMALL),(18,439))
    screen.blit(text("WASD / ARROWS • E INTERACT",SMALL,WHITE),(390,18))

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
    if battle_mode in ("medicine","rescue"):
        screen.blit(text(f"OBJECTIVE {objective_count}/3",SMALL,GOLD),(90,78))

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
    if index==0: set_dialog(BRANCH2[0][:4],"B2_BATTLE5")
    elif index==1: set_dialog(BRANCH2[1][:6],"B2_BATTLE6")
    else: set_dialog(BRANCH2[2],"DRAFT_MISSING")

def next_dialog():
    global dialog_i,dialog_page,state
    item=dialog_list[dialog_i]
    message=item[1]
    portrait=item[2] if len(item)>2 else None
    lines=wrap(message,FONT,420 if portrait else 550)
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
    if index==0: set_dialog(BRANCH2[0][5:],"CH2_DONE")
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
                if event.key==pygame.K_e:
                    if map_mode=="kentongan" and map_obj and map_player.inflate(48,48).colliderect(map_obj):
                        map_found=True; map_message="Kentongan ditemukan! Tekan ENTER untuk lanjut cerita."
                    else: map_message="Dekati objek misi terlebih dahulu."
                if event.key==pygame.K_RETURN:
                    if map_mode=="kentongan" and map_found:
                        set_dialog([BRANCH1[2][5]],"B1_BATTLE4")
                    elif map_mode=="medicine" and len(map_items)==0:
                        set_dialog(BRANCH2[0][4:7],"B2_B5_RETURN")
                if event.key==pygame.K_ESCAPE:
                    state="CHOICE1" if map_mode=="kentongan" else "CHOICE2"
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

    # state update
    if state=="MAP":
        # Patrol continues moving even when the player pauses.
        if map_mode=="medicine":
            map_patrol.x += map_patrol_dir*2.0
            if map_patrol.x<650 or map_patrol.x>1050: map_patrol_dir *= -1
            if map_patrol.colliderect(map_player):
                map_player.x=max(80,map_player.x-70)
                map_message="Patroli menghadang! Cari celah dan lanjutkan mencari obat."
        keys=pygame.key.get_pressed()
        speed=5.5
        dx=(keys[pygame.K_d] or keys[pygame.K_RIGHT])-(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy=(keys[pygame.K_s] or keys[pygame.K_DOWN])-(keys[pygame.K_w] or keys[pygame.K_UP])
        if dx or dy:
            # Update facing row; animation cycles only while walking.
            if abs(dx)>abs(dy): map_facing=2 if dx>0 else 1
            else: map_facing=0 if dy>0 else 3
            map_anim_frame=(pygame.time.get_ticks()//120)%4
            # Normalize diagonal speed and use road collision at the player's four corners.
            length=math.sqrt(dx*dx+dy*dy); dx=dx/length*speed; dy=dy/length*speed
            nx=map_player.x+dx; ny=map_player.y+dy
            corners=[(nx+2,ny+2),(nx+map_player.w-3,ny+2),(nx+2,ny+map_player.h-3),(nx+map_player.w-3,ny+map_player.h-3)]
            if all(on_walkable(px,py) for px,py in corners):
                map_player.x=nx; map_player.y=ny
            # A Dutch patrol moves along the road during the medicine mission.
            if map_mode=="medicine":
                if map_patrol.colliderect(map_player):
                    map_player.x=max(80,map_player.x-70)
                    map_message="Patroli menghadang! Cari celah dan lanjutkan mencari obat."
                # Mission pickup: Sari collects medicine packages by touching them.
                for item in map_items[:]:
                    if map_player.colliderect(item.inflate(18,18)):
                        map_items.remove(item)
                        map_message=f"Obat ditemukan! {map_total_items-len(map_items)}/{map_total_items}"
                        if not map_items: map_message="Semua obat terkumpul! Tekan ENTER untuk kembali."
    
    if state=="BATTLE":
        battle_t+=1
        if battle_t%32==0:
            # Hazards are abstract pixel dots in the dodge arena.
            count=2 if battle_mode=="dodge" else 1
            for _ in range(count):
                hazards.append(pygame.Rect(random.randint(105,530),95,7,17))
        if battle_mode in ("medicine","rescue") and battle_t%95==0 and objective_count<3 and len(objective_items)<3:
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
    elif state=="B2_BATTLE5":
        start_map("medicine")
    elif state=="B2_BATTLE6":
        battle_hp=100; start_battle(6,"rescue","B2_B6_POST")
    elif state=="B2_B5_RETURN":
        set_dialog(BRANCH2[0][7:],"CH2_DONE")
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
