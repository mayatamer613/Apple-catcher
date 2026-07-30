import array
import json
import math
import os
import random
import sys
import pygame

# --- وظيفة ذكية لتحديد مسار الملفات بأمان تام ---
def get_path(filename):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


# 1. تشغيل محرك الألعاب والنظام الصوتي أولاً
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# منع ظهور الكيبورد تلقائياً برمجياً على الموبايل
try:
  pygame.key.stop_text_input()
except:
  pass

# حل مشكلة الأبعاد والتحكم للموبايل
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Apple Catcher - Pro Edition")

# تحميل اللوجو والخطوط مع حماية كاملة من الانهيار
LOGO_PATH = get_path("logo.png")
FONT_PATH = get_path("cursive.ttf")

logo_img = None
if os.path.exists(LOGO_PATH):
  try:
    raw_logo = pygame.image.load(LOGO_PATH)
    logo_w = int(WIDTH * 0.28)
    logo_h = int(raw_logo.get_height() * (logo_w / raw_logo.get_width()))
    logo_img = pygame.transform.scale(raw_logo, (logo_w, logo_h))
  except Exception as e:
    print("تنبيه: لم يتم تحميل اللوجو:", e)


def get_game_font(size):
  if os.path.exists(FONT_PATH):
    try:
      return pygame.font.Font(FONT_PATH, size)
    except:
      pass
  return pygame.font.SysFont("sans", size, bold=True, italic=True)


font = get_game_font(int(WIDTH * 0.04))
top_bar_font = get_game_font(int(WIDTH * 0.032))
btn_font = get_game_font(int(WIDTH * 0.036))
over_font = get_game_font(int(WIDTH * 0.07))

# --- نظام حفظ البيانات (الـ High Scores وإجمالي الجواهر) في ملف JSON آمن ---
if "ANDROID_PRIVATE_DATA" in os.environ:
  SAVE_DIR = os.environ["ANDROID_PRIVATE_DATA"]
else:
  SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

GAME_DATA_FILE = os.path.join(SAVE_DIR, "apple_catcher_gamedata_v9.json")


def load_game_data():
  if os.path.exists(GAME_DATA_FILE):
    try:
      with open(GAME_DATA_FILE, "r") as f:
        data = json.load(f)
        if isinstance(data, dict) and "scores" in data:
          return data
    except:
      pass
  return {
      "scores": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "inf": 0},
      "total_gems": 0,
  }


def save_game_data(data):
  try:
    os.makedirs(os.path.dirname(GAME_DATA_FILE), exist_ok=True)
    with open(GAME_DATA_FILE, "w") as f:
      json.dump(data, f)
  except Exception as e:
    print("فشل الحفظ:", e)


game_data = load_game_data()
high_scores = game_data["scores"]

# الألوان الهادئة والفاخرة
SKY_BLUE = (145, 210, 245)
GRASS_GREEN = (52, 152, 219)
BROWN = (139, 69, 19)
RED = (231, 76, 60)
GOLD = (241, 196, 15)
LIME_GREEN = (46, 204, 113)
CYAN = (52, 152, 219)
SHIELD_BLUE = (0, 191, 255)
GEM_COLOR = (0, 229, 255)
MAGNET_RED = (231, 76, 60)
MAGNET_SILVER = (220, 220, 220)
BLACK = (44, 62, 80)
YELLOW = (241, 196, 15)
ORANGE = (230, 126, 34)
WHITE = (255, 255, 255)
BTN_COLOR = (52, 73, 94)
RESET_COLOR = (149, 165, 166)

particles = []
floating_texts = []
clouds = [
    {
        "x": random.randint(0, WIDTH),
        "y": random.randint(int(HEIGHT * 0.05), int(HEIGHT * 0.3)),
        "speed": random.uniform(0.4, 0.9),
        "w": random.randint(80, 140),
    }
    for _ in range(5)
]


