#!/usr/bin/env python3
"""
CYBER DRONE: OVERDRIVE - 8-BIT RETRO AERIAL EDITION
Eres un pequeño robot flotante morado que combate en el aire.
"""

import sys
import os
import math
import random
import pygame
import numpy as np

# Asegurar extracción de assets si no existen
if not os.path.exists("assets_cache") or len(os.listdir("assets_cache")) < 20:
    import extract_assets
    extract_assets.extract_all()

# --- CONSTANTES DE CONFIGURACIÓN ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "CYBER DRONE: OVERDRIVE [AERIAL ARCADE]"

# Paleta Retro Arcade de Alto Contraste
COLOR_BG = (8, 10, 18)
COLOR_WHITE = (255, 255, 255)
COLOR_PURPLE = (185, 80, 255)
COLOR_PURPLE_LIGHT = (235, 175, 255)
COLOR_CYAN = (0, 245, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_RED = (255, 55, 75)
COLOR_GREEN = (40, 255, 120)
COLOR_ORANGE = (255, 130, 20)
COLOR_ENEMY_OUTLINE = (255, 60, 40)

# --- SELECTOR DE DIFICULTADES Y MULTIPLICADORES ---
DIFFICULTIES = [
    "VERY EASY",
    "EASY",
    "MEDIUM",
    "HARD",
    "IMPOSSIBLE",
    "REALLY REALLY IMPOSSIBLE",
    "NOW IMPOSSIBLE FOR REAL",
]

DIFFICULTY_SETTINGS = {
    "VERY EASY": {
        "name": "VERY EASY",
        "description": "Estado base: ritmo pausado, tiros lentos y enemigos estándar.",
        "color": (0, 240, 255),
        "hp_mult": 1.00,             # Salud enemigos y boss
        "move_speed_mult": 1.00,     # Velocidad de movimiento
        "bullet_speed_mult": 1.00,   # Velocidad de balas
        "shoot_cooldown_mult": 1.00, # Cadencia de tiro (menor = disparan más rápido)
        "damage_mult": 1.00,         # Daño recibido por proyectiles y choques
        "score_mult": 1.00,          # Bonificador de puntuación
    },
    "EASY": {
        "name": "EASY",
        "description": "Desafío ligero: enemigos +20% veloces y resistentes.",
        "color": (60, 255, 120),
        "hp_mult": 1.25,
        "move_speed_mult": 1.20,
        "bullet_speed_mult": 1.18,
        "shoot_cooldown_mult": 0.85,
        "damage_mult": 1.20,
        "score_mult": 1.25,
    },
    "MEDIUM": {
        "name": "MEDIUM",
        "description": "Arcade balanceado: mayor cadencia de disparo y patrullas ágiles.",
        "color": (255, 215, 0),
        "hp_mult": 1.60,
        "move_speed_mult": 1.45,
        "bullet_speed_mult": 1.38,
        "shoot_cooldown_mult": 0.72,
        "damage_mult": 1.45,
        "score_mult": 1.60,
    },
    "HARD": {
        "name": "HARD",
        "description": "Intensidad alta: ráfagas constantes, disparos veloces y mayor daño.",
        "color": (255, 130, 20),
        "hp_mult": 2.10,
        "move_speed_mult": 1.75,
        "bullet_speed_mult": 1.62,
        "shoot_cooldown_mult": 0.58,
        "damage_mult": 1.75,
        "score_mult": 2.20,
    },
    "IMPOSSIBLE": {
        "name": "IMPOSSIBLE",
        "description": "Lluvia de balas: proyectiles feroces y enemigos con gran blindaje.",
        "color": (255, 45, 65),
        "hp_mult": 2.80,
        "move_speed_mult": 2.10,
        "bullet_speed_mult": 1.90,
        "shoot_cooldown_mult": 0.46,
        "damage_mult": 2.10,
        "score_mult": 3.20,
    },
    "REALLY REALLY IMPOSSIBLE": {
        "name": "REALLY REALLY IMPOSSIBLE",
        "description": "Caos extremo: proyectiles ultrarrápidos, alta salud y daño mortal.",
        "color": (215, 60, 255),
        "hp_mult": 3.60,
        "move_speed_mult": 2.50,
        "bullet_speed_mult": 2.25,
        "shoot_cooldown_mult": 0.36,
        "damage_mult": 2.50,
        "score_mult": 4.50,
    },
    "NOW IMPOSSIBLE FOR REAL": {
        "name": "NOW IMPOSSIBLE FOR REAL",
        "description": "¡PESADILLA ABSOLUTA! Reacciones milimétricas o muerte instantánea.",
        "color": (255, 0, 80),
        "hp_mult": 4.80,
        "move_speed_mult": 3.00,
        "bullet_speed_mult": 2.65,
        "shoot_cooldown_mult": 0.26,
        "damage_mult": 3.00,
        "score_mult": 7.00,
    }
}

# --- GENERADOR DE EFECTOS DE SONIDO PROCEDURALES (8-BIT) ---
class AudioManager:
    def __init__(self):
        self.sounds = {}
        try:
            pygame.mixer.init(44100, -16, 2, 512)
            self._create_procedural_sounds()
            self.enabled = True
        except Exception as e:
            print("Audio no disponible:", e)
            self.enabled = False

    def _create_procedural_sounds(self):
        sr = 44100

        # 1. Láser jugador
        dur = 0.11
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        freq = np.linspace(950, 250, n)
        wave = np.sin(2 * np.pi * freq * t) * (1 - t/dur)
        self.sounds['laser'] = self._to_sound(wave * 0.22)

        # 2. Láser enemigo (más suave y grave)
        dur = 0.16
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        freq = np.linspace(380, 140, n)
        wave = np.sin(2 * np.pi * freq * t) * (1 - t/dur)
        self.sounds['enemy_shot'] = self._to_sound(wave * 0.16)

        # 3. Explosión
        dur = 0.35
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        noise = np.random.uniform(-1, 1, n)
        env = (1 - t/dur) ** 2
        f_low = np.sin(2 * np.pi * 70 * t)
        wave = (noise * 0.7 + f_low * 0.3) * env
        self.sounds['explosion'] = self._to_sound(wave * 0.32)

        # 4. Impacto / Golpe
        dur = 0.08
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        noise = np.random.uniform(-1, 1, n) * (1 - t/dur)
        self.sounds['hit'] = self._to_sound(noise * 0.2)

        # 5. Recoger Ítem
        dur = 0.15
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        f1 = np.sin(2 * np.pi * 587.33 * t)
        f2 = np.sin(2 * np.pi * 880.00 * t)
        wave = (f1 * 0.5 + f2 * 0.5) * (1 - t/dur)
        self.sounds['item'] = self._to_sound(wave * 0.24)

        # 6. Level Up Fanfare
        dur = 0.45
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        n3 = n // 3
        freqs = np.zeros(n)
        freqs[:n3] = 523.25
        freqs[n3:2*n3] = 659.25
        freqs[2*n3:] = 783.99
        wave = np.sin(2 * np.pi * freqs * t) * (1 - (t/dur)*0.4)
        self.sounds['levelup'] = self._to_sound(wave * 0.3)

        # 7. Dash
        dur = 0.18
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        noise = np.random.uniform(-1, 1, n)
        env = np.sin(np.pi * t / dur)
        wave = noise * env * 0.25
        self.sounds['dash'] = self._to_sound(wave)

        # 8. Boss Alert Siren
        dur = 0.6
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        freq = 440 + 200 * np.sin(2 * np.pi * 5 * t)
        wave = np.sin(2 * np.pi * freq * t) * 0.28
        self.sounds['boss_alert'] = self._to_sound(wave)

        # 9. Mega Beam
        dur = 0.5
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        noise = np.random.uniform(-0.5, 0.5, n)
        saw = (2 * (t * 140 - np.floor(0.5 + t * 140)))
        wave = (noise * 0.4 + saw * 0.6) * (1 - t/dur)
        self.sounds['mega_beam'] = self._to_sound(wave * 0.35)

        # 10. Sonidos de Menú y Energía vacía
        dur = 0.05
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        self.sounds['menu_beep'] = self._to_sound(np.sin(2 * np.pi * 880 * t) * (1 - t/dur) * 0.2)
        self.sounds['menu_select'] = self._to_sound(np.sin(2 * np.pi * 660 * t) * (1 - t/dur) * 0.25)
        self.sounds['energy_empty'] = self._to_sound(np.sin(2 * np.pi * 120 * t) * (1 - t/dur) * 0.3)

        # 11. Carga de Super Láser (Zumbido ascendente de 1.0 segundo)
        dur = 1.05
        n = int(sr * dur)
        t = np.linspace(0, dur, n, False)
        freq = np.linspace(220, 880, n)
        wave = np.sin(2 * np.pi * freq * t) * np.linspace(0.08, 0.28, n)
        self.sounds['charging'] = self._to_sound(wave)

    def _to_sound(self, arr):
        sample = (arr * 32767).astype(np.int16)
        stereo = np.column_stack((sample, sample))
        return pygame.sndarray.make_sound(stereo)

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def stop(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].stop()

# --- CARGADOR DE ASSETS Y OPTIMIZADOR DE CONTRASTE ---
class AssetLoader:
    def __init__(self):
        self.cache = {}
        self.outline_cache = {}
        self.fondos = []
        self._load_fondos()

    def _load_fondos(self):
        fondos_dir = "fondos"
        level_files = [
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(1).png",  # Nivel 1: Azoteas Lluviosas
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(3).png",  # Nivel 2: Bio-Lab Aéreo
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(4).png",  # Nivel 3: Complejo Industrial
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(5).png",  # Nivel 4: Ruinas Neón
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(6).png",  # Nivel 5: Fortaleza Militar
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(2).png",  # Nivel 6: Cielo de Guerra
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(8).png",  # Nivel 7: Estratosfera Eléctrica
            "16_9_panoramic_pixel_art_side_scrolling_platformer_video_game_background(7).png",  # Nivel 8: Núcleo Supremo (Final Boss)
        ]
        for fname in level_files:
            p = os.path.join(fondos_dir, fname)
            if os.path.exists(p):
                img = pygame.image.load(p).convert()
                h = SCREEN_HEIGHT
                w = int(img.get_width() * (h / img.get_height()))
                img_scaled = pygame.transform.smoothscale(img, (w, h))

                # Reducción suave de brillo del fondo (~35%) para que los objetos resalten al máximo
                darken = pygame.Surface((w, h), pygame.SRCALPHA)
                darken.fill((0, 0, 0, 85))
                img_scaled.blit(darken, (0, 0))
                self.fondos.append(img_scaled)
            else:
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                surf.fill((15, 18, 28))
                self.fondos.append(surf)

    def get_image(self, name, scale=None):
        key = (name, scale)
        if key in self.cache:
            return self.cache[key]
        
        path = os.path.join("assets_cache", name)
        if not os.path.exists(path):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.fill(COLOR_PURPLE)
            return surf

        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.smoothscale(img, scale)
        self.cache[key] = img
        return img

    def get_outlined_image(self, name, scale=None, color=COLOR_ENEMY_OUTLINE, thickness=2):
        # Genera un contorno de alto contraste alrededor del sprite
        key = (name, scale, color, thickness)
        if key in self.outline_cache:
            return self.outline_cache[key]

        img = self.get_image(name, scale)
        w, h = img.get_size()
        mask = pygame.mask.from_surface(img)
        mask_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))

        # Crear superficie con margen para el contorno
        out_w = w + thickness * 2
        out_h = h + thickness * 2
        res = pygame.Surface((out_w, out_h), pygame.SRCALPHA)

        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx*dx + dy*dy <= thickness*thickness + 1:
                    res.blit(mask_surf, (dx + thickness, dy + thickness))
        
        # Superponer la imagen original centrada
        res.blit(img, (thickness, thickness))
        self.outline_cache[key] = res
        return res

