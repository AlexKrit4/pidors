import pygame
import random
import sys
import time
import asyncio
import platform
import os
import math
from collections import deque
import heapq
import json
import sqlite3
import hashlib
from datetime import datetime
from md_viewer import open_markdown


# Настройки экрана
CELL_SIZE = 70
GRID_ROWS = 7
GRID_COLS = 6
WIDTH = CELL_SIZE * GRID_COLS
HEIGHT = CELL_SIZE * GRID_ROWS
INFO_PANEL_HEIGHT = 150
FPS = 240  # Общий FPS для игры
ANIMATION_FPS = 240  # FPS для анимаций
IMAGE_SCALE = 2.6  # Масштаб символов
FADE_OUT_DURATION = 0.5  # Длительность исчезновения кнопок
FADE_IN_DURATION = 0.1  # Длительность появления кнопок
BIG_WIN_FADE_OUT = 0.5  # Длительность исчезновения фона Big Win

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 80)
BORDER = (0)
GOLD = (255, 215, 0)
TRANSPARENT = (0, 0, 0, 0)
HIGHLIGHT_COLOR = (255, 0, 0)  # Красный для подсветки
SETTINGS_BG = (50, 50, 50, 200)  # Полупрозрачный фон настроек
BIG_WIN_BG = (50, 50, 50, 200)  # Полупрозрачный фон Big Win

# Направления для поиска пути
directions = [(0, 1), (-1, 0), (0, -1), (1, 0)]

# Символы для слота
symbols = [
    'low1_1', 'low2_1', 'low3_1', 'low4_1',  # Кристаллы 1 уровня
    'low1_2', 'low2_2', 'low3_2', 'low4_2',  # Кристаллы 2 уровня
    'low1_3', 'low2_3', 'low3_3', 'low4_3',  # Кристаллы 3 уровня
    'low1_4', 'low2_4', 'low3_4', 'low4_4',  # Кристаллы 4 уровня
    'low1_5', 'low2_5', 'low3_5', 'low4_5',  # Кристаллы 5 уровня
    'low1_6', 'low2_6', 'low3_6', 'low4_6',  # Кристаллы 6 уровня
    'low1_7', 'low2_7', 'low3_7', 'low4_7',  # Кристаллы 7 уровня
    'high1', 'high2', 'high3', 'high4',      # Попугаи для сетки
    'high1win', 'high2win', 'high3win', 'high4win',  # Попугаи для Big Win
    'levelup', 'levelup_2', 'levelup_3',     # Улучшения одного цвета
    'levelupall', 'levelupall_2', 'levelupall_3',  # Улучшения всех цветов
    'coin2', 'coin5', 'coin10', 'coin25', 'coin50', 'coin100', 'coin500', 'coin1000', 'coin2500', 'coinmaxwin',  # Мешки с деньгами
    'rum',  # Ром
    'bonus',  # Символ бонуса
    'superbonus',  # Символ супербонуса
    'key'  # Ключ для вызова бандита
]
all_symbols = symbols + ['bandit']  # Добавляем бандита отдельно

# Вероятности выпадения символов (в процентах)
symbol_probabilities = {
    'levelup': 0.715,
    'levelup_2': 0.220,
    'levelup_3': 0.095,
    'levelupall': 0.200,
    'levelupall_2': 0.100,
    'levelupall_3': 0.033,
    'coin2': 0.100,
    'coin5': 0.050,
    'coin10': 0.024,
    'coin25': 0.012,
    'coin50': 0.006,
    'coin100': 0.003,
    'coin500': 0.001,
    'coin1000': 0.0003,
    'coin2500': 0.0001,
    'coinmaxwin': 0.00003,
    'rum': 0.700,
    'low1': 19.5365,
    'low2': 20.5365,
    'low3': 20.5365,
    'low4': 21.5365,
    'bonus': 2.0,  # Шанс появления символа бонуса (увеличен в 2.5 раза)
    'superbonus': 0,  # Убран с барабанов, можно получить только через gamble
    'key': 0.05  # Шанс появления ключа
}

# Таблица выплат
payout_table = {
    'low1': {1: 0.665, 2: 1.6625, 3: 3.325, 4: 4.9875, 5: 16.625, 6: 49.875, 7: 199.5},  # Красный
    'low2': {1: 0.665, 2: 1.33, 3: 2.66, 4: 3.99, 5: 10.64, 6: 33.25, 7: 99.75},     # Фиолетовый
    'low3': {1: 0.3325, 2: 0.9975, 3: 1.995, 4: 2.9925, 5: 7.98, 6: 23.94, 7: 66.5},  # Зеленый
    'low4': {1: 0.3325, 2: 0.665, 3: 1.33, 4: 1.995, 5: 5.32, 6: 16.625, 7: 49.875}   # Синий
}

# Множители для мешков с деньгами
coin_multipliers = {
    'coin2': 2, 'coin5': 5, 'coin10': 10, 'coin25': 25, 'coin50': 50,
    'coin100': 100, 'coin500': 500, 'coin1000': 1000, 'coin2500': 2500, 'coinmaxwin': 200000
}
COIN_SYMBOLS = list(coin_multipliers.keys())
UPGRADE_SYMBOLS = ['levelup', 'levelup_2', 'levelup_3', 'levelupall', 'levelupall_2', 'levelupall_3']
BANDIT_EXTRA_SYMBOLS = set(COIN_SYMBOLS + UPGRADE_SYMBOLS + ['rum', 'bonus', 'superbonus'])

# Уровни кристаллов для каждого цвета
crystal_levels = {'low1': 1, 'low2': 1, 'low3': 1, 'low4': 1}

# Загрузка изображений для символов
symbol_images = {}
for symbol in all_symbols:
    image_path = os.path.join('images', f'{symbol}.png')
    try:
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (int(CELL_SIZE * IMAGE_SCALE), int(CELL_SIZE * IMAGE_SCALE)))
        symbol_images[symbol] = image
    except pygame.error:
        color_map = {
            'low1_1': (255, 0, 0), 'low1_2': (255, 50, 50), 'low1_3': (255, 100, 100), 'low1_4': (255, 150, 150),
            'low1_5': (255, 180, 180), 'low1_6': (255, 200, 200), 'low1_7': (255, 220, 220),
            'low2_1': (128, 0, 128), 'low2_2': (150, 0, 150), 'low2_3': (170, 0, 170), 'low2_4': (190, 0, 190),
            'low2_5': (200, 0, 200), 'low2_6': (210, 0, 210), 'low2_7': (220, 0, 220),
            'low3_1': (0, 255, 0), 'low3_2': (50, 255, 50), 'low3_3': (100, 255, 100), 'low3_4': (150, 255, 150),
            'low3_5': (180, 255, 180), 'low3_6': (200, 255, 200), 'low3_7': (220, 255, 220),
            'low4_1': (0, 0, 255), 'low4_2': (50, 50, 255), 'low4_3': (100, 100, 255), 'low4_4': (150, 150, 255),
            'low4_5': (180, 180, 255), 'low4_6': (200, 200, 255), 'low4_7': (220, 220, 255),
            'high1': (255, 0, 0), 'high2': (128, 0, 128), 'high3': (0, 255, 0), 'high4': (0, 0, 255),
            'high1win': (255, 0, 0), 'high2win': (128, 0, 128), 'high3win': (0, 255, 0), 'high4win': (0, 0, 255),
            'levelup': (255, 255, 0), 'levelup_2': (255, 255, 100), 'levelup_3': (255, 255, 200),
            'levelupall': (255, 200, 0), 'levelupall_2': (255, 200, 100), 'levelupall_3': (255, 200, 200),
            'coin2': (200, 200, 0), 'coin5': (200, 200, 50), 'coin10': (200, 200, 100), 'coin25': (200, 200, 150),
            'coin50': (200, 200, 200), 'coin100': (220, 220, 0), 'coin500': (220, 220, 50), 'coin1000': (220, 220, 100),
            'coin2500': (220, 220, 150), 'coinmaxwin': (255, 255, 255),
            'rum': (139, 69, 19),
            'bandit': (100, 100, 100),  # Серый для бандита
            'superbonus': (255, 0, 255),  # Ярко-розовый для супербонуса
            'key': (255, 215, 0)  # Золотой для ключа
        }
        placeholder = pygame.Surface((int(CELL_SIZE * IMAGE_SCALE), int(CELL_SIZE * IMAGE_SCALE)), pygame.SRCALPHA)
        placeholder.fill(color_map.get(symbol, (100, 100, 100)))
        symbol_images[symbol] = placeholder

# Загрузка фонового изображения
try:
    background_image = pygame.image.load(os.path.join('images', 'Pirots3_BaseBg.jpg'))
except pygame.error:
    background_image = pygame.Surface((WIDTH, HEIGHT + INFO_PANEL_HEIGHT))
    background_image.fill(GRAY)

# Глобальная переменная для масштабированного фона
scaled_background = None

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
pygame.display.set_caption("Игра 3 в ряд 2")
clock = pygame.time.Clock()
font = pygame.font.SysFont("serif", 36)
small_font = pygame.font.SysFont("serif", 24)

balance = 100000
base_bet = 50
bet = base_bet
is_bet_plus = False
is_bet_plus_plus = False
is_bandit_mode = False
is_super_spin = False
is_garant_spin = False
is_3_lvl = False
is_bonus_game = False  # Add this line
settings_open = False
bet_selector_open = False  # Новая переменная для окна выбора ставки
selected_bet = None  # Выбранная ставка в окне
volume = 5
fast_spin = True
button_opacity = 255
info_opacity = 255
last_win = 0
hide_last_win_info = False
maxwin_triggered = False
maxwin_abort_cycle = False
is_spinning = False
super_spin_text_timer = 0
fs_price = base_bet * 54
super_bonus_price = base_bet * 160
dance_sound = None  # Для управления воспроизведением dance.ogg
bandit_active = False
bandit_pos = None  # Позиция бандита на сетке
bandit_lair_pos = (WIDTH + 10, HEIGHT // 3)  # Логово бандита справа от сетки
bandit_counter = 0
duel_count = 0
bandit_key_alpha = 0
# Шансы исхода дуэли (вероятность, что бандит выиграет). Индекс = номер дуэли (0,1,2...)
bandit_duel_chances = [0, 0, 0, 0]
dead_parrots = []  # Попугаи, убитые бандитом и ожидающие возрождения
collected_keys = 0  # Количество собранных ключей для вызова бандита
key_was_collected = False  # Флаг, что ключ уже был собран (ключ может выпасть только раз)
bandit_was_caught = False  # Флаг, что бандит был пойман (проиграл дуэль)
collected_bonus_this_spin = 0  # Количество собранных бонусов за текущий спин
collected_superbonus_this_spin = 0  # Количество собранных супербонусов за текущий спин
collected_key_this_spin = 0  # Количество собранных ключей за текущий спин
# Добавляем новую глобальную переменную для отслеживания уровня счетчика
total_crystals_collected = 0  # Общее количество собранных кристаллов
filled_counters = 0  # Количество заполненных счетчиков
current_counter_level = 0  # Текущий уровень счетчика (индекс в crystal_counter_goals)
crystal_counter_goals = [15, 20, 25, 30, 35, 40]  # Цели для заполнения счетчиков (15, 20, 30, затем 40)
bonus_sound = None
is_buy_fs = False
is_buy_fs_300 = False
is_buy_fs_900 = False
is_buy_fs_3600 = False
is_buy_fs_18000 = False
is_40_40_20 = False
last_free_buy_fs = False
superbonus_count = 0
num_parrots = 1  # Количество попугаев на поле (1 в обычном режиме, варьируется в бонусе)
active_parrots = ['high1']  # Какие попугаи сейчас активны
bonus_game_parrots = 1  # Сколько попугаев в бонусной игре
gamble_lost = False  # Проиграл ли gamble (уменьшает спины на 5)
force_super_gamble_then_collect = False  # Спец-режим gamble для FS 18000x
is_superbonus_game = False
total_bonus_win = 0  # Общий выигрыш за текущую бонусную/супербонусную игру
current_bonus_spin = 0  # Текущий спин в бонусной/супербонусной игре (начиная с 1)
super_spin_price = base_bet * 7.5   # будет пересчитываться при изменении base_bet
is_god_mode_bet = False  # Модификатор ставки God Mode (2000x)
is_god_mod = False  # Глобальный режим God Mod
is_buy_super = False  # Заглушка для обратной совместимости
is_75_25 = False  # Заглушка для обратной совместимости


def set_single_modifier(mod):
    """Включает только указанный модификатор ставок, выключая все остальные.
    Передать None чтобы выключить все модификаторы."""
    global is_bet_plus, is_bet_plus_plus, is_buy_fs, is_buy_fs_300, is_buy_fs_900, is_buy_fs_3600, is_buy_fs_18000, is_40_40_20, is_garant_spin, is_3_lvl, is_bandit_mode, is_super_spin, is_god_mode_bet
    is_bet_plus = is_bet_plus_plus = is_buy_fs = is_buy_fs_300 = is_buy_fs_900 = is_buy_fs_3600 = is_buy_fs_18000 = is_40_40_20 = is_garant_spin = is_3_lvl = is_bandit_mode = is_super_spin = is_god_mode_bet = False
    if mod == 'bet+':
        is_bet_plus = True
    elif mod == 'bet++':
        is_bet_plus_plus = True
    elif mod == 'buy_fs':
        is_buy_fs = True
    elif mod == 'buy_fs_300':
        is_buy_fs_300 = True
    elif mod == 'buy_fs_900':
        is_buy_fs_900 = True
    elif mod == 'buy_fs_3600':
        is_buy_fs_3600 = True
    elif mod == 'buy_fs_18000':
        is_buy_fs_18000 = True
    elif mod == '40_40_20':
        is_40_40_20 = True
    elif mod == 'garant':
        is_garant_spin = True
    elif mod == '3lvl':
        is_3_lvl = True
    elif mod == 'bandit':
        is_bandit_mode = True
    elif mod == 'super_spin':
        is_super_spin = True
    elif mod == 'god_mode':
        is_god_mode_bet = True


def toggle_modifier(mod):
    """Переключает указанный модификатор; если он был включён — выключает все модификаторы."""
    global is_bet_plus, is_bet_plus_plus, is_buy_fs, is_buy_fs_300, is_buy_fs_900, is_buy_fs_3600, is_buy_fs_18000, is_40_40_20, is_garant_spin, is_3_lvl, is_bandit_mode, is_super_spin, is_god_mode_bet
    current = False
    if mod == 'bet+':
        current = is_bet_plus
    elif mod == 'bet++':
        current = is_bet_plus_plus
    elif mod == 'buy_fs':
        current = is_buy_fs
    elif mod == 'buy_fs_300':
        current = is_buy_fs_300
    elif mod == 'buy_fs_900':
        current = is_buy_fs_900
    elif mod == 'buy_fs_3600':
        current = is_buy_fs_3600
    elif mod == 'buy_fs_18000':
        current = is_buy_fs_18000
    elif mod == '40_40_20':
        current = is_40_40_20
    elif mod == 'garant':
        current = is_garant_spin
    elif mod == '3lvl':
        current = is_3_lvl
    elif mod == 'bandit':
        current = is_bandit_mode
    elif mod == 'super_spin':
        current = is_super_spin
    elif mod == 'god_mode':
        current = is_god_mode_bet

    if current:
        set_single_modifier(None)
    else:
        set_single_modifier(mod)


# Модифицируем вероятности для не-кристаллов (без изменений)
non_crystal_symbols = [
    'levelup', 'levelup_2', 'levelup_3',
    'levelupall', 'levelupall_2', 'levelupall_3',
    'coin2', 'coin5', 'coin10', 'coin25', 'coin50', 'coin100', 'coin500', 'coin1000', 'coin2500', 'coinmaxwin',
    'rum'  # Добавляем бонус
]
non_crystal_probabilities = {
    sym: prob for sym, prob in symbol_probabilities.items() if sym in non_crystal_symbols
}
total_prob = sum(non_crystal_probabilities.values())
non_crystal_probabilities = {sym: prob / total_prob * 100 for sym, prob in non_crystal_probabilities.items()}

def show_admin_panel(window_width, window_height):
    """Админ-панель: просмотр пользователей, выдача баланса, God Mod."""
    global is_god_mod, balance, current_user
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, balance FROM users ORDER BY username')
    users = cursor.fetchall()
    conn.close()

    admin_open = True
    input_boxes = {}
    scroll_offset = 0
    button_height = 50
    max_visible = (window_height // 2) // button_height - 2

    # Создаём текстовые поля для каждого пользователя
    for username, bal in users:
        input_boxes[username] = ""

    while admin_open:
        screen.blit(scaled_background, (0, 0))
        panel_rect = pygame.Rect(window_width // 4, window_height // 6, window_width // 2, window_height * 2 // 3)
        pygame.draw.rect(screen, SETTINGS_BG, panel_rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, panel_rect, 3)

        # Заголовок
        title = font.render("АДМИН ПАНЕЛЬ", True, GOLD)
        screen.blit(title, (panel_rect.x + (panel_rect.width - title.get_width()) // 2, panel_rect.y + 15))

        # Кнопка God Mod
        god_mod_btn = pygame.Rect(panel_rect.x + 20, panel_rect.y + 60, 200, 40)
        pygame.draw.rect(screen, (0, 200, 0) if is_god_mod else (100, 100, 100), god_mod_btn, border_radius=8)
        screen.blit(small_font.render(f"God Mod: {'ON' if is_god_mod else 'OFF'}", True, WHITE), god_mod_btn.move(10, 10))

        # Кнопка закрытия
        close_btn = pygame.Rect(panel_rect.right - 60, panel_rect.top + 10, 50, 40)
        pygame.draw.rect(screen, (200, 0, 0), close_btn, border_radius=8)
        screen.blit(small_font.render("X", True, WHITE), close_btn.move(18, 10))

        # Список пользователей
        visible_users = users[scroll_offset:scroll_offset + max_visible]
        user_buttons = []
        for i, (username, bal) in enumerate(visible_users):
            y = panel_rect.y + 110 + i * button_height
            user_rect = pygame.Rect(panel_rect.x + 20, y, panel_rect.width - 40, button_height - 5)

            # Фон пользователя
            pygame.draw.rect(screen, (60, 60, 80), user_rect, border_radius=8)

            # Имя и баланс
            screen.blit(small_font.render(f"{username}: {bal:.2f} У.Е.", True, WHITE), (user_rect.x + 10, user_rect.y + 5))

            # Поле ввода
            input_text = input_boxes[username]
            input_rect = pygame.Rect(user_rect.x + 10, user_rect.y + 25, 100, 25)
            pygame.draw.rect(screen, WHITE, input_rect, border_radius=5)
            screen.blit(small_font.render(input_text, True, BLACK), (input_rect.x + 5, input_rect.y + 5))

            # Кнопка "Выдать"
            give_btn = pygame.Rect(user_rect.x + 120, user_rect.y + 25, 80, 25)
            pygame.draw.rect(screen, (0, 180, 0), give_btn, border_radius=5)
            screen.blit(small_font.render("Выдать", True, WHITE), give_btn.move(10, 5))

            user_buttons.append((username, input_rect, give_btn))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if close_btn.collidepoint(mx, my):
                    play_sound('button')
                    admin_open = False
                elif god_mod_btn.collidepoint(mx, my):
                    play_sound('button')
                    is_god_mod = not is_god_mod
                    # Применяем множитель к мешкам
                    update_coin_probabilities()
                else:
                    for username, input_rect, give_btn in user_buttons:
                        if input_rect.collidepoint(mx, my):
                            # Активируем ввод в это поле
                            for u in input_boxes:
                                input_boxes[u] = ""
                            input_boxes[username] = ""
                            active_input = username
                        elif give_btn.collidepoint(mx, my):
                            amount_str = input_boxes[username].strip()
                            if amount_str.replace('.', '').isdigit():
                                amount = float(amount_str)
                                conn = sqlite3.connect('users.db')
                                cursor = conn.cursor()
                                cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, username))
                                conn.commit()
                                conn.close()
                                # Обновляем локальный баланс, если это текущий игрок
                                if username == current_user:
                                    balance += amount
                                play_sound('button')
                                # Перезагружаем список
                                return show_admin_panel(window_width, window_height)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(scroll_offset - event.y * 3, len(users) - max_visible))
            elif event.type == pygame.KEYDOWN and 'active_input' in locals():
                if event.key == pygame.K_RETURN:
                    del active_input
                elif event.key == pygame.K_BACKSPACE:
                    input_boxes[active_input] = input_boxes[active_input][:-1]
                else:
                    input_boxes[active_input] += event.unicode

    return

def update_coin_probabilities():
    """Обновляет вероятности выпадения мешков в зависимости от God Mod."""
    global symbol_probabilities
    coin_keys = ['coin2', 'coin5', 'coin10', 'coin25', 'coin50', 'coin100', 'coin500', 'coin1000', 'coin2500', 'coinmaxwin']
    
    if is_god_mod:
        # Увеличиваем шансы на мешки в 66 раз
        for key in coin_keys:
            if key in symbol_probabilities:
                symbol_probabilities[key] *= 66
    else:
        # Восстанавливаем исходные значения (нужно сохранить оригиналы при старте)
        original_probs = {
            'coin2': 0.177, 'coin5': 0.138, 'coin10': 0.069, 'coin25': 0.055,
            'coin50': 0.018, 'coin100': 0.004, 'coin500': 0.001, 'coin1000': 0.0005,
            'coin2500': 0.0002, 'coinmaxwin': 0.0001
        }
        for key, prob in original_probs.items():
            symbol_probabilities[key] = prob

    # Нормализуем вероятности (если нужно — но в игре они и так в %)
    total = sum(symbol_probabilities.values())
    if total > 100:
        factor = 100 / total
        for key in symbol_probabilities:
            symbol_probabilities[key] *= factor

def get_random_non_crystal_symbol():
    """Возвращает случайный символ (не кристалл) с учетом вероятностей."""
    rand = random.uniform(0, 100)
    cumulative = 0
    for symbol, prob in non_crystal_probabilities.items():
        cumulative += prob
        if rand <= cumulative:
            return symbol
    return random.choice(non_crystal_symbols)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 5000.0,
            total_bet REAL DEFAULT 0,
            total_win REAL DEFAULT 0,
            bonus_games INTEGER DEFAULT 0
        )
    ''')
    # Добавляем столбцы, если их нет
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN total_bet REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN total_win REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN bonus_games INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute('INSERT INTO users (username, password_hash, balance) VALUES (?, ?, 5000.0)', (username, password_hash))
        conn.commit()
        return True  # Успешная регистрация
    except sqlite3.IntegrityError:
        return False  # Логин уже существует
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute('SELECT balance FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_stats(username, bet_amount=0, win_amount=0, bonus_inc=0):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET 
            total_bet = total_bet + ?, 
            total_win = total_win + ?, 
            bonus_games = bonus_games + ?
        WHERE username = ?
    ''', (bet_amount, win_amount, bonus_inc, username))
    conn.commit()
    conn.close()

def update_balance(username, new_balance):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE username = ?', (new_balance, username))
    conn.commit()
    conn.close()