# دالة توليد المؤثرات الصوتية الناعمة
def generate_sound(freq_start, freq_end, duration_ms, wave_type="sine"):
  sample_rate = 22050
  num_samples = int(sample_rate * (duration_ms / 1000.0))
  buf = array.array("h", [0] * num_samples)
  for i in range(num_samples):
    t = i / float(sample_rate)
    current_freq = freq_start + (freq_end - freq_start) * (
        i / float(num_samples)
    )
    envelope = math.sin(math.pi * i / num_samples)
    if wave_type == "sine":
      value = int(12000 * math.sin(2 * math.pi * current_freq * t) * envelope)
    elif wave_type == "square":
      value = (
          10000 if math.sin(2 * math.pi * current_freq * t) > 0 else -10000
      )
    buf[i] = value
  return pygame.mixer.Sound(buffer=buf)


# دالة توليد موسيقى خلفية هادئة تشبه البيانو تماماً
def generate_peaceful_piano_music():
  sample_rate = 22050
  piano_melody = [
      (261.63, 400),
      (329.63, 400),
      (392.00, 400),
      (523.25, 800),
      (392.00, 400),
      (329.63, 400),
      (220.00, 400),
      (261.63, 400),
      (349.23, 400),
      (440.00, 800),
      (349.23, 400),
      (293.66, 400),
  ]
  full_buf = array.array("h")
  for freq, dur_ms in piano_melody:
    num_samples = int(sample_rate * (dur_ms / 1000.0))
    for i in range(num_samples):
      t = i / float(sample_rate)
      envelope = math.exp(-3.0 * (i / sample_rate)) * math.sin(
          math.pi * i / num_samples
      )
      value = int(8000 * math.sin(2 * math.pi * freq * t) * envelope)
      full_buf.append(value)
  return pygame.mixer.Sound(buffer=full_buf)


# توليد المؤثرات وموسيقى البيانو الهادئة
apple_sound = generate_sound(440, 880, 120, "sine")
gold_sound = generate_sound(600, 1200, 180, "sine")
green_sound = generate_sound(350, 700, 220, "sine")
shield_sound = generate_sound(500, 1100, 200, "sine")
slow_sound = generate_sound(800, 400, 250, "sine")
gem_sound = generate_sound(900, 1600, 150, "sine")
magnet_sound = generate_sound(300, 700, 220, "sine")
fever_sound = generate_sound(500, 1000, 150, "sine")
bomb_sound = generate_sound(200, 60, 200, "square")
lose_sound = generate_sound(280, 50, 900, "square")

background_music = generate_peaceful_piano_music()
background_music.set_volume(0.3)
background_music.play(loops=-1)


def create_particles(
    x, y, color_palette, num=20, speed_min=4, speed_max=12, life_max=40
):
  for _ in range(num):
    angle = random.uniform(0, 6.28)
    speed = random.uniform(speed_min, speed_max)
    color = (
        random.choice(color_palette)
        if isinstance(color_palette, list)
        else color_palette
    )
    particles.append({
        "x": x,
        "y": y,
        "vx": speed * math.cos(angle),
        "vy": speed * math.sin(angle),
        "color": color,
        "radius": random.randint(4, 10),
        "life": random.randint(20, life_max),
    })


def add_floating_text(text, x, y, color=GOLD):
  floating_texts.append({"text": text, "x": x, "y": y, "color": color, "life": 30})


