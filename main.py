import pygame
import random
import sys
import array
import os
import math

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
pygame.display.set_caption("Apple Catcher Ultimate")

# تحميل اللوجو والخطوط مع حماية كاملة من الانهيار
LOGO_PATH = get_path("logo.png")
FONT_PATH = get_path("cursive.ttf")

logo_img = None
if os.path.exists(LOGO_PATH):
    try:
        raw_logo = pygame.image.load(LOGO_PATH)
        logo_w = int(WIDTH * 0.35)
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

font = get_game_font(int(WIDTH * 0.052))
btn_font = get_game_font(int(WIDTH * 0.042))
over_font = get_game_font(int(WIDTH * 0.085))

# --- تحديد المجلد الآمن لحفظ الـ High Score للأبد في الـ APK ---
if 'ANDROID_PRIVATE_DATA' in os.environ:
    SAVE_DIR = os.environ['ANDROID_PRIVATE_DATA']
else:
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

HIGH_SCORE_FILE = os.path.join(SAVE_DIR, "highscore_new.txt")

# الألوان الفاخرة للعبة
SKY_BLUE = (135, 206, 235)       
GRASS_GREEN = (46, 139, 87)      
BROWN = (139, 69, 19)            
RED = (231, 76, 60)              
GOLD = (241, 196, 15)             
LIME_GREEN = (46, 204, 113)       
BLACK = (44, 62, 80)             
YELLOW = (241, 196, 15)           
ORANGE = (230, 126, 34)           
WHITE = (255, 255, 255)          
BTN_COLOR = (52, 73, 94)         
EASY_COLOR = (39, 174, 96)      
HARD_COLOR = (192, 57, 43)       
RESET_COLOR = (127, 140, 141)    

particles = []
floating_texts = []

# دالة توليد المؤثرات الصوتية برمجياً
def generate_sound(freq_start, freq_end, duration_ms, wave_type="sine"):
    sample_rate = 22050
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / float(sample_rate)
        current_freq = freq_start + (freq_end - freq_start) * (i / float(num_samples))
        if wave_type == "sine":
            value = int(16383 * math.sin(2 * math.pi * current_freq * t))
        elif wave_type == "square":
            value = 16383 if math.sin(2 * math.pi * current_freq * t) > 0 else -16383
            if t > (duration_ms / 2000.0):
                value = int(value * (1.0 - t / (duration_ms / 1000.0)))
        buf[i] = value
    return pygame.mixer.Sound(buffer=buf)

# توليد أصوات اللعبة فورياً
apple_sound = generate_sound(500, 1000, 100, "sine")       
gold_sound = generate_sound(800, 1800, 150, "sine")        
green_sound = generate_sound(400, 900, 200, "sine")         
bomb_sound = generate_sound(250, 50, 250, "square")        
lose_sound = generate_sound(300, 60, 800, "square")        

# دالة صنع انفجارات وجزيئات بصرية مذهلة
def create_particles(x, y, color_palette, num=20, speed_min=4, speed_max=12, life_max=40):
    for _ in range(num):
        angle = random.uniform(0, 6.28)  
        speed = random.uniform(speed_min, speed_max)
        color = random.choice(color_palette) if isinstance(color_palette, list) else color_palette
        particles.append({
            "x": x, "y": y,
            "vx": speed * math.cos(angle),
            "vy": speed * math.sin(angle),
            "color": color,
            "radius": random.randint(4, 10),
            "life": random.randint(20, life_max)
        })

# إضافة نصوص تفاعلية متطايرة (بدون رموز تعبيرية)
def add_floating_text(text, x, y, color=GOLD):
    floating_texts.append({
        "text": text,
        "x": x,
        "y": y,
        "color": color,
        "life": 30
    })