# --- SISTEMA DE PARTÍCULAS ---
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, decay=0.96):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.decay = decay

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.decay
        self.vy *= self.decay
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        radius = max(1, int(self.size * (self.life / self.max_life)))
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        col = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(s, col, (radius, radius), radius)
        surf.blit(s, (int(self.x - radius), int(self.y - radius)))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add(self, p):
        self.particles.append(p)

    def spawn_thruster(self, x, y, vx=0, vy=0, color=COLOR_PURPLE_LIGHT):
        for _ in range(2):
            px = x + random.uniform(-3, 3)
            py = y + random.uniform(0, 4)
            pvx = vx * 0.2 + random.uniform(-0.5, 0.5)
            pvy = random.uniform(2.0, 5.0) + vy * 0.2
            self.particles.append(Particle(px, py, pvx, pvy, color, random.uniform(3, 6), random.randint(12, 22)))

    def spawn_explosion(self, x, y, count=25, colors=None):
        if colors is None:
            colors = [COLOR_ORANGE, COLOR_GOLD, COLOR_RED, COLOR_WHITE]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(2.0, 8.0)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            col = random.choice(colors)
            self.particles.append(Particle(x, y, vx, vy, col, random.uniform(3, 8), random.randint(20, 45), 0.94))

    def spawn_sparkle(self, x, y, color=COLOR_CYAN, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(1.2, 4.0)
            self.particles.append(Particle(x, y, math.cos(angle)*spd, math.sin(angle)*spd, color, random.uniform(2, 4), random.randint(14, 30)))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)