def update_and_draw_effects():
  for p in particles[:]:
    p["x"] += p["vx"]
    p["y"] += p["vy"]
    p["vy"] += 0.2
    p["life"] -= 1
    if p["life"] <= 0:
      particles.remove(p)
    else:
      pygame.draw.circle(
          screen, p["color"], (int(p["x"]), int(p["y"])), p["radius"]
      )

  for ft in floating_texts[:]:
    ft["y"] -= 2
    ft["life"] -= 1
    if ft["life"] <= 0:
      floating_texts.remove(ft)
    else:
      txt_surf = btn_font.render(ft["text"], True, ft["color"])
      screen.blit(txt_surf, (ft["x"] - txt_surf.get_width() // 2, ft["y"]))


def reset_all_data():
  global game_data, high_scores
  game_data = {
      "scores": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "inf": 0},
      "total_gems": 0,
  }
  high_scores = game_data["scores"]
  save_game_data(game_data)


# إعداد السلة ومقاساتها
basket_width, basket_height = int(WIDTH * 0.24), int(HEIGHT * 0.055)
basket_x = WIDTH // 2 - basket_width // 2
basket_y = HEIGHT - int(HEIGHT * 0.18)
basket_speed = int(WIDTH * 0.018)

# أزرار التحكم باللمس
side_btn_size = int(WIDTH * 0.18)
btn_display_y = HEIGHT - int(HEIGHT * 0.32)
left_btn_rect = pygame.Rect(15, btn_display_y, side_btn_size, side_btn_size)
right_btn_rect = pygame.Rect(
    WIDTH - 15 - side_btn_size, btn_display_y, side_btn_size, side_btn_size
)

# زر المنيو على الجنب في الأسفل بجوار أزرار الحركة
menu_btn_rect = pygame.Rect(
    15,
    btn_display_y - int(side_btn_size * 0.75) - 10,
    side_btn_size,
    int(side_btn_size * 0.65),
)

# أزرار القائمة الرئيسية
btn_w = int(WIDTH * 0.42)
btn_h = int(HEIGHT * 0.062)
left_x = int(WIDTH * 0.06)
right_x = int(WIDTH * 0.52)
start_y_offset = int(HEIGHT * 0.35)
row_gap = int(HEIGHT * 0.075)

level_buttons = [
    {
        "rect": pygame.Rect(left_x, start_y_offset, btn_w, btn_h),
        "key": "1",
        "name": "Level 1",
        "color": (255, 105, 180),
    },
    {
        "rect": pygame.Rect(right_x, start_y_offset, btn_w, btn_h),
        "key": "2",
        "name": "Level 2",
        "color": (255, 152, 0),
    },
    {
        "rect": pygame.Rect(left_x, start_y_offset + row_gap, btn_w, btn_h),
        "key": "3",
        "name": "Level 3",
        "color": (241, 196, 15),
    },
    {
        "rect": pygame.Rect(right_x, start_y_offset + row_gap, btn_w, btn_h),
        "key": "4",
        "name": "Level 4",
        "color": (46, 204, 113),
    },
    {
        "rect": pygame.Rect(
            left_x, start_y_offset + row_gap * 2, btn_w, btn_h
        ),
        "key": "5",
        "name": "Level 5",
        "color": (0, 188, 212),
    },
    {
        "rect": pygame.Rect(
            right_x, start_y_offset + row_gap * 2, btn_w, btn_h
        ),
        "key": "inf",
        "name": "Infinite",
        "color": (155, 89, 182),
    },
]

reset_hs_btn_rect = pygame.Rect(
    int(WIDTH * 0.15),
    start_y_offset + row_gap * 3 + int(HEIGHT * 0.01),
    int(WIDTH * 0.7),
    btn_h,
)

items = []
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 600)

score = 0
lives = 3
streak = 0
has_shield = False
slow_mo_timer = 0
magnet_timer = 0
game_state = "MENU"
selected_level = "1"


def reset_game():
  global score, lives, streak, has_shield, slow_mo_timer, magnet_timer, items, particles, floating_texts
  score = 0
  lives = 3
  streak = 0
  has_shield = False
  slow_mo_timer = 0
  magnet_timer = 0
  items = []
  particles = []
  floating_texts = []


def draw_basket(
    x, y, is_fever=False, shielded=False, magnetized=False
):
  basket_col = GOLD if is_fever else BROWN
  basket_base = (220, 150, 20) if is_fever else (100, 50, 20)

  if shielded:
    pygame.draw.rect(
        screen,
        SHIELD_BLUE,
        (x - 6, y - 6, basket_width + 12, basket_height + 12),
        width=3,
        border_radius=10,
    )

  if magnetized:
    pygame.draw.rect(
        screen,
        MAGNET_RED,
        (x - 10, y - 10, basket_width + 20, basket_height + 20),
        width=2,
        border_radius=14,
    )

  pygame.draw.rect(
      screen,
      basket_base,
      (x - 2, y + basket_height, basket_width + 4, 6),
      border_radius=3,
  )
  pygame.draw.polygon(
      screen,
      basket_col,
      [
          (x, y),
          (x + basket_width, y),
          (x + basket_width - 18, y + basket_height),
          (x + 18, y + basket_height),
      ],
  )
  for i in range(25, basket_width - 25, 25):
    line_col = (255, 215, 0) if is_fever else (90, 40, 10)
    pygame.draw.line(
        screen, line_col, (x + i, y), (x + i - 5, y + basket_height), 3
    )