# تحديث ورسم الجزيئات والنصوص المتحركة
def update_and_draw_effects():
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.2  
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["radius"])
            
    for ft in floating_texts[:]:
        ft["y"] -= 2
        ft["life"] -= 1
        if ft["life"] <= 0:
            floating_texts.remove(ft)
        else:
            txt_surf = btn_font.render(ft["text"], True, ft["color"])
            screen.blit(txt_surf, (ft["x"] - txt_surf.get_width()//2, ft["y"]))

# نظام حفظ وقراءة وتصفير الـ High Score
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(new_high):
    try:
        os.makedirs(os.path.dirname(HIGH_SCORE_FILE), exist_ok=True)
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(new_high))
    except Exception as e:
        print("فشل الحفظ في الخزنة الآمنة:", e)

def reset_high_score():
    global high_score
    high_score = 0
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            os.remove(HIGH_SCORE_FILE)
        except:
            pass
    save_high_score(0)

high_score = load_high_score()

# إعداد السلة ومقاساتها
basket_width, basket_height = int(WIDTH * 0.24), int(HEIGHT * 0.055)
basket_x = WIDTH // 2 - basket_width // 2
basket_y = HEIGHT - int(HEIGHT * 0.18)          
basket_speed = int(WIDTH * 0.018) 

# إعداد أزرار التحكم باللمس (استخدام رموز عادية بدلاً من الأسهم المعقدة)
side_btn_size = int(WIDTH * 0.18) 
btn_display_y = HEIGHT - int(HEIGHT * 0.32) 
left_btn_rect = pygame.Rect(15, btn_display_y, side_btn_size, side_btn_size)
right_btn_rect = pygame.Rect(WIDTH - 15 - side_btn_size, btn_display_y, side_btn_size, side_btn_size)

# أزرار شاشة البداية
menu_btn_w, menu_btn_h = int(WIDTH * 0.65), int(HEIGHT * 0.075)
easy_btn_rect = pygame.Rect(WIDTH//2 - menu_btn_w//2, HEIGHT//2 - int(menu_btn_h * 1.5), menu_btn_w, menu_btn_h)
hard_btn_rect = pygame.Rect(WIDTH//2 - menu_btn_w//2, HEIGHT//2 - int(menu_btn_h * 0.4), menu_btn_w, menu_btn_h)
reset_hs_btn_rect = pygame.Rect(WIDTH//2 - menu_btn_w//2, HEIGHT//2 + int(menu_btn_h * 0.7), menu_btn_w, menu_btn_h)

items = []
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 650)  

score = 0
lives = 3
game_state = "MENU"  
selected_level = "EASY" 

def reset_game():
    global score, lives, items, game_state, particles, floating_texts
    score = 0
    lives = 3
    items = []
    particles = []
    floating_texts = []

def draw_basket(x, y):
    pygame.draw.rect(screen, (100, 50, 20), (x - 2, y + basket_height, basket_width + 4, 6), border_radius=3)
    pygame.draw.polygon(screen, BROWN, [(x, y), (x + basket_width, y), (x + basket_width - 18, y + basket_height), (x + 18, y + basket_height)])
    for i in range(25, basket_width - 25, 25):
        pygame.draw.line(screen, (90, 40, 10), (x + i, y), (x + i - 5, y + basket_height), 3)

def draw_apple(x, y, color=RED):
    radius = int(WIDTH * 0.045)
    pygame.draw.circle(screen, color, (x, y), radius)
    pygame.draw.circle(screen, (255, 255, 255), (x - 5, y - 5), int(radius * 0.3))
    pygame.draw.rect(screen, (90, 60, 30), (x - 2, y - int(radius * 1.3), 4, 10))
    pygame.draw.ellipse(screen, (46, 139, 87), (x + 2, y - int(radius * 1.3), 12, 6))

def draw_bomb(x, y, tick):
    radius = int(WIDTH * 0.045)
    pygame.draw.circle(screen, BLACK, (x, y), radius)
    pygame.draw.circle(screen, (80, 80, 80), (x - 6, y - 6), 6)
    pygame.draw.line(screen, (180, 100, 0), (x, y - radius), (x + 12, y - radius - 12), 3)
    fire_color = YELLOW if (tick // 3) % 2 == 0 else ORANGE
    pygame.draw.circle(screen, fire_color, (x + 12, y - radius - 12), 7)

def draw_ui_buttons():
    pygame.draw.rect(screen, BTN_COLOR, left_btn_rect, border_radius=16)
    pygame.draw.rect(screen, WHITE, left_btn_rect, width=2, border_radius=16)
    left_surf = btn_font.render("<", True, WHITE)
    screen.blit(left_surf, left_surf.get_rect(center=left_btn_rect.center))
    
    pygame.draw.rect(screen, BTN_COLOR, right_btn_rect, border_radius=16)
    pygame.draw.rect(screen, WHITE, right_btn_rect, width=2, border_radius=16)
    right_surf = btn_font.render(">", True, WHITE)
    screen.blit(right_surf, right_surf.get_rect(center=right_btn_rect.center))

# حلقة اللعبة الأساسية
clock = pygame.time.Clock()
tick_count = 0

while True:
    tick_count += 1
    screen.fill(SKY_BLUE)
    
    sun_x, sun_y = WIDTH - int(WIDTH * 0.15), int(HEIGHT * 0.12)
    pygame.draw.circle(screen, (255, 243, 205), (sun_x, sun_y), int(WIDTH * 0.08))
    
    # --- شاشة القائمة الرئيسية ---
    if game_state == "MENU":
        if logo_img:
            logo_rect = logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 5))
            screen.blit(logo_img, logo_rect)
            menu_title = over_font.render("Apple Catcher Ultimate", True, BLACK)
            screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, HEIGHT // 2.8)))
        else:
            menu_title = over_font.render("Apple Catcher Ultimate", True, BLACK)
            screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))
        
        pygame.draw.rect(screen, EASY_COLOR, easy_btn_rect, border_radius=18)
        pygame.draw.rect(screen, WHITE, easy_btn_rect, width=2, border_radius=18)
        easy_surf = btn_font.render("Easy Level", True, WHITE)
        screen.blit(easy_surf, easy_surf.get_rect(center=easy_btn_rect.center))
        
        pygame.draw.rect(screen, HARD_COLOR, hard_btn_rect, border_radius=18)
        pygame.draw.rect(screen, WHITE, hard_btn_rect, width=2, border_radius=18)
        hard_surf = btn_font.render("Hard Level", True, WHITE)
        screen.blit(hard_surf, hard_surf.get_rect(center=hard_btn_rect.center))
        
        pygame.draw.rect(screen, RESET_COLOR, reset_hs_btn_rect, border_radius=18)
        pygame.draw.rect(screen, WHITE, reset_hs_btn_rect, width=2, border_radius=18)
        reset_surf = btn_font.render("Reset High Score", True, WHITE)
        screen.blit(reset_surf, reset_surf.get_rect(center=reset_hs_btn_rect.center))
        
        hs_surf = font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(hs_surf, hs_surf.get_rect(center=(WIDTH // 2, HEIGHT - int(HEIGHT * 0.12))))
        
    # --- شاشة اللعب الفعلي ---
    elif game_state == "PLAY":
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - int(HEIGHT * 0.1), WIDTH, int(HEIGHT * 0.1)))
        
        for gx in range(0, WIDTH, 30):
            pygame.draw.line(screen, (34, 115, 70), (gx, HEIGHT - int(HEIGHT * 0.1)), (gx + 5, HEIGHT - int(HEIGHT * 0.12)), 3)

        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            mouse_pos = pygame.mouse.get_pos()
            if left_btn_rect.collidepoint(mouse_pos):
                basket_x -= basket_speed
            if right_btn_rect.collidepoint(mouse_pos):
                basket_x += basket_speed

        basket_rect = pygame.Rect(basket_x, basket_y, basket_width, basket_height)
        for item in items[:]:
            item["y"] += item["speed"]
            item_rect = pygame.Rect(item["x"] - 20, item["y"] - 20, 40, 40)
            
            if basket_rect.colliderect(item_rect):
                if item["type"] == "apple":
                    score += 1
                    apple_sound.play()
                    add_floating_text("+1", item["x"], item["y"], RED)
                elif item["type"] == "gold_apple":
                    score += 3  
                    gold_sound.play()
                    create_particles(item["x"], item["y"], [GOLD, WHITE, YELLOW], num=30, speed_min=6, speed_max=14, life_max=30)
                    add_floating_text("+3 Star", item["x"], item["y"], GOLD)
                elif item["type"] == "green_apple":
                    if lives < 5:  
                        lives += 1
                    green_sound.play()
                    create_particles(item["x"], item["y"], [LIME_GREEN, WHITE], num=20, speed_min=4, speed_max=10, life_max=25)
                    add_floating_text("+1 HP", item["x"], item["y"], LIME_GREEN)
                elif item["type"] == "bomb":
                    lives -= 1
                    bomb_sound.play()
                    create_particles(item["x"], item["y"], [BLACK, RED, ORANGE], num=40, speed_min=6, speed_max=16, life_max=35)
                    add_floating_text("-1 Bomb", item["x"], item["y"], BLACK)
                    
                    if lives <= 0:
                        game_state = "LOSE"
                        lose_sound.play()
                        create_particles(basket_x + basket_width // 2, basket_y, [RED, BLACK, ORANGE, YELLOW, BROWN], num=150, speed_min=8, speed_max=24, life_max=90)
                
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                    
                items.remove(item)
                continue
                
            if item["y"] > HEIGHT - int(HEIGHT * 0.11):
                items.remove(item)

        draw_basket(basket_x, basket_y)
        for item in items:
            if item["type"] == "apple":
                draw_apple(item["x"], item["y"], RED)
            elif item["type"] == "gold_apple":
                draw_apple(item["x"], item["y"], GOLD)
            elif item["type"] == "green_apple":
                draw_apple(item["x"], item["y"], LIME_GREEN)
            else:
                draw_bomb(item["x"], item["y"], tick_count)
                
        update_and_draw_effects()
        draw_ui_buttons()

        pygame.draw.rect(screen, (255, 255, 255), (10, 10, WIDTH - 20, int(HEIGHT * 0.07)), border_radius=12)
        
        score_surf = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surf, (30, int(HEIGHT * 0.02)))
        
        lives_surf = font.render(f"Lives: {lives}", True, RED)
        screen.blit(lives_surf, (WIDTH - int(WIDTH * 0.28), int(HEIGHT * 0.02)))

    # --- شاشة الخسارة ---
    elif game_state == "LOSE":
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - int(HEIGHT * 0.1), WIDTH, int(HEIGHT * 0.1)))
        draw_basket(basket_x, basket_y)
        draw_ui_buttons()
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        
        update_and_draw_effects()
        
        lose_surf = over_font.render("GAME OVER", True, RED)
        screen.blit(lose_surf, lose_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        
        final_score_surf = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(final_score_surf, final_score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        
        hs_end_surf = font.render(f"High Score: {high_score}", True, GOLD)
        screen.blit(hs_end_surf, hs_end_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))
        
        restart_surf = btn_font.render("Tap anywhere to return to Menu", True, WHITE)
        screen.blit(restart_surf, restart_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130)))

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

            elif game_state == "MENU":
                if easy_btn_rect.collidepoint(event.pos):
                    reset_game()
                    game_state = "PLAY"
                    selected_level = "EASY"
                elif hard_btn_rect.collidepoint(event.pos):
                    reset_game()
                    game_state = "PLAY"
                    selected_level = "HARD"
                elif reset_hs_btn_rect.collidepoint(event.pos):
                    reset_high_score()
                    
            elif game_state == "LOSE":
                reset_game()
                game_state = "MENU"
            
        if event.type == SPAWN_EVENT and game_state == "PLAY":
            difficulty_multiplier = min(2.2, 1.0 + (score // 8) * 0.1)
            
            if selected_level == "EASY":
                base_speed = int(HEIGHT * 0.009)
                r = random.random()
                if r < 0.22: item_type = "bomb"
                elif r < 0.80: item_type = "apple"
                elif r < 0.93: item_type = "gold_apple"  
                else: item_type = "green_apple" 
            else:
                base_speed = int(HEIGHT * 0.013)
                r = random.random()
                if r < 0.42: item_type = "bomb"
                elif r < 0.78: item_type = "apple"
                elif r < 0.92: item_type = "gold_apple"  
                else: item_type = "green_apple" 
            
            item_speed = int(base_speed * difficulty_multiplier)
            item_x = random.randint(50, WIDTH - 50)
            items.append({"type": item_type, "x": item_x, "y": -20, "speed": item_speed})

    if basket_x < 0: basket_x = 0
    if basket_x > WIDTH - basket_width: basket_x = WIDTH - basket_width

    pygame.display.flip()
    clock.tick(30)