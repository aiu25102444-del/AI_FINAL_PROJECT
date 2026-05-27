
import pygame
import sys
import random
import math

# ==========================================
# 🎓 CCC1243 GROUP PROJECT: ADAPTIVE AI VOCABULARY GAME
# Target: Ages 4-6 | Framework: Pygame
# ==========================================

pygame.init()

# 📐 CONSTANTS
WIDTH, HEIGHT = 900, 600
FPS = 60
QUESTIONS_PER_ROUND = 15

# 🎨 KID-FRIENDLY COLOR PALETTE (Bright but soft for eyes)
BG_COLOR = (238, 248, 255)
CARD_BG = (255, 255, 255)
PRIMARY_BLUE = (59, 130, 246)
SUCCESS_GREEN = (34, 197, 94)
ENCOURAGE_YELLOW = (250, 204, 21)
TEXT_DARK = (31, 41, 55)
TEXT_SUB = (107, 114, 128)

# 📚 VOCABULARY DATABASE (Tiered for Adaptive Difficulty)
VOCAB_TIERS = {
    0: {"name": "Easy", "words": [
        {"target": "Cat", "emoji": "🐱", "distractors": ["Dog", "Sun", "Ball"]},
        {"target": "Sun", "emoji": "☀️", "distractors": ["Moon", "Cloud", "Hat"]},
        {"target": "Tree", "emoji": "🌳", "distractors": ["Flower", "Rock", "Bird"]},
        {"target": "Fish", "emoji": "🐟", "distractors": ["Frog", "Duck", "Bug"]}
    ]},
    1: {"name": "Medium", "words": [
        {"target": "Apple", "emoji": "🍎", "distractors": ["Grape", "Lemon", "Melon"]},
        {"target": "Train", "emoji": "🚂", "distractors": ["Plane", "Truck", "Boat"]},
        {"target": "Rain", "emoji": "🌧️", "distractors": ["Snow", "Wind", "Fog"]},
        {"target": "Star", "emoji": "⭐", "distractors": ["Moon", "Planet", "Sky"]}
    ]},
    2: {"name": "Hard", "words": [
        {"target": "Elephant", "emoji": "🐘", "distractors": ["Giraffe", "Monkey", "Zebra"]},
        {"target": "Rainbow", "emoji": "🌈", "distractors": ["Cloud", "Sunshine", "Storm"]},
        {"target": "Dinosaur", "emoji": "🦖", "distractors": ["Dragon", "Lizard", "Snake"]},
        {"target": "Castle", "emoji": "🏰", "distractors": ["Tower", "Bridge", "Palace"]}
    ]}
}

# 🔤 FONTS
FONT_TITLE = pygame.font.SysFont("comicsansms", 44, bold=True)
FONT_PROMPT = pygame.font.SysFont("comicsansms", 32, bold=True)
FONT_BUTTON = pygame.font.SysFont("comicsansms", 26, bold=True)
FONT_MSG = pygame.font.SysFont("comicsansms", 22)

# 🎮 GAME STATES
STATE_MENU = 0
STATE_PLAYING = 1
STATE_FEEDBACK = 2
STATE_ROUND_END = 3

# ==========================================
# 🤖 ADAPTIVE AI ENGINE (Tracks performance & adjusts difficulty)
# ==========================================
class AdaptiveEngine:
    def __init__(self):
        self.difficulty = 0  # 0=Easy, 1=Medium, 2=Hard
        self.streak = 0
        self.correct_count = 0
        self.questions_asked = 0
        self.hint_active = False

    def get_next_question(self):
        # 🧠 Adaptive Logic: Level up after 3 consecutive correct answers
        if self.streak >= 3 and self.difficulty < 2:
            self.difficulty += 1
            self.streak = 0  # Reset streak after difficulty jump
            
        pool = VOCAB_TIERS[self.difficulty]["words"]
        q = random.choice(pool).copy()
        
        # Shuffle options so correct answer isn't always in the same spot
        options = q["distractors"] + [q["target"]]
        random.shuffle(options)
        return q, options

    def process_answer(self, is_correct):
        self.questions_asked += 1
        if is_correct:
            self.streak += 1
            self.correct_count += 1
            return "celebrate"
        else:
            self.streak = 0
            self.hint_active = True
            return "hint"

    def get_encouragement(self):
        if self.correct_count == 0: return "🌟 Let's learn together!"
        if self.correct_count < 5: return "👏 Good start!"
        if self.correct_count < 10: return "🚀 You're doing great!"
        return "🏆 Amazing job!"