def draw_apple(x, y, color=RED):
  radius = int(WIDTH * 0.042)
  pygame.draw.circle(screen, color, (x, y), radius)
  pygame.draw.circle(screen, (255, 255, 255), (x - 5, y - 5), int(radius * 0.3))
  pygame.draw.rect(screen, (90, 60, 30), (x - 2, y - int(radius * 1.3), 4, 10))
  pygame.draw.ellipse(
      screen, (46, 139, 87), (x + 2, y - int(radius * 1.3), 12, 6)
  )


def draw_gem(x, y):
  radius = int(WIDTH * 0.042)
  pygame.draw.polygon(
      screen,
      GEM_COLOR,
      [
          (x, y - radius),
          (x + radius * 0.7, y),
          (x, y + radius),
          (x - radius * 0.7, y),
      ],
  )
  pygame.draw.polygon(
      screen,
      WHITE,
      [
          (x, y - radius * 0.6),
          (x + radius * 0.4, y),
          (x, y + radius * 0.6),
          (x - radius * 0.4, y),
      ],
      width=1,
  )


def draw_magnet_item(x, y):
  r = int(WIDTH * 0.042)
  pygame.draw.rect(
      screen,
      MAGNET_RED,
      (x - r, y - int(r * 0.6), int(r * 0.4), int(r * 1.4)),
      border_radius=4,
  )
  pygame.draw.rect(
      screen,
      MAGNET_RED,
      (x + int(r * 0.6) - int(r * 0.4), y - int(r * 0.6), int(r * 0.4), int(r * 1.4)),
      border_radius=4,
  )
  pygame.draw.rect(
      screen,
      MAGNET_RED,
      (x - r, y + int(r * 0.8) - int(r * 0.4), r * 2, int(r * 0.5)),
      border_radius=4,
  )
  pygame.draw.rect(
      screen,
      MAGNET_SILVER,
      (x - r, y - int(r * 0.6), int(r * 0.4), int(r * 0.5)),
      border_radius=2,
  )
  pygame.draw.rect(
      screen,
      MAGNET_SILVER,
      (x + int(r * 0.6) - int(r * 0.4), y - int(r * 0.6), int(r * 0.4), int(r * 0.5)),
      border_radius=2,
  )


def draw_shield_item(x, y):
  radius = int(WIDTH * 0.042)
  pygame.draw.circle(screen, SHIELD_BLUE, (x, y), radius)
  pygame.draw.circle(screen, WHITE, (x, y), radius - 4, width=2)
  pygame.draw.polygon(
      screen, WHITE, [(x, y - 10), (x + 10, y - 4), (x, y + 10), (x - 10, y - 4)]
  )


def draw_clock_item(x, y):
  radius = int(WIDTH * 0.042)
  pygame.draw.circle(screen, CYAN, (x, y), radius)
  pygame.draw.circle(screen, WHITE, (x, y), radius - 3, width=2)
  pygame.draw.circle(screen, WHITE, (x, y), 3)
  pygame.draw.line(screen, WHITE, (x, y), (x, y - 10), 3)
  pygame.draw.line(screen, WHITE, (x, y), (x + 8, y), 3)