# --- PROYECTILES CON VELOCIDAD Y RITMO MODERADOS ---
class Projectile:
    def __init__(self, x, y, vx, vy, is_player=True, damage=25, kind="laser", img=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_player = is_player
        self.damage = damage
        self.kind = kind
        self.img = img
        self.alive = True
        self.radius = 8
        self.homing_target = None
        self.lifetime = 190
        self.hit_entities = set()

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

        if self.kind == "missile" and self.homing_target and getattr(self.homing_target, 'alive', False):
            # Guiado suave y pausado para permitir esquivar
            dx = self.homing_target.x - self.x
            dy = self.homing_target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 5:
                target_vx = (dx / dist) * 4.8
                target_vy = (dy / dist) * 4.8
                self.vx += (target_vx - self.vx) * 0.05
                self.vy += (target_vy - self.vy) * 0.05

        self.x += self.vx
        self.y += self.vy

        if self.x < -100 or self.x > SCREEN_WIDTH + 100 or self.y < -100 or self.y > SCREEN_HEIGHT + 100:
            self.alive = False

    def draw(self, surf):
        if not self.alive:
            return

        # Resplandor brillante de alto contraste
        glow_col = (180, 70, 255, 95) if self.is_player else (255, 50, 50, 95)
        glow_size = 16 if self.kind != "beam" else 32
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_col, (glow_size, glow_size), glow_size)
        surf.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))

        if self.img:
            angle = math.degrees(math.atan2(-self.vy, self.vx))
            rotated = pygame.transform.rotate(self.img, angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surf.blit(rotated, rect.topleft)
        else:
            col = COLOR_PURPLE_LIGHT if self.is_player else COLOR_RED
            pygame.draw.circle(surf, col, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surf, COLOR_WHITE, (int(self.x), int(self.y)), max(1, self.radius - 2))

# --- ÍTEMS Y DROPS ---
class ItemDrop:
    def __init__(self, x, y, item_type, assets):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.2, 0.4)
        self.vy = random.uniform(-1.5, 1.5)
        self.item_type = item_type
        self.alive = True
        self.lifetime = 650
        self.time = random.uniform(0, 100)

        img_map = {
            "canister_blue": ("item_blue_canister.png", (34, 48)),    # Bote azul: Energía
            "canister_green": ("item_green_canister.png", (34, 48)),  # Bote verde: Vida
            "xp_blue": ("item_xp_blue.png", (34, 34)),
            "xp_purple": ("item_xp_purple.png", (40, 40)),
            "xp_gold": ("item_xp_gold.png", (48, 48)),
            "crystal": ("item_crystal.png", (42, 50)),
            "medkit": ("item_medkit.png", (38, 38)),
        }
        name, sz = img_map.get(item_type, ("item_blue_canister.png", (34, 48)))
        self.img = assets.get_image(name, sz)

    def update(self, player):
        self.lifetime -= 1
        self.time += 0.08
        if self.lifetime <= 0:
            self.alive = False

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        magnet_range = 240 if player.level >= 2 else 160
        if dist < magnet_range:
            spd = 8.5 * (1 - dist / magnet_range) + 2.0
            self.vx += (dx / dist) * spd * 0.22
            self.vy += (dy / dist) * spd * 0.22
            self.vx *= 0.92
            self.vy *= 0.92
        else:
            self.vx *= 0.97
            self.vy = math.sin(self.time) * 0.7

        self.x += self.vx
        self.y += self.vy

    def draw(self, surf):
        if not self.alive:
            return
        if self.lifetime < 120 and (self.lifetime // 6) % 2 == 0:
            return

        halo = pygame.Surface((56, 56), pygame.SRCALPHA)
        if self.item_type == "canister_blue":
            halo_c = (0, 240, 255, 95)
        elif self.item_type == "canister_green":
            halo_c = (50, 255, 80, 95)
        elif "xp" in self.item_type:
            halo_c = (180, 80, 255, 75)
        else:
            halo_c = (50, 255, 120, 75)
        pygame.draw.circle(halo, halo_c, (28, 28), 24 + int(3 * math.sin(self.time * 4)))
        surf.blit(halo, (int(self.x - 28), int(self.y - 28)))

        rect = self.img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(self.img, rect.topleft)

# --- ENEMIGOS (SOLO VOLADORES, ALTO CONTRASTE Y RITMO CALIBRADO POR DIFICULTAD) ---
class AerialEnemy:
    def __init__(self, x, y, enemy_type, assets, stage=1, diff_cfg=None):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.alive = True
        self.assets = assets
        self.time = random.uniform(0, 50)
        self.hit_flash = 0
        self.is_boss = False
        self.stage = stage
        self.diff_cfg = diff_cfg if diff_cfg is not None else DIFFICULTY_SETTINGS["VERY EASY"]

        # Configuración de unidades voladoras calibradas a ritmo pausado y desafiante
        if enemy_type == "scout_drone":
            self.max_hp = 42
            self.speed = random.uniform(1.0, 1.4)
            self.points = 120
            self.img_name = "enemy_scout_drone.png"
            self.scale = (62, 46)
            self.width, self.height = 54, 40
            self.shoot_cooldown = random.randint(180, 260)

        elif enemy_type == "hover_trooper":
            self.max_hp = 85
            self.speed = random.uniform(1.1, 1.5)
            self.points = 220
            self.img_name = "enemy_hover_trooper.png"
            self.scale = (72, 52)
            self.width, self.height = 64, 46
            self.shoot_cooldown = random.randint(200, 280)

        elif enemy_type == "hover_trooper_v2":  # Tropa de Asalto Avanzada
            self.max_hp = 125
            self.speed = random.uniform(1.2, 1.6)
            self.points = 320
            self.img_name = "enemy_hover_trooper_v2.png"
            self.scale = (74, 54)
            self.width, self.height = 66, 48
            self.shoot_cooldown = random.randint(170, 250)

        elif enemy_type == "escort_heli":
            self.max_hp = 175
            self.speed = 1.0
            self.points = 380
            self.img_name = "escort_heli_0.png"
            self.scale = (84, 58)
            self.width, self.height = 76, 52
            self.shoot_cooldown = 190

        elif enemy_type == "shield_breacher":  # Dron Acorazado con Escudo
            self.max_hp = 190
            self.speed = 0.95
            self.points = 450
            self.img_name = "enemy_shield_breacher.png"
            self.scale = (82, 68)
            self.width, self.height = 74, 60
            self.shoot_cooldown = 160

        elif enemy_type == "flying_mech":  # Mini-Boss Nivel 3
            self.max_hp = 1250
            self.speed = 0.75
            self.points = 1500
            self.img_name = "enemy_mech_brute.png"
            self.scale = (110, 125)
            self.width, self.height = 95, 115
            self.shoot_cooldown = 140
            self.is_boss = True
            self.boss_name = "MECHA TITAN BRUTE"

        elif enemy_type == "major_kira":   # Mini-Boss Nivel 5
            self.max_hp = 1800
            self.speed = 1.2
            self.points = 2200
            self.img_name = "enemy_major_kira.png"
            self.scale = (78, 108)
            self.width, self.height = 68, 98
            self.shoot_cooldown = 120
            self.is_boss = True
            self.boss_name = "COMANDANTE MAYOR KIRA"

        elif enemy_type == "heavy_brute":  # Mini-Boss Nivel 7
            self.max_hp = 2400
            self.speed = 0.7
            self.points = 3200
            self.img_name = "enemy_mech_brute_v2.png"
            self.scale = (120, 135)
            self.width, self.height = 105, 125
            self.shoot_cooldown = 110
            self.is_boss = True
            self.boss_name = "MECHA SUPREMO TITAN PRIME"

        # Escalar salud con la etapa y con la dificultad seleccionada
        hp_mult = (1.0 + (stage - 1) * 0.14) * self.diff_cfg["hp_mult"]
        self.max_hp = max(10, int(self.max_hp * hp_mult))
        self.hp = self.max_hp
        self.speed = self.speed * self.diff_cfg["move_speed_mult"]
        self.shoot_cooldown = max(20, int(self.shoot_cooldown * self.diff_cfg["shoot_cooldown_mult"]))
        self.facing = -1  # -1 = izquierda, 1 = derecha

    def update(self, player, projectiles, audio, particles):
        self.time += 0.025
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Movimiento horizontal con retorno: al llegar a un extremo, giran y regresan
        if self.enemy_type in ("scout_drone", "hover_trooper", "hover_trooper_v2", "escort_heli", "shield_breacher"):
            self.x += self.speed * self.facing
            # Al llegar al extremo izquierdo, giran hacia la derecha para volver
            if self.x <= 45 and self.facing < 0:
                self.facing = 1
                self.y = min(SCREEN_HEIGHT - 120, max(85, self.y + random.randint(-40, 40)))
            # Al llegar al extremo derecho, vuelven a girar hacia la izquierda
            elif self.x >= SCREEN_WIDTH - 45 and self.facing > 0:
                self.facing = -1
                self.y = min(SCREEN_HEIGHT - 120, max(85, self.y + random.randint(-40, 40)))

        # Movimiento aéreo suave y estelas de propulsión
        if self.enemy_type == "scout_drone":
            self.y += math.sin(self.time * 1.5) * 1.6
            particles.spawn_thruster(self.x - 20 * self.facing, self.y + 10, 0, 0, COLOR_CYAN)

        elif self.enemy_type in ("hover_trooper", "hover_trooper_v2"):
            self.y += math.sin(self.time * 1.1) * 1.9
            particles.spawn_thruster(self.x - 25 * self.facing, self.y + 15, 0, 0, COLOR_ORANGE)

        elif self.enemy_type == "escort_heli":
            self.y += math.sin(self.time * 0.9) * 1.5

        elif self.enemy_type == "shield_breacher":
            self.y += math.sin(self.time * 0.8) * 1.4
            particles.spawn_thruster(self.x - 30 * self.facing, self.y + 20, 0, 0, COLOR_CYAN)

        elif self.enemy_type in ("flying_mech", "heavy_brute"):
            if self.x > 840:
                self.x -= self.speed
            self.y += math.sin(self.time * 0.8) * 1.8
            particles.spawn_thruster(self.x - 10, self.y + 55, 0, 0, COLOR_RED)
            particles.spawn_thruster(self.x + 30, self.y + 55, 0, 0, COLOR_RED)

        elif self.enemy_type == "major_kira":
            if self.x > 860:
                self.x -= self.speed
            self.y += math.sin(self.time * 1.1) * 2.2
            particles.spawn_thruster(self.x + 20, self.y + 40, 0, 0, COLOR_CYAN)

        # Disparos pausados y calculados
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and 20 < self.x < SCREEN_WIDTH - 20:
            self.shoot(player, projectiles, audio)

    def shoot(self, player, projectiles, audio):
        bullet_img = self.assets.get_image("proj_enemy_bullet.png", (22, 10))
        rocket_img = self.assets.get_image("proj_enemy_rocket.png", (34, 16))
        spd_m = self.diff_cfg["bullet_speed_mult"]
        dmg_m = self.diff_cfg["damage_mult"]
        cd_m = self.diff_cfg["shoot_cooldown_mult"]

        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.hypot(dx, dy))
        # Determinar si el jugador está a la espalda del enemigo
        is_behind = (dx * self.facing < 0)

        # Posiciones de torreta frontal y trasera según hacia dónde mira el enemigo
        front_x = self.x + 24 * self.facing
        rear_x = self.x - 24 * self.facing

        if self.enemy_type in ("scout_drone", "hover_trooper"):
            self.shoot_cooldown = max(25, int(random.randint(180, 260) * cd_m))
            spd = 2.6 * spd_m
            dmg = int(18 * dmg_m)
            if is_behind:
                # Disparo defensivo hacia atrás apuntando al jugador que lo persigue
                projectiles.append(Projectile(rear_x, self.y, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
            else:
                # Disparo frontal hacia el jugador
                projectiles.append(Projectile(front_x, self.y, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
                # Probabilidad de soltar también un tiro de retaguardia hacia atrás
                if random.random() < 0.35:
                    rear_vx = -self.facing * (2.2 * spd_m)
                    projectiles.append(Projectile(rear_x, self.y, rear_vx, 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

        elif self.enemy_type == "hover_trooper_v2":
            self.shoot_cooldown = max(25, int(random.randint(170, 240) * cd_m))
            spd = 2.8 * spd_m
            dmg = int(18 * dmg_m)
            if is_behind:
                # Doble ráfaga hacia atrás apuntando al jugador
                projectiles.append(Projectile(rear_x, self.y - 6, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(rear_x, self.y + 6, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
            else:
                projectiles.append(Projectile(front_x, self.y - 6, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(front_x, self.y + 6, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
                # Fuego de cobertura hacia atrás
                rear_vx = -self.facing * (2.4 * spd_m)
                projectiles.append(Projectile(rear_x, self.y, rear_vx, 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

        elif self.enemy_type == "escort_heli":
            self.shoot_cooldown = max(25, int(190 * cd_m))
            dmg = int(20 * dmg_m)
            spd = 2.8 * spd_m
            # El helicóptero de escolta cuenta con torreta frontal y ametralladora de cola
            if is_behind:
                # Ametralladora de cola disparando hacia atrás contra el jugador
                projectiles.append(Projectile(rear_x, self.y + 8, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
            else:
                # Disparo de cañón frontal
                projectiles.append(Projectile(front_x, self.y + 12, self.facing * spd, 0, False, dmg, "bullet", bullet_img))
                # Disparo de cola hacia atrás
                projectiles.append(Projectile(rear_x, self.y + 8, -self.facing * (2.2 * spd_m), 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

        elif self.enemy_type == "shield_breacher":
            self.shoot_cooldown = max(25, int(160 * cd_m))
            spd = 3.0 * spd_m
            dmg = int(22 * dmg_m)
            if is_behind:
                # Cañón trasero de plasma anti-flanqueo
                projectiles.append(Projectile(rear_x, self.y, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
            else:
                projectiles.append(Projectile(front_x, self.y, (dx/dist)*spd, (dy/dist)*spd, False, dmg, "bullet", bullet_img))
                # Descarga de propulsor trasero
                projectiles.append(Projectile(rear_x, self.y, -self.facing * (2.5 * spd_m), 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

        elif self.enemy_type == "flying_mech":
            self.shoot_cooldown = max(25, int(140 * cd_m))
            dmg = int(22 * dmg_m)
            spd = 2.6 * spd_m
            mech_dir = 1 if player.x > self.x else -1
            if mech_dir == 1:
                # Jugador está a la espalda del Mecha: fuego de torretas traseras hacia la derecha
                projectiles.append(Projectile(self.x + 40, self.y - 15, spd, -0.5 * spd_m, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(self.x + 40, self.y + 20, spd, 0.5 * spd_m, False, dmg, "bullet", bullet_img))
            else:
                # Fuego frontal regular hacia la izquierda
                projectiles.append(Projectile(self.x - 40, self.y - 15, -spd, -0.5 * spd_m, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(self.x - 40, self.y + 20, -spd, 0.5 * spd_m, False, dmg, "bullet", bullet_img))
                # Disparo de seguridad hacia atrás
                projectiles.append(Projectile(self.x + 40, self.y, 2.0 * spd_m, 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

        elif self.enemy_type == "heavy_brute":
            self.shoot_cooldown = max(25, int(110 * cd_m))
            dmg = int(24 * dmg_m)
            brute_dir = 1 if player.x > self.x else -1
            if brute_dir == 1:
                # Batería pesada trasera disparando hacia atrás contra el jugador
                projectiles.append(Projectile(self.x + 40, self.y - 20, 2.8 * spd_m, -0.6 * spd_m, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(self.x + 40, self.y, 3.0 * spd_m, 0, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(self.x + 40, self.y + 20, 2.8 * spd_m, 0.6 * spd_m, False, dmg, "bullet", bullet_img))
            else:
                # Fuego triple frontal
                projectiles.append(Projectile(self.x - 40, self.y - 20, -2.8 * spd_m, -0.6 * spd_m, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(self.x - 40, self.y, -3.0 * spd_m, 0, False, dmg, "bullet", bullet_img))
                projectiles.append(Projectile(self.x - 40, self.y + 20, -2.8 * spd_m, 0.6 * spd_m, False, dmg, "bullet", bullet_img))
                # Disparo de artillería de retaguardia
                projectiles.append(Projectile(self.x + 40, self.y, 2.5 * spd_m, 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

        elif self.enemy_type == "major_kira":
            self.shoot_cooldown = max(25, int(120 * cd_m))
            dmg = int(18 * dmg_m)
            spd = 2.8 * spd_m
            kira_dir = 1 if player.x > self.x else -1
            if kira_dir == 1:
                # Ráfaga en abanico hacia atrás
                for a in (-0.16, 0, 0.16):
                    projectiles.append(Projectile(self.x + 30, self.y, math.cos(a)*spd, math.sin(a)*spd, False, dmg, "bullet", bullet_img))
            else:
                for a in (-0.16, 0, 0.16):
                    projectiles.append(Projectile(self.x - 30, self.y, -math.cos(a)*spd, math.sin(a)*spd, False, dmg, "bullet", bullet_img))
                # Tiro de retaguardia hacia atrás
                projectiles.append(Projectile(self.x + 30, self.y, spd * 0.8, 0, False, dmg, "bullet", bullet_img))
            audio.play('enemy_shot')

    def take_damage(self, amount, audio, particles):
        self.hp -= amount
        self.hit_flash = 4
        particles.spawn_sparkle(self.x, self.y, COLOR_PURPLE_LIGHT, 5)
        if self.hp <= 0:
            self.alive = False
            audio.play('explosion')
            count = 45 if self.is_boss else 22
            particles.spawn_explosion(self.x, self.y, count)
        else:
            audio.play('hit')

    def draw(self, surf):
        if not self.alive:
            return

        # ALTO CONTRASTE: Sprite con contorno neón rojo/naranja nítido
        outlined_img = self.assets.get_outlined_image(self.img_name, self.scale, COLOR_ENEMY_OUTLINE, 2)
        # Girar el sprite si está volando hacia la derecha
        if self.facing == 1:
            outlined_img = pygame.transform.flip(outlined_img, True, False)

        rect = outlined_img.get_rect(center=(int(self.x), int(self.y)))

        if self.hit_flash > 0:
            white_surf = outlined_img.copy()
            white_surf.fill((255, 255, 255, 210), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(white_surf, rect.topleft)
        else:
            surf.blit(outlined_img, rect.topleft)

        # Barra de vida para enemigos resistentes o mini-bosses
        if self.max_hp > 80:
            bw, bh = max(42, self.width), 6
            bx = int(self.x - bw // 2)
            by = int(self.y - self.height // 2 - 14)
            pygame.draw.rect(surf, (15, 15, 25), (bx, by, bw, bh))
            pct = max(0, self.hp / self.max_hp)
            bar_col = COLOR_RED if pct < 0.3 else (COLOR_GOLD if pct < 0.6 else COLOR_GREEN)
            pygame.draw.rect(surf, bar_col, (bx, by, int(bw * pct), bh))
            pygame.draw.rect(surf, COLOR_WHITE, (bx, by, bw, bh), 1)

# --- FINAL BOSS: TITAN GUNSHIP ---
class FinalBoss:
    def __init__(self, assets, diff_cfg=None):
        self.assets = assets
        self.diff_cfg = diff_cfg if diff_cfg is not None else DIFFICULTY_SETTINGS["VERY EASY"]
        self.x = SCREEN_WIDTH + 200
        self.y = SCREEN_HEIGHT // 2
        self.target_x = SCREEN_WIDTH - 260
        self.max_hp = int(5200 * self.diff_cfg["hp_mult"])
        self.hp = self.max_hp
        self.alive = True
        self.is_boss = True
        self.boss_name = "APEX WAR HELICOPTER: TITAN GUNSHIP"
        
        self.img_name = "boss_helicopter.png"
        self.scale = (360, 210)
        self.width, self.height = 320, 180
        self.time = 0
        self.phase = 1
        self.hit_flash = 0
        self.attack_timer = 0
        self.spawn_timer = 0
        self.enraged = False

    def update(self, player, projectiles, enemies, audio, particles):
        self.time += 0.02
        if self.hit_flash > 0:
            self.hit_flash -= 1

        spd_m = self.diff_cfg["bullet_speed_mult"]
        dmg_m = self.diff_cfg["damage_mult"]
        cd_m = self.diff_cfg["shoot_cooldown_mult"]
        move_m = self.diff_cfg["move_speed_mult"]

        if self.x > self.target_x:
            self.x -= 1.4 * move_m
        else:
            self.y = (SCREEN_HEIGHT // 2) + math.sin(self.time * 0.8 * move_m) * (140 if self.phase == 3 else 110)
            self.x = self.target_x + math.cos(self.time * 0.5 * move_m) * 25

        hp_pct = self.hp / self.max_hp
        if hp_pct <= 0.35 and self.phase < 3:
            self.phase = 3
            self.enraged = True
            audio.play('boss_alert')
            particles.spawn_explosion(self.x, self.y, 50)
        elif hp_pct <= 0.70 and self.phase < 2:
            self.phase = 2
            audio.play('boss_alert')

        self.attack_timer += 1
        bullet_img = self.assets.get_image("proj_enemy_bullet.png", (24, 12))
        missile_img = self.assets.get_image("proj_enemy_missile.png", (44, 20))

        # Chin Vulcan Gatling calibrado por dificultad
        gatling_rate = max(4, int((18 if self.phase == 3 else 28) * cd_m))
        if self.attack_timer % gatling_rate == 0:
            spread = 0.12 if self.phase >= 2 else 0.05
            angle = math.atan2(player.y - (self.y + 60), player.x - (self.x - 120)) + random.uniform(-spread, spread)
            spd = (3.6 if self.phase == 3 else 3.0) * spd_m
            projectiles.append(Projectile(self.x - 130, self.y + 65, math.cos(angle)*spd, math.sin(angle)*spd, False, int(18 * dmg_m), "bullet", bullet_img))
            # Si el jugador se sitúa detrás del Boss, o en fases avanzadas, la torreta de cola dispara hacia atrás
            if player.x > self.x - 40 or (self.phase >= 2 and self.attack_timer % (gatling_rate * 2) == 0):
                rear_angle = math.atan2(player.y - self.y, player.x - (self.x + 90)) + random.uniform(-spread, spread)
                projectiles.append(Projectile(self.x + 100, self.y + 15, math.cos(rear_angle)*spd, math.sin(rear_angle)*spd, False, int(16 * dmg_m), "bullet", bullet_img))
            audio.play('enemy_shot')

        # Salvas de Misiles Homing (disparan hacia atrás si el jugador está a la espalda)
        missile_interval = max(35, int(160 * cd_m))
        if self.phase >= 2 and self.attack_timer % missile_interval == 0:
            for offset_y in (-45, 45):
                spawn_x = (self.x + 80) if player.x > self.x else (self.x - 80)
                init_vx = (3.2 * spd_m) if player.x > self.x else (-3.2 * spd_m)
                p = Projectile(spawn_x, self.y + offset_y, init_vx, random.uniform(-1.5, 1.5) * spd_m, False, int(26 * dmg_m), "missile", missile_img)
                p.homing_target = player
                projectiles.append(p)
            audio.play('enemy_shot')

        # Bombardeo en abanico
        fan_interval = max(40, int(180 * cd_m))
        if self.phase == 3 and self.attack_timer % fan_interval == 0:
            for a in np.linspace(-0.4, 0.4, 4):
                spd = 3.2 * spd_m
                projectiles.append(Projectile(self.x - 100, self.y, -math.cos(a)*spd, math.sin(a)*spd, False, int(20 * dmg_m), "bullet", bullet_img))
            audio.play('enemy_shot')

        # Drones de escolta
        self.spawn_timer += 1
        spawn_interval = max(60, int(240 * cd_m))
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            if len([e for e in enemies if not getattr(e, 'is_boss', False)]) < 3:
                sy = random.choice([130, SCREEN_HEIGHT - 160])
                enemies.append(AerialEnemy(SCREEN_WIDTH + 40, sy, "scout_drone", self.assets, stage=8, diff_cfg=self.diff_cfg))

    def take_damage(self, amount, audio, particles):
        self.hp -= amount
        self.hit_flash = 4
        particles.spawn_sparkle(self.x - 50, self.y + random.uniform(-40, 40), COLOR_PURPLE_LIGHT, 5)
        if self.hp <= 0:
            self.alive = False
            audio.play('explosion')
            for _ in range(10):
                particles.spawn_explosion(self.x + random.uniform(-100, 100), self.y + random.uniform(-60, 60), 40)
        else:
            audio.play('hit')

    def draw(self, surf):
        if not self.alive:
            return

        outlined_img = self.assets.get_outlined_image(self.img_name, self.scale, (255, 80, 50), 3)
        rect = outlined_img.get_rect(center=(int(self.x), int(self.y)))
        
        if self.enraged:
            glow = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 30, 30, 55 + int(35 * math.sin(self.time * 6))), (0, 0, self.width + 40, self.height + 40))
            surf.blit(glow, (rect.centerx - (self.width + 40)//2, rect.centery - (self.height + 40)//2))

        if self.hit_flash > 0:
            white_surf = outlined_img.copy()
            white_surf.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(white_surf, rect.topleft)
        else:
            surf.blit(outlined_img, rect.topleft)

# --- JUGADOR (DISPARO BIDIRECCIONAL, ENERGÍA Y 1 SOLA VIDA) ---
class Player:
    def __init__(self, assets):
        self.assets = assets
        self.x = 180
        self.y = SCREEN_HEIGHT // 2
        self.vx = 0
        self.vy = 0
        self.base_speed = 4.8  # Movimiento más ágil y veloz
        
        # 1 SOLA VIDA (Sin sistema de 3 vidas)
        self.max_hp = 120
        self.hp = self.max_hp
        self.hit_flash = 0
        
        # BARRA DE ENERGÍA (Consume para Super-Disparo y Dash; NO se recarga sola, solo con botes azules)
        self.max_energy = 100.0
        self.energy = self.max_energy
        self.energy_regen = 0.0  # La energía NO se carga sola
        
        # CARGA DEL SUPER-DISPARO (1 segundo continuo = 60 frames a 60 FPS)
        self.charge_timer = 0
        self.charge_max = 60
        
        # DIRECCIÓN: 1 = Derecha, -1 = Izquierda (Disparar hacia atrás)
        self.facing = 1

        # Progresión pausada y desafiante distribuida en 8 sectores
        self.level = 1
        self.xp = 0
        self.xp_targets = [0, 3500, 9500, 18000]
        self.level_up_timer = 0
        
        self.anim_time = 0
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.shoot_cooldown = 0
        self.beam_cooldown = 0
        self.invulnerable_timer = 0
        self.orbit_angle = 0

    @property
    def alive(self):
        return self.hp > 0

    @alive.setter
    def alive(self, val):
        if not val:
            self.hp = 0

    def update(self, keys, mouse_pressed, projectiles, audio, particles):
        self.anim_time += 0.12
        self.orbit_angle += 0.06
        if self.level_up_timer > 0:
            self.level_up_timer -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.beam_cooldown > 0:
            self.beam_cooldown -= 1

        # Control de movimiento
        move_x = 0
        move_y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1
            self.facing = -1  # Mirar y disparar hacia atrás (Izquierda)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1
            self.facing = 1   # Mirar y disparar hacia adelante (Derecha)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        # Tecla de Disparo Hacia Atrás dedicado [Q]
        if keys[pygame.K_q]:
            self.facing = -1

        # Turbo Dash (Consume 20 de Energía explícitamente)
        is_dash_key = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or mouse_pressed[2]
        if is_dash_key and self.dash_cooldown <= 0 and (move_x != 0 or move_y != 0):
            if self.energy >= 20.0:
                self.energy -= 20.0
                self.dash_timer = 12
                self.dash_cooldown = 40
                self.invulnerable_timer = 16
                audio.play('dash')
                particles.spawn_sparkle(self.x, self.y, COLOR_CYAN, 14)
            else:
                self.dash_cooldown = 15
                audio.play('energy_empty')

        spd = (self.base_speed * 1.7) if self.dash_timer > 0 else self.base_speed
        if self.level == 2: spd += 0.4
        elif self.level == 3: spd += 0.8
        elif self.level >= 4: spd += 1.2

        if self.dash_timer > 0:
            self.dash_timer -= 1

        target_vx = move_x * spd
        target_vy = move_y * spd
        self.vx += (target_vx - self.vx) * 0.28
        self.vy += (target_vy - self.vy) * 0.28

        hover_bob = math.sin(self.anim_time * 2.0) * 0.6
        self.x += self.vx
        self.y += self.vy + hover_bob

        self.x = max(40, min(SCREEN_WIDTH - 60, self.x))
        self.y = max(40, min(SCREEN_HEIGHT - 60, self.y))

        # Propulsor morado/cian orientado según dirección
        thruster_x = self.x - (18 * self.facing)
        thruster_col = COLOR_CYAN if self.level >= 2 else COLOR_PURPLE_LIGHT
        particles.spawn_thruster(thruster_x, self.y + 16, self.vx, self.vy, thruster_col)

        # Disparo normal (Espacio o Clic Izquierdo) hacia self.facing
        is_shooting = keys[pygame.K_SPACE] or mouse_pressed[0] or keys[pygame.K_q]
        if is_shooting and self.shoot_cooldown <= 0:
            self.fire(projectiles, audio)

        # SUPER-DISPARO (Tecla [E]): Requiere cargar durante 1 segundo continuo (60 frames)
        if keys[pygame.K_e] and self.beam_cooldown <= 0:
            if self.energy >= 45.0:
                if self.charge_timer == 0:
                    audio.play('charging')
                self.charge_timer += 1

                # Partículas de energía convergiendo al núcleo del robot
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(20, 45)
                particles.spawn_sparkle(self.x + math.cos(angle)*dist, self.y + math.sin(angle)*dist, COLOR_CYAN, 1)

                # Al completar exactamente 1 segundo (60 frames a 60 FPS)
                if self.charge_timer >= self.charge_max:
                    audio.stop('charging')
                    self.energy -= 45.0
                    self.charge_timer = 0
                    self.beam_cooldown = 45
                    self.shoot_cooldown = 20
                    self.fire_mega_beam(projectiles, audio, particles)
            else:
                if self.charge_timer > 0:
                    audio.stop('charging')
                self.charge_timer = 0
                if self.beam_cooldown <= 0:
                    self.beam_cooldown = 25
                    audio.play('energy_empty')
        else:
            if self.charge_timer > 0:
                audio.stop('charging')
            self.charge_timer = 0

    def fire(self, projectiles, audio):
        laser_img = self.assets.get_image("proj_player_laser.png", (32, 14))
        f = self.facing
        vx_base = 9.8 * f  # Velocidad moderada y agradable

        # Requisito 2: El triple disparo y ráfagas avanzadas van SOLO HACIA ADELANTE.
        # Hacia atrás (f == -1) solo dispara un tiro simple defensivo para mantener el reto y evitar que sea demasiado fácil.
        if f == -1:
            self.shoot_cooldown = 14
            projectiles.append(Projectile(self.x - 22, self.y, vx_base, 0, True, 18, "laser", laser_img))
            audio.play('laser')
            return

        if self.level == 1:
            self.shoot_cooldown = 14
            projectiles.append(Projectile(self.x + 22, self.y - 4, vx_base, 0, True, 18, "laser", laser_img))
            projectiles.append(Projectile(self.x + 22, self.y + 4, vx_base, 0, True, 18, "laser", laser_img))
            audio.play('laser')

        elif self.level == 2:
            self.shoot_cooldown = 13
            projectiles.append(Projectile(self.x + 26, self.y - 7, vx_base, -0.9, True, 18, "laser", laser_img))
            projectiles.append(Projectile(self.x + 28, self.y, vx_base * 1.05, 0, True, 22, "laser", laser_img))
            projectiles.append(Projectile(self.x + 26, self.y + 7, vx_base, 0.9, True, 18, "laser", laser_img))
            audio.play('laser')

        elif self.level == 3:
            self.shoot_cooldown = 12
            projectiles.append(Projectile(self.x + 28, self.y - 10, vx_base, -1.2, True, 18, "laser", laser_img))
            projectiles.append(Projectile(self.x + 30, self.y - 3, vx_base * 1.05, 0, True, 20, "laser", laser_img))
            projectiles.append(Projectile(self.x + 30, self.y + 3, vx_base * 1.05, 0, True, 20, "laser", laser_img))
            projectiles.append(Projectile(self.x + 28, self.y + 10, vx_base, 1.2, True, 18, "laser", laser_img))
            audio.play('laser')

        elif self.level >= 4:
            self.shoot_cooldown = 11
            projectiles.append(Projectile(self.x + 28, self.y - 12, vx_base, -1.4, True, 20, "laser", laser_img))
            projectiles.append(Projectile(self.x + 32, self.y - 4, vx_base * 1.1, 0, True, 22, "laser", laser_img))
            projectiles.append(Projectile(self.x + 32, self.y + 4, vx_base * 1.1, 0, True, 22, "laser", laser_img))
            projectiles.append(Projectile(self.x + 28, self.y + 12, vx_base, 1.4, True, 20, "laser", laser_img))
            
            # Bits orbitales disparando hacia adelante
            bx1 = self.x + math.cos(self.orbit_angle) * 45
            by1 = self.y + math.sin(self.orbit_angle) * 45
            bx2 = self.x + math.cos(self.orbit_angle + math.pi) * 45
            by2 = self.y + math.sin(self.orbit_angle + math.pi) * 45
            projectiles.append(Projectile(bx1, by1, vx_base, 0, True, 14, "laser", laser_img))
            projectiles.append(Projectile(bx2, by2, vx_base, 0, True, 14, "laser", laser_img))
            audio.play('laser')

    def fire_mega_beam(self, projectiles, audio, particles):
        self.shoot_cooldown = 30
        beam_img = self.assets.get_image("proj_player_beam.png", (120, 48))
        audio.play('mega_beam')
        f = self.facing
        # Emite el rayo perforante: 7 segmentos calibrados (55 de daño por segmento)
        for offset_x in range(0, 680, 95):
            px = self.x + (60 + offset_x) * f
            p = Projectile(px, self.y, 22.0 * f, 0, True, 55, "beam", beam_img)
            p.lifetime = 16
            projectiles.append(p)
        particles.spawn_sparkle(self.x + 40 * f, self.y, COLOR_PURPLE_LIGHT, 25)

    def add_xp(self, amount, audio, particles):
        self.xp += amount
        if self.level == 1 and self.xp >= self.xp_targets[1]:
            self.level = 2
            self.max_hp = 135
            self.hp = min(self.max_hp, self.hp + 20)
            self.level_up_timer = 120
            audio.play('levelup')
            particles.spawn_sparkle(self.x, self.y, COLOR_GOLD, 30)
        elif self.level == 2 and self.xp >= self.xp_targets[2]:
            self.level = 3
            self.max_hp = 150
            self.hp = min(self.max_hp, self.hp + 20)
            self.level_up_timer = 130
            audio.play('levelup')
            particles.spawn_sparkle(self.x, self.y, COLOR_PURPLE, 35)
        elif self.level == 3 and self.xp >= self.xp_targets[3]:
            self.level = 4
            self.max_hp = 170
            self.hp = min(self.max_hp, self.hp + 25)
            self.level_up_timer = 140
            audio.play('levelup')
            particles.spawn_sparkle(self.x, self.y, COLOR_CYAN, 40)

    def take_damage(self, amount, audio, particles):
        if self.invulnerable_timer > 0:
            return False

        # El daño entra directo a la barra de vida (HP) sin período de inmortalidad
        self.hp -= amount
        self.hit_flash = 6  # Destello visual de impacto, sin otorgar invulnerabilidad
        audio.play('hit')
        particles.spawn_sparkle(self.x, self.y, COLOR_RED, 14)

        if self.hp <= 0:
            self.hp = 0
            audio.play('explosion')
            particles.spawn_explosion(self.x, self.y, 45)
            return True  # Fin del juego (1 sola vida)
        return False

    def draw(self, surf):
        # Resplandor morado de alto contraste
        glow_size = 40 if self.level == 1 else (48 if self.level == 2 else 58)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (190, 80, 255, 75), (glow_size, glow_size), glow_size)
        surf.blit(glow, (int(self.x - glow_size), int(self.y - glow_size)))

        # Cargar sprite según evolución
        if self.level == 1:
            frame_idx = int(self.anim_time) % 4
            spr_name = "player_dash.png" if self.dash_timer > 0 else f"player_idle_{frame_idx}.png"
            img = self.assets.get_image(spr_name, (52, 68))
        elif self.level == 2:
            img = self.assets.get_image("player_lv2.png", (78, 62))
        else:
            img = self.assets.get_image("player_lv3.png", (94, 94))
            bit_img = self.assets.get_image("player_bit_cannon.png", (24, 24))
            bx1 = self.x + math.cos(self.orbit_angle) * 45
            by1 = self.y + math.sin(self.orbit_angle) * 45
            bx2 = self.x + math.cos(self.orbit_angle + math.pi) * 45
            by2 = self.y + math.sin(self.orbit_angle + math.pi) * 45
            surf.blit(bit_img, bit_img.get_rect(center=(int(bx1), int(by1))))
            surf.blit(bit_img, bit_img.get_rect(center=(int(bx2), int(by2))))

        # GIRAR SPRITE HACIA LA IZQUIERDA SI DISPARA HACIA ATRÁS
        if self.facing == -1:
            img = pygame.transform.flip(img, True, False)

        rect = img.get_rect(center=(int(self.x), int(self.y)))

        # Destello de impacto al recibir daño
        if self.hit_flash > 0:
            self.hit_flash -= 1
            flash_surf = img.copy()
            flash_surf.fill((255, 60, 60, 210), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(flash_surf, rect.topleft)
        else:
            surf.blit(img, rect.topleft)

        # Efecto visual de CARGA durante el 1 segundo continuo
        if self.charge_timer > 0:
            pct = min(1.0, self.charge_timer / float(self.charge_max))
            # Anillo de plasma convergente
            ring_radius = max(8, int(46 * (1.0 - pct * 0.6)))
            charge_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            charge_alpha = int(100 + 155 * pct)
            pygame.draw.circle(charge_surf, (0, 240, 255, charge_alpha), (60, 60), ring_radius, 3)
            pygame.draw.circle(charge_surf, (220, 100, 255, int(charge_alpha * 0.7)), (60, 60), int(ring_radius * 0.7), 2)
            surf.blit(charge_surf, (int(self.x - 60), int(self.y - 60)))

            # Mini barra de progreso de carga sobre el dron
            cw, ch = 48, 6
            cx = int(self.x - cw // 2)
            cy = int(self.y - 44)
            pygame.draw.rect(surf, (10, 14, 25), (cx - 2, cy - 2, cw + 4, ch + 4), border_radius=3)
            bar_color = COLOR_GOLD if pct >= 1.0 else COLOR_CYAN
            pygame.draw.rect(surf, bar_color, (cx, cy, int(cw * pct), ch), border_radius=2)
            pygame.draw.rect(surf, COLOR_WHITE, (cx - 2, cy - 2, cw + 4, ch + 4), 1, border_radius=3)

# --- CLASE PRINCIPAL DEL JUEGO CON HUD DE ENERGÍA Y PAUSA ---
class CyberDroneGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Reloj pygame.time.Clock para control de FPS suave y constante (Smooth FPS control)
        self.clock = pygame.time.Clock()
        self.target_fps = FPS
        self.dt = 1.0 / FPS
        
        self.font_title = pygame.font.SysFont("Impact", 54)
        self.font_large = pygame.font.SysFont("Consolas", 42, bold=True)
        self.font_mid = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 16, bold=True)

        self.audio = AudioManager()
        self.assets = AssetLoader()
        self.particles = ParticleManager()
        self.scanlines = self._create_scanlines()

        self.state = "WELCOME"
        self.score = 0
        self.high_score = 50000
        self.current_level = 1
        self.enemies_killed = 0
        self.boss = None

        self.difficulties = DIFFICULTIES
        self.difficulty_index = 0  # Inicia en "VERY EASY" (estado base actual)

        self.pause_selected = 0

        self.bg_scroll_x = 0
        self.bg_scroll_speed = 0.6

        self.projectiles = []
        self.enemies = []
        self.items = []
        self.player = None

        self.spawn_timer = 0
        self.level_timer = 0
        self.level_duration = 1350

        self.ambient_particles = []
        self._init_ambient()

    @property
    def current_difficulty(self):
        return self.difficulties[self.difficulty_index]

    def get_difficulty_config(self):
        return DIFFICULTY_SETTINGS[self.current_difficulty]

    def change_difficulty(self, delta):
        self.difficulty_index = (self.difficulty_index + delta) % len(self.difficulties)
        self.audio.play('menu_beep')

    def get_pause_options(self):
        return [
            "CONTINUAR MISIÓN",
            f"DIFICULTAD: < {self.current_difficulty} >",
            "REINICIAR SECTOR",
            "MENÚ PRINCIPAL",
            "SALIR"
        ]

    def _create_scanlines(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(surf, (0, 0, 0, 40), (0, y), (SCREEN_WIDTH, y), 1)
        return surf

    def _init_ambient(self):
        self.ambient_particles = []
        for _ in range(60):
            self.ambient_particles.append([
                random.uniform(0, SCREEN_WIDTH),
                random.uniform(0, SCREEN_HEIGHT),
                random.uniform(2.5, 5.5),
                random.uniform(0.4, 1.6)
            ])

    def reset_game(self):
        self.player = Player(self.assets)
        self.projectiles.clear()
        self.enemies.clear()
        self.items.clear()
        self.particles.particles.clear()
        self.score = 0
        self.current_level = 1
        self.enemies_killed = 0
        self.spawn_timer = 0
        self.level_timer = 0
        self.boss = None
        self.state = "PLAYING"

    def advance_level(self):
        self.current_level += 1
        self.level_timer = 0
        self.enemies.clear()
        self.projectiles.clear()
        self.boss = None
        
        if self.current_level == 8:
            self.audio.play('boss_alert')
            self.boss = FinalBoss(self.assets, diff_cfg=self.get_difficulty_config())
        self.state = "PLAYING"

    def run(self):
        running = True
        while running:
            keys = pygame.key.get_pressed()
            mouse_pressed = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if self.state == "PLAYING":
                        if event.key in (pygame.K_p, pygame.K_ESCAPE):
                            self.state = "PAUSED"
                            self.pause_selected = 0
                            self.audio.play('menu_select')

                    elif self.state == "PAUSED":
                        opts = self.get_pause_options()
                        if event.key == pygame.K_UP:
                            self.pause_selected = (self.pause_selected - 1) % len(opts)
                            self.audio.play('menu_beep')
                        elif event.key == pygame.K_DOWN:
                            self.pause_selected = (self.pause_selected + 1) % len(opts)
                            self.audio.play('menu_beep')
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if self.pause_selected == 1:
                                self.change_difficulty(-1)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if self.pause_selected == 1:
                                self.change_difficulty(1)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.audio.play('menu_select')
                            self._handle_pause_action()
                        elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                            self.state = "PLAYING"

                    elif self.state == "WELCOME":
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self.change_difficulty(-1)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.change_difficulty(1)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.audio.play('menu_select')
                            self.reset_game()
                        else:
                            self.audio.play('menu_select')
                            self.reset_game()

                    elif self.state in ("GAME_OVER", "VICTORY"):
                        if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                            self.audio.play('menu_select')
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "WELCOME"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "WELCOME":
                        mx, my = event.pos
                        # Clic en flechas del selector o en la tarjeta
                        left_arrow = pygame.Rect(SCREEN_WIDTH // 2 - 330, 465, 56, 46)
                        right_arrow = pygame.Rect(SCREEN_WIDTH // 2 + 274, 465, 56, 46)
                        diff_card = pygame.Rect(SCREEN_WIDTH // 2 - 270, 465, 540, 46)
                        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 270, 615, 540, 50)

                        if left_arrow.collidepoint(mx, my):
                            self.change_difficulty(-1)
                        elif right_arrow.collidepoint(mx, my):
                            self.change_difficulty(1)
                        elif diff_card.collidepoint(mx, my):
                            self.change_difficulty(1)
                        elif start_btn.collidepoint(mx, my):
                            self.audio.play('menu_select')
                            self.reset_game()
                        else:
                            self.audio.play('menu_select')
                            self.reset_game()

                    elif self.state == "PAUSED":
                        mx, my = event.pos
                        opts = self.get_pause_options()
                        for idx in range(len(opts)):
                            rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 260 + idx * 52, 400, 44)
                            if rect.collidepoint(mx, my):
                                self.pause_selected = idx
                                self.audio.play('menu_select')
                                self._handle_pause_action()

            if self.state == "WELCOME":
                self.update_welcome()
                self.draw_welcome()
            elif self.state == "PLAYING":
                self.update_playing(keys, mouse_pressed)
                self.draw_playing()
            elif self.state == "PAUSED":
                self.draw_playing()
                self.draw_pause_menu()
            elif self.state == "LEVEL_CLEAR":
                self.update_level_clear()
                self.draw_playing()
                self.draw_level_clear()
            elif self.state == "GAME_OVER":
                self.draw_playing()
                self.draw_game_over()
            elif self.state == "VICTORY":
                self.draw_playing()
                self.draw_victory()

            self.screen.blit(self.scanlines, (0, 0))
            pygame.display.flip()
            # Control suave de fotogramas por segundo (Smooth FPS Control con pygame.time.Clock)
            self.dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

        pygame.quit()
        sys.exit()

    def _handle_pause_action(self):
        if self.pause_selected == 0:
            self.state = "PLAYING"
        elif self.pause_selected == 1:
            # Alternar dificultad desde el menú de pausa
            self.change_difficulty(1)
        elif self.pause_selected == 2:
            self.level_timer = 0
            self.enemies.clear()
            self.projectiles.clear()
            self.player.hp = self.player.max_hp
            self.player.energy = self.player.max_energy
            self.state = "PLAYING"
        elif self.pause_selected == 3:
            self.state = "WELCOME"
        elif self.pause_selected == 4:
            pygame.quit()
            sys.exit()

    def update_welcome(self):
        self.bg_scroll_x = (self.bg_scroll_x + 0.6) % SCREEN_WIDTH
        self.update_ambient()

    def update_ambient(self):
        for p in self.ambient_particles:
            p[0] -= p[3]
            p[1] += p[2]
            if p[1] > SCREEN_HEIGHT:
                p[1] = 0
                p[0] = random.uniform(0, SCREEN_WIDTH)
            if p[0] < 0:
                p[0] = SCREEN_WIDTH

    def update_playing(self, keys, mouse_pressed):
        self.level_timer += 1
        self.bg_scroll_x = (self.bg_scroll_x + self.bg_scroll_speed)
        self.update_ambient()

        # Actualizar Jugador (Fin si HP llega a 0)
        is_dead = self.player.update(keys, mouse_pressed, self.projectiles, self.audio, self.particles)
        if is_dead:
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = "GAME_OVER"
            return

        for p in self.projectiles:
            p.update()
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Spawning de enemigos exclusivamente aéreos y a ritmo manejable
        self.spawn_aerial_enemies()

        for e in self.enemies:
            e.update(self.player, self.projectiles, self.audio, self.particles)
        self.enemies = [e for e in self.enemies if e.alive]

        if self.boss:
            self.boss.update(self.player, self.projectiles, self.enemies, self.audio, self.particles)
            if not self.boss.alive:
                self.score += int(8000 * self.get_difficulty_config()["score_mult"])
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = "VICTORY"
                return

        for item in self.items:
            item.update(self.player)
            dx = item.x - self.player.x
            dy = item.y - self.player.y
            if math.hypot(dx, dy) < 34:
                item.alive = False
                self.audio.play('item')
                if item.item_type == "canister_blue":
                    # Bote azul: Recarga ENERGÍA (+40 de energía)
                    self.player.energy = min(self.player.max_energy, self.player.energy + 40.0)
                    self.particles.spawn_sparkle(self.player.x, self.player.y, COLOR_CYAN, 12)
                elif item.item_type == "canister_green":
                    # Bote verde: Recarga VIDA (+35 HP)
                    self.player.hp = min(self.player.max_hp, self.player.hp + 35)
                    self.particles.spawn_sparkle(self.player.x, self.player.y, COLOR_GREEN, 12)
                elif item.item_type == "xp_blue":
                    self.player.add_xp(35, self.audio, self.particles)
                    self.score += 50
                elif item.item_type == "xp_purple":
                    self.player.add_xp(90, self.audio, self.particles)
                    self.score += 150
                elif item.item_type == "xp_gold":
                    self.player.add_xp(250, self.audio, self.particles)
                    self.score += 400
                elif item.item_type == "crystal":
                    self.player.add_xp(600, self.audio, self.particles)
                    self.player.energy = min(self.player.max_energy, self.player.energy + 50.0)
                    self.score += 1000
                elif item.item_type == "medkit":
                    self.player.hp = self.player.max_hp
                    self.player.energy = self.player.max_energy
        self.items = [i for i in self.items if i.alive]

        self.particles.update()

        # Colisiones Proyectiles -> Enemigos
        for p in self.projectiles:
            if not p.is_player or not p.alive:
                continue

            if self.boss and self.boss.alive:
                bx1 = self.boss.x - self.boss.width // 2
                bx2 = self.boss.x + self.boss.width // 2
                by1 = self.boss.y - self.boss.height // 2
                by2 = self.boss.y + self.boss.height // 2
                if bx1 <= p.x <= bx2 and by1 <= p.y <= by2:
                    if p.kind == "beam":
                        if id(self.boss) not in p.hit_entities:
                            p.hit_entities.add(id(self.boss))
                            self.boss.take_damage(p.damage, self.audio, self.particles)
                    else:
                        p.alive = False
                        self.boss.take_damage(p.damage, self.audio, self.particles)
                    continue

            for e in self.enemies:
                if not e.alive:
                    continue
                ex1 = e.x - e.width // 2
                ex2 = e.x + e.width // 2
                ey1 = e.y - e.height // 2
                ey2 = e.y + e.height // 2
                if ex1 <= p.x <= ex2 and ey1 <= p.y <= ey2:
                    if p.kind == "beam":
                        if id(e) not in p.hit_entities:
                            p.hit_entities.add(id(e))
                            e.take_damage(p.damage, self.audio, self.particles)
                    else:
                        p.alive = False
                        e.take_damage(p.damage, self.audio, self.particles)

                    if not e.alive:
                        self.score += int(e.points * self.get_difficulty_config()["score_mult"])
                        self.enemies_killed += 1
                        self.drop_loot(e.x, e.y, e.is_boss)
                    if p.kind != "beam":
                        break

        # Colisiones Proyectiles Enemigos -> Jugador
        for p in self.projectiles:
            if p.is_player or not p.alive:
                continue
            dx = p.x - self.player.x
            dy = p.y - self.player.y
            if math.hypot(dx, dy) < 24:
                p.alive = False
                is_dead = self.player.take_damage(p.damage, self.audio, self.particles)
                if is_dead:
                    if self.score > self.high_score: self.high_score = self.score
                    self.state = "GAME_OVER"
                    return

        diff_dmg_m = self.get_difficulty_config()["damage_mult"]

        # Colisión de choque directo con enemigos
        for e in self.enemies:
            if not e.alive:
                continue
            dx = e.x - self.player.x
            dy = e.y - self.player.y
            dist = math.hypot(dx, dy)
            collide_dist = (e.width // 2 + 18)
            if dist < collide_dist:
                is_dead = self.player.take_damage(int(28 * diff_dmg_m), self.audio, self.particles)
                e.take_damage(40, self.audio, self.particles)
                # Rebote físico inmediato para repeler al jugador y evitar solapamiento múltiple
                if dist > 0.1:
                    push_x, push_y = (dx / dist), (dy / dist)
                else:
                    push_x, push_y = 1.0, 0.0
                self.player.x -= push_x * 24
                self.player.y -= push_y * 24
                self.player.vx = -push_x * 5.0
                self.player.vy = -push_y * 5.0
                if is_dead:
                    if self.score > self.high_score: self.high_score = self.score
                    self.state = "GAME_OVER"
                    return

        # Colisión de choque directo con Boss
        if self.boss and self.boss.alive:
            bx1 = self.boss.x - self.boss.width // 2
            bx2 = self.boss.x + self.boss.width // 2
            by1 = self.boss.y - self.boss.height // 2
            by2 = self.boss.y + self.boss.height // 2
            if bx1 <= self.player.x <= bx2 and by1 <= self.player.y <= by2:
                is_dead = self.player.take_damage(int(35 * diff_dmg_m), self.audio, self.particles)
                self.player.x -= 32
                self.player.vx = -6.5
                if is_dead:
                    if self.score > self.high_score: self.high_score = self.score
                    self.state = "GAME_OVER"
                    return

        if self.current_level < 8 and self.level_timer >= self.level_duration and len(self.enemies) == 0:
            self.state = "LEVEL_CLEAR"
            self.level_clear_timer = 160
            self.audio.play('levelup')

    def spawn_aerial_enemies(self):
        self.spawn_timer += 1
        diff = self.get_difficulty_config()

        # Ritmo desacelerado y controlable (SOLO UNIDADES AÉREAS, MÁXIMO 5 EN PANTALLA)
        active_regulars = len([e for e in self.enemies if not getattr(e, 'is_boss', False)])

        if self.current_level == 1:
            rate = 140
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 4:
                self.spawn_timer = 0
                etype = random.choices(["scout_drone", "hover_trooper"], weights=[75, 25])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 40, sy, etype, self.assets, stage=1, diff_cfg=diff))

        elif self.current_level == 2:
            rate = 125
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 5:
                self.spawn_timer = 0
                etype = random.choices(["scout_drone", "hover_trooper"], weights=[50, 50])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 50, sy, etype, self.assets, stage=2, diff_cfg=diff))

        elif self.current_level == 3:
            rate = 115
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 5:
                self.spawn_timer = 0
                etype = random.choices(["hover_trooper", "escort_heli", "scout_drone"], weights=[45, 30, 25])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 50, sy, etype, self.assets, stage=3, diff_cfg=diff))

            if self.level_timer == 750:
                self.audio.play('boss_alert')
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 80, SCREEN_HEIGHT // 2, "flying_mech", self.assets, stage=3, diff_cfg=diff))

        elif self.current_level == 4:
            rate = 110
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 5:
                self.spawn_timer = 0
                etype = random.choices(["hover_trooper_v2", "escort_heli", "scout_drone"], weights=[45, 30, 25])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 50, sy, etype, self.assets, stage=4, diff_cfg=diff))

        elif self.current_level == 5:
            rate = 105
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 5:
                self.spawn_timer = 0
                etype = random.choices(["shield_breacher", "hover_trooper_v2", "escort_heli"], weights=[40, 35, 25])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 50, sy, etype, self.assets, stage=5, diff_cfg=diff))

            if self.level_timer == 750:
                self.audio.play('boss_alert')
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 60, SCREEN_HEIGHT // 2, "major_kira", self.assets, stage=5, diff_cfg=diff))

        elif self.current_level == 6:
            rate = 100
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 5:
                self.spawn_timer = 0
                etype = random.choices(["shield_breacher", "escort_heli", "hover_trooper_v2"], weights=[40, 35, 25])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 50, sy, etype, self.assets, stage=6, diff_cfg=diff))

        elif self.current_level == 7:
            rate = 95
            if self.spawn_timer >= rate and self.level_timer < self.level_duration - 200 and active_regulars < 5:
                self.spawn_timer = 0
                etype = random.choices(["shield_breacher", "hover_trooper_v2", "escort_heli"], weights=[45, 35, 20])[0]
                sy = random.randint(90, SCREEN_HEIGHT - 130)
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 50, sy, etype, self.assets, stage=7, diff_cfg=diff))

            if self.level_timer == 750:
                self.audio.play('boss_alert')
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 70, SCREEN_HEIGHT // 2, "heavy_brute", self.assets, stage=7, diff_cfg=diff))

        elif self.current_level == 8:
            # En la batalla final del Boss, mantener escoltas ocasionales
            if self.spawn_timer >= 260 and active_regulars < 3:
                self.spawn_timer = 0
                sy = random.choice([120, SCREEN_HEIGHT - 140])
                self.enemies.append(AerialEnemy(SCREEN_WIDTH + 40, sy, "scout_drone", self.assets, stage=8, diff_cfg=diff))

    def drop_loot(self, x, y, is_boss=False):
        if is_boss:
            self.items.append(ItemDrop(x, y - 25, "crystal", self.assets))
            self.items.append(ItemDrop(x, y + 25, "xp_gold", self.assets))
            self.items.append(ItemDrop(x - 25, y, "canister_blue", self.assets))
            self.items.append(ItemDrop(x + 25, y, "medkit", self.assets))
            return

        r = random.random()
        # Reparto balanceado: Botes azules (energía), botes verdes (vida) y orbes de experiencia
        if r < 0.28:
            self.items.append(ItemDrop(x, y, "canister_blue", self.assets))   # Bote azul: Recarga Energía
        elif r < 0.52:
            self.items.append(ItemDrop(x, y, "canister_green", self.assets))  # Bote verde: Recarga Vida
        elif r < 0.74:
            self.items.append(ItemDrop(x, y, "xp_blue", self.assets))
        elif r < 0.88:
            self.items.append(ItemDrop(x, y, "xp_purple", self.assets))
        elif r < 0.96:
            self.items.append(ItemDrop(x, y, "xp_gold", self.assets))
        else:
            self.items.append(ItemDrop(x, y, "crystal", self.assets))

    def update_level_clear(self):
        self.level_clear_timer -= 1
        self.particles.update()
        if self.level_clear_timer <= 0:
            self.advance_level()

    def draw_background(self):
        idx = min(len(self.assets.fondos) - 1, self.current_level - 1)
        fondo = self.assets.fondos[idx]
        fw = fondo.get_width()
        
        rel_x = int(self.bg_scroll_x) % fw
        self.screen.blit(fondo, (-rel_x, 0))
        if rel_x > 0:
            self.screen.blit(fondo, (fw - rel_x, 0))

        for p in self.ambient_particles:
            if self.current_level in (1, 6):  # Lluvia intensa (Azoteas / Warzone)
                pygame.draw.line(self.screen, (130, 180, 255, 140), (int(p[0]), int(p[1])), (int(p[0] - p[3]*1.5), int(p[1] + p[2]*2.5)), 1)
            elif self.current_level == 2:      # Bio-esporas verdes flotantes
                pygame.draw.circle(self.screen, (80, 255, 160), (int(p[0]), int(p[1])), 2)
            elif self.current_level in (3, 4):  # Cenizas y chispas industriales
                pygame.draw.circle(self.screen, (255, 160, 60), (int(p[0]), int(p[1])), random.randint(1, 3))
            elif self.current_level == 5:      # Partículas de energía roja
                pygame.draw.circle(self.screen, (255, 80, 80), (int(p[0]), int(p[1])), 2)
            elif self.current_level == 7:      # Descargas estratosféricas blancas
                pygame.draw.circle(self.screen, (240, 240, 255), (int(p[0]), int(p[1])), random.randint(1, 3))
            else:                              # Núcleo Supremo: polvo cian cuántico
                pygame.draw.circle(self.screen, (0, 245, 255), (int(p[0]), int(p[1])), 2)

    def draw_hud(self):
        bar_x, bar_y = 30, 25
        hp_pct = max(0, self.player.hp / self.player.max_hp)
        energy_pct = max(0, self.player.energy / self.player.max_energy)

        # Panel HUD superior izquierdo
        pygame.draw.rect(self.screen, (10, 12, 22), (bar_x - 6, bar_y - 6, 260, 92), border_radius=6)
        pygame.draw.rect(self.screen, COLOR_PURPLE, (bar_x - 6, bar_y - 6, 260, 92), 2, border_radius=6)

        # 1. BARRA DE SALUD (1 SOLA VIDA)
        pygame.draw.rect(self.screen, (40, 20, 25), (bar_x, bar_y, 220, 18), border_radius=4)
        hp_col = COLOR_GREEN if hp_pct > 0.4 else COLOR_RED
        pygame.draw.rect(self.screen, hp_col, (bar_x, bar_y, int(220 * hp_pct), 18), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, 220, 18), 2, border_radius=4)
        hp_txt = self.font_small.render(f"VIDA: {int(self.player.hp)}/{self.player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_txt, (bar_x + 8, bar_y + 1))

        # 2. BARRA DE ENERGÍA (Para el Super-Disparo [E] y Dash)
        pygame.draw.rect(self.screen, (10, 25, 45), (bar_x, bar_y + 24, 220, 14), border_radius=3)
        en_col = COLOR_CYAN if self.player.energy >= 45.0 else (80, 160, 200)
        pygame.draw.rect(self.screen, en_col, (bar_x, bar_y + 24, int(220 * energy_pct), 14), border_radius=3)
        pygame.draw.rect(self.screen, (160, 230, 255), (bar_x, bar_y + 24, 220, 14), 1, border_radius=3)
        
        if self.player.charge_timer > 0:
            ch_pct = int((self.player.charge_timer / float(self.player.charge_max)) * 100)
            en_status = f"CARGANDO {ch_pct}% [E]"
        elif self.player.energy >= 45.0:
            en_status = f"{int(self.player.energy)}% [MANTÉN E 1s]"
        else:
            en_status = f"{int(self.player.energy)}% (BOTE AZUL)"
        en_txt = self.font_small.render(f"ENERGIA: {en_status}", True, COLOR_WHITE)
        self.screen.blit(en_txt, (bar_x + 8, bar_y + 23))

        # 3. BARRA DE EXPERIENCIA (XP)
        xp_next = self.player.xp_targets[self.player.level] if self.player.level < 4 else self.player.xp_targets[-1]
        xp_prev = self.player.xp_targets[self.player.level - 1]
        xp_pct = 1.0 if self.player.level >= 4 else max(0, (self.player.xp - xp_prev) / max(1, (xp_next - xp_prev)))
        
        badge_name = f"badge_lv{self.player.level}.png" if self.player.level < 4 else "badge_lvmax.png"
        badge_img = self.assets.get_image(badge_name, (70, 36))
        self.screen.blit(badge_img, (bar_x, bar_y + 44))

        pygame.draw.rect(self.screen, (25, 12, 40), (bar_x + 78, bar_y + 50, 142, 14), border_radius=3)
        pygame.draw.rect(self.screen, COLOR_PURPLE, (bar_x + 78, bar_y + 50, int(142 * xp_pct), 14), border_radius=3)
        pygame.draw.rect(self.screen, COLOR_PURPLE_LIGHT, (bar_x + 78, bar_y + 50, 142, 14), 1, border_radius=3)
        xp_txt = self.font_small.render("EXP", True, COLOR_WHITE)
        self.screen.blit(xp_txt, (bar_x + 82, bar_y + 48))

        # Botón de Pausa [P]
        pause_badge = self.font_small.render("[P] PAUSA", True, COLOR_GOLD)
        pygame.draw.rect(self.screen, (10, 12, 20), (bar_x, bar_y + 92, 95, 22), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_GOLD, (bar_x, bar_y + 92, 95, 22), 1, border_radius=4)
        self.screen.blit(pause_badge, (bar_x + 8, bar_y + 94))

        # Marcador Score Superior Derecho
        score_panel = pygame.Rect(SCREEN_WIDTH - 300, 20, 275, 84)
        pygame.draw.rect(self.screen, (10, 12, 22), score_panel, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_CYAN, score_panel, 2, border_radius=6)
        
        score_surf = self.font_mid.render(f"SCORE {self.score:06d}", True, COLOR_GOLD)
        self.screen.blit(score_surf, (score_panel.x + 15, score_panel.y + 6))

        stage_names = ["AZOTEAS", "BIO-LAB", "COMPLEJO", "RUINAS", "FORTALEZA", "WARZONE", "ESTRATOSFERA", "BOSS CORE"]
        stg_idx = min(len(stage_names) - 1, max(0, self.current_level - 1))
        stage_surf = self.font_small.render(f"STAGE {self.current_level} - {stage_names[stg_idx]}", True, COLOR_CYAN)
        self.screen.blit(stage_surf, (score_panel.x + 15, score_panel.y + 34))

        diff_cfg = self.get_difficulty_config()
        diff_surf = self.font_small.render(f"DIF: {diff_cfg['name']}", True, diff_cfg["color"])
        self.screen.blit(diff_surf, (score_panel.x + 15, score_panel.y + 56))

        # Indicador de FPS suave controlado por el reloj (Clock FPS Indicator)
        cur_fps = int(self.clock.get_fps())
        fps_str = f"FPS {cur_fps if cur_fps > 0 else FPS}"
        fps_surf = self.font_small.render(fps_str, True, COLOR_GREEN if cur_fps >= 55 or cur_fps == 0 else COLOR_GOLD)
        self.screen.blit(fps_surf, (score_panel.x + 195, score_panel.y + 56))

        if self.player.level_up_timer > 0:
            lvl_banner = self.assets.get_image("ui_level_up.png", (280, 80))
            bx = SCREEN_WIDTH // 2 - 140
            by = 80 + int(math.sin(self.player.level_up_timer * 0.2) * 5)
            self.screen.blit(lvl_banner, (bx, by))

        if self.boss and self.boss.alive:
            bb_w, bb_h = 600, 22
            bb_x = (SCREEN_WIDTH - bb_w) // 2
            bb_y = 30
            pygame.draw.rect(self.screen, (10, 12, 20), (bb_x - 4, bb_y - 24, bb_w + 8, bb_h + 32), border_radius=5)
            boss_pct = max(0, self.boss.hp / self.boss.max_hp)
            bar_c = COLOR_RED if boss_pct < 0.35 else (COLOR_ORANGE if boss_pct < 0.7 else (230, 45, 65))
            pygame.draw.rect(self.screen, bar_c, (bb_x, bb_y, int(bb_w * boss_pct), bb_h), border_radius=4)
            pygame.draw.rect(self.screen, COLOR_WHITE, (bb_x, bb_y, bb_w, bb_h), 2, border_radius=4)

            name_surf = self.font_small.render(f"BOSS: {self.boss.boss_name}", True, COLOR_WHITE)
            self.screen.blit(name_surf, (bb_x + 10, bb_y - 20))

    def draw_playing(self):
        self.draw_background()

        for item in self.items:
            item.draw(self.screen)

        for p in self.projectiles:
            p.draw(self.screen)

        for e in self.enemies:
            e.draw(self.screen)

        if self.boss:
            self.boss.draw(self.screen)

        self.particles.draw(self.screen)

        if self.player and self.player.hp > 0:
            self.player.draw(self.screen)

        self.draw_hud()

    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 18, 205))
        self.screen.blit(overlay, (0, 0))

        opts = self.get_pause_options()
        panel_w, panel_h = 570, 390
        px = (SCREEN_WIDTH - panel_w) // 2
        py = (SCREEN_HEIGHT - panel_h) // 2

        diff_cfg = self.get_difficulty_config()

        pygame.draw.rect(self.screen, (12, 16, 28), (px, py, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PURPLE, (px, py, panel_w, panel_h), 4, border_radius=10)
        pygame.draw.rect(self.screen, diff_cfg["color"], (px + 6, py + 6, panel_w - 12, panel_h - 12), 2, border_radius=8)

        p_title = self.font_large.render("= PAUSA =", True, COLOR_GOLD)
        self.screen.blit(p_title, ((SCREEN_WIDTH - p_title.get_width()) // 2, py + 22))

        for idx, opt_text in enumerate(opts):
            opt_y = py + 84 + idx * 52
            is_sel = (idx == self.pause_selected)

            if is_sel:
                sel_rect = pygame.Rect(px + 30, opt_y - 6, panel_w - 60, 40)
                pygame.draw.rect(self.screen, (45, 20, 75), sel_rect, border_radius=6)
                pygame.draw.rect(self.screen, COLOR_CYAN, sel_rect, 2, border_radius=6)
                col = diff_cfg["color"] if idx == 1 else COLOR_CYAN
                txt_surf = self.font_mid.render(f">> {opt_text}", True, col)
            else:
                col = diff_cfg["color"] if idx == 1 else COLOR_WHITE
                txt_surf = self.font_mid.render(f"   {opt_text}", True, col)

            self.screen.blit(txt_surf, (px + 45, opt_y))

        hint = self.font_small.render("[↑/↓] SELECCIONAR   [←/→] CAMBIAR DIFICULTAD   [ENTER] ACEPTAR", True, (170, 180, 210))
        self.screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, py + panel_h - 36))

    def draw_welcome(self):
        self.draw_background()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 8, 16, 190))
        self.screen.blit(overlay, (0, 0))

        top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 42)
        pygame.draw.rect(self.screen, (10, 14, 25), top_bar)
        pygame.draw.line(self.screen, COLOR_PURPLE, (0, 42), (SCREEN_WIDTH, 42), 2)
        
        t_1up = self.font_small.render(f"1UP  {self.score:06d}", True, COLOR_WHITE)
        t_high = self.font_small.render(f"HIGH SCORE  {self.high_score:06d}", True, COLOR_GOLD)
        t_credit = self.font_small.render("CREDIT  01", True, COLOR_GREEN)
        self.screen.blit(t_1up, (50, 12))
        self.screen.blit(t_high, (SCREEN_WIDTH // 2 - t_high.get_width() // 2, 12))
        self.screen.blit(t_credit, (SCREEN_WIDTH - 180, 12))

        t_ticks = pygame.time.get_ticks() / 1000.0
        title_text = "CYBER DRONE"
        sub_text = "OVERDRIVE: PROTOCOLO PURPURA"

        shadow_t = self.font_title.render(title_text, True, (0, 0, 0))
        main_t = self.font_title.render(title_text, True, COLOR_PURPLE_LIGHT)
        tx = (SCREEN_WIDTH - main_t.get_width()) // 2
        self.screen.blit(shadow_t, (tx + 4, 52))
        self.screen.blit(main_t, (tx, 48))

        sub_surf = self.font_mid.render(sub_text, True, COLOR_CYAN)
        self.screen.blit(sub_surf, ((SCREEN_WIDTH - sub_surf.get_width()) // 2, 110))

        # Preview Drone
        drone_y = 182 + math.sin(t_ticks * 3.0) * 8
        glow_size = 50
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (190, 80, 255, 75), (glow_size, glow_size), glow_size)
        self.screen.blit(glow, (SCREEN_WIDTH // 2 - glow_size, int(drone_y - glow_size + 10)))

        drone_spr = self.assets.get_image("p_idle_0.png", (72, 90))
        self.screen.blit(drone_spr, drone_spr.get_rect(center=(SCREEN_WIDTH // 2, int(drone_y))))

        # Caja de Instrucciones Arcade
        ctrl_box = pygame.Rect(SCREEN_WIDTH // 2 - 380, 235, 760, 192)
        pygame.draw.rect(self.screen, (10, 15, 28), ctrl_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_PURPLE, ctrl_box, 2, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_CYAN, (ctrl_box.x + 4, ctrl_box.y + 4, ctrl_box.w - 8, ctrl_box.h - 8), 1, border_radius=6)

        lines = [
            ("== SISTEMAS DE VUELO Y COMBATE AÉREO ==", COLOR_GOLD),
            ("Moverse y Girar: Flechas [←][→][↑][↓] o [W][A][S][D] (Más ágil y veloz)", COLOR_WHITE),
            ("Disparo Láser:  [ESPACIO] o Clic Izquierdo (Dispara en tu dirección de vuelo)", COLOR_WHITE),
            ("Girar y Atrás:  [A] o [←] para dar media vuelta y disparar hacia atrás", COLOR_CYAN),
            ("Mega Rayo [E]:  Mantén [E] durante 1 segundo para cargarlo (-45 Energía)", COLOR_PURPLE_LIGHT),
            ("Turbo Dash:     [SHIFT] o Clic Derecho para evasión rápida (-20 Energía)", COLOR_CYAN),
            ("Recargas:       Botes AZULES = Energía  |  Botes VERDES = Salud (1 Barra)", COLOR_GREEN),
        ]
        for idx, (txt, col) in enumerate(lines):
            s = self.font_small.render(txt, True, col)
            self.screen.blit(s, (ctrl_box.x + 22, ctrl_box.y + 10 + idx * 25))

        # --- SELECTOR DE DIFICULTAD INTERACTIVO ---
        diff_cfg = self.get_difficulty_config()
        diff_box = pygame.Rect(SCREEN_WIDTH // 2 - 380, 438, 760, 162)
        pygame.draw.rect(self.screen, (12, 14, 26), diff_box, border_radius=8)
        pygame.draw.rect(self.screen, diff_cfg["color"], diff_box, 3, border_radius=8)

        # Botones de navegación con flechas vectoriales poligonales nítidas
        left_btn = pygame.Rect(diff_box.x + 16, diff_box.y + 12, 54, 40)
        right_btn = pygame.Rect(diff_box.right - 70, diff_box.y + 12, 54, 40)
        pygame.draw.rect(self.screen, (30, 20, 50), left_btn, border_radius=6)
        pygame.draw.rect(self.screen, diff_cfg["color"], left_btn, 2, border_radius=6)
        pygame.draw.rect(self.screen, (30, 20, 50), right_btn, border_radius=6)
        pygame.draw.rect(self.screen, diff_cfg["color"], right_btn, 2, border_radius=6)

        # Flecha izquierda vectorial
        pts_left = [
            (left_btn.centerx + 8, left_btn.centery - 10),
            (left_btn.centerx - 10, left_btn.centery),
            (left_btn.centerx + 8, left_btn.centery + 10)
        ]
        pygame.draw.polygon(self.screen, diff_cfg["color"], pts_left)

        # Flecha derecha vectorial
        pts_right = [
            (right_btn.centerx - 8, right_btn.centery - 10),
            (right_btn.centerx + 10, right_btn.centery),
            (right_btn.centerx - 8, right_btn.centery + 10)
        ]
        pygame.draw.polygon(self.screen, diff_cfg["color"], pts_right)

        diff_title = self.font_large.render(f"[ {diff_cfg['name']} ]", True, diff_cfg["color"])
        self.screen.blit(diff_title, diff_title.get_rect(center=(SCREEN_WIDTH // 2, diff_box.y + 32)))

        # Multiplicadores de Dificultad
        cad_txt = f"x{(1.0/diff_cfg['shoot_cooldown_mult']):.2f}"
        stats_line = (
            f"VEL MOV: x{diff_cfg['move_speed_mult']:.2f}   "
            f"VEL BALA: x{diff_cfg['bullet_speed_mult']:.2f}   "
            f"CADENCIA: {cad_txt}   "
            f"SALUD: x{diff_cfg['hp_mult']:.2f}   "
            f"DAÑO: x{diff_cfg['damage_mult']:.2f}"
        )
        stats_surf = self.font_small.render(stats_line, True, COLOR_GOLD)
        self.screen.blit(stats_surf, stats_surf.get_rect(center=(SCREEN_WIDTH // 2, diff_box.y + 73)))

        # Descripción y Puntuación
        desc_surf = self.font_small.render(diff_cfg["description"], True, COLOR_WHITE)
        self.screen.blit(desc_surf, desc_surf.get_rect(center=(SCREEN_WIDTH // 2, diff_box.y + 100)))

        hint_nav = self.font_small.render(f"[←]/[→] o [A]/[D] CAMBIAR DIFICULTAD   |   BONIFICADOR SCORE: x{diff_cfg['score_mult']:.2f}", True, diff_cfg["color"])
        self.screen.blit(hint_nav, hint_nav.get_rect(center=(SCREEN_WIDTH // 2, diff_box.y + 130)))

        # Prompt de Inicio de Misión
        if int(t_ticks * 2.5) % 2 == 0:
            prompt_btn = pygame.Rect(SCREEN_WIDTH // 2 - 280, 615, 560, 48)
            pygame.draw.rect(self.screen, (10, 16, 28), prompt_btn, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_GOLD, prompt_btn, 2, border_radius=8)
            prompt_txt = self.font_mid.render(f">> INICIAR MISIÓN [{diff_cfg['name']}] <<", True, COLOR_GOLD)
            self.screen.blit(prompt_txt, prompt_txt.get_rect(center=prompt_btn.center))

    def draw_level_clear(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 14, 28, 170))
        self.screen.blit(overlay, (0, 0))

        clear_banner = self.assets.get_image("ui_stage_clear.png", (360, 140))
        cx = (SCREEN_WIDTH - 360) // 2
        cy = (SCREEN_HEIGHT - 140) // 2 - 50
        self.screen.blit(clear_banner, (cx, cy))

        txt = self.font_mid.render(f"¡SECTOR {self.current_level} ASEGURADO!", True, COLOR_CYAN)
        sub = self.font_small.render("Iniciando salto hiperespacial al siguiente nivel...", True, COLOR_WHITE)
        self.screen.blit(txt, ((SCREEN_WIDTH - txt.get_width()) // 2, cy + 160))
        self.screen.blit(sub, ((SCREEN_WIDTH - sub.get_width()) // 2, cy + 200))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((28, 6, 12, 215))
        self.screen.blit(overlay, (0, 0))

        t = self.font_large.render("M I S I Ó N   F A L L I D A", True, COLOR_RED)
        self.screen.blit(t, ((SCREEN_WIDTH - t.get_width()) // 2, 160))

        diff_cfg = self.get_difficulty_config()
        res_rect = pygame.Rect(SCREEN_WIDTH // 2 - 260, 225, 520, 215)
        pygame.draw.rect(self.screen, (15, 10, 18), res_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_RED, res_rect, 2, border_radius=8)

        s0 = self.font_small.render(f"DIFICULTAD JUGADA: {diff_cfg['name']}", True, diff_cfg["color"])
        s1 = self.font_mid.render(f"PUNTUACIÓN: {self.score:06d} (x{diff_cfg['score_mult']:.2f})", True, COLOR_GOLD)
        s2 = self.font_mid.render(f"RÉCORD:     {self.high_score:06d}", True, COLOR_WHITE)
        s3 = self.font_small.render(f"Enemigos aéreos destruidos: {self.enemies_killed}", True, COLOR_CYAN)
        s4 = self.font_small.render(f"Sector alcanzado:          NIVEL {self.current_level}", True, COLOR_PURPLE_LIGHT)
        
        self.screen.blit(s0, (res_rect.x + 35, res_rect.y + 18))
        self.screen.blit(s1, (res_rect.x + 35, res_rect.y + 46))
        self.screen.blit(s2, (res_rect.x + 35, res_rect.y + 86))
        self.screen.blit(s3, (res_rect.x + 35, res_rect.y + 126))
        self.screen.blit(s4, (res_rect.x + 35, res_rect.y + 158))

        prompt1 = self.font_mid.render("[R] o [ENTER] - REINTENTAR MISIÓN", True, COLOR_GREEN)
        prompt2 = self.font_small.render("[ESC] - REGRESAR AL MENÚ PRINCIPAL", True, (180, 180, 180))
        self.screen.blit(prompt1, ((SCREEN_WIDTH - prompt1.get_width()) // 2, 475))
        self.screen.blit(prompt2, ((SCREEN_WIDTH - prompt2.get_width()) // 2, 525))

    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 20, 35, 215))
        self.screen.blit(overlay, (0, 0))

        t = self.font_large.render("¡V I C T O R I A   A B S O L U T A!", True, COLOR_GOLD)
        sub = self.font_mid.render("EL TITAN GUNSHIP HA SIDO ELIMINADO", True, COLOR_CYAN)
        self.screen.blit(t, ((SCREEN_WIDTH - t.get_width()) // 2, 130))
        self.screen.blit(sub, ((SCREEN_WIDTH - sub.get_width()) // 2, 195))

        diff_cfg = self.get_difficulty_config()
        d_surf = self.font_mid.render(f"SUPERADO EN DIFICULTAD: {diff_cfg['name']}", True, diff_cfg["color"])
        self.screen.blit(d_surf, ((SCREEN_WIDTH - d_surf.get_width()) // 2, 235))

        res_rect = pygame.Rect(SCREEN_WIDTH // 2 - 270, 275, 540, 160)
        pygame.draw.rect(self.screen, (10, 18, 30), res_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_GOLD, res_rect, 2, border_radius=8)

        s1 = self.font_mid.render(f"PUNTUACIÓN FINAL: {self.score:06d} (x{diff_cfg['score_mult']:.2f})", True, COLOR_WHITE)
        s2 = self.font_small.render(f"Evolución máxima del Drone lograda (Lv.3)", True, COLOR_PURPLE_LIGHT)
        s3 = self.font_small.render(f"Total de enemigos destruidos: {self.enemies_killed}", True, COLOR_GREEN)
        self.screen.blit(s1, (res_rect.x + 40, res_rect.y + 25))
        self.screen.blit(s2, (res_rect.x + 40, res_rect.y + 70))
        self.screen.blit(s3, (res_rect.x + 40, res_rect.y + 105))

        prompt1 = self.font_mid.render("[R] o [ENTER] - VOLVER A JUGAR", True, COLOR_GREEN)
        prompt2 = self.font_small.render("[ESC] - SALIR AL MENÚ", True, (180, 180, 180))
        self.screen.blit(prompt1, ((SCREEN_WIDTH - prompt1.get_width()) // 2, 470))
        self.screen.blit(prompt2, ((SCREEN_WIDTH - prompt2.get_width()) // 2, 520))

if __name__ == "__main__":
    game = CyberDroneGame()
    game.run()