def show_login_screen(window_width, window_height):
    global screen, font, small_font, scaled_background
    username = ""
    password = ""
    active_field = "username"  # Активное поле ввода
    error_message = ""
    is_register = False  # Режим регистрации или входа

    while True:
        screen.blit(scaled_background, (0, 0))
        
        # Фон для формы
        form_rect = pygame.Rect(window_width // 2 - 200, window_height // 2 - 150, 400, 300)
        pygame.draw.rect(screen, SETTINGS_BG, form_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, form_rect, 2)
        
        # Заголовок
        title = font.render("Регистрация" if is_register else "Вход", True, WHITE)
        screen.blit(title, (form_rect.x + (form_rect.width - title.get_width()) // 2, form_rect.y + 20))
        
        # Поля ввода
        username_rect = pygame.Rect(form_rect.x + 50, form_rect.y + 80, 300, 40)
        password_rect = pygame.Rect(form_rect.x + 50, form_rect.y + 130, 300, 40)
        pygame.draw.rect(screen, WHITE if active_field == "username" else GRAY, username_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE if active_field == "password" else GRAY, password_rect, border_radius=5)
        screen.blit(small_font.render(username, True, BLACK), (username_rect.x + 10, username_rect.y + 10))
        screen.blit(small_font.render("*" * len(password), True, BLACK), (password_rect.x + 10, password_rect.y + 10))
        
        # Кнопки
        action_btn = pygame.Rect(form_rect.x + 50, form_rect.y + 180, 150, 40)
        switch_btn = pygame.Rect(form_rect.x + 200, form_rect.y + 180, 150, 40)
        pygame.draw.rect(screen, (0, 200, 0), action_btn, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), switch_btn, border_radius=8)
        screen.blit(small_font.render("Зарегистрироваться" if is_register else "Войти", True, WHITE), (action_btn.x + 10, action_btn.y + 10))
        screen.blit(small_font.render("Вход" if is_register else "Регистрация", True, WHITE), (switch_btn.x + 10, switch_btn.y + 10))
        
        # Ошибка
        if error_message:
            error_text = small_font.render(error_message, True, (255, 0, 0))
            screen.blit(error_text, (form_rect.x + (form_rect.width - error_text.get_width()) // 2, form_rect.y + 230))
        
        pygame.display.flip()
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if username_rect.collidepoint(mx, my):
                    active_field = "username"
                elif password_rect.collidepoint(mx, my):
                    active_field = "password"
                elif action_btn.collidepoint(mx, my):
                    play_sound('button')
                    if is_register:
                        if register(username, password):
                            error_message = "Регистрация успешна! Теперь войдите."
                            is_register = False
                        else:
                            error_message = "Логин уже существует!"
                    else:
                        user_balance = login(username, password)
                        if user_balance is not None:
                            return username, user_balance  # Успешный вход
                        else:
                            error_message = "Неверный логин или пароль!"
                elif switch_btn.collidepoint(mx, my):
                    play_sound('button')
                    is_register = not is_register
                    error_message = ""
            elif event.type == pygame.KEYDOWN:
                if active_field == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode
                elif active_field == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode

# Супербонусная игра
def superbonus_game(window_width, window_height):
    global GRID_ROWS, GRID_COLS, symbol_probabilities, is_superbonus_game, superbonus_spins_left, board
    global is_bonus_game, last_win, balance, current_bonus_spin, total_bonus_win, current_user
    global is_bet_plus, is_bet_plus_plus, is_garant_spin, is_3_lvl, is_bandit_mode, is_buy_fs, is_buy_super, is_75_25
    global num_parrots, active_parrots
    # Сохраняем оригинальные настройки
    orig_grid_rows = GRID_ROWS
    orig_grid_cols = GRID_COLS
    orig_probs = symbol_probabilities.copy()
    orig_num_parrots = num_parrots
    orig_active_parrots = active_parrots[:]

    # Настраиваем супербонусную игру
    GRID_ROWS = 8
    GRID_COLS = 7
    num_parrots = 4
    active_parrots = ['high1', 'high2', 'high3', 'high4']
    is_superbonus_game = True
    is_bonus_game = True
    # Отключаем все модификаторы в супербонусе
    is_bet_plus = is_bet_plus_plus = is_garant_spin = is_3_lvl = is_bandit_mode = is_buy_fs = is_buy_super = is_75_25 = False
    superbonus_spins_left = 8
    current_bonus_spin = 1  # Сброс на 1-й спин
    total_bonus_win = last_win  # Перенос выигрыша с активации

    # Модифицированные вероятности для супербонуса
    sb_probs = orig_probs.copy()
    sb_probs['levelup'] = sb_probs['levelup_2'] = sb_probs['levelup_3'] = 0
    sb_probs['levelupall'] = 1.277
    sb_probs['levelupall_2'] = 0.569
    sb_probs['levelupall_3'] = 0.218
    for coin in ['coin25', 'coin50', 'coin100', 'coin500', 'coin1000', 'coin2500', 'coinmaxwin']:
        if coin in sb_probs:
            sb_probs[coin] = sb_probs.get(coin, 0) * 6
    symbol_probabilities = sb_probs

    play_sound('startbonus1')
    time.sleep(1.5)
    play_sound('bonus', loop=True)

    spins_left = superbonus_spins_left
    last_win = 0  # Сброс для чистоты
    
    # Генерируем первую доску
    board, gigablocks = generate_board()

    for _ in range(spins_left):
        # Передаем текущую доску в spin_animation, она сама сгенерирует новую после анимации падения
        board, gigablocks = spin_animation(board, window_width, window_height)
        total_bonus_win += last_win
        last_win = 0
        if current_bonus_spin < 5:
            time.sleep(1.0)
        current_bonus_spin += 1

    pygame.mixer.stop()
    play_sound('endbonus')
    balance_add = total_bonus_win
    try:
        balance += balance_add
        update_balance(current_user, balance)  # Обновляем в БД
        try:
            # Добавляем выигрыш супербонусной игры в общую статистику
            update_stats(current_user, 0, balance_add)
        except Exception:
            pass
    except Exception:
        globals()['balance'] = globals().get('balance', 0) + balance_add
        update_balance(current_user, globals()['balance'])  # Обновляем в БД
        try:
            update_stats(current_user, 0, balance_add)
        except Exception:
            pass

    show_superbonus_win_screen(window_width, window_height, total_bonus_win, board)

    # Восстанавливаем настройки
    GRID_ROWS = orig_grid_rows
    GRID_COLS = orig_grid_cols
    symbol_probabilities = orig_probs
    num_parrots = orig_num_parrots
    active_parrots = orig_active_parrots
    is_superbonus_game = False
    is_bonus_game = False
    try:
        play_background_music('song')
    except Exception:
        pass

def show_superbonus_start_screen(window_width, window_height):

    time.sleep(1)
    pygame.mixer.stop()
    """Показывает экран запуска супербонусной игры и стартует её по нажатию START."""
    play_sound('startbonus')
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(BIG_WIN_BG)
    title = font.render("SUPER BONUS!", True, GOLD)
    text_rect = title.get_rect(center=(window_width // 2, window_height // 2 - 50))
    start_button = pygame.Rect(window_width // 2 - 75, window_height // 2 + 50, 150, 60)
    start_time = time.time()
    while True:
        screen.blit(bg_surface, (0, 0))
        screen.blit(title, text_rect)
        pygame.draw.rect(screen, (0, 200, 0), start_button, border_radius=8)
        screen.blit(small_font.render("START", True, WHITE), start_button.move(45, 20))
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if start_button.collidepoint(mx, my):
                    try:
                        pygame.mixer.stop()
                    except Exception:
                        pass
                    play_sound('button')
                    update_stats(current_user, 0, 0, 1)  # Увеличиваем счётчик бонусных игр (супер тоже считается)
                    superbonus_game(window_width, window_height)
                    return

def show_markdown_viewer(markdown_file, window_width, window_height):
    """Отображает Markdown файл внутри pygame интерфейса с прокруткой и картинками."""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        pass
        return

    # Кеш загруженных изображений
    image_cache = {}
    
    def load_image(path, max_width):
        """Загружает и масштабирует изображение"""
        if path in image_cache:
            return image_cache[path]
        
        try:
            # Пытаемся загрузить изображение
            img = pygame.image.load(path)
            # Масштабируем если нужно
            if img.get_width() > max_width:
                aspect = img.get_height() / img.get_width()
                new_width = max_width
                new_height = int(max_width * aspect)
                img = pygame.transform.scale(img, (new_width, new_height))
            image_cache[path] = img
            return img
        except Exception as e:
            # Создаём placeholder
            placeholder = pygame.Surface((max_width, 100))
            placeholder.fill((100, 100, 100))
            error_font = pygame.font.SysFont("serif", 16)
            error_text = error_font.render(f"Image not found: {path}", True, (255, 50, 50))
            placeholder.blit(error_text, (10, 40))
            return placeholder

    # Парсинг markdown в список строк с форматированием
    lines = []
    base_dir = os.path.dirname(os.path.abspath(markdown_file))
    
    for line in content.split('\n'):
        # Изображение ![alt](path)
        if '![' in line and '](' in line:
            import re
            match = re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
            if match:
                alt_text = match.group(1)
                img_path = match.group(2)
                # Если путь относительный, делаем его абсолютным относительно MD файла
                if not os.path.isabs(img_path):
                    img_path = os.path.join(base_dir, img_path)
                lines.append(('image', (img_path, alt_text)))
                continue
        
        # Заголовок H1
        if line.startswith('# '):
            lines.append(('h1', line[2:].strip()))
        # Заголовок H2
        elif line.startswith('## '):
            lines.append(('h2', line[3:].strip()))
        # Заголовок H3
        elif line.startswith('### '):
            lines.append(('h3', line[4:].strip()))
        # Код блок начало/конец
        elif line.strip() == '```':
            continue  # Пропускаем маркеры кодовых блоков
        # Разделитель
        elif line.strip().startswith('───') or line.strip().startswith('═══'):
            lines.append(('separator', ''))
        # Bullet point
        elif line.strip().startswith('•'):
            lines.append(('bullet', line.strip()))
        # Обычный текст
        elif line.strip():
            lines.append(('text', line.strip()))
        # Пустая строка
        else:
            lines.append(('empty', ''))

    scroll_offset = 0
    line_height = 25

    # Создаём шрифты разных размеров
    title_font = pygame.font.SysFont("serif", 42, bold=True)
    h2_font = pygame.font.SysFont("serif", 36, bold=True)
    h3_font = pygame.font.SysFont("serif", 30, bold=True)
    text_font = pygame.font.SysFont("serif", 22)
    
    # Предварительный расчёт общей высоты контента
    def calculate_total_height(lines, content_width):
        total_h = 0
        for line_type, text in lines:
            if line_type == 'h1':
                total_h += 50
            elif line_type == 'h2':
                total_h += 45
            elif line_type == 'h3':
                total_h += 38
            elif line_type == 'separator':
                total_h += 25
            elif line_type == 'image':
                img_path, alt_text = text
                img = load_image(img_path, content_width - 60)
                total_h += img.get_height() + 10
                if alt_text:
                    total_h += 30
            elif line_type == 'bullet':
                total_h += line_height
            elif line_type == 'text':
                # Подсчёт строк после переноса
                words = text.split()
                current_line = ""
                line_count = 0
                for word in words:
                    test_line = current_line + word + " "
                    if text_font.size(test_line)[0] > content_width - 60:
                        if current_line:
                            line_count += 1
                        current_line = word + " "
                    else:
                        current_line = test_line
                if current_line:
                    line_count += 1
                total_h += line_count * line_height
            elif line_type == 'empty':
                total_h += 15
        return total_h

    running = True
    total_content_height = 0
    while running:
        screen.blit(scaled_background, (0, 0))
        
        # Полупрозрачный фон
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Панель
        panel_width = int(window_width * 0.85)
        panel_height = int(window_height * 0.9)
        panel_rect = pygame.Rect(
            (window_width - panel_width) // 2,
            (window_height - panel_height) // 2,
            panel_width,
            panel_height
        )
        
        pygame.draw.rect(screen, (40, 40, 60), panel_rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, panel_rect, 3, border_radius=15)

        # Кнопка закрытия
        close_btn = pygame.Rect(panel_rect.right - 60, panel_rect.top + 10, 50, 40)
        pygame.draw.rect(screen, (200, 0, 0), close_btn, border_radius=8)
        screen.blit(small_font.render("X", True, WHITE), close_btn.move(18, 10))

        # Отрисовка контента с прокруткой
        y_pos = panel_rect.y + 60
        content_area = pygame.Rect(panel_rect.x + 20, y_pos, panel_rect.width - 40, panel_height - 80)
        
        # Рассчитываем общую высоту контента (только один раз)
        if total_content_height == 0:
            total_content_height = calculate_total_height(lines, content_area.width)
        
        # Ограничиваем область рендеринга
        screen.set_clip(content_area)
        
        # Начальная позиция с учётом прокрутки
        y_pos = content_area.y - scroll_offset

        for i in range(len(lines)):
            line_type, text = lines[i]
            
            # Пропускаем элементы, которые выше видимой области
            if y_pos + 200 < content_area.y:
                # Быстро пропускаем с подсчётом высоты
                if line_type == 'h1':
                    y_pos += 50
                elif line_type == 'h2':
                    y_pos += 45
                elif line_type == 'h3':
                    y_pos += 38
                elif line_type == 'separator':
                    y_pos += 25
                elif line_type == 'image':
                    img_path, alt_text = text
                    img = load_image(img_path, content_area.width - 60)
                    y_pos += img.get_height() + 10
                    if alt_text:
                        y_pos += 30
                elif line_type == 'bullet':
                    y_pos += line_height
                elif line_type == 'text':
                    words = text.split()
                    current_line = ""
                    line_count = 0
                    for word in words:
                        test_line = current_line + word + " "
                        if text_font.size(test_line)[0] > content_area.width - 60:
                            if current_line:
                                line_count += 1
                            current_line = word + " "
                        else:
                            current_line = test_line
                    if current_line:
                        line_count += 1
                    y_pos += line_count * line_height
                elif line_type == 'empty':
                    y_pos += 15
                continue
            
            # Прерываем если элемент ниже видимой области
            if y_pos > content_area.bottom + 100:
                break
            
            if line_type == 'h1':
                rendered = title_font.render(text, True, GOLD)
                screen.blit(rendered, (content_area.x + 10, y_pos))
                y_pos += 50
            elif line_type == 'h2':
                rendered = h2_font.render(text, True, (100, 200, 255))
                screen.blit(rendered, (content_area.x + 10, y_pos))
                y_pos += 45
            elif line_type == 'h3':
                rendered = h3_font.render(text, True, (150, 220, 255))
                screen.blit(rendered, (content_area.x + 20, y_pos))
                y_pos += 38
            elif line_type == 'separator':
                pygame.draw.line(screen, GOLD, 
                               (content_area.x + 10, y_pos + 10), 
                               (content_area.right - 10, y_pos + 10), 2)
                y_pos += 25
            elif line_type == 'image':
                img_path, alt_text = text
                img = load_image(img_path, content_area.width - 60)
                screen.blit(img, (content_area.x + 30, y_pos))
                y_pos += img.get_height() + 10
                # Подпись под картинкой
                if alt_text:
                    caption_font = pygame.font.SysFont("serif", 18, italic=True)
                    caption = caption_font.render(alt_text, True, (180, 180, 180))
                    screen.blit(caption, (content_area.x + 30, y_pos))
                    y_pos += 30
            elif line_type == 'bullet':
                rendered = text_font.render(text, True, (200, 255, 200))
                screen.blit(rendered, (content_area.x + 30, y_pos))
                y_pos += line_height
            elif line_type == 'text':
                # Разбиваем длинные строки
                words = text.split()
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if text_font.size(test_line)[0] > content_area.width - 60:
                        if current_line:
                            rendered = text_font.render(current_line, True, WHITE)
                            screen.blit(rendered, (content_area.x + 30, y_pos))
                            y_pos += line_height
                        current_line = word + " "
                    else:
                        current_line = test_line
                if current_line:
                    rendered = text_font.render(current_line, True, WHITE)
                    screen.blit(rendered, (content_area.x + 30, y_pos))
                    y_pos += line_height
            elif line_type == 'empty':
                y_pos += 15

        screen.set_clip(None)

        # Индикатор прокрутки
        if total_content_height > content_area.height:
            visible_ratio = content_area.height / total_content_height
            scrollbar_height = max(30, visible_ratio * content_area.height)
            scroll_ratio = scroll_offset / (total_content_height - content_area.height)
            scrollbar_y = content_area.y + scroll_ratio * (content_area.height - scrollbar_height)
            scrollbar_rect = pygame.Rect(
                panel_rect.right - 25,
                scrollbar_y,
                10,
                scrollbar_height
            )
            pygame.draw.rect(screen, GOLD, scrollbar_rect, border_radius=5)

        pygame.display.flip()

        # События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if close_btn.collidepoint(mx, my):
                    play_sound('button')
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                max_scroll = max(0, total_content_height - content_area.height)
                scroll_offset = max(0, min(scroll_offset - event.y * 30, max_scroll))

        clock.tick(FPS)


def show_stats_window(window_width, window_height):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT total_bet, total_win, bonus_games FROM users WHERE username = ?', (current_user,))
    stats = cursor.fetchone()
    conn.close()
    if not stats:
        return

    total_bet, total_win, bonus_games = stats
    percent = (total_win / total_bet * 100) if total_bet > 0 else 0

    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(SETTINGS_BG)
    panel_rect = pygame.Rect(window_width // 4, window_height // 4, window_width // 2, window_height // 2)
    pygame.draw.rect(screen, SETTINGS_BG, panel_rect, border_radius=15)
    pygame.draw.rect(screen, GOLD, panel_rect, 3)

    title = font.render("Статистика", True, GOLD)
    screen.blit(title, (panel_rect.x + (panel_rect.width - title.get_width()) // 2, panel_rect.y + 20))

    stats_texts = [
        f"Потрачено на ставки: {total_bet:.2f} У.Е.",
        f"Выиграно: {total_win:.2f} У.Е.",
        f"Процент возврата: {percent:.2f}%",
        f"Сыграно бонусных игр: {bonus_games}"
    ]
    for i, text in enumerate(stats_texts):
        stat_text = small_font.render(text, True, WHITE)
        screen.blit(stat_text, (panel_rect.x + 20, panel_rect.y + 60 + i * 40))

    close_btn = pygame.Rect(panel_rect.right - 60, panel_rect.top + 10, 50, 40)
    pygame.draw.rect(screen, (200, 0, 0), close_btn, border_radius=8)
    screen.blit(small_font.render("X", True, WHITE), close_btn.move(18, 10))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if close_btn.collidepoint(mx, my):
                    play_sound('button')
                    return
        clock.tick(FPS)

def draw_crystal_counter(window_width, window_height):
    """Отрисовка счетчика кристаллов справа от сетки."""
    global total_crystals_collected, filled_counters, current_counter_level
    grid_width = GRID_COLS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    counter_x = offset_x + grid_width + 20  # Справа от сетки
    counter_y = (window_height - INFO_PANEL_HEIGHT) // 2
    goal = crystal_counter_goals[min(current_counter_level, len(crystal_counter_goals) - 1)]
    
    # Отрисовка счетчика
    counter_text = small_font.render(f"Кристаллы: {total_crystals_collected}/{goal}", True, WHITE)
    screen.blit(counter_text, (counter_x, counter_y))
    
    # Отрисовка количества заполненных счетчиков
    if filled_counters > 0:
        filled_text = small_font.render(f"x{filled_counters}", True, GOLD)
        screen.blit(filled_text, (counter_x + counter_text.get_width() + 10, counter_y))

def get_random_symbol(color):
    level = crystal_levels[f'low{color}']
    return f'low{color}_{level}'

def get_random_symbol_with_chance():
    """Возвращает случайный символ с учетом вероятностей, исключая 'bonus' во время бонусной игры."""
    global is_bonus_game, is_bet_plus, is_bet_plus_plus, is_bandit_mode, key_was_collected
    # Копируем вероятности, чтобы модифицировать их
    current_probabilities = symbol_probabilities.copy()
    # Устанавливаем вероятность символа 'bonus' равной 0 во время бонусной игры
    if is_bonus_game:
        current_probabilities['bonus'] = 0
        current_probabilities['bonus'] = 0
    else:
        # Модифицируем шанс 'bonus' в зависимости от режимов bet+ или bet++
        if is_bet_plus:
            current_probabilities['bonus'] *= 2.5
            current_probabilities['superbonus'] *= 2
        elif is_bet_plus_plus:
            current_probabilities['bonus'] *= 5
            current_probabilities['superbonus'] *= 3
    # Во время Buy FS запрещаем выпадение 'superbonus'
    try:
        if is_buy_fs:
            current_probabilities['superbonus'] = 0
    except NameError:
        pass
    # Запрещаем выпадение 'key' при активном модификаторе бандита или если ключ уже был собран
    if is_bandit_mode or key_was_collected:
        current_probabilities['key'] = 0
    # Нормализуем вероятности
    total_prob = sum(current_probabilities.values())
    if total_prob == 0:
        return get_random_symbol(str(random.randint(1, 4)))
    rand = random.uniform(0, total_prob)
    cumulative = 0
    for symbol, prob in current_probabilities.items():
        cumulative += prob
        if rand <= cumulative:
            if symbol.startswith('low'):
                return get_random_symbol(symbol[-1])
            return symbol
    return get_random_symbol(str(random.randint(1, 4)))

def play_sound(sound_name, loop=False):
    global dance_sound, bonus_sound
    sound_path = os.path.join('images', f'{sound_name}.ogg')
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(volume / 100.0)
        if sound_name == 'dance':
            dance_sound = sound
            sound.play(-1 if loop else 0)  # Зацикливание для dance.ogg
        elif sound_name == 'bonus':
            bonus_sound = sound
            sound.play(-1 if loop else 0)  # Зацикливание для bonus.ogg
        else:
            sound.play()
    except pygame.error as e:
        pass

def stop_bonus_sound():
    global bonus_sound
    if bonus_sound:
        bonus_sound.stop()
        bonus_sound = None

def stop_dance_sound():
    global dance_sound
    if dance_sound:
        dance_sound.stop()
        dance_sound = None

def play_background_music(music_name='song'):
    music_path = os.path.join('images', f'{music_name}.ogg')
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume / 100.0)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        pass

def play_music_once(music_name):
    music_path = os.path.join('images', f'{music_name}.ogg')
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume / 100.0)
        pygame.mixer.music.play(0)
    except pygame.error:
        pass

def save_spin_data(seed, bet_multiplier):
    # важно: сохраняем минимально необходимую информацию и защищаемся от ошибок
    global total_bonus_win, last_free_buy_fs
    folder = 'spins'
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
    except Exception:
        # Если не удаётся создать папку — ничего не делаем, но не ломать игру
        return

    timestamp = time.time()
    filename = os.path.join(folder, f"spin_{timestamp}.json")

    # Берём значения безопасно, на случай, если какие-то глобальные ещё не определены
    try:
        user = globals().get('current_user', '')
    except Exception:
        user = ''
    try:
        b_bet = globals().get('base_bet', 0)
    except Exception:
        b_bet = 0
    try:
        win = globals().get('last_win', 0)
    except Exception:
        win = 0
    try:
        t_bonus = globals().get('total_bonus_win', 0)
    except Exception:
        t_bonus = 0

    data = {
        "seed": int(seed) if isinstance(seed, (int, float)) else seed,
        "bet_multiplier": bet_multiplier,
        "base_bet": b_bet,
        "user": user,
        "win": win,
        "total_bonus_win": t_bonus,
        "free_buy_fs": bool(last_free_buy_fs)
    }

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        # Игнорируем ошибки записи — не ломаем игру
        return

    # Логируем для отладки (печатаем seed и признак free_buy_fs)

    # — фикс бага: сбрасываем бонусный выигрыш после сохранения —
    try:
        total_bonus_win = 0
    except Exception:
        pass

def generate_board():
    global crystal_levels, is_garant_spin, is_3_lvl, is_bonus_game, is_buy_fs, is_god_mode_bet
    global num_parrots, active_parrots, is_buy_fs_300, is_buy_fs_900, is_buy_fs_3600, is_buy_fs_18000, is_40_40_20
    if is_3_lvl:
        crystal_levels = {'low1': 3, 'low2': 3, 'low3': 3, 'low4': 3}
    elif not is_bonus_game:
        crystal_levels = {'low1': 1, 'low2': 1, 'low3': 1, 'low4': 1}
    board = [[get_random_symbol_with_chance() for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    def is_adjacent(pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1

    # Определяем количество бонусных символов для модификатора 40/40/20
    buy_bonus_count = 0
    is_any_buy = is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20
    if is_40_40_20:
        roll = random.random()
        if roll < 0.4:
            buy_bonus_count = 3
        elif roll < 0.8:
            buy_bonus_count = 4
        else:
            buy_bonus_count = 5

    # Для buy_fs_900 попугай ставится строго по центру
    parrot_positions = []
    if is_buy_fs_900 or (is_40_40_20 and buy_bonus_count == 5):
        center_r, center_c = GRID_ROWS // 2, GRID_COLS // 2
        parrot_positions = [(center_r, center_c)]
        available_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if (r, c) != (center_r, center_c)]
    elif is_any_buy:
        available_positions = [(r, c) for r in range(1, GRID_ROWS-1) for c in range(1, GRID_COLS-1)]
    else:
        available_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)]

    target_parrots = num_parrots
    while len(parrot_positions) < target_parrots and available_positions:
        candidate = random.choice(available_positions)
        if all(not is_adjacent(candidate, p) for p in parrot_positions):
            parrot_positions.append(candidate)
        available_positions.remove(candidate)

    if len(parrot_positions) < target_parrots:
        return generate_board()

    all_parrots = ['high1', 'high2', 'high3', 'high4']
    random.shuffle(all_parrots)
    chosen_parrots = all_parrots[:target_parrots]
    active_parrots = chosen_parrots[:]
    for i, (r, c) in enumerate(parrot_positions):
        board[r][c] = chosen_parrots[i]

    # Шанс подставления не тех кристаллов
    # При бонусной игре — 0% (всегда правильные кристаллы)
    # При обычной игре — 74% шанс неправильных кристаллов рядом с попугаем
    forbidden_prob = 0.0 if (is_any_buy or is_bonus_game or is_superbonus_game) else 0.74
    if not is_garant_spin and random.random() < forbidden_prob:
        from collections import defaultdict
        forbidden_colors = defaultdict(set)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if board[r][c].startswith('high'):
                    parrot_color = int(board[r][c][-1])
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and not board[nr][nc].startswith('high'):
                            forbidden_colors[(nr, nc)].add(parrot_color)
        for (r, c), colors in forbidden_colors.items():
            available_colors = [1, 2, 3, 4]
            for color in colors:
                if color in available_colors:
                    available_colors.remove(color)
            if available_colors:
                new_symbol = get_random_symbol(random.choice(available_colors))
                board[r][c] = new_symbol

    # === Модификаторы покупки бонусной игры ===

    def place_bonus_near_parrot(parrot_pos, count, board_ref, used_positions, include_diagonal=False):
        """Размещает count бонусных символов рядом с попугаем."""
        r, c = parrot_pos
        adjacent = []
        near_dirs = directions + [(-1, -1), (-1, 1), (1, -1), (1, 1)] if include_diagonal else directions
        for dr, dc in near_dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                if not board_ref[nr][nc].startswith('high') and board_ref[nr][nc] != 'bonus' and (nr, nc) not in used_positions:
                    adjacent.append((nr, nc))
        placed = []
        random.shuffle(adjacent)
        for pos in adjacent[:count]:
            board_ref[pos[0]][pos[1]] = 'bonus'
            used_positions.add(pos)
            placed.append(pos)
        return placed

    # Buy FS 100x: 1 попугай + 3 бонуса рядом
    if is_buy_fs and not is_40_40_20:
        used = set()
        place_bonus_near_parrot(parrot_positions[0], 3, board, used)

    # Buy FS 300x: 1 попугай + 4 бонуса ортогонально
    if is_buy_fs_300 and not is_40_40_20:
        r, c = parrot_positions[0]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                board[nr][nc] = 'bonus'

    # Buy FS 900x: попугай по центру + 5 бонусов (4 ортогонально + 1 за бонусом)
    if is_buy_fs_900 and not is_40_40_20:
        r, c = parrot_positions[0]
        bonus_ortho = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                board[nr][nc] = 'bonus'
                bonus_ortho.append((nr, nc))
        # Пятый бонус за одним из ортогональных бонусов
        if bonus_ortho:
            random.shuffle(bonus_ortho)
            for br, bc in bonus_ortho:
                for dr, dc in directions:
                    nr, nc = br + dr, bc + dc
                    if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                        if not board[nr][nc].startswith('high') and board[nr][nc] != 'bonus':
                            board[nr][nc] = 'bonus'
                            break
                else:
                    continue
                break

    # Buy FS 3600x: 1 попугай + 6 бонусов вокруг (включая диагонали)
    if is_buy_fs_3600 and not is_40_40_20:
        used = set()
        place_bonus_near_parrot(parrot_positions[0], 6, board, used, include_diagonal=True)

    # Buy FS 18000x: 1 попугай + 6 бонусов вокруг (включая диагонали)
    if is_buy_fs_18000 and not is_40_40_20:
        used = set()
        place_bonus_near_parrot(parrot_positions[0], 6, board, used, include_diagonal=True)

    # 40/40/20: случайный выбор 3, 4 или 5 бонусов
    if is_40_40_20:
        r, c = parrot_positions[0]
        if buy_bonus_count == 3:
            used = set()
            place_bonus_near_parrot(parrot_positions[0], 3, board, used)
        elif buy_bonus_count == 4:
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                    board[nr][nc] = 'bonus'
        elif buy_bonus_count == 5:
            bonus_ortho = []
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                    board[nr][nc] = 'bonus'
                    bonus_ortho.append((nr, nc))
            if bonus_ortho:
                random.shuffle(bonus_ortho)
                for br, bc in bonus_ortho:
                    for dr, dc in directions:
                        nr, nc = br + dr, bc + dc
                        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                            if not board[nr][nc].startswith('high') and board[nr][nc] != 'bonus':
                                board[nr][nc] = 'bonus'
                                break
                    else:
                        continue
                    break

    # При активном модификаторе бандита: добавляем 3 случайных функциональных символа не рядом с попугаями
    if is_bandit_mode:
        functional_symbols = ['levelup', 'levelup_2', 'levelup_3', 'coin2', 'coin5', 'coin10', 'coin25', 'rum', 'bonus']
        safe_positions = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if not board[r][c].startswith('high'):
                    has_parrot_nearby = False
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                            if board[nr][nc].startswith('high'):
                                has_parrot_nearby = True
                                break
                    if not has_parrot_nearby:
                        safe_positions.append((r, c))
        if len(safe_positions) >= 3:
            selected_positions = random.sample(safe_positions, 3)
            for pos in selected_positions:
                board[pos[0]][pos[1]] = random.choice(functional_symbols)

    # При активном модификаторе God Mode: гарантируем появление coinmaxwin не рядом с попугаем
    if is_god_mode_bet:
        safe_positions = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if not board[r][c].startswith('high'):
                    has_parrot_nearby = False
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                            if board[nr][nc].startswith('high'):
                                has_parrot_nearby = True
                                break
                    if not has_parrot_nearby:
                        safe_positions.append((r, c))
        if safe_positions:
            chosen_pos = random.choice(safe_positions)
            board[chosen_pos[0]][chosen_pos[1]] = 'coinmaxwin'

    # Ограничиваем количество ключей и бонусов на доске
    key_positions = []
    bonus_positions = []
    superbonus_positions = []
    
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if board[r][c] == 'key':
                key_positions.append((r, c))
            elif board[r][c] == 'bonus':
                bonus_positions.append((r, c))
            elif board[r][c] == 'superbonus':
                superbonus_positions.append((r, c))
    
    if len(key_positions) > 1:
        keep_key = random.choice(key_positions)
        for pos in key_positions:
            if pos != keep_key:
                board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
    
    # Убираем все супербонусы с доски (получить можно только через gamble)
    for pos in superbonus_positions:
        board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))

    return board, []

def draw_bonus_counter(window_width, window_height):
    """Отрисовка счетчика бонусов справа от сетки под счетчиком кристаллов. 7 ячеек: 6 бонус + 1 супер."""
    global bonus_count, current_bonus_spin, is_bonus_game, is_superbonus_game, total_bonus_win
    grid_width = GRID_COLS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    counter_x = offset_x + grid_width + 20  # Справа от сетки
    counter_y = (window_height - INFO_PANEL_HEIGHT) // 2 + 50  # Ниже счетчика кристаллов
    
    slot_size = CELL_SIZE // 2
    slot_gap = 8
    
    # Отрисовка 6 ячеек для обычных бонусов
    for i in range(6):
        cell_rect = pygame.Rect(counter_x + i * (slot_size + slot_gap), counter_y, slot_size, slot_size)
        pygame.draw.rect(screen, GRAY, cell_rect, border_radius=5)
        if i < bonus_count:
            bonus_image = symbol_images['bonus']
            scaled_bonus = pygame.transform.scale(bonus_image, (slot_size, slot_size))
            screen.blit(scaled_bonus, cell_rect.topleft)
    
    # Отдельная ячейка для супербонуса (7-я, после пробела)
    sb_rect = pygame.Rect(counter_x + 6 * (slot_size + slot_gap) + 5, counter_y, slot_size, slot_size)
    pygame.draw.rect(screen, (80, 40, 80), sb_rect, border_radius=5)
    pygame.draw.rect(screen, (180, 0, 180), sb_rect, 2, border_radius=5)
    sb_count = globals().get('superbonus_count', 0)
    if sb_count > 0:
        sb_image = symbol_images.get('superbonus')
        if sb_image:
            scaled_sb = pygame.transform.scale(sb_image, (slot_size, slot_size))
            screen.blit(scaled_sb, sb_rect.topleft)

    # Отображение информации во время бонусной или супербонусной игры
    if is_bonus_game or is_superbonus_game:
        total_spins = 8
        spin_y = counter_y + slot_size + 10
        bonus_y = spin_y + 25
        
        spin_text = small_font.render(f"Spin {current_bonus_spin}/{total_spins}", True, WHITE)
        screen.blit(spin_text, (counter_x, spin_y))
        
        bonus_win_text = small_font.render(f"Bonus Win: {total_bonus_win:.2f} У.Е.", True, GOLD)
        screen.blit(bonus_win_text, (counter_x, bonus_y))

def draw_bet_selector(window_width, window_height):
    """Отрисовка окна выбора ставок."""
    global bet_selector_open
    
    if not bet_selector_open:
        return None
    
    # Размеры и позиция окна
    window_rect = pygame.Rect(window_width // 2 - 200, window_height // 2 - 250, 400, 500)
    
    # Полупрозрачный фон
    overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Окно с кнопками ставок
    window_surface = pygame.Surface(window_rect.size, pygame.SRCALPHA)
    window_surface.fill((30, 30, 60, 220))
    pygame.draw.rect(window_surface, (100, 150, 255), (0, 0, window_rect.width, window_rect.height), 3, border_radius=15)
    screen.blit(window_surface, window_rect.topleft)
    
    # Заголовок
    title_text = pygame.font.Font(None, 40).render("SELECT BET", True, (150, 200, 255))
    title_rect = title_text.get_rect(center=(window_rect.centerx, window_rect.y + 25))
    screen.blit(title_text, title_rect)
    
    # Размеры ставок
    bet_amounts = [10, 20, 30, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000]
    bet_buttons = []
    
    # Рисуем 3 колонки по 4 кнопки
    for i, bet_amount in enumerate(bet_amounts):
        col = i % 3
        row = i // 3
        
        btn_width = 100
        btn_height = 40
        btn_x = window_rect.x + 30 + col * (btn_width + 15)
        btn_y = window_rect.y + 70 + row * (btn_height + 15)
        
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        bet_buttons.append((btn_rect, bet_amount))
        
        # Рисуем кнопку
        pygame.draw.rect(screen, (100, 150, 200), btn_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 180, 255), btn_rect, 2, border_radius=8)
        
        # Текст ставки
        bet_text = small_font.render(str(bet_amount), True, WHITE)
        bet_text_rect = bet_text.get_rect(center=btn_rect.center)
        screen.blit(bet_text, bet_text_rect)
    
    return bet_buttons

def draw_board(board, window_width, window_height, gigablocks, sticky_wilds=None, offset_y=0, symbol_offsets=None, highlight_cells=None, button_opacity=255, parrot_offsets=None, current_user=None):
    global scaled_background, bandit_pos, bandit_lair_pos, bandit_counter, bandit_active, bandit_key_alpha, active_modifier, key_was_collected, bandit_was_caught, hide_last_win_info
    if scaled_background is None or scaled_background.get_size() != (window_width, window_height):
        scaled_background = pygame.transform.scale(background_image, (window_width, window_height))
    screen.blit(scaled_background, (0, 0))

    if board is None:
        board = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    if gigablocks is None:
        gigablocks = []
    if symbol_offsets is None:
        symbol_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    if highlight_cells is None:
        highlight_cells = []
    if parrot_offsets is None:
        parrot_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    grid_width = GRID_COLS * CELL_SIZE
    grid_height = GRID_ROWS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    
    # Дополнительное смещение вниз для супербонусной игры
    if globals().get('is_superbonus_game', False):
        offset_y_grid += 50  # Сдвигаем вниз на 50 пикселей

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x, y = offset_x + c * CELL_SIZE, offset_y_grid + r * CELL_SIZE + offset_y + symbol_offsets[r][c]
            symbol = board[r][c]
            if (r, c) in highlight_cells:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 4)
            if symbol in symbol_images and symbol != '':
                image = symbol_images[symbol]
                offset = parrot_offsets[r][c] if symbol.startswith('high') and not symbol.endswith('win') else 0
                image_rect = image.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2 + offset))
                screen.blit(image, image_rect)
            else:
                if symbol != '':
                    text = font.render(symbol[:4], True, WHITE)
                    screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # Отрисовка бандита или его логова
    if bandit_active:
        if bandit_pos:
            r, c = bandit_pos
            x, y = offset_x + c * CELL_SIZE, offset_y_grid + r * CELL_SIZE + offset_y
            image = symbol_images['bandit']
            image_rect = image.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            screen.blit(image, image_rect)
        # Счетчик вместо логова
        counter_text = small_font.render(f"{bandit_counter:.2f} У.Е.", True, WHITE)
        screen.blit(counter_text, (bandit_lair_pos[0] + CELL_SIZE // 2 - counter_text.get_width() // 2, bandit_lair_pos[1] + CELL_SIZE // 2 - counter_text.get_height() // 2))
    else:
        # Логово бандита или надпись "ПОЙМАН"
        if bandit_was_caught:
            # Отображаем "ПОЙМАН" вместо логова
            caught_text = font.render("ПОЙМАН", True, (255, 50, 50))
            text_rect = caught_text.get_rect(center=(bandit_lair_pos[0] + CELL_SIZE // 2, bandit_lair_pos[1] + CELL_SIZE // 2))
            screen.blit(caught_text, text_rect)
        else:
            image = symbol_images['bandit']
            image_rect = image.get_rect(center=(bandit_lair_pos[0] + CELL_SIZE // 2, bandit_lair_pos[1] + CELL_SIZE // 2))
            screen.blit(image, image_rect)
            if is_bandit_mode:
                key_image = symbol_images.get('key', pygame.Surface((0,0)))
                key_image.set_alpha(bandit_key_alpha)
                key_rect = key_image.get_rect(center=(bandit_lair_pos[0] + CELL_SIZE // 2, bandit_lair_pos[1] + CELL_SIZE // 2 - 50))
                screen.blit(key_image, key_rect)

    # Отрисовка счетчика кристаллов
    draw_crystal_counter(window_width, window_height)

    # Отрисовка счетчика бонусов
    draw_bonus_counter(window_width, window_height)

    btn_y = window_height - INFO_PANEL_HEIGHT
    buttons = [
        ('bet_btn', pygame.Rect(20, btn_y, 100, 40), (255, 100, 0), "BET", (40, 10)),
        ('spin_btn', pygame.Rect((window_width - 120) // 2, btn_y, 120, 50), (0, 200, 0), "SPIN", (35, 15)),
        ('bet_plus_btn', pygame.Rect(window_width - 130, btn_y, 150, 40), (255, 165, 0) if is_bet_plus else (100, 100, 100), f"Bet+: {'ON' if is_bet_plus else 'OFF'}", (10, 10)),
        ('bet_plus_plus_btn', pygame.Rect(window_width - 290, btn_y, 150, 40), (255, 215, 0) if is_bet_plus_plus else (100, 100, 100), f"Bet++: {'ON' if is_bet_plus_plus else 'OFF'}", (10, 10)),
        ('bandit_btn', pygame.Rect(window_width - 450, btn_y, 150, 40), (0, 255, 255) if is_bandit_mode else (100, 100, 100), f"Bandit: {'ON' if is_bandit_mode else 'OFF'}", (10, 10)),
        ('super_spin_btn', pygame.Rect(window_width - 610, btn_y, 150, 40), (255, 100, 0) if is_super_spin else (100, 100, 100), f"Super: {'ON' if is_super_spin else 'OFF'}", (10, 10)),
        ('settings_btn', pygame.Rect(window_width - 770, btn_y, 150, 40), (100, 100, 255), "Settings", (30, 10)),
        ('buy_fs_btn', pygame.Rect(20, btn_y + 50, 150, 40), (0, 200, 200) if is_buy_fs else (100, 100, 100), f"FS 100x: {'ON' if is_buy_fs else 'OFF'}", (20, 10)),
        ('buy_fs_300_btn', pygame.Rect(180, btn_y + 50, 150, 40), (0, 160, 200) if is_buy_fs_300 else (100, 100, 100), f"FS 300x: {'ON' if is_buy_fs_300 else 'OFF'}", (20, 10)),
        ('buy_fs_900_btn', pygame.Rect(340, btn_y + 50, 150, 40), (0, 120, 220) if is_buy_fs_900 else (100, 100, 100), f"FS 900x: {'ON' if is_buy_fs_900 else 'OFF'}", (20, 10)),
        ('buy_40_40_20_btn', pygame.Rect(500, btn_y + 50, 150, 40), (255, 215, 0) if is_40_40_20 else (100, 100, 100), f"40/40/20: {'ON' if is_40_40_20 else 'OFF'}", (10, 10)),
        ('buy_fs_3600_btn', pygame.Rect(660, btn_y + 50, 150, 40), (255, 140, 0) if is_buy_fs_3600 else (100, 100, 100), f"FS 3600x: {'ON' if is_buy_fs_3600 else 'OFF'}", (10, 10)),
        ('buy_fs_18000_btn', pygame.Rect(820, btn_y + 50, 170, 40), (255, 80, 0) if is_buy_fs_18000 else (100, 100, 100), f"FS 18000x: {'ON' if is_buy_fs_18000 else 'OFF'}", (8, 10)),
        ('garant_spin_btn', pygame.Rect(window_width - 450, btn_y + 50, 150, 40), (0, 128, 255) if is_garant_spin else (80, 80, 80), "Garant Spin", (15, 10)),
        ('3_lvl_btn', pygame.Rect(window_width - 290, btn_y + 50, 150, 40), (255, 0, 255) if is_3_lvl else (80, 80, 80), "3 LVL", (45, 10)),
        ('replay_btn', pygame.Rect(window_width - 130, btn_y + 50, 150, 40), (100, 200, 100), "Replay", (45, 10)),
        ('stats_btn', pygame.Rect(window_width - 930, btn_y + 50, 150, 40), (150, 150, 255), "Stats", (45, 10)),
        ('md_btn', pygame.Rect(window_width - 1090, btn_y + 50, 150, 40), (255, 200, 50), "INFO", (30, 10)),
        ('god_mode_btn', pygame.Rect(window_width - 610, btn_y + 50, 150, 40), (255, 215, 0) if is_god_mode_bet else (80, 80, 80), f"GOD: {'ON' if is_god_mode_bet else 'OFF'}", (30, 10)),
    ]
    # --- Добавляем кнопку Admin ТОЛЬКО для alexkrit ---
    admin_btn = None
    if current_user == 'alexkrit' or current_user ==  '1':
        admin_btn_rect = pygame.Rect(window_width - 1080, btn_y, 150, 40)
        admin_btn_color = (200, 0, 200)
        pygame.draw.rect(screen, admin_btn_color, admin_btn_rect, border_radius=8)
        admin_text = small_font.render("Admin", True, WHITE)
        screen.blit(admin_text, admin_btn_rect.move(45, 10))
        admin_btn = admin_btn_rect
    
    # --- Часы в левом верхнем углу ---
    current_time = datetime.now().strftime("%H:%M:%S")
    time_text = small_font.render(current_time, True, WHITE)
    time_text.set_alpha(int(button_opacity))
    screen.blit(time_text, (20, 20))
    
    # --- Кнопка выхода в правом верхнем углу ---
    logout_btn_rect = pygame.Rect(window_width - 120, 20, 100, 40)
    logout_btn_surface = pygame.Surface(logout_btn_rect.size, pygame.SRCALPHA)
    logout_btn_color = (200, 0, 0) + (int(button_opacity),)
    pygame.draw.rect(logout_btn_surface, logout_btn_color, (0, 0, logout_btn_rect.width, logout_btn_rect.height), border_radius=8)
    screen.blit(logout_btn_surface, logout_btn_rect.topleft)
    logout_text = small_font.render("Logout", True, WHITE)
    logout_text.set_alpha(int(button_opacity))
    screen.blit(logout_text, logout_btn_rect.move(25, 10))
    logout_btn = logout_btn_rect

    for name, rect, color, text, text_offset in buttons:
        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        button_color = color + (int(button_opacity),)
        pygame.draw.rect(button_surface, button_color, (0, 0, rect.width, rect.height), border_radius=8)
        screen.blit(button_surface, rect.topleft)
        text_surface = small_font.render(text, True, WHITE)
        text_surface.set_alpha(int(button_opacity))
        screen.blit(text_surface, rect.move(*text_offset))

    info_y = btn_y + 100
    info_texts = [
        (f"Balance: {balance:.2f} У.Е.", (20, info_y)),
        (f"Base Bet: {base_bet:.2f} У.Е.", (window_width - 300, info_y)),
        (f"Total Bet: {bet:.2f} У.Е.", (window_width - 300, info_y + 30))
    ]
    if not hide_last_win_info:
        info_texts.append((f"Last Win: {last_win:.2f} У.Е.", (window_width // 2 - 75, info_y)))
    for text, pos in info_texts:
        text_surface = small_font.render(text, True, WHITE)
        text_surface.set_alpha(int(info_opacity))
        screen.blit(text_surface, pos)

    # Отрисовка картинки модификатора выше баланса, только во время спина (когда интерфейс скрыт)
    if button_opacity < 255 and active_modifier:
        mod_image = modifier_images.get(active_modifier)
        if mod_image:
            mod_pos = (20, info_y - 60)  # Выше текста баланса
            screen.blit(mod_image, mod_pos)

    settings_rect = None
    volume_slider = None
    fast_spin_btn = None
    close_btn = None
    if settings_open:
        settings_width, settings_height = 400, 300
        settings_x = (window_width - settings_width) // 2
        settings_y = (window_height - settings_height) // 2
        settings_rect = pygame.Rect(settings_x, settings_y, settings_width, settings_height)
        pygame.draw.rect(screen, SETTINGS_BG, settings_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)
        title_text = small_font.render("Settings", True, WHITE)
        screen.blit(title_text, (settings_x + (settings_width - title_text.get_width()) // 2, settings_y + 20))
        volume_label = small_font.render(f"Volume: {int(volume)}%", True, WHITE)
        screen.blit(volume_label, (settings_x + 20, settings_y + 80))
        volume_slider = pygame.Rect(settings_x + 20, settings_y + 110, 360, 20)
        pygame.draw.rect(screen, GRAY, volume_slider)
        slider_pos = volume_slider.x + (volume / 100.0) * volume_slider.width
        pygame.draw.circle(screen, WHITE, (int(slider_pos), volume_slider.centery), 10)
        fast_spin_btn = pygame.Rect(settings_x + 20, settings_y + 160, 150, 40)
        pygame.draw.rect(screen, (0, 255, 0) if fast_spin else (100, 100, 100), fast_spin_btn, border_radius=8)
        screen.blit(small_font.render("Fast Spin: " + ("ON" if fast_spin else "OFF"), True, WHITE), fast_spin_btn.move(10, 10))
        close_btn = pygame.Rect(settings_x + settings_width - 50, settings_y + 10, 40, 40)
        pygame.draw.rect(screen, (200, 0, 0), close_btn, border_radius=8)
        screen.blit(small_font.render("X", True, WHITE), close_btn.move(15, 10))

    # Отрисовка окна выбора ставок
    bet_buttons = draw_bet_selector(window_width, window_height)

    return (buttons[0][1], buttons[1][1], buttons[2][1], buttons[3][1], buttons[4][1], buttons[5][1], buttons[6][1],
        buttons[7][1], buttons[8][1], buttons[9][1], buttons[10][1], buttons[11][1], buttons[12][1], buttons[13][1], buttons[14][1], buttons[15][1], buttons[16][1], buttons[17][1], buttons[18][1],
        admin_btn, logout_btn,
        settings_rect, volume_slider, fast_spin_btn, close_btn, bet_buttons)



def animate_bonus_jump(start_pos, target_pos, board, window_width, window_height, button_opacity, symbol='bonus'):
    """Анимация перепрыгивания символа бонуса/ключа в ячейку счетчика."""
    grid_width = GRID_COLS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    offset_y_grid = (window_height - GRID_ROWS * CELL_SIZE - INFO_PANEL_HEIGHT) // 2
    start_x = offset_x + start_pos[1] * CELL_SIZE + CELL_SIZE // 2
    start_y = offset_y_grid + start_pos[0] * CELL_SIZE + CELL_SIZE // 2
    end_x = target_pos[0]
    end_y = target_pos[1]
    duration = 0.5
    start_time = time.time()
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        progress = elapsed / duration
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress - 100 * math.sin(math.pi * progress)  # Прыжок вверх
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        jump_image = symbol_images.get(symbol, symbol_images['bonus'])
        jump_rect = jump_image.get_rect(center=(current_x, current_y))
        screen.blit(jump_image, jump_rect)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

# ============ ПРОФЕССИОНАЛЬНЫЕ EASING ФУНКЦИИ ============
def ease_out_bounce(t):
    """Отскок при приземлении - классика AAA игр"""
    if t < 1 / 2.75:
        return 3.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 3.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 3.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 3.5625 * t * t + 0.984375

def ease_out_expo(t):
    """Резкое замедление - premium feel"""
    return 1 if t == 1 else 1 - pow(2, -10 * t)

def ease_in_out_cubic(t):
    """Плавное ускорение/замедление"""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def create_particle(x, y, color_base, is_premium=False):
    """Создает частицу с физикой"""
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(2, 5) if is_premium else random.uniform(1, 3)
    return {
        'x': x + random.uniform(-15, 15),
        'y': y + random.uniform(-10, 10),
        'vx': math.cos(angle) * speed,
        'vy': math.sin(angle) * speed - random.uniform(3, 6),
        'life': 1.0,
        'size': random.uniform(3, 6) if is_premium else random.uniform(2, 4),
        'color': color_base,
        'rotation': random.uniform(0, 360),
        'spin': random.uniform(-15, 15)
    }

def update_particle(p):
    """Обновляет физику частицы"""
    p['x'] += p['vx']
    p['y'] += p['vy']
    p['vy'] += 0.25  # гравитация
    p['vx'] *= 0.98  # воздушное сопротивление
    p['life'] -= 0.025
    p['size'] *= 0.96
    p['rotation'] += p['spin']
    return p['life'] > 0

def draw_particle(surface, p):
    """Рисует частицу с альфа-каналом"""
    alpha = int(255 * p['life'])
    size = max(1, int(p['size']))
    color = (*p['color'], alpha)
    
    # Создаем поверхность для частицы с вращением
    particle_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    pygame.draw.circle(particle_surf, color, (size * 1.5, size * 1.5), size)
    
    # Добавляем свечение для премиум частиц
    if p['color'] == (255, 215, 0):  # золотые
        glow_alpha = int(100 * p['life'])
        pygame.draw.circle(particle_surf, (255, 215, 0, glow_alpha), (size * 1.5, size * 1.5), size * 2, 1)
    
    rotated = pygame.transform.rotate(particle_surf, p['rotation'])
    rect = rotated.get_rect(center=(int(p['x']), int(p['y'])))
    surface.blit(rotated, rect)

def animate_fall_out(board, window_width, window_height, do_fade=True):
    global button_opacity
    frames = ANIMATION_FPS
    duration = 1.2  # Чуть дольше для плавности
    offset_y = 0
    start_time = time.time()
    grid_height = GRID_ROWS * CELL_SIZE
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    target_offset = grid_height + window_height - offset_y_grid
    current_opacity = button_opacity

    while offset_y < target_offset:
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        
        # Применяем easing для плавного ускорения
        eased_progress = ease_in_out_cubic(progress)
        offset_y = eased_progress * target_offset * 1.5
        
        if do_fade:
            fade_progress = min(elapsed / FADE_OUT_DURATION, 1.0) if elapsed <= FADE_OUT_DURATION else 1.0
            button_opacity = max(0, current_opacity * (1 - fade_progress))
        else:
            button_opacity = 0
        
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], offset_y=offset_y, button_opacity=button_opacity)
        
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    button_opacity = 0

def show_replay_window(window_width, window_height, board):
    folder = 'spins'
    spin_files = []
    if os.path.exists(folder):
        spin_files = [f for f in os.listdir(folder) if f.endswith('.json')]
        spin_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)

    replay_open = True
    selected_spin = None

    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(SETTINGS_BG)
    replay_rect = pygame.Rect(window_width // 4, window_height // 4, window_width // 2, window_height // 2)
    close_btn = pygame.Rect(replay_rect.right - 50, replay_rect.top + 10, 40, 40)

    button_height = 70
    scroll_offset = 0
    max_visible = replay_rect.height // button_height - 2

    while replay_open:
        screen.blit(bg_surface, (0, 0))
        pygame.draw.rect(screen, WHITE, replay_rect, 2)

        title = font.render("Select Spin to Replay", True, WHITE)
        screen.blit(title, (replay_rect.x + (replay_rect.width - title.get_width()) // 2, replay_rect.y + 20))

        pygame.draw.rect(screen, (200, 0, 0), close_btn, border_radius=8)
        screen.blit(small_font.render("X", True, WHITE), close_btn.move(15, 10))

        spin_buttons = []

        for i, spin_file in enumerate(spin_files[scroll_offset:scroll_offset + max_visible]):
            btn_rect = pygame.Rect(
                replay_rect.x + 20,
                replay_rect.y + 60 + i * button_height,
                replay_rect.width - 40,
                button_height - 5
            )
            pygame.draw.rect(screen, (100, 100, 100), btn_rect, border_radius=8)
            spin_buttons.append((spin_file, btn_rect))

            # --- читаем данные реплея ---
            try:
                with open(os.path.join(folder, spin_file), "r") as f:
                    data = json.load(f)
                    pass

                user = data.get("user", "—")
                base = data.get("base_bet", 0)
                mult = data.get("bet_multiplier", 1)
                total = base * mult
                win = data.get("win", 0)
                bonus_win = data.get("total_bonus_win", 0)

                screen.blit(small_font.render(f"User: {user}", True, WHITE), btn_rect.move(10, 5))
                screen.blit(small_font.render(f"Base: {base:.2f} У.Е.  Total Bet: {total:.2f} У.Е.", True, WHITE), btn_rect.move(10, 25))

                # --- показываем выигрыш ---
                win_text = f"Win: {win:.2f} У.Е."
                if bonus_win > 0:
                    win_text += f"   Bonus: {bonus_win:.2f} У.Е."

                screen.blit(small_font.render(win_text, True, GOLD), btn_rect.move(10, 45))

            except:
                screen.blit(small_font.render(spin_file, True, WHITE), btn_rect.move(10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        # --- события ---
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if close_btn.collidepoint(mx, my):
                    play_sound("button")
                    replay_open = False

                for spin_file, btn_rect in spin_buttons:
                    if btn_rect.collidepoint(mx, my):
                        play_sound("button")
                        selected_spin = spin_file
                        replay_open = False

            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(scroll_offset - event.y, len(spin_files) - max_visible))

        # --- запуск реплея ---
        if selected_spin:
            with open(os.path.join(folder, selected_spin)) as f:
                data = json.load(f)

            seed = data.get("seed")
            bet_data = {
                "bet_multiplier": data.get("bet_multiplier", 1),
                "base_bet": data.get("base_bet", base_bet),
                "free_buy_fs": data.get("free_buy_fs", False)
            }

            if seed is not None:
                board = replay_spin(seed, window_width, window_height, board, bet_data)

            selected_spin = None

    return board



def replay_spin(seed, window_width, window_height, board, bet_multiplier):
    """Воспроизводит спин по заданному сиду и модификатору ставки без изменения баланса."""
    global button_opacity, total_crystals_collected, filled_counters, current_counter_level, bonus_count, is_buy_fs, is_buy_fs_300, is_buy_fs_900, is_buy_fs_3600, is_buy_fs_18000, is_40_40_20, is_buy_super, last_win, is_super_spin
    global is_3_lvl, is_garant_spin, is_bet_plus, is_bet_plus_plus, is_bandit_mode, bet, superbonus_count, base_bet, active_modifier, balance, is_god_mode_bet

    # Сохраняем текущее состояние
    original_board = [row[:] for row in board]
    original_total_crystals = total_crystals_collected
    original_filled_counters = filled_counters
    original_counter_level = current_counter_level
    original_bonus_count = bonus_count
    original_superbonus_count = superbonus_count
    original_is_buy_fs = is_buy_fs
    original_is_buy_fs_300 = is_buy_fs_300
    original_is_buy_fs_900 = is_buy_fs_900
    original_is_buy_fs_3600 = is_buy_fs_3600
    original_is_buy_fs_18000 = is_buy_fs_18000
    original_is_40_40_20 = is_40_40_20
    original_is_buy_super = is_buy_super
    original_last_win = last_win
    original_is_3_lvl = is_3_lvl
    original_is_super_spin = is_super_spin
    original_is_garant_spin = is_garant_spin
    original_is_bet_plus = is_bet_plus
    original_is_bet_plus_plus = is_bet_plus_plus
    original_is_bandit_mode = is_bandit_mode
    original_is_god_mode_bet = is_god_mode_bet
    original_bet = bet
    original_base_bet = base_bet
    original_active_modifier = active_modifier
    original_balance = balance

    # СБРАСЫВАЕМ СЧЁТЧИКИ ПЕРЕД РЕПЛЕЕМ
    total_crystals_collected = 0
    filled_counters = 0
    current_counter_level = 0
    bonus_count = 0
    superbonus_count = 0

    # Восстанавливаем base_bet и рассчитываем bet из сохранённых данных
    base_bet = bet_multiplier.get('base_bet', base_bet)
    bet = base_bet * bet_multiplier.get('bet_multiplier', 1)

    # Устанавливаем режимы по bet_multiplier
    is_god_mode_bet = bet_multiplier.get('bet_multiplier') == 2000
    is_super_spin = bet_multiplier.get('bet_multiplier') == 7.5
    is_3_lvl = bet_multiplier.get('bet_multiplier') == 10
    is_garant_spin = bet_multiplier.get('bet_multiplier') == 5
    is_bet_plus_plus = bet_multiplier.get('bet_multiplier') == 3
    is_bet_plus = bet_multiplier.get('bet_multiplier') == 2
    is_bandit_mode = bet_multiplier.get('bet_multiplier') == 25
    # If bet_multiplier indicates a buy, or saved data included a free_buy_fs flag, enable buy flags
    is_buy_fs = bet_multiplier.get('bet_multiplier') == 100 or bet_multiplier.get('free_buy_fs', False)
    is_buy_super = bet_multiplier.get('bet_multiplier') == 500
    is_buy_fs_300 = bet_multiplier.get('bet_multiplier') == 300
    is_buy_fs_900 = bet_multiplier.get('bet_multiplier') == 900
    is_buy_fs_3600 = bet_multiplier.get('bet_multiplier') == 3600
    is_buy_fs_18000 = bet_multiplier.get('bet_multiplier') == 18000
    is_40_40_20 = bet_multiplier.get('bet_multiplier') == 200

    # Устанавливаем active_modifier на основе режимов (аналогично обычному спину)
    active_modifier = 'god_mode' if is_god_mode_bet else '3lvl' if is_3_lvl else 'garant_spin' if is_garant_spin else 'super_spin' if is_super_spin else 'bonus_hunt_3x' if is_bet_plus_plus else 'bonus_hunt_2x' if is_bet_plus else 'bonus_buy' if (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20) else None
    if is_super_spin == True:
        filled_counters = 1
    # Устанавливаем сид и выполняем спин
    random.seed(seed)
    # Consume the same pre-board RNG call that `spin_animation` makes
    # (the free-buy check) so the RNG sequence is identical for replay.
    try:
        try:
            special_modes_selected = (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20 or is_3_lvl or is_garant_spin or is_bandit_mode or is_super_spin)
        except NameError:
            special_modes_selected = (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20)

        if not special_modes_selected:
            if is_bet_plus_plus:
                denom = 78
            elif is_bet_plus:
                denom = 132
            else:
                denom = 264

            consumed_trigger = (random.randint(1, denom) == 1)
            # If saved data disagrees with the consumed RNG outcome, log for debugging
            try:
                if consumed_trigger != bool(bet_multiplier.get('free_buy_fs', False)):
                    pass
            except Exception:
                pass
    except Exception:
        pass
    animate_fall_out(board, window_width, window_height, do_fade=True)
    time.sleep(0.5)
    new_board, gigablocks = generate_board()
    animate_drop_in(new_board, window_width, window_height, button_opacity=button_opacity)
    total_win, final_board = collection_cycle(new_board, window_width, window_height, seed=seed, is_replay=True)
    screen.blit(scaled_background, (0, 0))
    draw_board(final_board, window_width, window_height, [], button_opacity=button_opacity)
    pygame.display.flip()

    # Восстанавливаем состояние
    total_crystals_collected = original_total_crystals
    filled_counters = original_filled_counters
    current_counter_level = original_counter_level
    bonus_count = original_bonus_count
    superbonus_count = original_superbonus_count
    is_buy_fs = original_is_buy_fs
    is_buy_fs_300 = original_is_buy_fs_300
    is_buy_fs_900 = original_is_buy_fs_900
    is_buy_fs_3600 = original_is_buy_fs_3600
    is_buy_fs_18000 = original_is_buy_fs_18000
    is_40_40_20 = original_is_40_40_20
    is_buy_super = original_is_buy_super
    last_win = original_last_win
    is_3_lvl = original_is_3_lvl
    is_super_spin = original_is_super_spin
    is_garant_spin = original_is_garant_spin
    is_bet_plus = original_is_bet_plus
    is_bet_plus_plus = original_is_bet_plus_plus
    is_bandit_mode = original_is_bandit_mode
    is_god_mode_bet = original_is_god_mode_bet
    bet = original_bet
    base_bet = original_base_bet
    active_modifier = original_active_modifier
    balance = original_balance  # Восстанавливаем active_modifier

    return final_board

def animate_drop_in(new_board, window_width, window_height, button_opacity=0):
    duration_per_symbol = 0.5 if fast_spin else 0.65  # Дольше для bounce
    delay_per_column = 0.05 if fast_spin else 0.08  # Задержка между колонками
    grid_height = GRID_ROWS * CELL_SIZE
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    start_offset = -grid_height - offset_y_grid - 150  # Начинаем выше

    symbol_offsets = [[start_offset for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    start_times = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    actual_start_times = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    active_animations = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    played_sounds = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # Падение волнами по колонкам
    current_time = time.time()
    for c in range(GRID_COLS):
        base_delay = c * delay_per_column
        for r in range(GRID_ROWS - 1, -1, -1):
            jitter = random.uniform(-0.01, 0.01)
            start_times[r][c] = current_time + base_delay + (GRID_ROWS - 1 - r) * 0.015 + jitter

    while any(active_animations[r][c] or start_times[r][c] is not None for r in range(GRID_ROWS) for c in range(GRID_COLS)):
        now = time.time()
        
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if start_times[r][c] is not None and now >= start_times[r][c]:
                    active_animations[r][c] = True
                    actual_start_times[r][c] = now
                    start_times[r][c] = None
                
                if active_animations[r][c]:
                    elapsed = now - actual_start_times[r][c]
                    progress = min(elapsed / duration_per_symbol, 1.0)
                    
                    # BOUNCE EASING
                    eased = ease_out_bounce(progress)
                    symbol_offsets[r][c] = start_offset * (1 - eased)
                    
                    if progress >= 1.0 and not played_sounds[r][c]:
                        symbol = new_board[r][c]
                        is_premium = symbol in ['high1', 'high2', 'high3', 'high4']
                        
                        play_sound('padenie_popuga' if is_premium else 'padenie')
                        played_sounds[r][c] = True
                        active_animations[r][c] = False
                        symbol_offsets[r][c] = 0
        
        screen.blit(scaled_background, (0, 0))
        draw_board(new_board, window_width, window_height, [], symbol_offsets=symbol_offsets, button_opacity=button_opacity)
        
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

    screen.blit(scaled_background, (0, 0))
    draw_board(new_board, window_width, window_height, [], button_opacity=button_opacity)
    pygame.display.flip()

def animate_cascade(board, owners, window_width, window_height, button_opacity=0, respawn_parrots=True):
    global dead_parrots, bandit_active, bandit_pos
    
    # Сохраняем текущую позицию бандита и временно обнуляем её
    # чтобы draw_board не рисовал бандита из глобальной переменной
    saved_bandit_pos = bandit_pos
    bandit_pos = None
    
    # ШАГ 1: Создаём промежуточную доску (старые символы падают вниз)
    intermediate_board = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    intermediate_owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    falling_distances = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    for c in range(GRID_COLS):
        bottom = GRID_ROWS - 1
        for r in range(GRID_ROWS - 1, -1, -1):
            if board[r][c] != '':
                intermediate_board[bottom][c] = board[r][c]
                intermediate_owners[bottom][c] = owners[r][c]
                falling_distances[bottom][c] = (bottom - r) * CELL_SIZE
                bottom -= 1
    
    # Анимация падения старых символов с bounce эффектом
    duration_fall = 0.5 if fast_spin else 0.90
    delay_per_column = 0.05 if fast_spin else 0.08
    start_times_fall = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    actual_start_times_fall = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    active_animations_fall = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    played_sounds_fall = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    symbol_offsets_fall = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    # Инициализируем начальные смещения для символов (показываем их в исходных позициях)
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if intermediate_board[r][c] != '':
                symbol_offsets_fall[r][c] = -falling_distances[r][c]
    
    current_time = time.time()
    for c in range(GRID_COLS):
        base_delay = c * delay_per_column
        for r in range(GRID_ROWS - 1, -1, -1):
            if intermediate_board[r][c] != '':
                jitter = random.uniform(-0.01, 0.01)
                start_times_fall[r][c] = current_time + base_delay + jitter
    
    # Анимация падения старых символов
    while any(active_animations_fall[r][c] or start_times_fall[r][c] is not None for r in range(GRID_ROWS) for c in range(GRID_COLS)):
        now = time.time()
        
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if start_times_fall[r][c] is not None and now >= start_times_fall[r][c]:
                    active_animations_fall[r][c] = True
                    actual_start_times_fall[r][c] = now
                    start_times_fall[r][c] = None
                
                if active_animations_fall[r][c]:
                    elapsed = now - actual_start_times_fall[r][c]
                    progress = min(elapsed / duration_fall, 1.0)
                    
                    eased = ease_out_bounce(progress)
                    symbol_offsets_fall[r][c] = falling_distances[r][c] * (eased - 1)
                    
                    if progress >= 1.0 and not played_sounds_fall[r][c]:
                        # Воспроизводим звук только если символ действительно падал
                        if falling_distances[r][c] > 0:
                            symbol = intermediate_board[r][c]
                            if symbol.startswith('high'):
                                play_sound('padenie_popuga')
                            else:
                                play_sound('padenie')
                        played_sounds_fall[r][c] = True
                        active_animations_fall[r][c] = False
                        symbol_offsets_fall[r][c] = 0
        
        screen.blit(scaled_background, (0, 0))
        draw_board(intermediate_board, window_width, window_height, [], symbol_offsets=symbol_offsets_fall, button_opacity=button_opacity)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    
    # Пауза 0.3 секунды
    time.sleep(0.3)
    
    # ШАГ 2: Создаём новую доску с новыми символами сверху
    new_board = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    new_owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    new_random_slots = []
    
    # Копируем упавшие символы
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            new_board[r][c] = intermediate_board[r][c]
            new_owners[r][c] = intermediate_owners[r][c]
    
    # Добавляем новые символы в пустые ячейки сверху
    for c in range(GRID_COLS):
        for r in range(GRID_ROWS):
            if new_board[r][c] == '':
                new_board[r][c] = get_random_symbol_with_chance()
                new_owners[r][c] = ''
                new_random_slots.append((r, c))
    
    # Ограничиваем количество бонусов, супербонусов и ключей на доске после каскада
    # Учитываем уже собранные символы за текущий спин
    # ВАЖНО: заменяем только НОВЫЕ символы (из new_random_slots), чтобы не "телепортировать" существующие
    global collected_bonus_this_spin, collected_superbonus_this_spin, collected_key_this_spin
    
    key_positions_new = []  # Только новые ключи
    bonus_positions_new = []  # Только новые бонусы
    superbonus_positions_new = []  # Только новые супербонусы
    key_positions_old = []  # Старые ключи (были до каскада)
    bonus_positions_old = []  # Старые бонусы (были до каскада)
    superbonus_positions_old = []  # Старые супербонусы (были до каскада)
    
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            is_new = (r, c) in new_random_slots
            if new_board[r][c] == 'key':
                if is_new:
                    key_positions_new.append((r, c))
                else:
                    key_positions_old.append((r, c))
            elif new_board[r][c] == 'bonus':
                if is_new:
                    bonus_positions_new.append((r, c))
                else:
                    bonus_positions_old.append((r, c))
            elif new_board[r][c] == 'superbonus':
                if is_new:
                    superbonus_positions_new.append((r, c))
                else:
                    superbonus_positions_old.append((r, c))
    
    # Максимум ключей за весь спин = 1, учитываем уже собранные и старые на доске
    max_keys_allowed = max(0, 1 - collected_key_this_spin - len(key_positions_old))
    if len(key_positions_new) > max_keys_allowed:
        if max_keys_allowed > 0:
            keep_keys = random.sample(key_positions_new, max_keys_allowed)
            for pos in key_positions_new:
                if pos not in keep_keys:
                    new_board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
        else:
            # Заменяем все НОВЫЕ ключи
            for pos in key_positions_new:
                new_board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
    
    # Максимум бонусов за весь спин = 3, учитываем уже собранные и старые на доске
    max_bonuses_allowed = max(0, 3 - collected_bonus_this_spin - len(bonus_positions_old))
    if len(bonus_positions_new) > max_bonuses_allowed:
        if max_bonuses_allowed > 0:
            keep_bonuses = random.sample(bonus_positions_new, max_bonuses_allowed)
            for pos in bonus_positions_new:
                if pos not in keep_bonuses:
                    new_board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
        else:
            # Заменяем все НОВЫЕ бонусы
            for pos in bonus_positions_new:
                new_board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
    
    # Максимум супербонусов за весь спин = 1, учитываем уже собранные и старые на доске
    max_superbonuses_allowed = max(0, 1 - collected_superbonus_this_spin - len(superbonus_positions_old))
    if len(superbonus_positions_new) > max_superbonuses_allowed:
        if max_superbonuses_allowed > 0:
            keep_superbonuses = random.sample(superbonus_positions_new, max_superbonuses_allowed)
            for pos in superbonus_positions_new:
                if pos not in keep_superbonuses:
                    new_board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
        else:
            # Заменяем все НОВЫЕ супербонусы
            for pos in superbonus_positions_new:
                new_board[pos[0]][pos[1]] = get_random_symbol(str(random.randint(1, 4)))
    
    # Респавн попугаев
    respawned_parrots = []  # Список позиций респавненных попугаев
    if respawn_parrots:
        respawn_queue = []

        if not bandit_active and dead_parrots:
            respawn_queue.extend(dead_parrots)
            dead_parrots = []

        current_parrots = [symbol for row in new_board for symbol in row if symbol.startswith('high')]
        for parrot_sym in active_parrots:
            if parrot_sym not in current_parrots and parrot_sym not in respawn_queue:
                respawn_queue.append(parrot_sym)

        available_slots = new_random_slots[:] if new_random_slots else [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)]
        random.shuffle(available_slots)
        leftovers = []
        for parrot in respawn_queue:
            if available_slots:
                r, c = available_slots.pop()
                new_board[r][c] = parrot
                new_owners[r][c] = ''
                respawned_parrots.append((r, c))  # Запоминаем позицию респавненного попугая
            else:
                leftovers.append(parrot)

        if leftovers and not bandit_active:
            dead_parrots.extend(leftovers)
    
    # Анимация падения новых символов с bounce эффектом
    grid_height = GRID_ROWS * CELL_SIZE
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    start_offset_new = -grid_height - offset_y_grid - 150
    
    symbol_offsets_new = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    start_times_new = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    actual_start_times_new = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    active_animations_new = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    played_sounds_new = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    # Устанавливаем время старта только для новых символов и респавненных попугаев
    current_time_new = time.time()
    for c in range(GRID_COLS):
        base_delay = c * delay_per_column
        for r in range(GRID_ROWS):
            if (r, c) in new_random_slots or (r, c) in respawned_parrots:
                jitter = random.uniform(-0.01, 0.01)
                start_times_new[r][c] = current_time_new + base_delay + jitter
                symbol_offsets_new[r][c] = start_offset_new
    
    # Анимация падения новых символов
    while any(active_animations_new[r][c] or start_times_new[r][c] is not None for r in range(GRID_ROWS) for c in range(GRID_COLS)):
        now = time.time()
        
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if start_times_new[r][c] is not None and now >= start_times_new[r][c]:
                    active_animations_new[r][c] = True
                    actual_start_times_new[r][c] = now
                    start_times_new[r][c] = None
                
                if active_animations_new[r][c]:
                    elapsed = now - actual_start_times_new[r][c]
                    progress = min(elapsed / duration_fall, 1.0)
                    
                    eased = ease_out_bounce(progress)
                    symbol_offsets_new[r][c] = start_offset_new * (1 - eased)
                    
                    if progress >= 1.0 and not played_sounds_new[r][c]:
                        symbol = new_board[r][c]
                        if symbol.startswith('high'):
                            play_sound('padenie_popuga')
                        else:
                            play_sound('padenie')
                        played_sounds_new[r][c] = True
                        active_animations_new[r][c] = False
                        symbol_offsets_new[r][c] = 0
        
        screen.blit(scaled_background, (0, 0))
        draw_board(new_board, window_width, window_height, [], symbol_offsets=symbol_offsets_new, button_opacity=button_opacity)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

    # Восстанавливаем позицию бандита
    bandit_pos = saved_bandit_pos
    
    return new_board, new_owners

def animate_dance(board, window_width, window_height, parrot_pos, parrot, button_opacity):
    # Остановка фоновой музыки
    if is_bonus_game:
        stop_bonus_sound()
    else:
        pygame.mixer.music.stop()
    
    # Воспроизведение dance.ogg с зацикливанием
    play_sound('dance', loop=True)
    
    # Анимация прыжков попугая (2 раза вверх-вниз за 2 секунды)
    duration = 1.0 if fast_spin else 2.0  # Ускоряем танец при fast_spin
    cycles = 2
    frame_time = duration / (cycles * 2)  # Время на подъем и опускание
    max_offset = -30  # Максимальное смещение вверх
    parrot_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    start_time = time.time()
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        cycle_progress = (elapsed % (frame_time * 2)) / frame_time
        if cycle_progress < 1:
            offset = max_offset * math.sin(math.pi * cycle_progress)  # Плавный подъем/опускание
        else:
            offset = max_offset * math.sin(math.pi * (2 - cycle_progress))
        parrot_offsets[parrot_pos[0]][parrot_pos[1]] = offset
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity, parrot_offsets=parrot_offsets)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

def animate_symbols_fall_out(board, window_width, window_height, button_opacity=0):
    """Плавно уводит все НЕ-попугаи вниз с доски в стиле падения старта спина."""
    symbol_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)
                        if board[r][c] != '' and not board[r][c].startswith('high')]
    if not symbol_positions:
        return board

    duration = 0.9 if fast_spin else 1.2
    start_time = time.time()
    grid_height = GRID_ROWS * CELL_SIZE
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    target_offset = grid_height + window_height - offset_y_grid

    while True:
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        eased_progress = ease_in_out_cubic(progress)
        offset_y = eased_progress * target_offset * 1.5

        symbol_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for r, c in symbol_positions:
            symbol_offsets[r][c] = offset_y

        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], symbol_offsets=symbol_offsets, button_opacity=button_opacity)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

        if progress >= 1.0:
            break

    for r, c in symbol_positions:
        board[r][c] = ''
    return board

def show_maxwin_congrats(window_width, window_height):
    """Показывает окно поздравления с кнопкой OK."""
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(BIG_WIN_BG)
    title_font = pygame.font.SysFont("serif", 48)
    text_font = pygame.font.SysFont("serif", 30)

    title_text = title_font.render("MAX WIN!", True, GOLD)
    body_text = text_font.render("ПОЗДРАВЛЯЕМ С МАКСИМАЛЬНЫМ ВЫИГРЫШЕМ", True, WHITE)

    title_rect = title_text.get_rect(center=(window_width // 2, window_height // 2 - 60))
    body_rect = body_text.get_rect(center=(window_width // 2, window_height // 2 - 10))

    ok_button = pygame.Rect(window_width // 2 - 75, window_height // 2 + 40, 150, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if ok_button.collidepoint(mx, my):
                    play_sound('button')
                    return

        screen.blit(bg_surface, (0, 0))
        screen.blit(title_text, title_rect)
        screen.blit(body_text, body_rect)
        pygame.draw.rect(screen, (0, 200, 0), ok_button, border_radius=8)
        screen.blit(small_font.render("OK", True, WHITE), ok_button.move(55, 12))
        pygame.display.flip()
        clock.tick(FPS)

def maybe_trigger_maxwin(board, window_width, window_height):
    global maxwin_triggered, maxwin_abort_cycle
    if maxwin_triggered:
        return True
    if last_win > base_bet * 200000:
        maxwin_triggered = True
        maxwin_abort_cycle = True
        run_maxwin_sequence(board, window_width, window_height)
        return True
    return False

def run_maxwin_sequence(board, window_width, window_height):
    """Запускает сценарий максимального выигрыша (200000x base_bet)."""
    global hide_last_win_info, last_win

    target_win = base_bet * 2000000000000000000000000000000000000000000000000000000

    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    stop_dance_sound()

    hide_last_win_info = True

    screen.blit(scaled_background, (0, 0))
    draw_board(board, window_width, window_height, [], button_opacity=0)
    pygame.display.flip()

    time.sleep(1.0)
    play_sound('spin')
    board = animate_symbols_fall_out(board, window_width, window_height, button_opacity=0)

    try:
        play_music_once('maxwin')
    except Exception:
        pass

    counter_font = pygame.font.SysFont("serif", 96)
    duration = 39.0
    start_time = time.time()
    cycles = 2
    frame_time = 2.0 / (cycles * 2)
    max_offset = -30

    parrot_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith('high')]

    while True:
        elapsed = time.time() - start_time
        t = min(elapsed / duration, 1.0)
        # Квадратичное ускорение: сначала медленно, потом всё быстрее
        progress = t * t
        display_win = target_win * progress

        cycle_progress = (elapsed % (frame_time * 2)) / frame_time
        if cycle_progress < 1:
            offset = max_offset * math.sin(math.pi * cycle_progress)
        else:
            offset = max_offset * math.sin(math.pi * (2 - cycle_progress))

        parrot_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for r, c in parrot_positions:
            parrot_offsets[r][c] = offset

        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0, parrot_offsets=parrot_offsets)

        counter_text = counter_font.render(f"{display_win:.2f} У.Е.", True, GOLD)
        counter_rect = counter_text.get_rect(center=(window_width // 2, window_height // 2))
        screen.blit(counter_text, counter_rect)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

        if t >= 1.0:
            break

    hold_start = time.time()
    while time.time() - hold_start < 5.0:
        elapsed = time.time() - hold_start
        cycle_progress = (elapsed % (frame_time * 2)) / frame_time
        if cycle_progress < 1:
            offset = max_offset * math.sin(math.pi * cycle_progress)
        else:
            offset = max_offset * math.sin(math.pi * (2 - cycle_progress))

        parrot_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for r, c in parrot_positions:
            parrot_offsets[r][c] = offset

        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0, parrot_offsets=parrot_offsets)

        counter_text = counter_font.render(f"{target_win:.2f} У.Е.", True, GOLD)
        counter_rect = counter_text.get_rect(center=(window_width // 2, window_height // 2))
        screen.blit(counter_text, counter_rect)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

    show_maxwin_congrats(window_width, window_height)
    try:
        play_background_music('song')
    except Exception:
        pass
    hide_last_win_info = False
    last_win = target_win

    # Перерисовываем интерфейс после закрытия окна поздравления
    global button_opacity
    button_opacity = 255
    screen.blit(scaled_background, (0, 0))
    draw_board(board, window_width, window_height, [], button_opacity=255)
    pygame.display.flip()

    return board

def show_win_screen(board, window_width, window_height, parrot_win, button_opacity):
    # Остановка музыки dance.ogg
    stop_dance_sound()
    
    # Полупрозрачный фон для Big Win
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(BIG_WIN_BG)
    big_win_text = font.render("BIG WIN!", True, GOLD)
    text_rect = big_win_text.get_rect(center=(window_width // 2, window_height // 2 - 50))
    
    # Определение стадий и длительностей
    win_stages = [
        ('bigwin', 0, 40, 3.2),
        ('superwin', 40, 60, 3.2),
        ('megawin', 60, 80, 6.4),
        ('epicwin', 80, 200, 6.4),
        ('goldrush', 200, float('inf'), 6.4)
    ]
    
    # Настройка анимации попугаев
    parrot_positions = [
        (window_width // 2 - int(CELL_SIZE * IMAGE_SCALE * 2), window_height // 2 - 150),  # high1win (красный)
        (window_width // 2 - int(CELL_SIZE * IMAGE_SCALE * 0.5), window_height // 2 - 150),  # high2win (фиолетовый)
        (window_width // 2 + int(CELL_SIZE * IMAGE_SCALE * 0.5), window_height // 2 - 150),  # high3win (зеленый)
        (window_width // 2 + int(CELL_SIZE * IMAGE_SCALE * 2), window_height // 2 - 150)   # high4win (синий)
    ]
    parrot_offsets = [0] * 4  # Смещения для анимации каждого попугая
    cycles = 2
    frame_time = 2.0 / (cycles * 2)  # Время на подъем и опускание
    max_offset = -30  # Максимальное смещение вверх
    rotation_angle = 0  # Угол вращения для синего попугая
    
    current_x = parrot_win / base_bet  # Множитель выигрыша
    current_display_win = 0
    stage_index = 0
    
    for stage_name, start_x, end_x, duration in win_stages:
        if current_x > start_x:
            play_sound(stage_name)
            target_x = min(current_x, end_x)
            target_win = target_x * base_bet
            stage_start_time = time.time()
            while time.time() - stage_start_time < duration:
                elapsed = time.time() - stage_start_time
                progress = min(elapsed / duration, 1.0)
                eased_progress = 1 - (1 - progress) ** 3
                display_win = current_display_win + (target_win - current_display_win) * eased_progress
                
                # Анимация попугаев
                cycle_progress = (elapsed % (frame_time * 2)) / frame_time
                if cycle_progress < 1:
                    offset = max_offset * math.sin(math.pi * cycle_progress)
                else:
                    offset = max_offset * math.sin(math.pi * (2 - cycle_progress))
                
                # Определяем, какие попугаи отображаются
                active_parrots = []
                if start_x >= 0:  # от 0x (bigwin)
                    active_parrots.append('high1win')  # Красный
                if start_x >= 40:  # от 40x (superwin)
                    active_parrots.append('high2win')  # Фиолетовый
                if start_x >= 60:  # от 60x (megawin)
                    active_parrots.append('high3win')  # Зеленый
                if start_x >= 80:  # от 80x (epicwin)
                    active_parrots.append('high4win')  # Синий
                
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
                screen.blit(bg_surface, (0, 0))
                screen.blit(big_win_text, text_rect)
                counter_text = font.render(f"{display_win:.2f} У.Е.", True, WHITE)
                counter_rect = counter_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
                screen.blit(counter_text, counter_rect)
                
                # Отрисовка танцующих попугаев
                for i, parrot in enumerate(['high1win', 'high2win', 'high3win', 'high4win']):
                    if parrot in active_parrots:
                        image = symbol_images[parrot]
                        if parrot == 'high4win' and stage_name == 'epicwin':
                            # Вращение синего попугая
                            rotation_angle = (rotation_angle + 10) % 360
                            rotated_image = pygame.transform.rotate(image, rotation_angle)
                            image_rect = rotated_image.get_rect(center=(parrot_positions[i][0], parrot_positions[i][1] + offset))
                            screen.blit(rotated_image, image_rect)
                        else:
                            image_rect = image.get_rect(center=(parrot_positions[i][0], parrot_positions[i][1] + offset))
                            screen.blit(image, image_rect)
                
                pygame.display.flip()
                clock.tick(ANIMATION_FPS)
            current_display_win = target_win
            if current_display_win >= parrot_win:
                break
        stage_index += 1
    
    # Воспроизведение end.ogg или eng.ogg
    if current_x < 40:
        play_sound('end')
    else:
        play_sound('end')
    
    # Ожидание 1.5 секунды с анимацией попугаев
    start_time = time.time()
    while time.time() - start_time < 2:
        elapsed = time.time() - start_time
        cycle_progress = (elapsed % (frame_time * 2)) / frame_time
        if cycle_progress < 1:
            offset = max_offset * math.sin(math.pi * cycle_progress)
        else:
            offset = max_offset * math.sin(math.pi * (2 - cycle_progress))
        
        active_parrots = []
        if current_x >= 0:
            active_parrots.append('high1win')
        if current_x >= 40:
            active_parrots.append('high2win')
        if current_x >= 60:
            active_parrots.append('high3win')
        if current_x >= 80:
            active_parrots.append('high4win')
        
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        screen.blit(bg_surface, (0, 0))
        screen.blit(big_win_text, text_rect)
        counter_text = font.render(f"{parrot_win:.2f} У.Е.", True, WHITE)
        counter_rect = counter_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
        screen.blit(counter_text, counter_rect)
        
        for i, parrot in enumerate(['high1win', 'high2win', 'high3win', 'high4win']):
            if parrot in active_parrots:
                image = symbol_images[parrot]
                if parrot == 'high4win' and current_x >= 80 and current_x < 200:
                    rotation_angle = (rotation_angle + 10) % 360
                    rotated_image = pygame.transform.rotate(image, rotation_angle)
                    image_rect = rotated_image.get_rect(center=(parrot_positions[i][0], parrot_positions[i][1] + offset))
                    screen.blit(rotated_image, image_rect)
                else:
                    image_rect = image.get_rect(center=(parrot_positions[i][0], parrot_positions[i][1] + offset))
                    screen.blit(image, image_rect)
        
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    
    # Плавное исчезновение фона с анимацией попугаев
    fade_start_time = time.time()
    while time.time() - fade_start_time < BIG_WIN_FADE_OUT:
        elapsed = time.time() - fade_start_time
        progress = elapsed / BIG_WIN_FADE_OUT
        alpha = int(200 * (1 - progress))
        bg_surface.set_alpha(alpha)
        big_win_text.set_alpha(alpha)
        counter_text = font.render(f"{parrot_win:.2f} У.Е.", True, WHITE)
        counter_text.set_alpha(alpha)
        counter_rect = counter_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
        
        cycle_progress = (elapsed % (frame_time * 2)) / frame_time
        if cycle_progress < 1:
            offset = max_offset * math.sin(math.pi * cycle_progress)
        else:
            offset = max_offset * math.sin(math.pi * (2 - cycle_progress))
        
        active_parrots = []
        if current_x >= 0:
            active_parrots.append('high1win')
        if current_x >= 40:
            active_parrots.append('high2win')
        if current_x >= 60:
            active_parrots.append('high3win')
        if current_x >= 80:
            active_parrots.append('high4win')
        
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        screen.blit(bg_surface, (0, 0))
        screen.blit(big_win_text, text_rect)
        screen.blit(counter_text, counter_rect)
        
        for i, parrot in enumerate(['high1win', 'high2win', 'high3win', 'high4win']):
            if parrot in active_parrots:
                image = symbol_images[parrot]
                if parrot == 'high4win' and current_x >= 80 and current_x < 200:
                    rotation_angle = (rotation_angle + 10) % 360
                    rotated_image = pygame.transform.rotate(image, rotation_angle)
                    rotated_image.set_alpha(alpha)
                    image_rect = rotated_image.get_rect(center=(parrot_positions[i][0], parrot_positions[i][1] + offset))
                    screen.blit(rotated_image, image_rect)
                else:
                    image_copy = image.copy()  # Создаем копию изображения
                    image_copy.set_alpha(alpha)
                    image_rect = image_copy.get_rect(center=(parrot_positions[i][0], parrot_positions[i][1] + offset))
                    screen.blit(image_copy, image_rect)
        
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    
    # Возобновление фоновой музыки после исчезновения экрана
    if is_bonus_game:
        play_sound('bonus', loop=True)
    else:
        play_background_music()

def find_popugay(board, popugay):
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if board[r][c] == popugay:
                return (r, c)
    return None


def show_parrot_request(board, window_width, window_height, parrot_pos, image_name, sound_name):
    """Показывает картинку `image_name`.png справа-вверху от `parrot_pos` и воспроизводит `sound_name`.ogg на 1 секунду."""
    try:
        img_path = os.path.join('images', f'{image_name}.png')
        img = pygame.image.load(img_path)
        img = pygame.transform.scale(img, (int(CELL_SIZE * 0.9), int(CELL_SIZE * 0.9)))
    except Exception:
        img = None
    play_sound(sound_name)
    # Координаты для отображения: немного справа и выше попугая
    grid_width = GRID_COLS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    offset_y_grid = (window_height - GRID_ROWS * CELL_SIZE - INFO_PANEL_HEIGHT) // 2
    r, c = parrot_pos
    x = offset_x + c * CELL_SIZE + CELL_SIZE // 2 + 20
    y = offset_y_grid + r * CELL_SIZE - 20
    start = time.time()
    while time.time() - start < 1.0:
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0)
        if img:
            rect = img.get_rect(center=(x, y))
            screen.blit(img, rect)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)


def attempt_parrot_swaps(board, window_width, window_height):
    """Проверяет рядом стоящие пары попугаев и с шансом 20% выполняет обмен местами
    если после обмена попугай, который просил, сможет собрать свои кристаллы.
    Возвращает True, если был выполнен хотя бы один обмен (тогда нужно заново запустить cycle).
    """
    pairs = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            sym = board[r][c]
            if not sym.startswith('high'):
                continue
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and board[nr][nc].startswith('high'):
                    # добавляем пару в упорядоченном виде, чтобы не дублировать
                    a = (r, c); b = (nr, nc)
                    if (b, a) not in pairs:
                        pairs.append((a, b))

    random.shuffle(pairs)
    swap_chance = 0.2  # вероятность запроса обмена (20%)
    for a_pos, b_pos in pairs:
        # шанс для одного из попугаев попросить обмен
        rv = random.random()
        if rv >= swap_chance:
            continue

        # Попробуем оба попугая в паре в случайном порядке
        order = [a_pos, b_pos]
        random.shuffle(order)
        for asker_pos in order:
            other_pos = b_pos if asker_pos == a_pos else a_pos
            ar, ac = asker_pos
            orr, oc = other_pos
            asker_sym = board[ar][ac]
            try:
                asker_color = asker_sym[-1]
            except Exception:
                continue

            # Быстрая adjacency-проверка на новой позиции (other_pos)
            crystal_prefix = f'low{asker_color}'
            adj_count = 0
            for dr, dc in directions:
                nr, nc = orr + dr, oc + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and board[nr][nc].startswith(crystal_prefix):
                    adj_count += 1

            if adj_count > 0:
                can_collect = True
                available = [(nr, nc) for dr, dc in directions for nr, nc in [(orr + dr, oc + dc)] if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and board[nr][nc].startswith(crystal_prefix)]
            else:
                # Fallback: строгая проверка достижимости (reachability)
                board[ar][ac], board[orr][oc] = board[orr][oc], board[ar][ac]
                crystal_targets = [f'low{asker_color}_{i}' for i in range(1, 8)]
                owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                available = get_available_targets(board, owners, (orr, oc), crystal_targets, asker_color)
                can_collect = bool(available)
                board[ar][ac], board[orr][oc] = board[orr][oc], board[ar][ac]

            if not can_collect:
                # попробуем следующего попугая в паре
                continue

            # Показываем последовательность: asker -> havashuga, other -> zaebis, затем обмениваем
            show_parrot_request(board, window_width, window_height, asker_pos, 'havashuga', 'havashuga')
            show_parrot_request(board, window_width, window_height, other_pos, 'zaebis', 'zaebis')

            # Выполняем обмен на доске
            board[ar][ac], board[orr][oc] = board[orr][oc], board[ar][ac]
            # Небольшая визуализация обмена
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=0)
            pygame.display.flip()
            time.sleep(0.25)

            return True
    return False

def get_available_targets(board, owners, start_pos, targets, color):
    visited = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    q = deque([start_pos])
    visited[start_pos[0]][start_pos[1]] = True
    available = []

    while q:
        r, c = q.popleft()
        sym = board[r][c]
        if sym in targets and (r, c) != start_pos:
            available.append((r, c))
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and not visited[nr][nc]:
                sym = board[nr][nc]
                if sym in targets or (sym == '' and owners[nr][nc] == color):
                    visited[nr][nc] = True
                    q.append((nr, nc))
    return available

def bfs_path(board, owners, start, goal, color, targets):
    if start == goal:
        return [start]
    queue = deque([(start, [start])])
    visited = set([start])
    while queue:
        current, path = queue.popleft()
        r, c = current
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            pos = (nr, nc)
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and pos not in visited:
                sym = board[nr][nc]
                if sym in targets or (sym == '' and owners[nr][nc] == color) or pos == goal:
                    visited.add(pos)
                    new_path = path + [pos]
                    if pos == goal:
                        return new_path
                    queue.append((pos, new_path))
    return None

def a_star_path(board, owners, start, goal, color, targets, allowed_positions=None):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    pq = []
    heapq.heappush(pq, (0 + heuristic(start, goal), 0, start, [start]))
    visited = set([start])
    while pq:
        _, cost, current, path = heapq.heappop(pq)
        if current == goal:
            return path
        r, c = current
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            pos = (nr, nc)
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and pos not in visited:
                sym = board[nr][nc]
                if allowed_positions is not None:
                    # Для бандита разрешаем ходить по пустым клеткам даже с allowed_positions
                    if color == 'b':
                        # Можем идти если: это разрешенная позиция ИЛИ пустая клетка ИЛИ цель ИЛИ старт
                        can_step = (pos in allowed_positions or sym == '' or owners[nr][nc] == color or pos == goal or pos == start)
                    else:
                        if pos not in allowed_positions and pos != goal and pos != start:
                            continue
                        can_step = True
                else:
                    # Для бандита (color == 'b') разрешаем ходить по пустым клеткам
                    if color == 'b':
                        can_step = sym in targets or sym == '' or owners[nr][nc] == color or pos == goal
                    else:
                        can_step = sym in targets or (sym == '' and owners[nr][nc] == color) or pos == goal
                if can_step:
                    visited.add(pos)
                    new_cost = cost + 1
                    new_path = path + [pos]
                    heapq.heappush(pq, (new_cost + heuristic(pos, goal), new_cost, pos, new_path))
    return None

def highlight_targets(available, window_width, window_height, board, duration=0.5, button_opacity=0):
    start_time = time.time()
    while time.time() - start_time < duration:
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], highlight_cells=available, button_opacity=button_opacity)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

def upgrade_crystals(board, color, levels, all_colors=False):
    global crystal_levels
    if all_colors:
        for c in ['low1', 'low2', 'low3', 'low4']:
            crystal_levels[c] = min(7, crystal_levels[c] + levels)
    else:
        crystal_levels[f'low{color}'] = min(7, crystal_levels[f'low{color}'] + levels)
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            sym = board[r][c]
            if sym.startswith('low'):
                sym_color = sym.split('_')[0]
                board[r][c] = f'{sym_color}_{crystal_levels[sym_color]}'

def find_connected_group(board, start_pos, target_color):
    if not (0 <= start_pos[0] < GRID_ROWS and 0 <= start_pos[1] < GRID_COLS):
        return []
    start_sym = board[start_pos[0]][start_pos[1]]
    if not start_sym.startswith(f'low{target_color}'):
        return []
    visited = set()
    group = []
    queue = deque([start_pos])
    visited.add(start_pos)
    while queue:
        r, c = queue.popleft()
        group.append((r, c))
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and
                (nr, nc) not in visited and
                board[nr][nc].startswith(f'low{target_color}')):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return group

def get_random_non_crystal_symbol_with_rum_probabilities():
    """Возвращает случайный символ с учетом вероятностей для эффекта рома."""
    # Во время бонусной игры ром не должен превращать кристалл в бонус
    in_bonus = bool(globals().get('is_bonus_game'))
    # Вес для замены на 'bonus' — 0.8 при обычных спинах, 0 в бонусной игре
    bonus_weight = 0.0 if in_bonus else 0.8
    # 'low' остаётся большим весом (80) как раньше
    probabilities = {
        'levelup': 1.383,
        'levelup_2': 0.715,
        'levelup_3': 0.338,
        'levelupall': 1.092,
        'levelupall_2': 0.577,
        'levelupall_3': 0.169,
        'coin2': 0.177,
        'coin5': 0.138,
        'coin10': 0.069,
        'coin25': 0.055,
        'coin50': 0.018,
        'coin100': 0.004,
        'coin500': 0.001,
        'coin1000': 0.0005,
        'coin2500': 0.0002,
        'coinmaxwin': 0.0001,
        'rum': 0.715,
        'bonus': bonus_weight,
        'superbonus': 0.1,
        'low': 80
    }
    total_prob = sum(probabilities.values())
    probabilities = {sym: prob / total_prob * 100 for sym, prob in probabilities.items()}
    rand = random.uniform(0, 100)
    cumulative = 0
    for symbol, prob in probabilities.items():
        cumulative += prob
        if rand <= cumulative:
            if symbol == 'low':
                return get_random_symbol(str(random.randint(1, 4)))
            return symbol
    return get_random_symbol(str(random.randint(1, 4)))

def apply_rum_effect(board, owners, current_pos, popugay_color, window_width, window_height, button_opacity):
    """Применяет эффект рома, превращая соседние группы кристаллов в кристаллы цвета попугая или другие символы с заданными вероятностями."""
    adjacent_groups = []
    for dr, dc in directions:
        nr, nc = current_pos[0] + dr, current_pos[1] + dc
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
            sym = board[nr][nc]
            if sym.startswith('low') and not sym.startswith(f'low{popugay_color}'):
                group_color = sym.split('_')[0][-1]
                group = find_connected_group(board, (nr, nc), group_color)
                if group:
                    adjacent_groups.append((group, group_color))
    
    if adjacent_groups:
        # Выбираем группу с наибольшим количеством кристаллов одного цвета
        chosen_group, _ = max(adjacent_groups, key=lambda x: len(x[0]))
        for r, c in chosen_group:
            # Применяем вероятности для выбора нового символа
            new_symbol = get_random_non_crystal_symbol_with_rum_probabilities()
            if new_symbol.startswith('low'):
                new_symbol = get_random_symbol(popugay_color)  # Если 'low', заменяем на кристалл цвета попугая
            board[r][c] = new_symbol
            owners[r][c] = popugay_color
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        pygame.display.flip()

def animate_bandit_move(window_width, window_height, target_pos, board, button_opacity):
    global bandit_lair_pos
    grid_width = GRID_COLS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    offset_y_grid = (window_height - GRID_ROWS * CELL_SIZE - INFO_PANEL_HEIGHT) // 2
    start_x = bandit_lair_pos[0] + CELL_SIZE // 2
    start_y = bandit_lair_pos[1] + CELL_SIZE // 2
    end_x = offset_x + target_pos[1] * CELL_SIZE + CELL_SIZE // 2
    end_y = offset_y_grid + target_pos[0] * CELL_SIZE + CELL_SIZE // 2
    duration = 1.0
    start_time = time.time()
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        progress = elapsed / duration
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress - 100 * math.sin(math.pi * progress)  # Взлет вверх
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        bandit_image = symbol_images['bandit']
        bandit_rect = bandit_image.get_rect(center=(current_x, current_y))
        screen.blit(bandit_image, bandit_rect)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

def draw_parrot_counter(board, window_width, window_height, parrot_pos, parrot_win, alpha=255):
    """Отрисовка счетчика выигрыша над попугаем."""
    grid_width = GRID_COLS * CELL_SIZE
    grid_height = GRID_ROWS * CELL_SIZE
    offset_x = (window_width - grid_width) // 2
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    r, c = parrot_pos
    x = offset_x + c * CELL_SIZE + CELL_SIZE // 2
    y = offset_y_grid + r * CELL_SIZE  # Над попугаем
    counter_text = small_font.render(f"{parrot_win:.2f} У.Е.", True, WHITE)
    counter_text.set_alpha(int(alpha))
    text_rect = counter_text.get_rect(center=(x, y))
    screen.blit(counter_text, text_rect)

def collect_targets(board, owners, start_pos, popugay, crystal_base, color, window_width, window_height, button_opacity=0):
    global last_win, total_crystals_collected, filled_counters, current_counter_level, bonus_count
    upgrade_symbols = ['levelup', 'levelup_2', 'levelup_3', 'levelupall', 'levelupall_2', 'levelupall_3']
    coin_symbols = ['coin2', 'coin5', 'coin10', 'coin25', 'coin50', 'coin100', 'coin500', 'coin1000', 'coin2500', 'coinmaxwin']
    rum_symbols = ['rum']
    bonus_symbols = ['bonus', 'superbonus', 'key']  # Добавляем бонус, супербонус и ключ
    crystal_targets = [f'{crystal_base}_{i}' for i in range(1, 8)]
    all_targets = upgrade_symbols + crystal_targets + coin_symbols + rum_symbols + bonus_symbols
    available = get_available_targets(board, owners, start_pos, all_targets, color)
    if not available:
        return 0

    highlight_targets(available, window_width, window_height, board, duration=0.5 if fast_spin else 1.0, button_opacity=button_opacity)

    # Проверка на наличие мешка >=2x или кристалла 7 уровня
    has_big_coin = any(board[r][c] in coin_symbols and coin_multipliers[board[r][c]] >= 25 for r, c in available)
    has_level_7_crystal = any(board[r][c] == f'{crystal_base}_8' for r, c in available)

    if has_big_coin or has_level_7_crystal:
        animate_dance(board, window_width, window_height, start_pos, popugay, button_opacity)

    collected = 0
    current_pos = start_pos
    available = list(available)
    parrot_win = 0  # Накопленный выигрыш попугая в деньгах

    upgrades_and_rum = [pos for pos in available if board[pos[0]][pos[1]] in (upgrade_symbols + rum_symbols + bonus_symbols)]
    while upgrades_and_rum:
        reachable_targets = [target for target in upgrades_and_rum if a_star_path(board, owners, current_pos, target, color, all_targets)]
        if not reachable_targets:
            break
        target = min(reachable_targets, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
        path = a_star_path(board, owners, current_pos, target, color, all_targets)
        if not path:
            break

        for i in range(1, len(path)):
            next_pos = path[i]
            prev_sym = board[next_pos[0]][next_pos[1]]
            board[current_pos[0]][current_pos[1]] = ''
            owners[current_pos[0]][current_pos[1]] = color
            board[next_pos[0]][next_pos[1]] = popugay
            if prev_sym in upgrade_symbols:
                collected += 1
                play_sound('upgrade')
                if next_pos in available:
                    available.remove(next_pos)
                if next_pos in upgrades_and_rum:
                    upgrades_and_rum.remove(next_pos)
                upgrade_type = prev_sym
                levels = {'levelup': 1, 'levelup_2': 2, 'levelup_3': 3, 'levelupall': 1, 'levelupall_2': 2, 'levelupall_3': 3}
                all_colors = upgrade_type.startswith('levelupall')
                upgrade_crystals(board, color, levels[upgrade_type], all_colors)
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
                draw_parrot_counter(board, window_width, window_height, next_pos, parrot_win)
                pygame.display.flip()
                time.sleep(0.075 if fast_spin else 0.15)  # Ускоряем паузу между шагами
                available = get_available_targets(board, owners, next_pos, all_targets, color)
                upgrades_and_rum = [pos for pos in available if board[pos[0]][pos[1]] in (upgrade_symbols + rum_symbols + bonus_symbols)]
            elif prev_sym in rum_symbols:
                collected += 1
                play_sound('podbor')
                if next_pos in available:
                    available.remove(next_pos)
                if next_pos in upgrades_and_rum:
                    upgrades_and_rum.remove(next_pos)
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
                draw_parrot_counter(board, window_width, window_height, next_pos, parrot_win)
                pygame.display.flip()
                time.sleep(0.5 if fast_spin else 1.0)  # Ускоряем паузу для ромового эффекта
                apply_rum_effect(board, owners, next_pos, color, window_width, window_height, button_opacity)
                time.sleep(0.075 if fast_spin else 0.15)
                available = get_available_targets(board, owners, next_pos, all_targets, color)
                upgrades_and_rum = [pos for pos in available if board[pos[0]][pos[1]] in (upgrade_symbols + rum_symbols + bonus_symbols)]
            elif prev_sym in bonus_symbols:
                collected += 1
                play_sound('podbor')
                if next_pos in available:
                    available.remove(next_pos)
                if next_pos in upgrades_and_rum:
                    upgrades_and_rum.remove(next_pos)
                
                # Отслеживаем собранные символы
                global collected_bonus_this_spin, collected_superbonus_this_spin, collected_key_this_spin
                if prev_sym == 'bonus':
                    collected_bonus_this_spin += 1
                elif prev_sym == 'superbonus':
                    collected_superbonus_this_spin += 1
                elif prev_sym == 'key':
                    collected_key_this_spin += 1
                
                # Анимация перепрыгивания бонуса или супербонуса в счетчик
                grid_width = GRID_COLS * CELL_SIZE
                offset_x = (window_width - grid_width) // 2
                counter_x = offset_x + grid_width + 20
                counter_y = (window_height - INFO_PANEL_HEIGHT) // 2 + 50
                if prev_sym == 'bonus':
                    target_x = counter_x + bonus_count * (CELL_SIZE // 2 + 10) + CELL_SIZE // 4
                    target_y = counter_y + CELL_SIZE // 4
                    animate_bonus_jump(next_pos, (target_x, target_y), board, window_width, window_height, button_opacity)
                    bonus_count += 1
                elif prev_sym == 'superbonus':
                    # Для супербонуса - отдельная ячейка (например, справа)
                    target_x = counter_x + (bonus_count + 1) * (CELL_SIZE // 2 + 10) + CELL_SIZE // 4
                    target_y = counter_y + CELL_SIZE // 4
                    animate_bonus_jump(next_pos, (target_x, target_y), board, window_width, window_height, button_opacity)
                    superbonus_count = globals().get('superbonus_count', 0)
                    superbonus_count += 1
                    globals()['superbonus_count'] = superbonus_count
                elif prev_sym == 'key':
                    # Анимация подкидывания ключа к логову бандита
                    global collected_keys, key_was_collected
                    animate_bonus_jump(next_pos, (bandit_lair_pos[0] + CELL_SIZE // 2, bandit_lair_pos[1] + CELL_SIZE // 2), board, window_width, window_height, button_opacity, symbol='key')
                    collected_keys += 1
                    key_was_collected = True
                    play_sound('podbor')
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
                draw_parrot_counter(board, window_width, window_height, next_pos, parrot_win)
                pygame.display.flip()
                time.sleep(0.075 if fast_spin else 0.15)
                available = get_available_targets(board, owners, next_pos, all_targets, color)
                upgrades_and_rum = [pos for pos in available if board[pos[0]][pos[1]] in (upgrade_symbols + rum_symbols + bonus_symbols)]
            elif prev_sym in crystal_targets:
                level = int(prev_sym.split('_')[1])
                win_amount = payout_table[crystal_base][level] * base_bet
                last_win += win_amount
                parrot_win += win_amount
                if maybe_trigger_maxwin(board, window_width, window_height):
                    return collected
                total_crystals_collected += 1
                collected += 1
                if next_pos in available:
                    available.remove(next_pos)
                play_sound('podbor')
                # Проверяем, достигнута ли цель счетчика
                goal = crystal_counter_goals[min(current_counter_level, len(crystal_counter_goals) - 1)]
                if total_crystals_collected >= goal:
                    filled_counters += 1
                    current_counter_level += 1
                    total_crystals_collected = 0
            elif prev_sym in coin_symbols:
                multiplier = coin_multipliers[prev_sym]
                win_amount = multiplier * base_bet
                last_win += win_amount
                parrot_win += win_amount
                if maybe_trigger_maxwin(board, window_width, window_height):
                    return collected
                collected += 1
                if next_pos in available:
                    available.remove(next_pos)
                play_sound('podbor')
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
            draw_parrot_counter(board, window_width, window_height, next_pos, parrot_win)
            pygame.display.flip()
            time.sleep(0.075 if fast_spin else 0.15)
            current_pos = next_pos
            if not upgrades_and_rum and not available:
                break

    secondary_targets = crystal_targets + coin_symbols + upgrade_symbols + rum_symbols + bonus_symbols
    available = get_available_targets(board, owners, current_pos, secondary_targets, color)
    while available:
        reachable = [target for target in available if bfs_path(board, owners, current_pos, target, color, secondary_targets)]
        if not reachable:
            break
        target = min(reachable, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
        path = bfs_path(board, owners, current_pos, target, color, secondary_targets)
        if not path:
            break
        for i in range(1, len(path)):
            next_pos = path[i]
            prev_sym = board[next_pos[0]][next_pos[1]]
            board[current_pos[0]][current_pos[1]] = ''
            owners[current_pos[0]][current_pos[1]] = color
            board[next_pos[0]][next_pos[1]] = popugay
            if prev_sym in crystal_targets:
                level = int(prev_sym.split('_')[1])
                win_amount = payout_table[crystal_base][level] * base_bet
                last_win += win_amount
                parrot_win += win_amount
                if maybe_trigger_maxwin(board, window_width, window_height):
                    return collected
                total_crystals_collected += 1
                collected += 1
                if next_pos in available:
                    available.remove(next_pos)
                play_sound('podbor')
                # Проверяем, достигнута ли цель счетчика
                goal = crystal_counter_goals[min(current_counter_level, len(crystal_counter_goals) - 1)]
                if total_crystals_collected >= goal:
                    filled_counters += 1
                    current_counter_level += 1
                    total_crystals_collected = 0
            elif prev_sym in coin_symbols:
                multiplier = coin_multipliers[prev_sym]
                win_amount = multiplier * base_bet
                last_win += win_amount
                parrot_win += win_amount
                if maybe_trigger_maxwin(board, window_width, window_height):
                    return collected
                collected += 1
                if next_pos in available:
                    available.remove(next_pos)
                play_sound('podbor')
            elif prev_sym in upgrade_symbols:
                collected += 1
                play_sound('upgrade')
                if next_pos in available:
                    available.remove(next_pos)
                upgrade_type = prev_sym
                levels = {'levelup': 1, 'levelup_2': 2, 'levelup_3': 3, 'levelupall': 1, 'levelupall_2': 2, 'levelupall_3': 3}
                all_colors = upgrade_type.startswith('levelupall')
                upgrade_crystals(board, color if not all_colors else 0, levels[upgrade_type], all_colors)
            elif prev_sym in rum_symbols:
                collected += 1
                play_sound('podbor')
                if next_pos in available:
                    available.remove(next_pos)
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
                draw_parrot_counter(board, window_width, window_height, next_pos, parrot_win)
                pygame.display.flip()
                time.sleep(0.5 if fast_spin else 1.0)
                apply_rum_effect(board, owners, next_pos, color, window_width, window_height, button_opacity)
                time.sleep(0.075 if fast_spin else 0.15)
            elif prev_sym in bonus_symbols:
                collected += 1
                play_sound('podbor')
                if next_pos in available:
                    available.remove(next_pos)
                grid_width = GRID_COLS * CELL_SIZE
                offset_x = (window_width - grid_width) // 2
                counter_x = offset_x + grid_width + 20
                counter_y = (window_height - INFO_PANEL_HEIGHT) // 2 + 50
                if prev_sym == 'bonus':
                    target_x = counter_x + bonus_count * (CELL_SIZE // 2 + 10) + CELL_SIZE // 4
                    target_y = counter_y + CELL_SIZE // 4
                    animate_bonus_jump(next_pos, (target_x, target_y), board, window_width, window_height, button_opacity)
                    bonus_count += 1
                else:
                    target_x = counter_x + (bonus_count + 1) * (CELL_SIZE // 2 + 10) + CELL_SIZE // 4
                    target_y = counter_y + CELL_SIZE // 4
                    animate_bonus_jump(next_pos, (target_x, target_y), board, window_width, window_height, button_opacity)
                    superbonus_count = globals().get('superbonus_count', 0)
                    superbonus_count += 1
                    globals()['superbonus_count'] = superbonus_count
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
            draw_parrot_counter(board, window_width, window_height, next_pos, parrot_win)
            pygame.display.flip()
            time.sleep(0.075 if fast_spin else 0.15)
            current_pos = next_pos
        available = get_available_targets(board, owners, current_pos, crystal_targets + coin_symbols, color)

    # Плавное исчезновение счетчика за 0.25 секунды при fast_spin
    start_time = time.time()
    while time.time() - start_time < (0.05 if fast_spin else 0.1):
        elapsed = time.time() - start_time
        progress = elapsed / (0.05 if fast_spin else 0.1)
        alpha = 255 * (1 - progress)
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        draw_parrot_counter(board, window_width, window_height, current_pos, parrot_win, alpha)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

    # Показ экрана выигрыша после хода попугая, если был большой мешок или кристалл 7 уровня
    if has_big_coin or has_level_7_crystal:
        show_win_screen(board, window_width, window_height, parrot_win, button_opacity)

    return collected

def add_bonus_symbols(board, window_width, window_height, button_opacity):
    """Заменяет кристаллы на случайные не-кристаллические символы за каждый заполненный счетчик и анимирует их появление."""
    global filled_counters, total_crystals_collected, current_counter_level
    if filled_counters == 0:
        return board, False

    # Собираем позиции с кристаллами (символы, начинающиеся с 'low')
    crystal_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith('low')]
    if not crystal_positions:
        filled_counters = 0
        return board, False

    # Заменяем по 3 кристалла за каждый заполненный счетчик
    symbols_to_replace = []
    for _ in range(filled_counters):
        for _ in range(3):
            if crystal_positions:
                pos = random.choice(crystal_positions)
                symbol = get_random_non_crystal_symbol()
                symbols_to_replace.append((pos, symbol))
                crystal_positions.remove(pos)

    # Анимация замены символов - по одному символу
    duration_per_symbol = 0.5 if fast_spin else 0.65
    delay_per_symbol = 0.05 if fast_spin else 0.08
    grid_height = GRID_ROWS * CELL_SIZE
    offset_y_grid = (window_height - grid_height - INFO_PANEL_HEIGHT) // 2
    start_offset = -grid_height - offset_y_grid - 150

    # Анимируем каждый символ по очереди
    for idx, ((r, c), symbol) in enumerate(symbols_to_replace):
        board[r][c] = symbol
        
        # Анимация падения одного символа с bounce эффектом
        symbol_offsets = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        symbol_offsets[r][c] = start_offset
        
        start_time = time.time()
        played_sound = False
        
        while True:
            now = time.time()
            elapsed = now - start_time
            progress = min(elapsed / duration_per_symbol, 1.0)
            
            eased = ease_out_bounce(progress)
            symbol_offsets[r][c] = start_offset * (1 - eased)
            
            if progress >= 1.0 and not played_sound:
                play_sound('padenie')
                played_sound = True
                symbol_offsets[r][c] = 0
                break
            
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], symbol_offsets=symbol_offsets, button_opacity=button_opacity)
            pygame.display.flip()
            clock.tick(ANIMATION_FPS)
        
        # Небольшая пауза между символами (только если это не последний символ)
        if idx < len(symbols_to_replace) - 1:
            time.sleep(delay_per_symbol)

    # Проверяем, есть ли новые ходы
    has_moves = False
    for color in ['1', '2', '3', '4']:
        popugay = 'high' + color
        crystal_base = 'low' + color
        pos = find_popugay(board, popugay)
        if pos is None:
            continue
        targets = [f'{crystal_base}_{i}' for i in range(1, 8)] + non_crystal_symbols
        available = get_available_targets(board, [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)], pos, targets, color)
        if available:
            has_moves = True
            break

    # Сбрасываем только количество заполненных счетчиков
    filled_counters = 0

    return board, has_moves

def activate_bandit(board, owners, window_width, window_height, button_opacity):
    """Активирует бандита после сбора ключа"""
    global bandit_active, bandit_counter, duel_count, bandit_pos, bandit_key_alpha, last_win, balance, key_was_collected
    
    bandit_active = True
    bandit_counter = 0
    duel_count = 0
    pygame.mixer.music.stop()
    play_background_music('banditmusic')
    play_sound('banditact')
    
    # Анимация затухания ключа
    fade_duration = 0.5
    start_time = time.time()
    while time.time() - start_time < fade_duration:
        elapsed = time.time() - start_time
        progress = elapsed / fade_duration
        bandit_key_alpha = int(255 * (1 - progress))
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    bandit_key_alpha = 0
    
    # Находим позицию для бандита
    crystal_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith('low')]
    parrot_positions = [find_popugay(board, f'high{i}') for i in range(1, 5) if find_popugay(board, f'high{i}')]
    valid_positions = [pos for pos in crystal_positions if all(not (abs(pos[0] - p[0]) + abs(pos[1] - p[1]) == 1) for p in parrot_positions)]
    
    if valid_positions:
        landing_pos = random.choice(valid_positions)
        bandit_color = int(board[landing_pos[0]][landing_pos[1]].split('_')[0][-1])
        group = find_connected_group(board, landing_pos, bandit_color)
        group = extend_bandit_group(board, group)
        highlight_targets(group + [landing_pos], window_width, window_height, board, duration=1.0, button_opacity=0)
        animate_bandit_move(window_width, window_height, landing_pos, board, button_opacity=0)
        
        prev_sym = board[landing_pos[0]][landing_pos[1]]
        level = int(prev_sym.split('_')[1])
        win_amount = payout_table[f'low{bandit_color}'][level] * base_bet
        bandit_counter += win_amount
        board[landing_pos[0]][landing_pos[1]] = 'bandit'
        owners[landing_pos[0]][landing_pos[1]] = 'b'
        bandit_pos = landing_pos
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0)
        pygame.display.flip()
        time.sleep(0.15)
        
        if landing_pos in group:
            group.remove(landing_pos)
        board, owners = bandit_collect(board, owners, group, bandit_color, window_width, window_height, button_opacity=0)
    
    return board

def collection_cycle(board, window_width, window_height, seed, is_replay=False, reset_last=True):
    global last_win, button_opacity, bandit_active, bandit_counter, duel_count, bandit_pos, bandit_key_alpha, total_crystals_collected, filled_counters, bonus_count, collected_keys, key_was_collected, maxwin_abort_cycle, balance, force_super_gamble_then_collect
    if reset_last:
        last_win = 0
    if maxwin_abort_cycle:
        return last_win, board
    # Первый цикл сбора для попугаев
    while True:
        owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        collected = 0
        for color in ['1', '2', '3', '4']:
            popugay = 'high' + color
            crystal_base = 'low' + color
            pos = find_popugay(board, popugay)
            if pos is None:
                continue
            collected += collect_targets(board, owners, pos, popugay, crystal_base, color, window_width, window_height, button_opacity=0)
            if maxwin_abort_cycle:
                return last_win, board
            time.sleep(0.1)
        if collected == 0:
            break
        board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=True)
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0)
        pygame.display.flip()
        time.sleep(0.1)

    # Добавление бонусных символов и повторный цикл, если есть заполненные счетчики
    if filled_counters > 0:
        board, has_moves = add_bonus_symbols(board, window_width, window_height, button_opacity=0)
        if has_moves:
            while True:
                owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                collected = 0
                for color in ['1', '2', '3', '4']:
                    popugay = 'high' + color
                    crystal_base = 'low' + color
                    pos = find_popugay(board, popugay)
                    if pos is None:
                        continue
                    collected += collect_targets(board, owners, pos, popugay, crystal_base, color, window_width, window_height, button_opacity=0)
                    if maxwin_abort_cycle:
                        return last_win, board
                    time.sleep(0.1)
                if collected == 0:
                    break
                board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=True)
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=0)
                pygame.display.flip()
                time.sleep(0.1)

    # --- Новая механика: обмен попугаев когда ходы закончились ---
    try:
        prev_last = last_win
        swap_done = attempt_parrot_swaps(board, window_width, window_height)
    except Exception as e:
        swap_done = False
    if swap_done:
        # Если обмен произошёл — запускаем цикл сбора заново для новой доски,
        # но не сбрасываем `last_win` в начале вложенного вызова, чтобы
        # внутренняя агрегация прибавлялась к уже существующему значению.
        new_last, new_board = collection_cycle(board, window_width, window_height, seed, is_replay=is_replay, reset_last=False)
        # Вложенный вызов уже добавил к глобальному last_win, просто возвращаем его.
        return last_win, new_board

    if is_bandit_mode:
        bandit_active = True
        bandit_counter = 0
        duel_count = 0
        pygame.mixer.music.stop()
        play_background_music('banditmusic')
        play_sound('banditact')
        fade_duration = 0.5
        start_time = time.time()
        while time.time() - start_time < fade_duration:
            elapsed = time.time() - start_time
            progress = elapsed / fade_duration
            bandit_key_alpha = int(255 * (1 - progress))
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=0)
            pygame.display.flip()
            clock.tick(ANIMATION_FPS)
        bandit_key_alpha = 0
        crystal_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith('low')]
        parrot_positions = [find_popugay(board, f'high{i}') for i in range(1, 5) if find_popugay(board, f'high{i}')]
        valid_positions = [pos for pos in crystal_positions if all(not (abs(pos[0] - p[0]) + abs(pos[1] - p[1]) == 1) for p in parrot_positions)]
        if valid_positions:
            landing_pos = random.choice(valid_positions)
            bandit_color = int(board[landing_pos[0]][landing_pos[1]].split('_')[0][-1])
            group = find_connected_group(board, landing_pos, bandit_color)
            group = extend_bandit_group(board, group)
            highlight_targets(group + [landing_pos], window_width, window_height, board, duration=1.0, button_opacity=0)
            animate_bandit_move(window_width, window_height, landing_pos, board, button_opacity=0)
            prev_sym = board[landing_pos[0]][landing_pos[1]]
            level = int(prev_sym.split('_')[1])
            win_amount = payout_table[f'low{bandit_color}'][level] * base_bet
            bandit_counter += win_amount
            board[landing_pos[0]][landing_pos[1]] = 'bandit'
            owners[landing_pos[0]][landing_pos[1]] = 'b'
            bandit_pos = landing_pos
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=0)
            pygame.display.flip()
            time.sleep(0.15)
            if landing_pos in group:
                group.remove(landing_pos)
            board, owners = bandit_collect(board, owners, group, bandit_color, window_width, window_height, button_opacity=0)
            # Проверка ходов для попугаев после смерти бандита
            if not bandit_active:
                while True:
                    owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                    collected = 0
                    for color in ['1', '2', '3', '4']:
                        popugay = 'high' + color
                        crystal_base = 'low' + color
                        pos = find_popugay(board, popugay)
                        if pos is None:
                            continue
                        collected += collect_targets(board, owners, pos, popugay, crystal_base, color, window_width, window_height, button_opacity=0)
                        time.sleep(0.1)
                    if collected == 0:
                        break
                    board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=True)
                    screen.blit(scaled_background, (0, 0))
                    draw_board(board, window_width, window_height, [], button_opacity=0)
                    pygame.display.flip()
                    time.sleep(0.1)

    if maxwin_abort_cycle:
        return last_win, board

    # Проверка на активацию бонусной игры под конец ходов
    if bonus_count >= 3:
        show_bonus_activation(window_width, window_height)
        final_count, has_super, lost, maxwin_won = show_gamble_screen(
            window_width,
            window_height,
            bonus_count,
            forced_super_stage=force_super_gamble_then_collect
        )
        force_super_gamble_then_collect = False
        if maxwin_won:
            # Максвин через гэмбл — запускаем сцену максвина
            bonus_count = 0
            globals()['superbonus_count'] = 0
            run_maxwin_sequence(board, window_width, window_height)
            last_win = base_bet * 200000
            balance += last_win
            update_balance(current_user, balance)
            update_stats(current_user, 0, last_win)
        elif has_super:
            # Супербонус через гэмбл — запускаем супербонус
            bonus_count = 0
            globals()['superbonus_count'] = 0
            show_superbonus_start_screen(window_width, window_height)
        else:
            gamble_lost = lost
            board = bonus_game(window_width, window_height, seed, is_replay=is_replay, board=board)
        bonus_count = 0
        globals()['superbonus_count'] = 0
    
    # Проверка на активацию бандита после сбора ключей
    if collected_keys > 0 and not is_bonus_game:
        collected_keys = 0
        # Запускаем бандита
        board_after_bandit = activate_bandit(board, owners, window_width, window_height, button_opacity)
        if board_after_bandit is not None:
            board = board_after_bandit
        
        # Проверка ходов для попугаев после смерти бандита
        if not bandit_active:
            while True:
                owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                collected = 0
                for color in ['1', '2', '3', '4']:
                    popugay = 'high' + color
                    crystal_base = 'low' + color
                    pos = find_popugay(board, popugay)
                    if pos is None:
                        continue
                    collected += collect_targets(board, owners, pos, popugay, crystal_base, color, window_width, window_height, button_opacity=0)
                    time.sleep(0.1)
                if collected == 0:
                    break
                board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=True)
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=0)
                pygame.display.flip()
                time.sleep(0.1)
            
            # Проверяем заполненные счетчики кристаллов после смерти бандита
            if filled_counters > 0:
                board, has_moves = add_bonus_symbols(board, window_width, window_height, button_opacity=0)
                if has_moves:
                    while True:
                        owners = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                        collected = 0
                        for color in ['1', '2', '3', '4']:
                            popugay = 'high' + color
                            crystal_base = 'low' + color
                            pos = find_popugay(board, popugay)
                            if pos is None:
                                continue
                            collected += collect_targets(board, owners, pos, popugay, crystal_base, color, window_width, window_height, button_opacity=0)
                            time.sleep(0.1)
                        if collected == 0:
                            break
                        board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=True)
                        screen.blit(scaled_background, (0, 0))
                        draw_board(board, window_width, window_height, [], button_opacity=0)
                        pygame.display.flip()
                        time.sleep(0.1)
            
            # Проверяем активацию бонусной игры после смерти бандита
            if bonus_count >= 3 and globals().get('superbonus_count', 0) == 0:
                show_bonus_activation(window_width, window_height)
                board = bonus_game(window_width, window_height, seed, is_replay=is_replay, board=board)
                bonus_count = 0
                globals()['superbonus_count'] = 0
            elif bonus_count >= 2 and globals().get('superbonus_count', 0) >= 1:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                bonus_count = 0
                globals()['superbonus_count'] = 0
                show_superbonus_start_screen(window_width, window_height)

    # Отображаем интерфейс только после завершения всех ходов, если не в бонусной игре
    if not is_bonus_game:
        start_time = time.time()
        while time.time() - start_time < FADE_IN_DURATION:
            elapsed = time.time() - start_time
            progress = elapsed / FADE_IN_DURATION
            button_opacity = min(255, 255 * progress)
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
            pygame.display.flip()
            clock.tick(ANIMATION_FPS)
        button_opacity = 255

    return last_win, board

def show_bonus_win_screen(window_width, window_height, total_bonus_win, board):
    """Показ полупрозрачного окна с выигрышем за бонусную игру."""
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(BIG_WIN_BG)
    bonus_win_text = font.render("BONUS WIN!", True, GOLD)
    text_rect = bonus_win_text.get_rect(center=(window_width // 2, window_height // 2 - 50))
    win_amount_text = font.render(f"{total_bonus_win:.2f} У.Е.", True, WHITE)
    amount_rect = win_amount_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
    # Animate counter from 0 to total_bonus_win over 1.5 seconds, then hold final value
    anim_duration = 1.2
    hold_duration = 5.0 - anim_duration if 5.0 > anim_duration else 1.2
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed < anim_duration:
            progress = elapsed / anim_duration
            display_amount = total_bonus_win * progress
        else:
            display_amount = total_bonus_win

        # Рисуем фон и сетку
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0)
        screen.blit(bg_surface, (0, 0))
        screen.blit(bonus_win_text, text_rect)

        # Обновляем текст с текущим значением
        win_amount_text = font.render(f"{display_amount:.2f} У.Е.", True, WHITE)
        amount_rect = win_amount_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
        screen.blit(win_amount_text, amount_rect)
        pygame.display.flip()
        clock.tick(FPS)

        if elapsed >= anim_duration + hold_duration:
            break

def show_superbonus_win_screen(window_width, window_height, total_bonus_win, board):
    """Показ полупрозрачного окна с выигрышем за супербонусную игру."""
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(BIG_WIN_BG)
    bonus_win_text = font.render("SUPER BONUS WIN!", True, GOLD)
    text_rect = bonus_win_text.get_rect(center=(window_width // 2, window_height // 2 - 50))
    win_amount_text = font.render(f"{total_bonus_win:.2f} У.Е.", True, WHITE)
    amount_rect = win_amount_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
    # Animate counter from 0 to total_bonus_win over 1.2 seconds, then hold final value
    anim_duration = 1
    hold_duration = 5.0 - anim_duration if 5.0 > anim_duration else 1
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed < anim_duration:
            progress = elapsed / anim_duration
            display_amount = total_bonus_win * progress
        else:
            display_amount = total_bonus_win

        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=0)
        screen.blit(bg_surface, (0, 0))
        screen.blit(bonus_win_text, text_rect)

        win_amount_text = font.render(f"{display_amount:.2f}", True, WHITE)
        amount_rect = win_amount_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
        screen.blit(win_amount_text, amount_rect)
        pygame.display.flip()
        clock.tick(FPS)

        if elapsed >= anim_duration + hold_duration:
            break

active_modifier = None  # Активный модификатор для показа картинки во время спина

# Загрузка изображений для модификаторов
modifier_images = {}
modifier_files = {
    'bonus_hunt_2x': 'bonus_hunt_2x.png',
    'bonus_hunt_3x': 'bonus_hunt_3x.png',
    'bonus_buy': 'bonus_buy.png',
    'super_bonus_buy': 'super_bonus_buy.png',
    'garant_spin': 'garant_spin.png',
    '3lvl': '3lvl.png',
    'god_mode': 'god_mode.png'
}
for mod, filename in modifier_files.items():
    image_path = os.path.join('images', filename)
    try:
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (150, 50))  # Масштаб для единообразия
        modifier_images[mod] = image
    except (pygame.error, FileNotFoundError):
        placeholder = pygame.Surface((150, 50), pygame.SRCALPHA)
        placeholder.fill((100, 100, 100))  # Серый плейсхолдер
        modifier_images[mod] = placeholder

def show_bonus_activation(window_width, window_height):
    """Показ полупрозрачного окна с надписью 'BONUS!' и кнопкой 'START' через 4 секунды.
    Кнопка появляется плавно и остаётся видимой до нажатия."""
    time.sleep(1)
    pygame.mixer.music.stop()
    play_sound('startbonus')

    # Полупрозрачный фон
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill(BIG_WIN_BG)

    # Текст BONUS!
    bonus_text = font.render("BONUS!", True, GOLD)
    text_rect = bonus_text.get_rect(center=(window_width // 2, window_height // 2))

    # Кнопка START (создаём заранее, но изначально невидимая)
    start_button = pygame.Rect(window_width // 2 - 75, window_height // 2 + 100, 150, 50)
    start_text = small_font.render("START", True, WHITE)

    # Время старта анимации
    start_time = time.time()
    show_start_button = False
    button_alpha = 0  # Прозрачность кнопки (0 — невидима, 255 — полностью видима)

    while True:
        current_time = time.time()
        elapsed = current_time - start_time

        # === 1. Показываем фон и текст всегда ===
        screen.blit(bg_surface, (0, 0))
        screen.blit(bonus_text, text_rect)

        # === 2. Через 4 секунды начинаем показывать кнопку ===
        if elapsed >= 4.0 and not show_start_button:
            show_start_button = True
            button_alpha = 0  # Начинаем с невидимой

        if show_start_button:
            # Плавное появление кнопки за 0.5 секунды
            if button_alpha < 255:
                button_alpha = min(255, int(255 * (elapsed - 4.0) / 0.5))

            # Рисуем кнопку с текущей прозрачностью
            button_surface = pygame.Surface(start_button.size, pygame.SRCALPHA)
            button_color = (0, 200, 0, button_alpha)
            pygame.draw.rect(button_surface, button_color, (0, 0, start_button.width, start_button.height), border_radius=8)
            screen.blit(button_surface, start_button.topleft)

            # Текст кнопки тоже с альфой
            text_surface = start_text.copy()
            text_surface.set_alpha(button_alpha)
            screen.blit(text_surface, start_button.move(45, 15))

        pygame.display.flip()
        clock.tick(FPS)

        # === 3. Обработка нажатия на кнопку ===
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and show_start_button and button_alpha >= 255:
                mx, my = pygame.mouse.get_pos()
                if start_button.collidepoint(mx, my):
                    play_sound('button')
                    update_stats(current_user, 0, 0, 1)  # Увеличиваем счётчик бонусных игр
                    return  # Выходим — бонусная игра начнётся

        # Если кнопка уже видима — выходим из цикла только по клику
        if show_start_button and button_alpha >= 255:
            # Проверяем нажатие мыши вне цикла событий — на случай, если игрок кликает сразу
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if start_button.collidepoint(mx, my):
                    play_sound('button')
                    update_stats(current_user, 0, 0, 1)  # Увеличиваем счётчик бонусных игр
                    return


def show_gamble_screen(window_width, window_height, initial_bonus_count, forced_super_stage=False):
    """Экран гэмбла перед бонусной игрой.
    Игрок может рисковать собранными бонусами для увеличения числа попугаев.
    Возвращает (final_bonus_count, has_super, gamble_lost)."""
    global bonus_game_parrots, gamble_lost

    current_count = initial_bonus_count
    has_super = False
    slot_size = CELL_SIZE
    slot_gap = 10
    total_slots_width = 6 * (slot_size + slot_gap) + 5 + slot_size  # 6 bonus + gap + 1 super
    slots_x = (window_width - total_slots_width) // 2
    slots_y = window_height // 4

    # Вероятности гэмбла: при текущем count, шанс получить +1
    gamble_chances = {3: 123/4, 4: 1123/4, 5: 1123/5, 6: 7/6, 7: 14/7}

    # Overlay
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 200))

    def draw_gamble_state(highlight_slot=-1, show_symbol=True, symbol_y_offset=0, lost=False):
        """Отрисовка текущего состояния гэмбл-экрана."""
        screen.blit(bg_surface, (0, 0))

        # Заголовок
        title = font.render("GAMBLE", True, GOLD)
        screen.blit(title, title.get_rect(center=(window_width // 2, slots_y - 60)))

        # 6 обычных слотов
        for i in range(6):
            cell_rect = pygame.Rect(slots_x + i * (slot_size + slot_gap), slots_y, slot_size, slot_size)
            pygame.draw.rect(screen, GRAY, cell_rect, border_radius=5)
            if i < current_count:
                bonus_img = symbol_images.get('bonus')
                if bonus_img:
                    scaled = pygame.transform.scale(bonus_img, (slot_size, slot_size))
                    screen.blit(scaled, cell_rect.topleft)
            if i == highlight_slot:
                pygame.draw.rect(screen, GOLD, cell_rect, 3, border_radius=5)

        # Супер-слот
        sb_x = slots_x + 6 * (slot_size + slot_gap) + 5
        sb_rect = pygame.Rect(sb_x, slots_y, slot_size, slot_size)
        pygame.draw.rect(screen, (80, 40, 80), sb_rect, border_radius=5)
        pygame.draw.rect(screen, (180, 0, 180), sb_rect, 2, border_radius=5)
        if has_super:
            sb_img = symbol_images.get('superbonus')
            if sb_img:
                scaled_sb = pygame.transform.scale(sb_img, (slot_size, slot_size))
                screen.blit(scaled_sb, sb_rect.topleft)
        if highlight_slot == 6:
            pygame.draw.rect(screen, (255, 0, 255), sb_rect, 3, border_radius=5)

        # Символ бонуса для гэмбла (по центру, ниже слотов)
        symbol_center_x = window_width // 2
        symbol_center_y = slots_y + slot_size + 100 + symbol_y_offset
        if show_symbol and not lost:
            is_maxwin_gamble = (current_count >= 6 and has_super)
            is_super_gamble = (current_count >= 6 and not has_super)
            if is_maxwin_gamble:
                sym_key = 'coinmaxwin'
            elif is_super_gamble:
                sym_key = 'superbonus'
            else:
                sym_key = 'bonus'
            sym_img = symbol_images.get(sym_key)
            if sym_img:
                sz = int(slot_size * 1.5)
                scaled_sym = pygame.transform.scale(sym_img, (sz, sz))
                sym_rect = scaled_sym.get_rect(center=(symbol_center_x, symbol_center_y))
                screen.blit(scaled_sym, sym_rect)
            label = "MAX WIN" if is_maxwin_gamble else "+1"
            plus_text = font.render(label, True, GOLD)
            screen.blit(plus_text, plus_text.get_rect(center=(symbol_center_x, symbol_center_y + slot_size)))

        # Шанс текущего гэмбла
        is_maxwin_gamble_ch = (current_count >= 6 and has_super)
        gamble_key = 7 if is_maxwin_gamble_ch else current_count
        is_forced_super_stage = forced_super_stage and (current_count >= 6 and not has_super)
        is_forced_collect_stage = forced_super_stage and (current_count >= 6 and has_super)
        if is_forced_collect_stage:
            chance = 0
        elif is_forced_super_stage:
            chance = 1.0
        else:
            chance = gamble_chances.get(gamble_key, 0)
        if chance > 0 and show_symbol and not lost:
            chance_pct = f"Chance: {chance*100:.0f}%"
            chance_text = small_font.render(chance_pct, True, WHITE)
            screen.blit(chance_text, chance_text.get_rect(center=(window_width // 2, symbol_center_y + slot_size + 40)))

    def draw_buttons(show_gamble=True, show_collect=True):
        """Рисует кнопки GAMBLE/COLLECT, возвращает их rect'ы."""
        btn_w, btn_h = 180, 60
        gap = 40
        total_w = btn_w * 2 + gap if (show_gamble and show_collect) else btn_w
        base_x = (window_width - total_w) // 2
        btn_y = window_height * 3 // 4

        gamble_rect = None
        collect_rect = None

        if show_gamble:
            gamble_x = base_x
            gamble_rect = pygame.Rect(gamble_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (180, 30, 30), gamble_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 80, 80), gamble_rect, 2, border_radius=10)
            g_text = font.render("GAMBLE", True, WHITE)
            screen.blit(g_text, g_text.get_rect(center=gamble_rect.center))

        if show_collect:
            collect_x = base_x + (btn_w + gap if show_gamble else 0)
            collect_rect = pygame.Rect(collect_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (30, 150, 30), collect_rect, border_radius=10)
            pygame.draw.rect(screen, (80, 220, 80), collect_rect, 2, border_radius=10)
            c_text = font.render("COLLECT", True, WHITE)
            screen.blit(c_text, c_text.get_rect(center=collect_rect.center))

        return gamble_rect, collect_rect

    def animate_win():
        """Анимация выигрыша: символ подпрыгивает 2 сек, затем летит в слот."""
        nonlocal current_count, has_super, maxwin_won
        is_maxwin_gamble = (current_count >= 6 and has_super)
        is_super_gamble = (current_count >= 6 and not has_super)

        # Максвин — особая анимация, без полёта в слот
        if is_maxwin_gamble:
            maxwin_won = True
            play_sound('button')
            return

        target_slot = current_count if not is_super_gamble else 6

        # Позиция символа
        sym_start_y = slots_y + slot_size + 100
        sym_x = window_width // 2

        # Целевая позиция (слот)
        if target_slot < 6:
            target_x = slots_x + target_slot * (slot_size + slot_gap) + slot_size // 2
        else:
            target_x = slots_x + 6 * (slot_size + slot_gap) + 5 + slot_size // 2
        target_y = slots_y + slot_size // 2

        # Фаза 1: подпрыгивание (2 сек)
        bounce_duration = 2.0
        start_time = time.time()
        while time.time() - start_time < bounce_duration:
            elapsed = time.time() - start_time
            bounce = -abs(math.sin(elapsed * 4)) * 30
            draw_gamble_state(highlight_slot=target_slot, show_symbol=False)
            # Рисуем прыгающий символ
            sym_key = 'superbonus' if is_super_gamble else 'bonus'
            sym_img = symbol_images.get(sym_key)
            if sym_img:
                sz = int(slot_size * 1.5)
                scaled_sym = pygame.transform.scale(sym_img, (sz, sz))
                sym_rect = scaled_sym.get_rect(center=(sym_x, sym_start_y + bounce))
                screen.blit(scaled_sym, sym_rect)
            win_text = font.render("WIN!", True, GOLD)
            screen.blit(win_text, win_text.get_rect(center=(window_width // 2, slots_y - 60)))
            pygame.display.flip()
            clock.tick(ANIMATION_FPS)

        # Фаза 2: перемещение в слот (0.5 сек)
        fly_duration = 0.5
        start_time = time.time()
        while time.time() - start_time < fly_duration:
            progress = (time.time() - start_time) / fly_duration
            progress = min(1.0, progress)
            # Easing
            t = 1 - (1 - progress) ** 2
            cur_x = sym_x + (target_x - sym_x) * t
            cur_y = sym_start_y + (target_y - sym_start_y) * t
            cur_size = int(slot_size * 1.5 + (slot_size - slot_size * 1.5) * t)

            draw_gamble_state(highlight_slot=target_slot, show_symbol=False)
            sym_key = 'superbonus' if is_super_gamble else 'bonus'
            sym_img = symbol_images.get(sym_key)
            if sym_img:
                scaled_sym = pygame.transform.scale(sym_img, (max(1, cur_size), max(1, cur_size)))
                sym_rect = scaled_sym.get_rect(center=(int(cur_x), int(cur_y)))
                screen.blit(scaled_sym, sym_rect)
            pygame.display.flip()
            clock.tick(ANIMATION_FPS)

        # Обновляем состояние
        if is_super_gamble:
            has_super = True
        else:
            current_count += 1

        play_sound('button')
        time.sleep(0.5)

    def animate_lose():
        """Анимация проигрыша: символ исчезает."""
        sym_y = slots_y + slot_size + 100
        fade_duration = 1.0
        start_time = time.time()
        is_super_gamble = (current_count >= 6 and not has_super)
        sym_key = 'superbonus' if is_super_gamble else 'bonus'

        while time.time() - start_time < fade_duration:
            progress = (time.time() - start_time) / fade_duration
            alpha = int(255 * (1 - progress))
            draw_gamble_state(show_symbol=False)

            sym_img = symbol_images.get(sym_key)
            if sym_img:
                sz = int(slot_size * 1.5)
                scaled_sym = pygame.transform.scale(sym_img, (sz, sz))
                scaled_sym.set_alpha(alpha)
                sym_rect = scaled_sym.get_rect(center=(window_width // 2, sym_y))
                screen.blit(scaled_sym, sym_rect)

            lose_text = font.render("LOSE!", True, (255, 50, 50))
            screen.blit(lose_text, lose_text.get_rect(center=(window_width // 2, slots_y - 60)))
            pygame.display.flip()
            clock.tick(ANIMATION_FPS)

        time.sleep(1.0)

    # === Главный цикл гэмбл-экрана ===
    maxwin_won = False
    running = True
    while running:
        draw_gamble_state()
        # Можно гэмблить если есть шанс в таблице, или если это этап максвина (6+super)
        is_maxwin_stage = (current_count >= 6 and has_super)
        is_super_stage = (current_count >= 6 and not has_super)
        gamble_key = 7 if is_maxwin_stage else current_count
        can_gamble = gamble_key in gamble_chances

        # Спец-режим FS 18000x: супербонус принудительно через кнопку GAMBLE,
        # а на этапе MAX WIN доступен только COLLECT.
        if forced_super_stage and is_super_stage:
            gamble_btn, collect_btn = draw_buttons(show_gamble=True, show_collect=False)
        elif forced_super_stage and is_maxwin_stage:
            gamble_btn, collect_btn = draw_buttons(show_gamble=False, show_collect=True)
        elif can_gamble:
            gamble_btn, collect_btn = draw_buttons(show_gamble=True, show_collect=True)
        else:
            # Больше нельзя гэмблить — только collect
            btn_w, btn_h = 180, 60
            btn_y = window_height * 3 // 4
            collect_btn = pygame.Rect((window_width - btn_w) // 2, btn_y, btn_w, btn_h)
            pygame.draw.rect(screen, (30, 150, 30), collect_btn, border_radius=10)
            pygame.draw.rect(screen, (80, 220, 80), collect_btn, 2, border_radius=10)
            c_text = font.render("COLLECT", True, WHITE)
            screen.blit(c_text, c_text.get_rect(center=collect_btn.center))
            gamble_btn = None

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if gamble_btn and gamble_btn.collidepoint(mx, my):
                    play_sound('button')
                    chance = 1.0 if (forced_super_stage and is_super_stage) else gamble_chances.get(gamble_key, 0)
                    won = random.random() < chance
                    if won:
                        animate_win()
                        if maxwin_won:
                            running = False
                        # Если после выигрыша нельзя больше гэмблить, автоматически collect
                        elif current_count not in gamble_chances and not (current_count >= 6 and not has_super):
                            running = False
                    else:
                        animate_lose()
                        gamble_lost = True
                        running = False
                elif collect_btn and collect_btn.collidepoint(mx, my):
                    play_sound('button')
                    gamble_lost = False
                    running = False

    # Устанавливаем количество попугаев для бонусной игры
    parrot_map = {3: 1, 4: 2, 5: 3, 6: 4}
    bonus_game_parrots = parrot_map.get(min(current_count, 6), 4)

    return current_count, has_super, gamble_lost, maxwin_won


def bonus_game(window_width, window_height, seed, is_replay=False, board=None):
    """Бонусная игра с 8 бесплатными спинами (или 3, если gamble проигран)."""
    global is_bonus_game, balance, last_win, bonus_count, button_opacity, is_bet_plus, is_bet_plus_plus
    global is_garant_spin, is_3_lvl, is_bandit_mode, is_buy_fs, current_bonus_spin, total_bonus_win, current_user
    global num_parrots, active_parrots, bonus_game_parrots, gamble_lost
    is_bonus_game = True
    is_bet_plus = is_bet_plus_plus = is_garant_spin = is_3_lvl = is_bandit_mode = False
    bonus_count = 0
    globals()['superbonus_count'] = 0
    button_opacity = 0
    current_bonus_spin = 1
    total_bonus_win = last_win  # Перенос выигрыша с активации

    # Устанавливаем количество попугаев на основе собранных символов бонуса
    num_parrots = bonus_game_parrots
    
    # Определяем количество спинов
    spins_left = 3 if gamble_lost else 8
    gamble_lost = False  # Сбрасываем

    pygame.mixer.stop()
    play_sound('startbonus1')
    time.sleep(1)
    play_sound('bonus', loop=True)

    if is_replay:
        is_buy_fs = False

    # Если доска не передана — создаём новую
    if board is None:
        board, _ = generate_board()

    freespin_seeds = [random.randint(0, 2**32 - 1) for _ in range(spins_left)]

    bonus_maxwin_triggered = False
    for fs_seed in freespin_seeds:
        board, _ = spin_animation(board, window_width, window_height, seed=fs_seed)
        total_bonus_win += last_win
        last_win = 0

        # Проверка на максвин во время бонусной игры
        if total_bonus_win >= base_bet * 200000:
            total_bonus_win = base_bet * 200000
            bonus_maxwin_triggered = True
            pygame.mixer.stop()
            run_maxwin_sequence(board, window_width, window_height)
            break

        if current_bonus_spin < spins_left:
            time.sleep(1.0)
        current_bonus_spin += 1

    if not bonus_maxwin_triggered:
        pygame.mixer.stop()
        play_sound('endbonus')

        # Передаём board в экран выигрыша
        show_bonus_win_screen(window_width, window_height, total_bonus_win, board)

    if not is_replay:
        balance += total_bonus_win
        update_balance(current_user, balance)  # Обновляем в БД
        try:
            # Добавляем выигрыш бонусной игры в общую статистику
            update_stats(current_user, 0, total_bonus_win)
        except Exception:
            pass

    is_bonus_game = False
    num_parrots = 1
    active_parrots = [random.choice(['high1', 'high2', 'high3', 'high4'])]
    play_background_music('song')

    # Плавное появление интерфейса
    start_time = time.time()
    while time.time() - start_time < FADE_IN_DURATION:
        elapsed = time.time() - start_time
        progress = elapsed / FADE_IN_DURATION
        button_opacity = min(255, 255 * progress)
        screen.blit(scaled_background, (0, 0))
        draw_board(board, window_width, window_height, [], button_opacity=button_opacity)
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    button_opacity = 255

    return board  # Возвращаем доску после бонусной игры


def sync_bandit_position(board, owners):
    """Обновить глобальную позицию бандита по текущей доске."""
    global bandit_pos
    bandit_pos = None
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if owners[r][c] == 'b' and board[r][c] != 'bandit':
                owners[r][c] = ''
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if board[r][c] == 'bandit':
                bandit_pos = (r, c)
                owners[r][c] = 'b'
                return


def extend_bandit_group(board, group):
    """Добавляет к группе все соседние бонусы/ромы/мешки, чтобы бандит видел весь маршрут."""
    if not group:
        return []
    group_set = set(group)
    queue = deque(group)
    while queue:
        r, c = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            pos = (nr, nc)
            if not (0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS):
                continue
            if pos in group_set:
                continue
            symbol = board[nr][nc]
            if symbol in BANDIT_EXTRA_SYMBOLS:
                group_set.add(pos)
                queue.append(pos)
    return list(group_set)


def bandit_collect(board, owners, initial_group, initial_color, window_width, window_height, button_opacity):
    global bandit_pos, bandit_counter, duel_count, bandit_active, last_win, balance, dead_parrots, bonus_count
    upgrade_symbols = ['levelup', 'levelup_2', 'levelup_3', 'levelupall', 'levelupall_2', 'levelupall_3']
    coin_symbols = ['coin2', 'coin5', 'coin10', 'coin25', 'coin50', 'coin100', 'coin500', 'coin1000', 'coin2500', 'coinmaxwin']
    crystal_targets = [f'low{i}_{j}' for i in range(1, 5) for j in range(1, 8)]
    all_targets = upgrade_symbols + crystal_targets + coin_symbols
    bandit_color = 'b'

    def find_adjacent_parrot(pos):
        for dr, dc in directions:
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                symbol = board[nr][nc]
                if symbol.startswith('high'):
                    return (nr, nc, symbol)
        return None

    def resolve_duel(parrot_pos, parrot_symbol):
        global duel_count, bandit_active, bandit_pos, last_win, balance, dead_parrots, bandit_was_caught
        nonlocal current_pos, board, owners
        time.sleep(1.5)
        idx = min(duel_count, len(bandit_duel_chances) - 1)
        duel_outcome = random.random() < bandit_duel_chances[idx]
        duel_count += 1
        show_duel_window(window_width, window_height, bandit_counter, not duel_outcome, parrot_symbol)
        if not duel_outcome:
            bandit_active = False
            bandit_was_caught = True
            if bandit_pos:
                board[bandit_pos[0]][bandit_pos[1]] = ''
            bandit_pos = None
            last_win += bandit_counter
            balance += bandit_counter
            pygame.mixer.music.stop()
            show_win_screen(board, window_width, window_height, bandit_counter, button_opacity)
            play_background_music('song')
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    if owners[r][c] == 'b' and board[r][c] == '':
                        board[r][c] = ''
            board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=True)
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=0)
            pygame.display.flip()
            return 'parrot_win'
        else:
            if parrot_symbol not in dead_parrots:
                dead_parrots.append(parrot_symbol)
            board[parrot_pos[0]][parrot_pos[1]] = ''
            board, owners = animate_cascade(board, owners, window_width, window_height, respawn_parrots=False)
            sync_bandit_position(board, owners)
            if bandit_pos is None:
                return 'parrot_win'
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=0)
            pygame.display.flip()
            time.sleep(0.15)
            current_pos = bandit_pos
            return 'bandit_continue'

    # Удаляем всех бандитов с сетки, кроме текущего
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if board[r][c] == 'bandit' and (r, c) != bandit_pos:
                board[r][c] = ''
                owners[r][c] = ''

    # Сбор начальной группы
    current_pos = bandit_pos
    initial_group = list(initial_group)
    initial_allowed_cells = set(initial_group)
    while initial_group:
        allowed_cells = initial_allowed_cells | {current_pos}
        reachable = [pos for pos in initial_group if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=allowed_cells)]
        if not reachable:
            break
        # Бандит собирает все кристаллы, включая те что рядом с попугаем
        target = min(reachable, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
        defer_duel = False  # Не откладываем дуэль
        path = a_star_path(board, owners, current_pos, target, bandit_color, all_targets, allowed_positions=allowed_cells)
        if not path:
            break
        duel_triggered = False
        for i in range(1, len(path)):
            next_pos = path[i]
            is_last_step = (i == len(path) - 1)
            
            # Сначала собираем символ на клетке
            prev_sym = board[next_pos[0]][next_pos[1]]
            if prev_sym in crystal_targets:
                level = int(prev_sym.split('_')[1])
                win_amount = payout_table[prev_sym.split('_')[0]][level] * base_bet
                bandit_counter += win_amount
                play_sound('podbor')
            elif prev_sym in coin_symbols:
                multiplier = coin_multipliers[prev_sym]
                win_amount = multiplier * base_bet
                bandit_counter += win_amount
                play_sound('podbor')
            elif prev_sym in upgrade_symbols:
                levels = {'levelup': 1, 'levelup_2': 2, 'levelup_3': 3, 'levelupall': 1, 'levelupall_2': 2, 'levelupall_3': 3}[prev_sym]
                all_colors = 'all' in prev_sym
                if all_colors:
                    upgrade_crystals(board, 0, levels, True)
                else:
                    random_color = random.randint(1, 4)
                    upgrade_crystals(board, random_color, levels)
                play_sound('upgrade')
            
            # Двигаем бандита на новую позицию
            board[current_pos[0]][current_pos[1]] = ''
            owners[current_pos[0]][current_pos[1]] = bandit_color
            board[next_pos[0]][next_pos[1]] = 'bandit'
            current_pos = next_pos
            bandit_pos = next_pos
            screen.blit(scaled_background, (0, 0))
            draw_board(board, window_width, window_height, [], button_opacity=0)
            pygame.display.flip()
            time.sleep(0.15)
            
            if next_pos in initial_group:
                initial_group.remove(next_pos)
            
            # ПОСЛЕ того как встали на клетку, проверяем есть ли попугай рядом
            adjacent_info = find_adjacent_parrot(next_pos)
            if adjacent_info:
                duel_result = resolve_duel((adjacent_info[0], adjacent_info[1]), adjacent_info[2])
                duel_triggered = True
                if duel_result == 'parrot_win':
                    return board, owners
                break
        if duel_triggered:
            break
    while bandit_pos:
        # Пробуем найти доступный цвет для сбора
        available_colors = []
        for target_color in range(1, 5):
            color_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith(f'low{target_color}')]
            if color_positions:
                available_colors.append(target_color)
        
        if not available_colors:
            break
        
        # Перемешиваем цвета для случайного выбора
        random.shuffle(available_colors)
        
        # Ищем цвет с доступными кристаллами
        chosen_color = None
        all_accessible_crystals = []
        
        for try_color in available_colors:
            # Находим все позиции кристаллов этого цвета
            color_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith(f'low{try_color}')]
            
            # Разбиваем на связанные группы
            connected_groups = []
            remaining_positions = list(color_positions)
            
            while remaining_positions:
                base_group = find_connected_group(board, remaining_positions[0], try_color)
                connected_groups.append(base_group)
                for pos in base_group:
                    if pos in remaining_positions:
                        remaining_positions.remove(pos)
            
            # Проверяем, можем ли добраться до какой-либо группы (двигаясь по кристаллам этого цвета)
            initial_group = None
            for group in connected_groups:
                allowed = set(group) | {current_pos}
                reachable = False
                for pos in group:
                    if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=allowed):
                        reachable = True
                        break
                
                # Если группа доступна, выбираем её как начальную
                if reachable:
                    initial_group = group
                    chosen_color = try_color
                    break
            
            # Если нашли начальную группу, собираем ВСЕ доступные кристаллы этого цвета
            if initial_group:
                all_accessible_crystals = list(initial_group)
                break
        
        # Если не нашли доступных групп ни одного цвета, выходим
        if not chosen_color or not all_accessible_crystals:
            break
        
        # Сортируем кристаллы: сначала без попугаев рядом, потом с попугаями
        def has_adjacent_parrot(pos):
            for dr, dc in directions:
                nr, nc = pos[0] + dr, pos[1] + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                    if board[nr][nc].startswith('high'):
                        return True
            return False
        
        crystals_without_parrots = [pos for pos in all_accessible_crystals if not has_adjacent_parrot(pos)]
        crystals_with_parrots = [pos for pos in all_accessible_crystals if has_adjacent_parrot(pos)]
        
        # Собираем в правильном порядке: сначала без попугаев, потом с попугаями
        ordered_crystals = crystals_without_parrots + crystals_with_parrots
        
        # Находим ТОЛЬКО доступные кристаллы и функциональные символы для подсветки
        all_color_crystals = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith(f'low{chosen_color}')]
        
        # Находим функциональные символы рядом с кристаллами этого цвета
        functional_near_crystals = []
        for crystal_pos in all_color_crystals:
            for dr, dc in directions:
                nr, nc = crystal_pos[0] + dr, crystal_pos[1] + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                    sym = board[nr][nc]
                    pos = (nr, nc)
                    if sym in upgrade_symbols or sym in coin_symbols or sym == 'rum' or sym == 'bonus' or sym == 'superbonus':
                        if pos not in functional_near_crystals:
                            functional_near_crystals.append(pos)
        
        empty_cells = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c] == '' and owners[r][c] == bandit_color]
        temp_allowed = set(all_color_crystals) | set(empty_cells) | {current_pos}
        accessible_for_highlight = [pos for pos in all_color_crystals if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=temp_allowed)]
        accessible_functional = [pos for pos in functional_near_crystals if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=temp_allowed)]
        
        # Подсвечиваем только доступные кристаллы И функциональные символы
        highlight_targets(accessible_for_highlight + accessible_functional + [current_pos], window_width, window_height, board, duration=0.5, button_opacity=0)
        
        # Собираем кристаллы
        duel_triggered = False
        while True:
            # Ищем ВСЕ доступные кристаллы выбранного цвета (через пустые клетки и через кристаллы этого цвета)
            all_color_crystals = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c].startswith(f'low{chosen_color}')]
            
            # Находим ВСЕ функциональные символы на доске (не только рядом с кристаллами)
            functional_near_crystals = []
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    sym = board[r][c]
                    pos = (r, c)
                    if sym in upgrade_symbols or sym in coin_symbols or sym == 'rum' or sym == 'bonus' or sym == 'superbonus':
                        functional_near_crystals.append(pos)
            
            if not all_color_crystals and not functional_near_crystals:
                break
            
            # Кристаллы: делим на безопасные и опасные
            danger_crystals = []
            safe_crystals = []
            for pos in all_color_crystals:
                if has_adjacent_parrot(pos):
                    danger_crystals.append(pos)
                else:
                    safe_crystals.append(pos)
            
            # Функциональные: делим на безопасные и опасные
            danger_functional = []
            safe_functional = []
            for pos in functional_near_crystals:
                if has_adjacent_parrot(pos):
                    danger_functional.append(pos)
                else:
                    safe_functional.append(pos)
            
            # ВАЖНО: Если есть безопасные цели, ИСКЛЮЧАЕМ опасные из allowed_positions!
            # Это не даст бандиту случайно пройти через опасный кристалл к безопасному
            empty_cells = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board[r][c] == '' and owners[r][c] == bandit_color]
            
            if safe_crystals or safe_functional:
                # Есть безопасные цели - ИСКЛЮЧАЕМ опасные из пути
                allowed_positions = set(safe_crystals) | set(safe_functional) | set(empty_cells) | {current_pos}
            else:
                # Только опасные цели остались - разрешаем идти через опасные
                allowed_positions = set(all_color_crystals) | set(functional_near_crystals) | set(empty_cells) | {current_pos}
            
            # Строгий приоритет с проверкой доступности
            reachable_safe_crystals = []
            reachable_safe_functional = []
            reachable_danger_functional = []
            reachable_danger_crystals = []
            
            # Проверяем доступность безопасных кристаллов
            for pos in safe_crystals:
                if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=allowed_positions):
                    reachable_safe_crystals.append(pos)
            
            # Проверяем доступность безопасных функциональных
            for pos in safe_functional:
                if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=allowed_positions):
                    reachable_safe_functional.append(pos)
            
            # Если нет безопасных целей, проверяем опасные
            if not reachable_safe_crystals and not reachable_safe_functional:
                # Теперь можно идти к опасным, обновляем allowed_positions
                allowed_positions = set(all_color_crystals) | set(functional_near_crystals) | set(empty_cells) | {current_pos}
                
                for pos in danger_functional:
                    if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=allowed_positions):
                        reachable_danger_functional.append(pos)
                
                for pos in danger_crystals:
                    if a_star_path(board, owners, current_pos, pos, bandit_color, all_targets, allowed_positions=allowed_positions):
                        reachable_danger_crystals.append(pos)
            
            # Выбираем цель по строгому приоритету
            if reachable_safe_crystals:
                target_pos = min(reachable_safe_crystals, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
            elif reachable_safe_functional:
                target_pos = min(reachable_safe_functional, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
            elif reachable_danger_functional:
                target_pos = min(reachable_danger_functional, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
            elif reachable_danger_crystals:
                target_pos = min(reachable_danger_crystals, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
            else:
                break
            
            # Строим путь с правильными allowed_positions
            path = a_star_path(board, owners, current_pos, target_pos, bandit_color, all_targets, allowed_positions=allowed_positions)
            if not path:
                break
            
            for i in range(1, len(path)):
                next_pos = path[i]
                is_last_step = (i == len(path) - 1)
                
                # Сначала собираем символ на клетке
                prev_sym = board[next_pos[0]][next_pos[1]]
                if prev_sym in crystal_targets:
                    level = int(prev_sym.split('_')[1])
                    win_amount = payout_table[prev_sym.split('_')[0]][level] * base_bet
                    bandit_counter += win_amount
                    play_sound('podbor')
                elif prev_sym in coin_symbols:
                    multiplier = coin_multipliers[prev_sym]
                    win_amount = multiplier * base_bet
                    bandit_counter += win_amount
                    play_sound('podbor')
                elif prev_sym in upgrade_symbols:
                    levels = {'levelup': 1, 'levelup_2': 2, 'levelup_3': 3, 'levelupall': 1, 'levelupall_2': 2, 'levelupall_3': 3}[prev_sym]
                    all_colors = 'all' in prev_sym
                    if all_colors:
                        upgrade_crystals(board, 0, levels, True)
                    else:
                        # Бандит апгрейдит случайный цвет
                        random_color = random.randint(1, 4)
                        upgrade_crystals(board, random_color, levels)
                    play_sound('upgrade')
                elif prev_sym == 'rum':
                    # Бандит поднимает ром - трансформирует соседние кристаллы в текущий цвет
                    # Но гарантирует хотя бы один специальный символ
                    adjacent_positions = []
                    for dr, dc in directions:
                        nr, nc = next_pos[0] + dr, next_pos[1] + dc
                        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                            if board[nr][nc].startswith('low'):
                                adjacent_positions.append((nr, nc))
                    
                    if adjacent_positions:
                        # Гарантируем один специальный символ
                        special_symbols = ['coin2', 'coin5', 'coin10', 'bonus', 'rum', 'levelup']
                        special_pos = random.choice(adjacent_positions)
                        board[special_pos[0]][special_pos[1]] = random.choice(special_symbols)
                        
                        # Остальные перекрашиваем в текущий цвет
                        for pos in adjacent_positions:
                            if pos != special_pos and board[pos[0]][pos[1]].startswith('low'):
                                old_level = board[pos[0]][pos[1]].split('_')[1]
                                board[pos[0]][pos[1]] = f'low{chosen_color}_{old_level}'
                    play_sound('upgrade')
                elif prev_sym == 'bonus':
                    # Бандит поднимает бонус - добавляем в счетчик
                    bonus_count += 1
                    play_sound('podbor')
                elif prev_sym == 'superbonus':
                    # Бандит поднимает супербонус - добавляем в счетчик
                    bonus_count += 1
                    play_sound('podbor')
                
                # Двигаем бандита на новую позицию
                board[current_pos[0]][current_pos[1]] = ''
                owners[current_pos[0]][current_pos[1]] = bandit_color
                board[next_pos[0]][next_pos[1]] = 'bandit'
                current_pos = next_pos
                bandit_pos = next_pos
                screen.blit(scaled_background, (0, 0))
                draw_board(board, window_width, window_height, [], button_opacity=0)
                pygame.display.flip()
                time.sleep(0.15)
                
                # ПОСЛЕ того как встали на клетку, проверяем есть ли попугай рядом
                adjacent_info = find_adjacent_parrot(next_pos)
                if adjacent_info:
                    duel_result = resolve_duel((adjacent_info[0], adjacent_info[1]), adjacent_info[2])
                    duel_triggered = True
                    if duel_result == 'parrot_win':
                        return board, owners
                    break
            if duel_triggered:
                break
    return board, owners

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def show_duel_window(window_width, window_height, amount, parrot_wins, parrot):
    bg_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    bg_surface.fill((50, 50, 50, 200))
    duel_text = font.render("DUEL", True, WHITE)
    amount_text = small_font.render(f"{amount:.2f}", True, WHITE)
    bandit_image = symbol_images['bandit']
    parrot_image = symbol_images[parrot + 'win'] if parrot + 'win' in symbol_images else symbol_images[parrot]
    start_time = time.time()
    while time.time() - start_time < 1.5:
        screen.blit(bg_surface, (0, 0))
        screen.blit(duel_text, (window_width // 2 - duel_text.get_width() // 2, window_height // 2 - 100))
        screen.blit(amount_text, (window_width // 2 - amount_text.get_width() // 2, window_height // 2))
        screen.blit(bandit_image, (window_width // 2 - 250, window_height // 2 - 50))
        screen.blit(parrot_image, (window_width // 2 + 50, window_height // 2 - 50))
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)
    fade_duration = 0.5
    fade_start = time.time()
    while time.time() - fade_start < fade_duration:
        elapsed = time.time() - fade_start
        progress = elapsed / fade_duration
        alpha = int(255 * (1 - progress))
        if parrot_wins:
            bandit_copy = bandit_image.copy()
            bandit_copy.set_alpha(alpha)
            screen.blit(bg_surface, (0, 0))
            screen.blit(duel_text, (window_width // 2 - duel_text.get_width() // 2, window_height // 2 - 100))
            screen.blit(amount_text, (window_width // 2 - amount_text.get_width() // 2, window_height // 2))
            screen.blit(bandit_copy, (window_width // 2 - 250, window_height // 2 - 50))
            screen.blit(parrot_image, (window_width // 2 + 50, window_height // 2 - 50))
        else:
            parrot_copy = parrot_image.copy()
            parrot_copy.set_alpha(alpha)
            screen.blit(bg_surface, (0, 0))
            screen.blit(duel_text, (window_width // 2 - duel_text.get_width() // 2, window_height // 2 - 100))
            screen.blit(amount_text, (window_width // 2 - amount_text.get_width() // 2, window_height // 2))
            screen.blit(bandit_image, (window_width // 2 - 250, window_height // 2 - 50))
            screen.blit(parrot_copy, (window_width // 2 + 50, window_height // 2 - 50))
        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

def spin_animation(board, window_width, window_height, seed=None):
    global last_win, button_opacity, total_crystals_collected, filled_counters, \
           current_counter_level, is_bonus_game, bonus_count, is_buy_fs, is_buy_fs_300, is_buy_fs_900, is_buy_fs_3600, is_buy_fs_18000, is_40_40_20, \
           superbonus_count, active_modifier, is_super_spin, key_was_collected, bandit_was_caught, \
           collected_bonus_this_spin, collected_superbonus_this_spin, collected_key_this_spin, \
           maxwin_triggered, maxwin_abort_cycle, force_super_gamble_then_collect

    last_win = 0
    maxwin_triggered = False
    maxwin_abort_cycle = False
    key_was_collected = False  # Сбрасываем флаг при новом спине
    bandit_was_caught = False  # Сбрасываем флаг при новом спине
    collected_bonus_this_spin = 0  # Сбрасываем счетчик собранных бонусов
    collected_superbonus_this_spin = 0  # Сбрасываем счетчик собранных супербонусов
    collected_key_this_spin = 0  # Сбрасываем счетчик собранных ключей
    if seed is not None:
        random.seed(seed)

    if not is_bonus_game:
        superbonus_count = 0
        bonus_count = 0
        total_crystals_collected = 0
        filled_counters = 0
        current_counter_level = 0

        # <<< Super-модификатор: каждый спин даёт 1 заполненный счётчик >>>
        if is_super_spin:
            filled_counters = 1

    # Сохраняем копию доски для анимации падения
    board_copy = [row[:] for row in board]
    animate_fall_out(board_copy, window_width, window_height, do_fade=not is_bonus_game)
    time.sleep(0.5)

    # Шанс бесплатного срабатывания модификатора Buy FS во время обычного спина
    # Применяется только если игрок не выбрал явный модификатор покупки/специальный режим
    trigger_free_buy_fs = False
    try:
        special_modes_selected = (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20 or is_3_lvl or is_garant_spin or is_bandit_mode or is_super_spin)
    except NameError:
        special_modes_selected = (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20)

    # Не даём случайному Free Buy FS срабатывать во время бонусной или супербонусной игры
    try:
        superbonus_active = globals().get('is_superbonus_game', False)
    except Exception:
        superbonus_active = False

    if not special_modes_selected and not is_bonus_game and not superbonus_active:
        # Определяем знаменатель (1 из N)
        if is_bet_plus_plus:
            denom = 92
        elif is_bet_plus:
            denom = 138
        else:
            denom = 277

        if random.randint(1, denom) == 1:
            trigger_free_buy_fs = True
            is_buy_fs = True
            active_modifier = 'bonus_buy'  # Показываем картинку модификатора

    # Сохраняем флаг для возможности правильного реплея
    try:
        globals()['last_free_buy_fs'] = trigger_free_buy_fs
    except Exception:
        pass

    new_board, gigablocks = generate_board()

    # Для FS 18000x включаем спец-режим гэмбла на текущий спин
    force_super_gamble_then_collect = bool(is_buy_fs_18000)

    # Если сработал бесплатный Buy FS — делаем паузу в 1 секунду перед падением сетки
    if trigger_free_buy_fs:
        time.sleep(1.0)

    # Отключаем одноразовые покупки (Buy FS / 300 / 900 / 40-40-20)
    is_buy_fs = False
    is_buy_fs_300 = False
    is_buy_fs_900 = False
    is_buy_fs_3600 = False
    is_buy_fs_18000 = False
    is_40_40_20 = False

    animate_drop_in(new_board, window_width, window_height, button_opacity=button_opacity)
    total_win, final_board = collection_cycle(new_board, window_width, window_height, seed=seed)
    force_super_gamble_then_collect = False

    screen.blit(scaled_background, (0, 0))
    draw_board(final_board, window_width, window_height, [], button_opacity=button_opacity)
    pygame.display.flip()

    active_modifier = None                     # сбрасываем картинку модификатора
    # <<< НЕ сбрасываем is_super_spin – он остаётся включённым >>>

    return final_board, gigablocks

async def main():
    global scaled_background, button_opacity, is_buy_fs, balance, current_user
    init_db()  # Инициализация БД
    # Сохраняем исходные вероятности мешков
    original_coin_probs = {
        'coin2': 0.177, 'coin5': 0.138, 'coin10': 0.069, 'coin25': 0.055,
        'coin50': 0.018, 'coin100': 0.004, 'coin500': 0.001, 'coin1000': 0.0005,
        'coin2500': 0.0002, 'coinmaxwin': 0.0001
    }
    for k, v in original_coin_probs.items():
        if k not in symbol_probabilities:
            symbol_probabilities[k] = v
    play_background_music()
    global base_bet, bet, last_win, is_spinning
    global is_bet_plus, is_bet_plus_plus, is_bandit_mode, is_super_spin
    global fs_price, super_bonus_price, is_garant_spin, is_3_lvl
    global bet_selector_open
    global settings_open, volume, fast_spin, bandit_key_alpha, bonus_count
    bonus_count = 0  # Инициализация счетчика бонусов
    
    display_info = pygame.display.Info()
    window_width = display_info.current_w
    window_height = display_info.current_h

    global WIDTH, HEIGHT, INFO_PANEL_HEIGHT
    INFO_PANEL_HEIGHT = 150
    WIDTH = min(window_width, GRID_COLS * CELL_SIZE)
    HEIGHT = min(window_height - INFO_PANEL_HEIGHT, GRID_ROWS * CELL_SIZE)
    INFO_PANEL_HEIGHT = window_height - HEIGHT if window_height - HEIGHT >= 150 else 150

    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("3 в ряд)")
    scaled_background = pygame.transform.scale(background_image, (window_width, window_height))

    # Экран авторизации
    login_result = show_login_screen(window_width, window_height)
    if login_result is None:
        pygame.quit()
        sys.exit()
    current_user, balance = login_result  # Загружаем баланс из БД
    # После загрузки пользователя
    if current_user == 'alexkrit' or current_user == '1':
    # Восстанавливаем исходные вероятности мешков (на случай перезапуска)
        update_coin_probabilities()  # с is_god_mod = False
    board, gigablocks = generate_board()

    minus_btn = plus_btn = spin_btn = bet_plus_btn = bet_plus_plus_btn = bandit_btn = super_spin_btn = None
    buy_fs_btn = buy_fs_300_btn = buy_fs_900_btn = buy_40_40_20_btn = buy_fs_3600_btn = buy_fs_18000_btn = garant_spin_btn = three_lvl_btn = settings_btn = replay_btn = stats_btn = md_btn = god_mode_btn = None
    settings_rect = volume_slider = fast_spin_btn = close_btn = None
    dragging_slider = False
    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPACTIVE:
                    if event.gain == 0:
                        running = False
                        # Здесь можно приостановить игру, музыку и т.д.
                    elif event.gain == 1:
                        running = True
                        # Здесь можно возобновить игру
        while running:
            fs_price = base_bet * 54
            super_bonus_price = base_bet * 500
            buy_fs_price = base_bet * 100  # Стоимость Buy FS
            if is_3_lvl:
                bet = base_bet * 10
            elif is_super_spin:
                bet = base_bet * 7.5
            elif is_garant_spin:
                bet = base_bet * 5
            elif is_bet_plus_plus:
                bet = base_bet * 3
            elif is_bet_plus:
                bet = base_bet * 2
            elif is_bandit_mode:
                bet = base_bet * 25
            elif is_buy_fs_18000:
                bet = base_bet * 18000
            elif is_buy_fs_3600:
                bet = base_bet * 3600
            elif is_buy_fs_900:
                bet = base_bet * 900
            elif is_buy_fs_300:
                bet = base_bet * 300
            elif is_40_40_20:
                bet = base_bet * 200
            elif is_buy_fs:
                bet = base_bet * 100
            else:
                bet = base_bet

            bandit_key_alpha = 255 if is_bandit_mode else 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.ACTIVEEVENT:
                    if event.state == pygame.APPACTIVE:
                        if event.gain == 0:
                            running = False
                            # Здесь можно приостановить игру, музыку и т.д.
                        elif event.gain == 1:
                            running = True
                            # Здесь можно возобновить игру
                elif event.type == pygame.VIDEORESIZE:
                    window_width, window_height = event.w, event.h
                    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                    WIDTH = min(window_width, GRID_COLS * CELL_SIZE)
                    HEIGHT = min(window_height - INFO_PANEL_HEIGHT, GRID_ROWS * CELL_SIZE)
                    INFO_PANEL_HEIGHT = window_height - HEIGHT if window_height - HEIGHT >= 150 else 150
                    scaled_background = pygame.transform.scale(background_image, (window_width, window_height))
                # -------------------------------------------------
# 1. В обработчике клавиши SPACE
# -------------------------------------------------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not settings_open:
                        if not is_spinning and balance >= bet:
                            play_sound('button')
                            play_sound('spin')
                            is_spinning = True
                
                            # <-- НОВАЯ СТРОКА: задаём модификатор перед спином -->
                            active_modifier = (
                                'god_mode'       if is_god_mode_bet else
                                '3lvl'           if is_3_lvl else
                                'garant_spin'    if is_garant_spin else
                                'bonus_hunt_3x'  if is_bet_plus_plus else
                                'bonus_hunt_2x'  if is_bet_plus else
                                'bonus_buy'      if (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20) else
                                'super_spin'     if is_super_spin else
                                None
                            )
                            # -------------------------------------------------
                
                            # Генерируем сид перед спином
                            seed = random.randint(0, 2**32 - 1)
                            bet_multiplier = (
                                2000 if is_god_mode_bet else
                                10 if is_3_lvl else
                                5  if is_garant_spin else
                                3  if is_bet_plus_plus else
                                2 if is_bet_plus else
                                25 if is_bandit_mode else
                                18000 if is_buy_fs_18000 else
                                3600 if is_buy_fs_3600 else
                                900 if is_buy_fs_900 else
                                300 if is_buy_fs_300 else
                                200 if is_40_40_20 else
                                100 if is_buy_fs else
                                7.5 if is_super_spin else
                                1
                            )
                            balance -= bet
                            update_balance(current_user, balance)  # Обновляем баланс в БД после списания
                            update_stats(current_user, bet)  # Обновляем статистику: добавляем bet
                            board, gigablocks = spin_animation(board, window_width, window_height, seed=seed)
                            balance += last_win
                            update_balance(current_user, balance)  # Обновляем в БД после выигрыша
                            update_stats(current_user, 0, last_win)  # Обновляем статистику: добавляем win
                            save_spin_data(seed, bet_multiplier)
                            is_spinning = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if settings_open:
                        if volume_slider and volume_slider.collidepoint(mx, my):
                            dragging_slider = True
                        elif fast_spin_btn and fast_spin_btn.collidepoint(mx, my):
                            play_sound('button')
                            fast_spin = not fast_spin
                        elif close_btn and close_btn.collidepoint(mx, my):
                            play_sound('button')
                            settings_open = False
                    # Обработка нажатия на кнопки в окне выбора ставок
                    if bet_buttons:
                        for bet_rect, bet_amount in bet_buttons:
                            if bet_rect.collidepoint(mx, my):
                                play_sound('button')
                                base_bet = bet_amount
                                bet = base_bet * (10 if is_3_lvl else 5 if is_garant_spin else 3 if is_bet_plus_plus else 2 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                                bet_selector_open = False
                    elif not is_spinning:
                        if bet_btn and bet_btn.collidepoint(mx, my):
                            play_sound('button')
                            bet_selector_open = not bet_selector_open
                        elif spin_btn and spin_btn.collidepoint(mx, my) and balance >= bet:
                            play_sound('button')
                            play_sound('spin')
                            is_spinning = True
                            # Устанавливаем active_modifier перед спином
                            active_modifier = 'god_mode' if is_god_mode_bet else '3lvl' if is_3_lvl else 'garant_spin' if is_garant_spin else 'super_spin' if is_super_spin else 'bonus_hunt_3x' if is_bet_plus_plus else 'bonus_hunt_2x' if is_bet_plus else 'bonus_buy' if (is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20) else None
                            # Генерируем сид перед спином
                            seed = random.randint(0, 2**32 - 1)  # Случайный сид как int
                            # Вычисляем модификатор ставки
                            bet_multiplier = (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 3 if is_bet_plus_plus else 2 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                            balance -= bet
                            update_balance(current_user, balance)  # Обновляем в БД
                            update_stats(current_user, bet)  # Обновляем статистику: добавляем bet
                            board, gigablocks = spin_animation(board, window_width, window_height, seed=seed)  # Передаём seed
                            balance += last_win
                            update_balance(current_user, balance)  # Обновляем в БД
                            update_stats(current_user, 0, last_win)  # Обновляем статистику: добавляем win
                            # После спина сохраняем данные
                            save_spin_data(seed, bet_multiplier)
                            is_spinning = False
                        elif bet_plus_btn and bet_plus_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('bet+')
                            if is_buy_fs or is_buy_fs_300 or is_buy_fs_900 or is_buy_fs_3600 or is_buy_fs_18000 or is_40_40_20:
                                available_positions = [(r, c) for r in range(1, GRID_ROWS-1) for c in range(1, GRID_COLS-1)]
                            else:
                                available_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)]
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif bet_plus_plus_btn and bet_plus_plus_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('bet++')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif bandit_btn and bandit_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('bandit')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif super_spin_btn and super_spin_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('super_spin')
                        elif settings_btn and settings_btn.collidepoint(mx, my):
                            play_sound('button')
                            settings_open = True
                        elif buy_fs_btn and buy_fs_btn.collidepoint(mx, my) and balance >= buy_fs_price:
                            play_sound('button')
                            toggle_modifier('buy_fs')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif buy_fs_300_btn and buy_fs_300_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('buy_fs_300')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif buy_fs_900_btn and buy_fs_900_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('buy_fs_900')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif buy_fs_3600_btn and buy_fs_3600_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('buy_fs_3600')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif buy_fs_18000_btn and buy_fs_18000_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('buy_fs_18000')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif buy_40_40_20_btn and buy_40_40_20_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('40_40_20')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif god_mode_btn and god_mode_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('god_mode')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif garant_spin_btn and garant_spin_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('garant')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif three_lvl_btn and three_lvl_btn.collidepoint(mx, my):
                            play_sound('button')
                            toggle_modifier('3lvl')
                            bet = base_bet * (2000 if is_god_mode_bet else 10 if is_3_lvl else 5 if is_garant_spin else 2 if is_bet_plus_plus else 1.5 if is_bet_plus else 25 if is_bandit_mode else 18000 if is_buy_fs_18000 else 3600 if is_buy_fs_3600 else 900 if is_buy_fs_900 else 300 if is_buy_fs_300 else 200 if is_40_40_20 else 100 if is_buy_fs else 1)
                        elif replay_btn and replay_btn.collidepoint(mx, my):
                            play_sound('button')
                            board = show_replay_window(window_width, window_height, board)
                        elif stats_btn and stats_btn.collidepoint(mx, my):
                            play_sound('button')
                            show_stats_window(window_width, window_height)
                        elif md_btn and md_btn.collidepoint(mx, my):
                            play_sound('button')
                            show_markdown_viewer('EXAMPLE_WITH_IMAGES.md', window_width, window_height)
                        elif admin_btn and admin_btn.collidepoint(mx, my) and current_user == 'alexkrit' and current_user == '1':
                            play_sound('button')
                        elif logout_btn and logout_btn.collidepoint(mx, my):
                            play_sound('button')
                            # Выход из аккаунта - перезапуск игры
                            login_result = show_login_screen(window_width, window_height)
                            if login_result is None:
                                pygame.quit()
                                sys.exit()
                            current_user, balance = login_result
                            if current_user == 'alexkrit' or current_user == '1':
                                update_coin_probabilities()
                            board, gigablocks = generate_board()
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_slider = False
                elif event.type == pygame.MOUSEMOTION and dragging_slider:
                    mx, my = pygame.mouse.get_pos()
                    if volume_slider:
                        new_volume = ((mx - volume_slider.x) / volume_slider.width) * 100
                        volume = max(0, min(100, new_volume))
                        pygame.mixer.music.set_volume(volume / 100.0)
                        for sound in ['podbor', 'button', 'upgrade', 'spin', 'padenie', 'padenie_popuga', 'dance']:
                            try:
                                play_sound(sound)
                                pygame.mixer.stop()
                            except:
                                pass

            (bet_btn, spin_btn, bet_plus_btn, bet_plus_plus_btn, bandit_btn, super_spin_btn, settings_btn,
            buy_fs_btn, buy_fs_300_btn, buy_fs_900_btn, buy_40_40_20_btn, buy_fs_3600_btn, buy_fs_18000_btn, garant_spin_btn, three_lvl_btn, replay_btn, stats_btn, md_btn, god_mode_btn,
            admin_btn, logout_btn, settings_rect, volume_slider, fast_spin_btn, close_btn, bet_buttons) = draw_board(
                board, window_width, window_height, gigablocks, button_opacity=button_opacity, current_user=current_user)

            pygame.display.flip()
            clock.tick(FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())