def draw_bomb(x, y, tick):
  radius = int(WIDTH * 0.042)
  pygame.draw.circle(screen, BLACK, (x, y), radius)
  pygame.draw.circle(screen, (80, 80, 80), (x - 6, y - 6), 6)
  pygame.draw.line(
      screen, (180, 100, 0), (x, y - radius), (x + 12, y - radius - 12), 3
  )
  fire_color = YELLOW if (tick // 3) % 2 == 0 else ORANGE
  pygame.draw.circle(screen, fire_color, (x + 12, y - radius - 12), 7)


def draw_ui_buttons():
  # أزرار الحركة
  pygame.draw.rect(screen, BTN_COLOR, left_btn_rect, border_radius=16)
  pygame.draw.rect(screen, WHITE, left_btn_rect, width=2, border_radius=16)
  left_surf = btn_font.render("<", True, WHITE)
  screen.blit(left_surf, left_surf.get_rect(center=left_btn_rect.center))

  pygame.draw.rect(screen, BTN_COLOR, right_btn_rect, border_radius=16)
  pygame.draw.rect(screen, WHITE, right_btn_rect, width=2, border_radius=16)
  right_surf = btn_font.render(">", True, WHITE)
  screen.blit(right_surf, right_surf.get_rect(center=right_btn_rect.center))

  # زر المنيو الجانبي في الأسفل
  pygame.draw.rect(screen, (192, 57, 43), menu_btn_rect, border_radius=12)
  pygame.draw.rect(screen, WHITE, menu_btn_rect, width=2, border_radius=12)
  menu_btn_surf = top_bar_font.render("Menu", True, WHITE)
  screen.blit(
      menu_btn_surf, menu_btn_surf.get_rect(center=menu_btn_rect.center)
  )


def draw_clouds():
  for c in clouds:
    c["x"] -= c["speed"]
    if c["x"] + c["w"] < 0:
      c["x"] = WIDTH + 50
      c["y"] = random.randint(int(HEIGHT * 0.05), int(HEIGHT * 0.3))
    cloud_surf = pygame.Surface((c["w"], 35), pygame.SRCALPHA)
    pygame.draw.ellipse(cloud_surf, (255, 255, 255, 140), (0, 10, c["w"], 22))
    pygame.draw.circle(
        cloud_surf, (255, 255, 255, 140), (int(c["w"] * 0.3), 14), 13
    )
    pygame.draw.circle(
        cloud_surf, (255, 255, 255, 140), (int(c["w"] * 0.7), 12), 15
    )
    screen.blit(cloud_surf, (int(c["x"]), int(c["y"])))


# حلقة اللعبة الأساسية
clock = pygame.time.Clock()
tick_count = 0

while True:
  tick_count += 1
  screen.fill(SKY_BLUE)
  draw_clouds()

  sun_x, sun_y = WIDTH - int(WIDTH * 0.15), int(HEIGHT * 0.12)
  pygame.draw.circle(screen, (255, 245, 220), (sun_x, sun_y), int(WIDTH * 0.08))

  # --- شاشة القائمة الرئيسية ---
  if game_state == "MENU":
    if logo_img:
      logo_rect = logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 7))
      screen.blit(logo_img, logo_rect)
      menu_title = over_font.render("Apple Catcher", True, BLACK)
      screen.blit(
          menu_title, menu_title.get_rect(center=(WIDTH // 2, HEIGHT // 4.1))
      )
    else:
      menu_title = over_font.render("Apple Catcher", True, BLACK)
      screen.blit(
          menu_title, menu_title.get_rect(center=(WIDTH // 2, HEIGHT // 5))
      )

    total_gems_banner = pygame.Rect(
        int(WIDTH * 0.2), int(HEIGHT * 0.25), int(WIDTH * 0.6), int(HEIGHT * 0.055)
    )
    pygame.draw.rect(screen, (44, 62, 80), total_gems_banner, border_radius=12)
    pygame.draw.rect(screen, GEM_COLOR, total_gems_banner, width=2, border_radius=12)
    gems_text_surf = btn_font.render(
        f"💎 Total Gems: {game_data['total_gems']}", True, GEM_COLOR
    )
    screen.blit(
        gems_text_surf,
        gems_text_surf.get_rect(center=total_gems_banner.center),
    )

    for btn in level_buttons:
      pygame.draw.rect(screen, btn["color"], btn["rect"], border_radius=14)
      pygame.draw.rect(screen, WHITE, btn["rect"], width=2, border_radius=14)

      lvl_text = btn["name"]
      hs_val = high_scores.get(btn["key"], 0)
      text_surf = btn_font.render(f"{lvl_text}", True, WHITE)
      hs_surf = get_game_font(int(WIDTH * 0.026)).render(
          f"Best: {hs_val}", True, WHITE
      )

      screen.blit(
          text_surf,
          (
              btn["rect"].centerx - text_surf.get_width() // 2,
              btn["rect"].y + int(btn["rect"].height * 0.14),
          ),
      )
      screen.blit(
          hs_surf,
          (
              btn["rect"].centerx - hs_surf.get_width() // 2,
              btn["rect"].y + int(btn["rect"].height * 0.55),
          ),
      )

    pygame.draw.rect(screen, RESET_COLOR, reset_hs_btn_rect, border_radius=14)
    pygame.draw.rect(screen, WHITE, reset_hs_btn_rect, width=2, border_radius=14)
    reset_surf = btn_font.render("Reset All Data", True, WHITE)
    screen.blit(reset_surf, reset_surf.get_rect(center=reset_hs_btn_rect.center))

  # --- شاشة اللعب الفعلي ---
  elif game_state == "PLAY":
    pygame.draw.rect(
        screen,
        GRASS_GREEN,
        (0, HEIGHT - int(HEIGHT * 0.1), WIDTH, int(HEIGHT * 0.1)),
    )

    for gx in range(0, WIDTH, 30):
      pygame.draw.line(
          screen,
          (41, 128, 185),
          (gx, HEIGHT - int(HEIGHT * 0.1)),
          (gx + 5, HEIGHT - int(HEIGHT * 0.12)),
          3,
      )

    mouse_pressed = pygame.mouse.get_pressed()
    is_fever_mode = streak >= 5
    current_speed = basket_speed * 1.3 if is_fever_mode else basket_speed

    if mouse_pressed[0]:
      mouse_pos = pygame.mouse.get_pos()
      if left_btn_rect.collidepoint(mouse_pos):
        basket_x -= current_speed
      if right_btn_rect.collidepoint(mouse_pos):
        basket_x += current_speed

    if slow_mo_timer > 0:
      slow_mo_timer -= 1
      slow_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
      slow_overlay.fill((0, 200, 255, 12))
      screen.blit(slow_overlay, (0, 0))

    if magnet_timer > 0:
      magnet_timer -= 1

    basket_rect = pygame.Rect(basket_x, basket_y, basket_width, basket_height)
    for item in items[:]:
      if magnet_timer > 0 and item["type"] != "bomb":
        target_x = basket_x + basket_width // 2
        target_y = basket_y
        dx = target_x - item["x"]
        dy = target_y - item["y"]
        dist = math.hypot(dx, dy)
        if dist < 300:
          item["x"] += dx * 0.12
          item["y"] += dy * 0.12

      spd = item["speed"] * 0.5 if slow_mo_timer > 0 else item["speed"]
      item["y"] += spd
      item_rect = pygame.Rect(item["x"] - 20, item["y"] - 20, 40, 40)

      if basket_rect.colliderect(item_rect):
        if item["type"] == "apple":
          streak += 1
          points_earned = 2 if streak >= 5 else 1
          score += points_earned
          apple_sound.play()
          add_floating_text(
              f"+{points_earned}" + (" 🔥" if streak >= 5 else ""),
              item["x"],
              item["y"],
              GOLD if streak >= 5 else RED,
          )
          if streak == 5:
            fever_sound.play()
            add_floating_text("FEVER MODE!", WIDTH // 2, HEIGHT // 3, GOLD)
        elif item["type"] == "gold_apple":
          streak += 1
          score += 3
          gold_sound.play()
          create_particles(
              item["x"],
              item["y"],
              [GOLD, WHITE, YELLOW],
              num=25,
              speed_min=5,
              speed_max=12,
              life_max=25,
          )
          add_floating_text("+3 Star", item["x"], item["y"], GOLD)
        elif item["type"] == "gem":
          streak += 1
          score += 5
          game_data["total_gems"] += 1
          save_game_data(game_data)
          gem_sound.play()
          create_particles(
              item["x"],
              item["y"],
              [GEM_COLOR, WHITE, CYAN],
              num=30,
              speed_min=6,
              speed_max=14,
              life_max=25,
          )
          add_floating_text("+5 GEM! 💎", item["x"], item["y"], GEM_COLOR)
        elif item["type"] == "green_apple":
          if lives < 3:
            lives += 1
          green_sound.play()
          create_particles(
              item["x"],
              item["y"],
              [LIME_GREEN, WHITE],
              num=18,
              speed_min=4,
              speed_max=10,
              life_max=22,
          )
          add_floating_text("+1 HP", item["x"], item["y"], LIME_GREEN)
        elif item["type"] == "shield":
          has_shield = True
          shield_sound.play()
          create_particles(
              item["x"],
              item["y"],
              [SHIELD_BLUE, WHITE],
              num=20,
              speed_min=4,
              speed_max=10,
              life_max=25,
          )
          add_floating_text("SHIELD ON!", item["x"], item["y"], SHIELD_BLUE)
        elif item["type"] == "magnet":
          magnet_timer = 200
          magnet_sound.play()
          create_particles(
              item["x"],
              item["y"],
              [MAGNET_RED, WHITE],
              num=22,
              speed_min=4,
              speed_max=11,
              life_max=25,
          )
          add_floating_text("MAGNET 🧲", item["x"], item["y"], MAGNET_RED)
        elif item["type"] == "slow_mo":
          slow_mo_timer = 220
          slow_sound.play()
          create_particles(
              item["x"],
              item["y"],
              [CYAN, WHITE],
              num=20,
              speed_min=4,
              speed_max=10,
              life_max=25,
          )
          add_floating_text("SLOW-MO ⏳", item["x"], item["y"], CYAN)
        elif item["type"] == "bomb":
          if has_shield:
            has_shield = False
            bomb_sound.play()
            create_particles(
                item["x"],
                item["y"],
                [SHIELD_BLUE, BLACK],
                num=30,
                speed_min=5,
                speed_max=12,
                life_max=25,
            )
            add_floating_text(
                "Shield Blocked!", item["x"], item["y"], SHIELD_BLUE
            )
          else:
            lives -= 1
            streak = 0
            bomb_sound.play()
            create_particles(
                item["x"],
                item["y"],
                [BLACK, RED, ORANGE],
                num=35,
                speed_min=6,
                speed_max=15,
                life_max=30,
            )
            add_floating_text("-1 Bomb", item["x"], item["y"], BLACK)

            if lives <= 0:
              game_state = "LOSE"
              lose_sound.play()
              create_particles(
                  basket_x + basket_width // 2,
                  basket_y,
                  [RED, BLACK, ORANGE, YELLOW, BROWN],
                  num=140,
                  speed_min=18,
                  speed_max=38,
                  life_max=50,
              )

        current_hs = high_scores.get(selected_level, 0)
        if score > current_hs:
          high_scores[selected_level] = score
          game_data["scores"] = high_scores
          save_game_data(game_data)

        items.remove(item)
        continue

      if item["y"] > HEIGHT - int(HEIGHT * 0.11):
        items.remove(item)

    if is_fever_mode and random.random() < 0.5:
      particles.append({
          "x": basket_x + random.randint(0, basket_width),
          "y": basket_y + basket_height,
          "vx": random.uniform(-2, 2),
          "vy": random.uniform(-4, -1),
          "color": random.choice([GOLD, YELLOW, WHITE]),
          "radius": random.randint(3, 6),
          "life": 15,
      })

    draw_basket(
        basket_x,
        basket_y,
        is_fever=is_fever_mode,
        shielded=has_shield,
        magnetized=(magnet_timer > 0),
    )
    for item in items:
      if item["type"] == "apple":
        draw_apple(item["x"], item["y"], RED)
      elif item["type"] == "gold_apple":
        draw_apple(item["x"], item["y"], GOLD)
      elif item["type"] == "gem":
        draw_gem(item["x"], item["y"])
      elif item["type"] == "green_apple":
        draw_apple(item["x"], item["y"], LIME_GREEN)
      elif item["type"] == "shield":
        draw_shield_item(item["x"], item["y"])
      elif item["type"] == "magnet":
        draw_magnet_item(item["x"], item["y"])
      elif item["type"] == "slow_mo":
        draw_clock_item(item["x"], item["y"])
      else:
        draw_bomb(item["x"], item["y"], tick_count)

    update_and_draw_effects()
    draw_ui_buttons()

    # شريط علوي منظم لمنع أي تداخل في النصوص
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (10, 10, WIDTH - 20, int(HEIGHT * 0.055)),
        border_radius=12,
    )

    score_surf = top_bar_font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surf, (20, int(HEIGHT * 0.016)))

    mode_name = (
        f"Lvl {selected_level}"
        if selected_level != "inf"
        else "Infinite"
    )
    if is_fever_mode:
      mode_name += " [FEVER]"
    if slow_mo_timer > 0:
      mode_name += " [SLOW]"
    if magnet_timer > 0:
      mode_name += " [MAG]"

    lvl_surf = top_bar_font.render(
        mode_name, True, GOLD if is_fever_mode else ORANGE
    )
    screen.blit(
        lvl_surf, (WIDTH // 2 - lvl_surf.get_width() // 2, int(HEIGHT * 0.016))
    )

    lives_text = f"Lives: {lives}"
    if has_shield:
      lives_text += " [🛡️]"
    lives_surf = top_bar_font.render(
        lives_text, True, SHIELD_BLUE if has_shield else RED
    )
    screen.blit(
        lives_surf, (WIDTH - lives_surf.get_width() - 20, int(HEIGHT * 0.016))
    )

  # --- شاشة الخسارة ---
  elif game_state == "LOSE":
    pygame.draw.rect(
        screen,
        GRASS_GREEN,
        (0, HEIGHT - int(HEIGHT * 0.1), WIDTH, int(HEIGHT * 0.1)),
    )
    draw_basket(basket_x, basket_y)
    draw_ui_buttons()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    update_and_draw_effects()

    lose_surf = over_font.render("GAME OVER", True, RED)
    screen.blit(
        lose_surf, lose_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90))
    )

    final_score_surf = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(
        final_score_surf,
        final_score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)),
    )

    current_hs = high_scores.get(selected_level, 0)
    hs_end_surf = font.render(f"Level Best: {current_hs}", True, GOLD)
    screen.blit(
        hs_end_surf,
        hs_end_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)),
    )

    restart_surf = btn_font.render("Tap anywhere to return to Menu", True, WHITE)
    screen.blit(
        restart_surf,
        restart_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)),
    )

  # --- إدارة الأحداث واللمس ---
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN:
      if game_state == "PLAY":
        if left_btn_rect.collidepoint(event.pos):
          basket_x -= basket_speed * 2
        if right_btn_rect.collidepoint(event.pos):
          basket_x += basket_speed * 2
        elif menu_btn_rect.collidepoint(event.pos):
          game_state = "MENU"

      elif game_state == "MENU":
        for btn in level_buttons:
          if btn["rect"].collidepoint(event.pos):
            selected_level = btn["key"]
            reset_game()
            game_state = "PLAY"
            break

        if reset_hs_btn_rect.collidepoint(event.pos):
          reset_all_data()

      elif game_state == "LOSE":
        reset_game()
        game_state = "MENU"

    if event.type == SPAWN_EVENT and game_state == "PLAY":
      if selected_level == "1":
        base_speed = int(HEIGHT * 0.008)
        bomb_prob = 0.18
      elif selected_level == "2":
        base_speed = int(HEIGHT * 0.010)
        bomb_prob = 0.25
      elif selected_level == "3":
        base_speed = int(HEIGHT * 0.012)
        bomb_prob = 0.32
      elif selected_level == "4":
        base_speed = int(HEIGHT * 0.014)
        bomb_prob = 0.38
      elif selected_level == "5":
        base_speed = int(HEIGHT * 0.016)
        bomb_prob = 0.45
      else:
        base_speed = int(HEIGHT * 0.018) + int(score * 0.0006)
        bomb_prob = 0.50

      r = random.random()
      if r < bomb_prob:
        item_type = "bomb"
      elif r < 0.68:
        item_type = "apple"
      elif r < 0.78:
        item_type = "gold_apple"
      elif r < 0.86:
        item_type = "gem"
      elif r < 0.91:
        item_type = "green_apple"
      elif r < 0.95:
        item_type = "shield"
      elif r < 0.98:
        item_type = "magnet"
      else:
        item_type = "slow_mo"

      item_x = random.randint(50, WIDTH - 50)
      items.append(
          {"type": item_type, "x": item_x, "y": -20, "speed": base_speed}
      )

  if basket_x < 0:
    basket_x = 0
  if basket_x > WIDTH - basket_width:
    basket_x = WIDTH - basket_width

  pygame.display.flip()
  clock.tick(30)
