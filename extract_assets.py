import os
from PIL import Image
import numpy as np
from collections import deque

CACHE_DIR = "assets_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def smart_clean_sprite(crop_img, bg_rgb=(64, 73, 76), bg_tol=26, grid_tol=32):
    rgba = crop_img.convert('RGBA')
    arr = np.array(rgba)
    H, W, _ = arr.shape
    
    rgb = arr[:, :, :3].astype(np.int16)
    diff = np.max(np.abs(rgb - np.array(bg_rgb, dtype=np.int16)), axis=2)
    is_grid = np.all(arr[:, :, :3] < grid_tol, axis=2)
    is_bg_candidate = (diff <= bg_tol) | is_grid
    
    to_clear = np.zeros((H, W), dtype=bool)
    q = deque()
    for y in range(H):
        if is_bg_candidate[y, 0]: to_clear[y, 0] = True; q.append((y, 0))
        if is_bg_candidate[y, W-1]: to_clear[y, W-1] = True; q.append((y, W-1))
    for x in range(W):
        if is_bg_candidate[0, x]: to_clear[0, x] = True; q.append((0, x))
        if is_bg_candidate[H-1, x]: to_clear[H-1, x] = True; q.append((H-1, x))
        
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((-1,0), (1,0), (0,-1), (0,1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < H and 0 <= nx < W and not to_clear[ny, nx]:
                if is_bg_candidate[ny, nx]:
                    to_clear[ny, nx] = True
                    q.append((ny, nx))
                    
    # Also clean internal background pixels
    to_clear = to_clear | (diff <= 16)
    alpha = np.where(to_clear, 0, 255).astype(np.uint8)
    arr[:, :, 3] = alpha
    res = Image.fromarray(arr)
    
    # Auto crop non-zero
    non_zero = np.where(alpha > 0)
    if len(non_zero[0]) > 0:
        y1, y2 = non_zero[0].min(), non_zero[0].max()
        x1, x2 = non_zero[1].min(), non_zero[1].max()
        res = res.crop((x1, y1, x2 + 1, y2 + 1))
    return res

def clean_large_boss(crop_img):
    rgba = crop_img.convert('RGBA')
    arr = np.array(rgba)
    H, W, _ = arr.shape
    
    bg = np.array([64, 73, 76], dtype=np.int16)
    rgb = arr[:, :, :3].astype(np.int16)
    diff = np.max(np.abs(rgb - bg), axis=2)
    
    is_empty_candidate = (diff <= 28) | np.all(arr[:, :, :3] < 34, axis=2)
    to_clear = np.zeros((H, W), dtype=bool)
    q = deque()
    for y in range(H):
        if is_empty_candidate[y, 0]: to_clear[y, 0] = True; q.append((y, 0))
        if is_empty_candidate[y, W-1]: to_clear[y, W-1] = True; q.append((y, W-1))
    for x in range(W):
        if is_empty_candidate[0, x]: to_clear[0, x] = True; q.append((0, x))
        if is_empty_candidate[H-1, x]: to_clear[H-1, x] = True; q.append((H-1, x))
        
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((-1,0), (1,0), (0,-1), (0,1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < H and 0 <= nx < W and not to_clear[ny, nx]:
                if is_empty_candidate[ny, nx]:
                    to_clear[ny, nx] = True
                    q.append((ny, nx))
                    
    to_clear = to_clear | (diff <= 16)
    alpha = np.where(to_clear, 0, 255).astype(np.uint8)
    arr[:, :, 3] = alpha
    
    # Filter thin isolated dark grid lines
    lum = 0.299*arr[:, :, 0] + 0.587*arr[:, :, 1] + 0.114*arr[:, :, 2]
    is_dark = lum < 35
    for _ in range(2):
        cur_alpha = arr[:, :, 3] > 0
        pad = np.pad(cur_alpha.astype(int), 1, mode='constant', constant_values=0)
        neighbors = (
            pad[:-2, :-2] + pad[:-2, 1:-1] + pad[:-2, 2:] +
            pad[1:-1, :-2] + pad[1:-1, 2:] +
            pad[2:, :-2] + pad[2:, 1:-1] + pad[2:, 2:]
        )
        drop = is_dark & cur_alpha & (neighbors <= 4)
        arr[drop, 3] = 0
        
    non_zero = np.where(arr[:, :, 3] > 0)
    res = Image.fromarray(arr)
    if len(non_zero[0]) > 0:
        y1, y2 = non_zero[0].min(), non_zero[0].max()
        x1, x2 = non_zero[1].min(), non_zero[1].max()
        res = res.crop((x1, y1, x2 + 1, y2 + 1))
    return res

def extract_all():
    print("Extracting and preparing sprites...")
    
    # --- Sheet: Player & Helicopter Boss ---
    sheet_p_path = "sprites/modify_the_player_character_the_little_floating_ai_robot_drone_sprites_in_this.png"
    if os.path.exists(sheet_p_path):
        sheet_p = Image.open(sheet_p_path)
        
        # Player Idle (4 frames)
        for i, (x1, x2) in enumerate([(20, 85), (105, 170), (190, 255), (270, 335)]):
            smart_clean_sprite(sheet_p.crop((x1, 30, x2, 122))).save(f"{CACHE_DIR}/player_idle_{i}.png")
            
        # Player Dash
        smart_clean_sprite(sheet_p.crop((360, 30, 485, 120))).save(f"{CACHE_DIR}/player_dash.png")
        
        # Player Shooting (4 frames)
        for i, (x1, x2) in enumerate([(20, 95), (102, 185), (195, 280), (285, 410)]):
            smart_clean_sprite(sheet_p.crop((x1, 148, x2, 245))).save(f"{CACHE_DIR}/player_shoot_{i}.png")
            
        # Charged Shooting (4 frames)
        for i, (x1, x2) in enumerate([(20, 90), (105, 180), (195, 275), (288, 385)]):
            smart_clean_sprite(sheet_p.crop((x1, 275, x2, 375))).save(f"{CACHE_DIR}/player_charge_{i}.png")
            
        # Player Projectile / Laser
        smart_clean_sprite(sheet_p.crop((440, 150, 490, 195))).save(f"{CACHE_DIR}/proj_player_laser.png")
        # Charged Beam Segment
        smart_clean_sprite(sheet_p.crop((380, 410, 820, 475))).save(f"{CACHE_DIR}/proj_player_beam.png")
        
        # Soldiers
        smart_clean_sprite(sheet_p.crop((515, 30, 600, 125))).save(f"{CACHE_DIR}/enemy_soldier1.png")
        smart_clean_sprite(sheet_p.crop((515, 145, 605, 245))).save(f"{CACHE_DIR}/enemy_soldier2.png")
        smart_clean_sprite(sheet_p.crop((700, 260, 865, 370))).save(f"{CACHE_DIR}/enemy_bazooka.png")
        
        # Enemy Projectiles
        smart_clean_sprite(sheet_p.crop((890, 75, 970, 100))).save(f"{CACHE_DIR}/proj_enemy_bullet.png")
        smart_clean_sprite(sheet_p.crop((860, 265, 960, 365))).save(f"{CACHE_DIR}/proj_enemy_rocket.png")
        smart_clean_sprite(sheet_p.crop((570, 815, 730, 860))).save(f"{CACHE_DIR}/proj_enemy_missile.png")
        
        # Boss Helicopter
        clean_large_boss(sheet_p.crop((20, 515, 480, 800))).save(f"{CACHE_DIR}/boss_helicopter.png")
        
        # Gunship escorts
        for i in range(4):
            smart_clean_sprite(sheet_p.crop((505 + i*128, 515, 505 + (i+1)*128, 635))).save(f"{CACHE_DIR}/escort_heli_{i}.png")
            
        # Big Explosion
        smart_clean_sprite(sheet_p.crop((750, 800, 1000, 1010))).save(f"{CACHE_DIR}/explosion_large.png")

    # --- Sheet: Progression, Evolutions & Level Up ---
    sheet_3_path = "sprites/pixel_art_sprite_sheet_in_authentic_8_bit_16_bit_retro_arcade_game_style(3).png"
    if os.path.exists(sheet_3_path):
        s3 = Image.open(sheet_3_path)
        
        # Player Lv 2 (Winged Jet Drone)
        smart_clean_sprite(s3.crop((320, 560, 570, 750))).save(f"{CACHE_DIR}/player_lv2.png")
        
        # Player Lv 3 (Mecha Overlord Drone with Halo)
        smart_clean_sprite(s3.crop((650, 500, 970, 780))).save(f"{CACHE_DIR}/player_lv3.png")
        
        # Orbiting Bit Cannons (top left and top right bits of Lv 3)
        smart_clean_sprite(s3.crop((655, 520, 735, 620))).save(f"{CACHE_DIR}/player_bit_cannon.png")
        
        # Level Up Banner
        smart_clean_sprite(s3.crop((20, 15, 550, 150))).save(f"{CACHE_DIR}/ui_level_up.png")
        smart_clean_sprite(s3.crop((415, 160, 560, 235))).save(f"{CACHE_DIR}/ui_stage_clear.png")
        
        # Level Badges
        smart_clean_sprite(s3.crop((600, 20, 765, 110))).save(f"{CACHE_DIR}/badge_lv1.png")
        smart_clean_sprite(s3.crop((800, 20, 965, 110))).save(f"{CACHE_DIR}/badge_lv2.png")
        smart_clean_sprite(s3.crop((600, 145, 765, 235))).save(f"{CACHE_DIR}/badge_lv3.png")
        smart_clean_sprite(s3.crop((785, 145, 985, 235))).save(f"{CACHE_DIR}/badge_lvmax.png")
        
        # XP Cubes and Crystals
        smart_clean_sprite(s3.crop((20, 840, 120, 980))).save(f"{CACHE_DIR}/item_xp_blue.png")
        smart_clean_sprite(s3.crop((160, 840, 280, 980))).save(f"{CACHE_DIR}/item_xp_purple.png")
        smart_clean_sprite(s3.crop((320, 810, 480, 980))).save(f"{CACHE_DIR}/item_xp_gold.png")
        smart_clean_sprite(s3.crop((800, 830, 940, 980))).save(f"{CACHE_DIR}/item_crystal.png")

    # --- Sheet 1: Specialized Enemies & Mini-Boss ---
    sheet_1_path = "sprites/pixel_art_sprite_sheet_in_authentic_8_bit_16_bit_retro_arcade_game_style.png"
    if os.path.exists(sheet_1_path):
        s1 = Image.open(sheet_1_path)
        
        # Cyber Dog
        smart_clean_sprite(s1.crop((150, 350, 280, 440))).save(f"{CACHE_DIR}/enemy_cyber_dog.png")
        
        # Scout Drone
        smart_clean_sprite(s1.crop((615, 335, 740, 410))).save(f"{CACHE_DIR}/enemy_scout_drone.png")
        
        # Ground Sentry Turret
        smart_clean_sprite(s1.crop((790, 340, 980, 460))).save(f"{CACHE_DIR}/enemy_turret.png")
        
        # Shield Vanguard Breacher
        smart_clean_sprite(s1.crop((615, 140, 710, 240))).save(f"{CACHE_DIR}/enemy_shield_breacher.png")
        
        # Exo-Suit Brute
        smart_clean_sprite(s1.crop((245, 555, 435, 740))).save(f"{CACHE_DIR}/enemy_mech_brute.png")
        
        # Hover Trooper
        smart_clean_sprite(s1.crop((780, 560, 990, 700))).save(f"{CACHE_DIR}/enemy_hover_trooper.png")
        
        # Combat Buggy
        smart_clean_sprite(s1.crop((465, 550, 740, 725))).save(f"{CACHE_DIR}/enemy_buggy.png")
        
        # Mini-Boss: Major Kira
        smart_clean_sprite(s1.crop((280, 805, 410, 965))).save(f"{CACHE_DIR}/enemy_major_kira.png")

    # --- UI & Items Sheet ---
    ui_sheet_path = "sprites/pixel_art_game_ui_and_item_sprite_sheet_in_authentic_8_bit_retro_arcade_pixel.png"
    if os.path.exists(ui_sheet_path):
        s_ui = Image.open(ui_sheet_path)
        
        # Health Bar frame
        smart_clean_sprite(s_ui.crop((45, 40, 340, 140))).save(f"{CACHE_DIR}/ui_health_bar.png")
        # Energy Bar frame
        smart_clean_sprite(s_ui.crop((360, 40, 650, 140))).save(f"{CACHE_DIR}/ui_energy_bar.png")
        
        # Pickups: Blue Canister (Energy), Green Canister (Health), Battery, Medkit, Barrel
        smart_clean_sprite(s_ui.crop((95, 495, 178, 635))).save(f"{CACHE_DIR}/item_blue_canister.png")
        smart_clean_sprite(s_ui.crop((455, 495, 545, 635))).save(f"{CACHE_DIR}/item_green_canister.png")
        smart_clean_sprite(s_ui.crop((100, 500, 175, 630))).save(f"{CACHE_DIR}/item_nano_capsule.png")
        smart_clean_sprite(s_ui.crop((275, 500, 350, 630))).save(f"{CACHE_DIR}/item_battery.png")
        smart_clean_sprite(s_ui.crop((625, 510, 745, 630))).save(f"{CACHE_DIR}/item_medkit.png")
        smart_clean_sprite(s_ui.crop((425, 710, 555, 915))).save(f"{CACHE_DIR}/item_barrel.png")

    print(f"Extraction complete! Extracted {len(os.listdir(CACHE_DIR))} assets.")

if __name__ == "__main__":
    extract_all()