# ==========================================
# 🎨 UI COMPONENTS
# ==========================================
class ProgressBar:
    def __init__(self, x, y, w, h, total):
        self.rect = pygame.Rect(x, y, w, h)
        self.total = total
        self.current = 0
        self.color = PRIMARY_BLUE

    def update(self, correct=True):
        if self.current < self.total:
            self.current += 1

    def draw(self, screen):
        # Background
        pygame.draw.rect(screen, (226, 232, 240), self.rect, border_radius=15)
        # Fill
        fill_w = (self.current / self.total) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
        pygame.draw.rect(screen, self.color, fill_rect, border_radius=15)
        # Progress text
        txt = FONT_MSG.render(f"{self.current}/{self.total}", True, TEXT_SUB)
        screen.blit(txt, (self.rect.x + self.rect.w//2 - txt.get_width()//2, 
                          self.rect.y + self.rect.h//2 - txt.get_height()//2))

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.life = 60
        self.color = random.choice([SUCCESS_GREEN, ENCOURAGE_YELLOW, PRIMARY_BLUE, (244, 114, 182)])
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravity
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            alpha = min(255, self.life * 4)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# ==========================================
# 🕹️ MAIN GAME CLASS
# ==========================================
class KidsVocabGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🌟 Kids Word Explorer")
        self.clock = pygame.time.Clock()
        
        self.ai = AdaptiveEngine()
        self.progress = ProgressBar(50, 40, WIDTH - 100, 35, QUESTIONS_PER_ROUND)
        self.particles = []
        
        self.state = STATE_MENU
        self.buttons = []
        self.target_q = None
        self.options = []
        self.feedback_msg = ""
        self.feedback_timer = 0
        self.hovered_btn = -1

    def create_buttons(self, options):
        self.buttons = []
        btn_w, btn_h = 140, 90
        start_x = (WIDTH - (btn_w * 4 + 30)) // 2
        y = HEIGHT - 200
        for i, opt in enumerate(options):
            rect = pygame.Rect(start_x + i * (btn_w + 10), y, btn_w, btn_h)
            self.buttons.append({"rect": rect, "text": opt})

    def get_button_rects(self):
        return [b["rect"] for b in self.buttons]

    def handle_click(self, pos):
        if self.state == STATE_MENU:
            self.start_round()
            return

        if self.state == STATE_ROUND_END:
            self.ai = AdaptiveEngine()
            self.progress = ProgressBar(50, 40, WIDTH - 100, 35, QUESTIONS_PER_ROUND)
            self.start_round()
            return

        if self.state == STATE_PLAYING:
            for i, btn in enumerate(self.buttons):
                if btn["rect"].collidepoint(pos):
                    is_correct = (btn["text"] == self.target_q["target"])
                    result = self.ai.process_answer(is_correct)
                    
                    if result == "celebrate":
                        self.feedback_msg = f"🎉 Correct! It's {self.target_q['emoji']} {self.target_q['target']}!"
                        self.spawn_particles(WIDTH//2, HEIGHT//3)
                    else:
                        self.feedback_msg = f"😊 Try again! Hint: It starts with '{self.target_q['target'][0]}'"
                        self.feedback_msg += f"\n{self.ai.get_encouragement()}"
                        
                    self.progress.update()
                    self.state = STATE_FEEDBACK
                    self.feedback_timer = 120
                    break

        elif self.state == STATE_FEEDBACK:
            # Allow skipping feedback early
            self.state = STATE_PLAYING if self.ai.questions_asked < QUESTIONS_PER_ROUND else STATE_ROUND_END
            if self.state == STATE_PLAYING:
                self.next_question()

    def next_question(self):
        self.target_q, self.options = self.ai.get_next_question()
        self.create_buttons(self.options)
        self.state = STATE_PLAYING

    def start_round(self):
        self.next_question()

    def spawn_particles(self, x, y):
        for _ in range(40):
            self.particles.append(Particle(x, y))

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING or self.state == STATE_FEEDBACK:
            self.draw_game()
        elif self.state == STATE_ROUND_END:
            self.draw_round_end()

        # Draw particles on top
        for p in self.particles:
            p.update()
            p.draw(self.screen)
        self.particles = [p for p in self.particles if p.life > 0]

        pygame.display.flip()

    def draw_menu(self):
        title = FONT_TITLE.render("🌈 Word Explorer", True, TEXT_DARK)
        sub = FONT_MSG.render("Tap anywhere to start!", True, TEXT_SUB)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 260))

    def draw_game(self):
        # Progress Bar
        self.progress.draw(self.screen)

        # Prompt
        prompt = FONT_PROMPT.render(f"Find: {self.target_q['emoji']} {self.target_q['target']}", True, TEXT_DARK)
        self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 100))

        # Difficulty Indicator (Shows AI Adaptation)
        diff_txt = FONT_MSG.render(f"Level: {VOCAB_TIERS[self.ai.difficulty]['name']}", True, TEXT_SUB)
        self.screen.blit(diff_txt, (WIDTH//2 - diff_txt.get_width()//2, 150))

        # Feedback Overlay
        if self.state == STATE_FEEDBACK:
            self.draw_feedback_overlay()
            self.feedback_timer -= 1
            if self.feedback_timer <= 0 and self.ai.questions_asked < QUESTIONS_PER_ROUND:
                self.state = STATE_PLAYING
                self.next_question()
            elif self.feedback_timer <= 0:
                self.state = STATE_ROUND_END
            return

        # Buttons
        self.hovered_btn = -1
        for i, btn in enumerate(self.buttons):
            color = PRIMARY_BLUE if i == self.hovered_btn else (226, 232, 240)
            pygame.draw.rect(self.screen, CARD_BG, btn["rect"], border_radius=20)
            pygame.draw.rect(self.screen, color, btn["rect"], 4, border_radius=20)
            
            txt = FONT_BUTTON.render(btn["text"], True, TEXT_DARK)
            self.screen.blit(txt, (btn["rect"].x + (btn["rect"].w - txt.get_width())//2,
                                   btn["rect"].y + (btn["rect"].h - txt.get_height())//2))

    def draw_feedback_overlay(self):
        # Dim background
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 80))
        self.screen.blit(s, (0, 0))
        
        # Message box
        box_w, box_h = 500, 120
        box_x, box_y = (WIDTH - box_w)//2, (HEIGHT - box_h)//2 - 40
        pygame.draw.rect(self.screen, CARD_BG, (box_x, box_y, box_w, box_h), border_radius=25)
        
        # Multi-line text
        lines = self.feedback_msg.split('\n')
        for i, line in enumerate(lines):
            txt = FONT_MSG.render(line, True, TEXT_DARK if i == 0 else TEXT_SUB)
            self.screen.blit(txt, (box_x + 30, box_y + 20 + i*30))

    def draw_round_end(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        self.screen.blit(s, (0, 0))
        
        box_w, box_h = 500, 250
        box_x, box_y = (WIDTH - box_w)//2, (HEIGHT - box_h)//2
        pygame.draw.rect(self.screen, CARD_BG, (box_x, box_y, box_w, box_h), border_radius=30)
        
        title = FONT_TITLE.render("🎊 Round Complete!", True, SUCCESS_GREEN)
        score = FONT_PROMPT.render(f"Stars Earned: {self.ai.correct_count} ⭐", True, TEXT_DARK)
        retry = FONT_MSG.render("Tap to play again!", True, TEXT_SUB)
        
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, box_y + 30))
        self.screen.blit(score, (WIDTH//2 - score.get_width()//2, box_y + 90))
        self.screen.blit(retry, (WIDTH//2 - retry.get_width()//2, box_y + 160))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos) 
                elif event.type == pygame.MOUSEMOTION:
                    if self.state == STATE_PLAYING:
                        pos = event.pos
                        self.hovered_btn = -1
                        for i, btn in enumerate(self.buttons):
                            if btn["rect"].collidepoint(pos):
                                self.hovered_btn = i
                                break

            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = KidsVocabGame()
    game.run()
    # 

    # 1. Load sounds at the top (after pygame.init())
pygame.mixer.init()
clap_sound = pygame.mixer.Sound("clap.mp3")  # Download free .mp3
hint_sound = pygame.mixer.Sound("ding.mp3")

# 2. Play in handle_click()
if result == "celebrate":
    clap_sound.play()
else:
    hint_sound.play()
    #  github
