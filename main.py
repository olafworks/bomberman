import pygame
import sys
import random
import math

# 初期化
pygame.init()
pygame.mixer.init()  # 音声機能の初期化

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# 音声ファイルの読み込み
try:
    # 効果音
    bomb_place_sound = pygame.mixer.Sound("sounds/bomb_place.mp3")
    bomb_explosion_sound = pygame.mixer.Sound("sounds/explosion.mp3")
    item_pickup_sound = pygame.mixer.Sound("sounds/item_pickup.mp3")  # アイテム取得音を追加
    game_over_sound = pygame.mixer.Sound("sounds/game_over.mp3")  # ゲームオーバー音を追加
    stage_clear_sound = pygame.mixer.Sound("sounds/stage_clear.mp3")  # ステージクリア音を追加
    # 音量調整
    bomb_place_sound.set_volume(0.5)
    bomb_explosion_sound.set_volume(0.7)
    item_pickup_sound.set_volume(0.6)  # アイテム取得音の音量設定
    game_over_sound.set_volume(0.7)  # ゲームオーバー音の音量設定
    stage_clear_sound.set_volume(0.7)  # ステージクリア音の音量設定
    sound_enabled = True
except:
    print("音声ファイルの読み込みに失敗しました。ゲームは音なしで続行します。")
    sound_enabled = False

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
# マインクラフトスタイルの色を追加
DARK_GRAY = (64, 64, 64)
STONE_COLOR = (120, 120, 120)
BRICK_COLOR = (139, 69, 19)
BRICK_LINES = (101, 51, 14)
# 肌色を追加
SKIN_COLOR = (255, 220, 177)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
# 爆弾と爆発の色を追加
BOMB_COLOR = (30, 30, 30)
BOMB_HIGHLIGHT = (60, 60, 60)
EXPLOSION_COLORS = [(255, 200, 0), (255, 150, 0), (255, 100, 0)]
EXPLOSION_RED = (255, 0, 0)  # 爆発範囲の赤色
# アイテムの色を追加
POWER_UP_COLOR = (255, 50, 50)
POWER_UP_GLOW = (255, 100, 100)
SPEED_UP_COLOR = (255, 215, 0)
SPEED_UP_GLOW = (255, 235, 100)
BOMB_UP_COLOR = (148, 0, 211)
BOMB_UP_GLOW = (186, 85, 211)

# ゲーム画面の作成
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ボンバーマン")

# フォントの初期化
font = pygame.font.Font(None, 36)

# ゲームオブジェクトの種類
EMPTY = 0
WALL = 1
BLOCK = 2
BOMB = 3
POWER_UP = 4
SPEED_UP = 5
BOMB_UP = 6

# 敵の種類を定義
ENEMY_SLIME = 0
ENEMY_CHASER = 1
ENEMY_SMART = 2

# ゲームの状態
MENU = 0
GAME = 1
GAME_OVER = 2
STAGE_CLEAR = 3  # ステージクリア状態を追加

class Bomb:
    def __init__(self, x, y, explosion_range=2):
        self.x = x
        self.y = y
        self.timer = 180  # 3秒 (60FPS × 3)
        self.explosion_range = explosion_range
        self.exploded = False
        self.explosions = []
        self.explosion_frames = 0  # 爆発アニメーション用
        self.explosion_duration = 60  # 爆発エフェクトの持続時間（フレーム数）
        self.explosion_alpha = 180  # 爆発の透明度（最大値）

    def update(self):
        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0:
                self.exploded = True
                return True
        else:
            # 爆発後のアニメーション更新
            self.explosion_frames += 1
        return False

    def draw(self):
        if not self.exploded:
            # 爆弾の本体
            center_x = self.x * TILE_SIZE + TILE_SIZE // 2
            center_y = self.y * TILE_SIZE + TILE_SIZE // 2
            radius = TILE_SIZE // 3
            
            # 爆弾の本体（黒い円）
            pygame.draw.circle(screen, BOMB_COLOR, (center_x, center_y), radius)
            
            # 導火線
            fuse_start = (center_x, center_y - radius)
            fuse_end = (center_x + radius//2, center_y - radius * 1.5)
            pygame.draw.line(screen, BOMB_COLOR, fuse_start, fuse_end, 3)
            
            # ハイライト（光の反射）
            highlight_pos = (center_x - radius//3, center_y - radius//3)
            pygame.draw.circle(screen, BOMB_HIGHLIGHT, highlight_pos, radius//4)
            
            # タイマーに応じて点滅効果
            if self.timer < 60 and self.timer % 10 < 5:  # 最後の1秒で点滅
                pygame.draw.circle(screen, RED, (center_x, center_y), radius, 2)
        
        # 爆発の描画（爆発後かつエフェクト表示期間内の場合のみ）
        elif self.exploded and self.explosion_frames < self.explosion_duration:
            # 爆発範囲の半透明エフェクト用のサーフェス
            # 透明度を計算（徐々にフェードアウト）
            current_alpha = int(self.explosion_alpha * (1 - self.explosion_frames / self.explosion_duration))
            explosion_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # 爆発範囲の各マスを描画
            for ex, ey in self.explosions:
                # 爆発範囲を赤色の半透明で表示
                rect = pygame.Rect(ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                explosion_color = (EXPLOSION_RED[0], EXPLOSION_RED[1], EXPLOSION_RED[2], current_alpha)
                pygame.draw.rect(explosion_surface, explosion_color, rect)
                
                # 爆発範囲の境界線
                border_color = (EXPLOSION_RED[0], EXPLOSION_RED[1], EXPLOSION_RED[2], min(255, current_alpha + 50))
                pygame.draw.rect(explosion_surface, border_color, rect, 2)
                
                # 爆発エフェクトは爆発開始直後のみ表示（最初の15フレーム）
                if self.explosion_frames < 15:
                    # 爆発の中心
                    center_x = ex * TILE_SIZE + TILE_SIZE // 2
                    center_y = ey * TILE_SIZE + TILE_SIZE // 2
                    
                    # 複数の円を重ねて爆発エフェクトを作成
                    for i, color in enumerate(EXPLOSION_COLORS):
                        size = TILE_SIZE - (i * 8)
                        offset = random.randint(-2, 2)  # ランダムなずれを加える
                        pos = (center_x + offset, center_y + offset)
                        pygame.draw.circle(screen, color, pos, size // 2)
                    
                    # 十字の光線エフェクト
                    for color in EXPLOSION_COLORS:
                        for angle in [0, 90, 180, 270]:
                            start_pos = (center_x, center_y)
                            end_x = center_x + math.cos(math.radians(angle)) * TILE_SIZE//2
                            end_y = center_y + math.sin(math.radians(angle)) * TILE_SIZE//2
                            pygame.draw.line(screen, color, start_pos, (end_x, end_y), 2)
            
            # 半透明の爆発範囲を画面に描画
            screen.blit(explosion_surface, (0, 0))

class Enemy:
    def __init__(self, x, y, enemy_type=ENEMY_SLIME):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.size = TILE_SIZE
        self.move_cooldown = 0
        self.enemy_type = enemy_type
        
        # 敵の種類に応じたパラメータ設定
        if enemy_type == ENEMY_SLIME:
            self.color = (0, 100, 255)  # 青色のスライム
            self.move_delay = 60  # ゆっくり移動（40から60に変更）
        elif enemy_type == ENEMY_CHASER:
            self.color = (220, 50, 50)  # 赤色の追跡者
            self.move_delay = 45  # 中程度の速さ（25から45に変更）
        elif enemy_type == ENEMY_SMART:
            self.color = (50, 180, 50)  # 緑色の賢い敵
            self.move_delay = 35  # やや速い（20から35に変更）
        
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.bounce_offset = 0
        self.bounce_speed = 0.01
        self.eye_size = TILE_SIZE // 6

    def draw(self):
        if self.enemy_type == ENEMY_SLIME:
            self.draw_slime()
        elif self.enemy_type == ENEMY_CHASER:
            self.draw_chaser()
        elif self.enemy_type == ENEMY_SMART:
            self.draw_smart()

    def draw_slime(self):
        # 跳ねるアニメーション
        self.bounce_offset = math.sin(pygame.time.get_ticks() * self.bounce_speed) * 5
        
        # スライムの体（円）
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2 + self.bounce_offset
        radius = TILE_SIZE // 2 - 2
        
        # スライムの体を描画
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
        
        # スライムの目（白い部分）
        eye_offset_x = 3
        eye_offset_y = -2 + self.bounce_offset // 2
        pygame.draw.circle(screen, WHITE, 
                         (center_x - eye_offset_x, center_y + eye_offset_y), 
                         self.eye_size)
        pygame.draw.circle(screen, WHITE, 
                         (center_x + eye_offset_x, center_y + eye_offset_y), 
                         self.eye_size)
        
        # 瞳（黒い部分）
        pupil_size = self.eye_size // 2
        pygame.draw.circle(screen, BLACK, 
                         (center_x - eye_offset_x, center_y + eye_offset_y), 
                         pupil_size)
        pygame.draw.circle(screen, BLACK, 
                         (center_x + eye_offset_x, center_y + eye_offset_y), 
                         pupil_size)
        
        # スライムの口
        mouth_y = center_y + self.eye_size + 2
        pygame.draw.arc(screen, (0, 50, 200), 
                      [center_x - self.eye_size, mouth_y, 
                       self.eye_size * 2, self.eye_size], 
                      0, math.pi, 2)

    def draw_chaser(self):
        # 追跡者の体（四角形）
        rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, self.color, rect)
        
        # 目（怒った表情）
        eye_size = self.eye_size
        eye_y = self.y + TILE_SIZE // 3
        left_eye_x = self.x + TILE_SIZE // 3 - 2
        right_eye_x = self.x + 2 * TILE_SIZE // 3 + 2
        
        # 白目
        pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_size)
        pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_size)
        
        # 黒目（プレイヤーを見る方向に少しずらす）
        pupil_offset = 2
        pygame.draw.circle(screen, BLACK, (left_eye_x + pupil_offset, eye_y), eye_size // 2)
        pygame.draw.circle(screen, BLACK, (right_eye_x + pupil_offset, eye_y), eye_size // 2)
        
        # 口（怒った表情）
        mouth_y = self.y + 2 * TILE_SIZE // 3
        pygame.draw.line(screen, BLACK, 
                       (self.x + TILE_SIZE // 3, mouth_y), 
                       (self.x + 2 * TILE_SIZE // 3, mouth_y), 
                       2)

    def draw_smart(self):
        # 賢い敵の体（三角形）
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2
        
        # 三角形の頂点
        triangle_points = [
            (center_x, self.y + 5),  # 上
            (self.x + 5, self.y + TILE_SIZE - 5),  # 左下
            (self.x + TILE_SIZE - 5, self.y + TILE_SIZE - 5)  # 右下
        ]
        
        # 三角形の体を描画
        pygame.draw.polygon(screen, self.color, triangle_points)
        
        # 目（賢そうな表情）
        eye_y = self.y + TILE_SIZE // 3
        left_eye_x = self.x + TILE_SIZE // 3
        right_eye_x = self.x + 2 * TILE_SIZE // 3
        
        # 白目
        pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), self.eye_size)
        pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), self.eye_size)
        
        # 黒目（細い目）
        pygame.draw.ellipse(screen, BLACK, 
                          [left_eye_x - self.eye_size//2, eye_y - self.eye_size//4, 
                           self.eye_size, self.eye_size//2])
        pygame.draw.ellipse(screen, BLACK, 
                          [right_eye_x - self.eye_size//2, eye_y - self.eye_size//4, 
                           self.eye_size, self.eye_size//2])
        
        # 口（微笑み）
        mouth_y = self.y + 2 * TILE_SIZE // 3
        pygame.draw.arc(screen, BLACK, 
                      [center_x - self.eye_size * 1.5, mouth_y - self.eye_size, 
                       self.eye_size * 3, self.eye_size * 2], 
                      0, math.pi, 2)

    def move_slime(self, game_map):
        # ランダムに方向を変更する可能性
        if random.random() < 0.2:  # 20%の確率で方向転換
            self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        dx, dy = self.direction
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy

        if (0 <= new_grid_x < GRID_WIDTH and 
            0 <= new_grid_y < GRID_HEIGHT and
            game_map[new_grid_y][new_grid_x] == EMPTY):
            
            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            self.x = self.grid_x * TILE_SIZE
            self.y = self.grid_y * TILE_SIZE
        else:
            # 壁にぶつかったら方向転換
            self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

    def move_chaser(self, game_map, player):
        if player is None:
            self.move_slime(game_map)
            return
            
        # プレイヤーの方向を計算
        dx = 1 if player.grid_x > self.grid_x else -1 if player.grid_x < self.grid_x else 0
        dy = 1 if player.grid_y > self.grid_y else -1 if player.grid_y < self.grid_y else 0
        
        # 70%の確率でプレイヤーの方向に移動
        if random.random() < 0.7:
            # 水平か垂直のどちらかをランダムに選択
            if random.choice([True, False]) and dx != 0:
                self.try_move(dx, 0, game_map)
            elif dy != 0:
                self.try_move(0, dy, game_map)
        else:
            # ランダムな方向に移動
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.try_move(direction[0], direction[1], game_map)

    def move_smart(self, game_map, player, bombs):
        # プレイヤーがいない場合や爆弾がない場合は通常の追跡
        if player is None or bombs is None or len(bombs) == 0:
            self.move_chaser(game_map, player)
            return
        
        # 爆弾の爆発範囲内にいるかチェック
        in_danger = False
        bomb = bombs[0]  # 最初の爆弾を参照
        
        # 爆弾と同じ行にいる場合
        if self.grid_y == bomb.y and abs(self.grid_x - bomb.x) <= bomb.explosion_range:
            in_danger = True
        # 爆弾と同じ列にいる場合
        elif self.grid_x == bomb.x and abs(self.grid_y - bomb.y) <= bomb.explosion_range:
            in_danger = True
        
        if in_danger:
            # 安全な方向に逃げる
            safe_directions = []
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x = self.grid_x + dx
                new_y = self.grid_y + dy
                
                # 新しい位置が有効かチェック
                if (0 <= new_x < len(game_map[0]) and 
                    0 <= new_y < len(game_map) and 
                    game_map[new_y][new_x] == EMPTY):
                    
                    # 新しい位置が爆発範囲内かチェック
                    new_in_danger = False
                    if new_y == bomb.y and abs(new_x - bomb.x) <= bomb.explosion_range:
                        new_in_danger = True
                    elif new_x == bomb.x and abs(new_y - bomb.y) <= bomb.explosion_range:
                        new_in_danger = True
                    
                    if not new_in_danger:
                        safe_directions.append((dx, dy))
            
            # 安全な方向があれば、ランダムに選択して移動
            if safe_directions:
                dx, dy = random.choice(safe_directions)
                self.grid_x += dx
                self.grid_y += dy
                self.x = self.grid_x * TILE_SIZE
                self.y = self.grid_y * TILE_SIZE
                return
        
        # 危険がなければプレイヤーを追跡
        self.move_chaser(game_map, player)

    def try_move(self, dx, dy, game_map):
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy

        if (0 <= new_grid_x < GRID_WIDTH and 
            0 <= new_grid_y < GRID_HEIGHT and
            game_map[new_grid_y][new_grid_x] == EMPTY):
            
            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            self.x = self.grid_x * TILE_SIZE
            self.y = self.grid_y * TILE_SIZE
            return True
        return False

class Player:
    def __init__(self, x, y):
        self.grid_x = x // TILE_SIZE
        self.grid_y = y // TILE_SIZE
        self.x = self.grid_x * TILE_SIZE
        self.y = self.grid_y * TILE_SIZE
        self.size = TILE_SIZE
        self.bombs = []
        self.moving = False
        self.move_cooldown = 0
        self.move_delay = 10
        self.bomb_range = 2
        self.max_bombs = 1
        self.speed_level = 1
        self.alive = True
        self.score = 0
        # キャラクタータイプは常にロボット
        self.character_type = 2

    def draw(self):
        if self.alive:
            self.draw_robot()
    
    def draw_robot(self):
        # 基本的な体（メタリックな四角形）- 背景は透明
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # 頭部（丸い形）
        head_size = self.size // 3
        head_x = self.x + self.size // 2
        head_y = self.y + head_size
        pygame.draw.circle(screen, DARK_GRAY, (head_x, head_y), head_size)
        
        # 目（光るLED）
        eye_size = 3
        pygame.draw.circle(screen, BLUE, (head_x - 5, head_y - 2), eye_size)
        pygame.draw.circle(screen, BLUE, (head_x + 5, head_y - 2), eye_size)
        
        # アンテナ
        antenna_top = (head_x, self.y + 2)
        pygame.draw.line(screen, BLACK, (head_x, head_y - head_size), antenna_top, 2)
        pygame.draw.circle(screen, RED, antenna_top, 3)
        
        # 胴体（透明な背景に金属パーツ）
        # 胸部プレート
        chest_rect = pygame.Rect(self.x + 8, self.y + self.size // 2 - 5, 
                               self.size - 16, self.size // 4)
        pygame.draw.rect(screen, GRAY, chest_rect)
        
        # 腕（左右）
        arm_width = 4
        # 左腕
        pygame.draw.line(screen, GRAY, 
                       (self.x + 8, self.y + self.size // 2), 
                       (self.x + 2, self.y + self.size // 2 + 10), 
                       arm_width)
        # 右腕
        pygame.draw.line(screen, GRAY, 
                       (self.x + self.size - 8, self.y + self.size // 2), 
                       (self.x + self.size - 2, self.y + self.size // 2 + 10), 
                       arm_width)
        
        # 脚（左右）
        leg_width = 5
        # 左脚
        pygame.draw.line(screen, GRAY, 
                       (self.x + self.size // 3, self.y + 3 * self.size // 4), 
                       (self.x + self.size // 4, self.y + self.size - 2), 
                       leg_width)
        # 右脚
        pygame.draw.line(screen, GRAY, 
                       (self.x + 2 * self.size // 3, self.y + 3 * self.size // 4), 
                       (self.x + 3 * self.size // 4, self.y + self.size - 2), 
                       leg_width)
        
        # ボタンやライト
        for i in range(3):
            light_x = self.x + 12 + i * 8
            light_y = self.y + self.size // 2 + 5
            light_color = random.choice([RED, GREEN, YELLOW, BLUE]) if random.random() > 0.7 else GREEN
            pygame.draw.circle(screen, light_color, (light_x, light_y), 2)

    def move(self, dx, dy, game_map):
        if not self.alive or self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy

        if (0 <= new_grid_x < GRID_WIDTH and 
            0 <= new_grid_y < GRID_HEIGHT and
            game_map[new_grid_y][new_grid_x] != WALL and
            game_map[new_grid_y][new_grid_x] != BLOCK and
            game_map[new_grid_y][new_grid_x] != BOMB):  # 爆弾もすり抜けられないように追加
            
            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            self.x = self.grid_x * TILE_SIZE
            self.y = self.grid_y * TILE_SIZE
            
            # アイテム取得
            if game_map[new_grid_y][new_grid_x] in [POWER_UP, SPEED_UP, BOMB_UP]:
                self.collect_item(game_map[new_grid_y][new_grid_x])
                game_map[new_grid_y][new_grid_x] = EMPTY

            self.move_cooldown = max(5, self.move_delay - (self.speed_level - 1) * 2)

    def place_bomb(self, game_map):
        if not self.alive:
            return None
        if len(self.bombs) < self.max_bombs and game_map[self.grid_y][self.grid_x] != BOMB:
            bomb = Bomb(self.grid_x, self.grid_y, self.bomb_range)
            self.bombs.append(bomb)
            game_map[self.grid_y][self.grid_x] = BOMB
            if sound_enabled:
                bomb_place_sound.play()
            return bomb
        return None

    def collect_item(self, item_type):
        if item_type == POWER_UP:
            self.bomb_range += 1
            self.score += 100
        elif item_type == SPEED_UP:
            self.speed_level += 1
            self.score += 100
        elif item_type == BOMB_UP:
            self.max_bombs += 1
            self.score += 100
        
        # アイテム取得時に音を再生
        if sound_enabled:
            item_pickup_sound.play()

def create_map(stage_num=1):
    game_map = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # 外壁の配置
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1:
                game_map[y][x] = WALL

    # ステージに応じてブロックの配置密度を変更
    block_density = 0.2 + (stage_num * 0.1)  # ステージが上がるごとにブロックが増える
    
    # ブロックをランダムに配置
    for y in range(2, GRID_HEIGHT-2):
        for x in range(2, GRID_WIDTH-2):
            if random.random() < block_density:
                game_map[y][x] = BLOCK

    # プレイヤーの初期位置を確保
    game_map[1][1] = EMPTY
    game_map[1][2] = EMPTY
    game_map[2][1] = EMPTY

    # アイテムをランダムに配置
    items = 0
    max_items = 3 + stage_num  # ステージごとにアイテム数が増える
    while items < max_items:
        x = random.randint(1, GRID_WIDTH-2)
        y = random.randint(1, GRID_HEIGHT-2)
        if game_map[y][x] == BLOCK:
            item_type = random.choice([POWER_UP, SPEED_UP, BOMB_UP])
            game_map[y][x] = item_type
            items += 1
    
    return game_map

def draw_map(game_map):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if game_map[y][x] == WALL:
                # 壊れないブロック（石ブロック風）
                pygame.draw.rect(screen, STONE_COLOR, rect)
                # 石のテクスチャを表現する線
                pygame.draw.line(screen, DARK_GRAY, 
                               (x * TILE_SIZE, y * TILE_SIZE), 
                               (x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE), 2)
                pygame.draw.line(screen, DARK_GRAY, 
                               (x * TILE_SIZE, y * TILE_SIZE), 
                               (x * TILE_SIZE, y * TILE_SIZE + TILE_SIZE), 2)
                # 影の効果を追加
                pygame.draw.line(screen, DARK_GRAY, 
                               (x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE), 
                               (x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE + TILE_SIZE), 1)
                pygame.draw.line(screen, DARK_GRAY, 
                               (x * TILE_SIZE, y * TILE_SIZE + TILE_SIZE), 
                               (x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE + TILE_SIZE), 1)
                
            elif game_map[y][x] == BLOCK:
                # 壊れるブロック（レンガ風）
                pygame.draw.rect(screen, BRICK_COLOR, rect)
                # レンガのパターンを描画
                pygame.draw.line(screen, BRICK_LINES,
                               (x * TILE_SIZE, y * TILE_SIZE + TILE_SIZE//2),
                               (x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE + TILE_SIZE//2), 1)
                pygame.draw.line(screen, BRICK_LINES,
                               (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE),
                               (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE), 1)
                # 影の効果を追加
                pygame.draw.rect(screen, BRICK_LINES, 
                               (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
                
            elif game_map[y][x] == POWER_UP:
                # 火力アップアイテム（炎のデザイン）
                center_x = x * TILE_SIZE + TILE_SIZE // 2
                center_y = y * TILE_SIZE + TILE_SIZE // 2
                
                # 炎の形を描く
                flame_points = [
                    (center_x, center_y - TILE_SIZE//3),  # 上部
                    (center_x + TILE_SIZE//4, center_y),  # 右
                    (center_x, center_y + TILE_SIZE//4),  # 下
                    (center_x - TILE_SIZE//4, center_y),  # 左
                ]
                pygame.draw.polygon(screen, POWER_UP_COLOR, flame_points)
                # 内側の炎
                small_flame_points = [
                    (center_x, center_y - TILE_SIZE//4),
                    (center_x + TILE_SIZE//6, center_y),
                    (center_x, center_y + TILE_SIZE//6),
                    (center_x - TILE_SIZE//6, center_y),
                ]
                pygame.draw.polygon(screen, POWER_UP_GLOW, small_flame_points)
                
            elif game_map[y][x] == SPEED_UP:
                # スピードアップアイテム（稲妻デザイン）
                center_x = x * TILE_SIZE + TILE_SIZE // 2
                center_y = y * TILE_SIZE + TILE_SIZE // 2
                
                # 稲妻の描画
                lightning_points = [
                    (center_x - TILE_SIZE//3, center_y - TILE_SIZE//3),  # 開始点
                    (center_x, center_y - TILE_SIZE//6),                  # 第1折れ点
                    (center_x - TILE_SIZE//6, center_y + TILE_SIZE//6),  # 第2折れ点
                    (center_x + TILE_SIZE//3, center_y + TILE_SIZE//3)   # 終点
                ]
                # 稲妻の外側（輝き）
                pygame.draw.lines(screen, SPEED_UP_GLOW, False, lightning_points, 5)
                # 稲妻の内側（本体）
                pygame.draw.lines(screen, SPEED_UP_COLOR, False, lightning_points, 2)
                
            elif game_map[y][x] == BOMB_UP:
                # ボム増加アイテム（ボムのような見た目）
                center_x = x * TILE_SIZE + TILE_SIZE // 2
                center_y = y * TILE_SIZE + TILE_SIZE // 2
                # 外側の光る円
                pygame.draw.circle(screen, BOMB_UP_GLOW, (center_x, center_y), TILE_SIZE//2 - 4)
                # ボムの形
                pygame.draw.circle(screen, BOMB_UP_COLOR, (center_x, center_y), TILE_SIZE//3)
                # 導火線
                pygame.draw.line(screen, BOMB_UP_COLOR,
                               (center_x, center_y - TILE_SIZE//3),
                               (center_x + TILE_SIZE//4, center_y - TILE_SIZE//2), 2)

def check_explosion(bomb, game_map, player, enemies):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    explosions = [(bomb.x, bomb.y)]
    
    # プレイヤーの死亡判定
    if player.alive and (player.grid_x, player.grid_y) == (bomb.x, bomb.y):
        player.alive = False

    for dx, dy in directions:
        for r in range(1, bomb.explosion_range + 1):
            x = bomb.x + (dx * r)
            y = bomb.y + (dy * r)
            
            if (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                if game_map[y][x] == WALL:
                    break
                if game_map[y][x] == BLOCK:
                    game_map[y][x] = EMPTY
                    player.score += 50
                    explosions.append((x, y))  # 壊れるブロックも爆発範囲に含める
                    break

                # プレイヤーの死亡判定
                if player.alive and (player.grid_x, player.grid_y) == (x, y):
                    player.alive = False

                # 敵の死亡判定
                for enemy in enemies[:]:
                    if (enemy.grid_x, enemy.grid_y) == (x, y):
                        enemies.remove(enemy)
                        player.score += 200

                explosions.append((x, y))
            else:
                break
    
    bomb.explosions = explosions
    bomb.exploded = True
    if sound_enabled:
        bomb_explosion_sound.play()
    return explosions

def draw_game_info(player, stage):
    # スコア表示
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # ステージ表示
    stage_text = font.render(f"Stage: {stage}", True, WHITE)
    screen.blit(stage_text, (SCREEN_WIDTH - 120, 10))
    
    # パワーアップ状態表示
    power_text = font.render(f"Range: {player.bomb_range}", True, WHITE)
    speed_text = font.render(f"Speed: {player.speed_level}", True, WHITE)
    bombs_text = font.render(f"Bombs: {player.max_bombs}", True, WHITE)
    
    screen.blit(power_text, (10, SCREEN_HEIGHT - 90))
    screen.blit(speed_text, (10, SCREEN_HEIGHT - 60))
    screen.blit(bombs_text, (10, SCREEN_HEIGHT - 30))

def game_over_screen():
    text = font.render("GAME OVER - Press SPACE to restart", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)

def stage_clear_screen(stage):
    text = font.render(f"STAGE {stage} CLEAR! - Press SPACE to continue", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)

def main():
    # ゲームの状態
    game_state = MENU
    
    # ゲーム変数
    current_stage = 1
    max_cleared_stage = 0  # クリアした最大ステージ
    score = 0
    
    # メインループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # メニュー画面の処理
            if game_state == MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # ゲーム開始
                        game_map = create_map(current_stage)
                        player = Player(TILE_SIZE, TILE_SIZE)
                        enemies = []
                        
                        # ステージに応じた敵の生成
                        num_enemies = current_stage + 2
                        for _ in range(num_enemies):
                            enemy_type = random.randint(0, min(2, (current_stage - 1)))
                            spawn_enemy(enemies, game_map, player, enemy_type)
                        
                        game_state = GAME
                    # ステージ選択（クリア済みステージのみ）
                    elif event.key == pygame.K_RIGHT and current_stage < max_cleared_stage + 1:
                        current_stage += 1
                    elif event.key == pygame.K_LEFT and current_stage > 1:
                        current_stage -= 1
            
            # ゲームプレイ中の処理
            elif game_state == GAME:
                # 既存のゲームプレイ処理
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bomb = player.place_bomb(game_map)
                        if bomb:
                            game_map[bomb.y][bomb.x] = BOMB
            
            # ゲームオーバー画面の処理
            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # 同じステージを再開
                        game_map = create_map(current_stage)
                        player = Player(TILE_SIZE, TILE_SIZE)
                        enemies = []
                        
                        # ステージに応じた敵の生成
                        num_enemies = current_stage + 2
                        for _ in range(num_enemies):
                            enemy_type = random.randint(0, min(2, (current_stage - 1)))
                            spawn_enemy(enemies, game_map, player, enemy_type)
                        
                        game_state = GAME
                    elif event.key == pygame.K_ESCAPE:
                        # メニューに戻る
                        game_state = MENU
            
            # ステージクリア画面の処理
            elif game_state == STAGE_CLEAR:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # 次のステージへ
                        current_stage += 1
                        max_cleared_stage = max(max_cleared_stage, current_stage - 1)
                        
                        game_map = create_map(current_stage)
                        player = Player(TILE_SIZE, TILE_SIZE)
                        enemies = []
                        
                        # 新しいステージの敵を生成
                        num_enemies = current_stage + 2
                        for _ in range(num_enemies):
                            enemy_type = random.randint(0, min(2, (current_stage - 1)))
                            spawn_enemy(enemies, game_map, player, enemy_type)
                        
                        game_state = GAME
                    elif event.key == pygame.K_ESCAPE:
                        # メニューに戻る（クリアしたステージを記録）
                        max_cleared_stage = max(max_cleared_stage, current_stage)
                        game_state = MENU
        
        # 画面クリア
        screen.fill(BLACK)
        
        # メニュー画面の描画
        if game_state == MENU:
            draw_menu(current_stage, max_cleared_stage)
        
        # ゲームプレイ中の描画と更新
        elif game_state == GAME:
            # プレイヤーの入力処理
            keys = pygame.key.get_pressed()
            if player.alive and player.move_cooldown <= 0:
                if keys[pygame.K_UP]:
                    player.move(0, -1, game_map)
                elif keys[pygame.K_DOWN]:
                    player.move(0, 1, game_map)
                elif keys[pygame.K_LEFT]:
                    player.move(-1, 0, game_map)
                elif keys[pygame.K_RIGHT]:
                    player.move(1, 0, game_map)
            
            # 敵の移動
            for enemy in enemies:
                if enemy.move_cooldown <= 0:
                    if enemy.enemy_type == 0:  # スライム（ランダム移動）
                        enemy.move_slime(game_map)
                    elif enemy.enemy_type == 1:  # チェイサー（追跡）
                        enemy.move_chaser(game_map, player)
                    elif enemy.enemy_type == 2:  # スマート（爆弾回避）
                        enemy.move_smart(game_map, player, player.bombs if player.alive else None)
                    # 移動後にクールダウンをリセット
                    enemy.move_cooldown = enemy.move_delay
                else:
                    enemy.move_cooldown -= 1
            
            # プレイヤーのクールダウン更新
            if player.move_cooldown > 0:
                player.move_cooldown -= 1
            
            # 爆弾の更新
            for bomb in player.bombs[:]:
                if not bomb.exploded:
                    if bomb.update():
                        # 爆発の処理
                        explosions = check_explosion(bomb, game_map, player, enemies)
                        game_map[bomb.y][bomb.x] = EMPTY
                        # プレイヤーが死亡した場合はゲームオーバー状態に移行
                        if not player.alive:
                            game_state = GAME_OVER
                            if sound_enabled:
                                game_over_sound.play()  # ゲームオーバー音を再生
                else:
                    # 爆発後の更新
                    bomb.update()
                    # 爆発後のエフェクト表示期間が終了したら削除
                    if bomb.explosion_frames >= bomb.explosion_duration:
                        player.bombs.remove(bomb)
            
            # 敵との衝突判定
            if player.alive:
                for enemy in enemies:
                    if (player.grid_x == enemy.grid_x and 
                        player.grid_y == enemy.grid_y):
                        player.alive = False
                        game_state = GAME_OVER
                        if sound_enabled:
                            game_over_sound.play()  # ゲームオーバー音を再生
                        break  # 一度死亡判定が出たらループを抜ける
            
            # すべての敵を倒したらステージクリア
            if not enemies and player.alive:
                max_cleared_stage = max(max_cleared_stage, current_stage)
                game_state = STAGE_CLEAR
                if sound_enabled:
                    stage_clear_sound.play()  # ステージクリア音を再生
            
            # マップの描画
            draw_map(game_map)
            
            # 爆弾の描画
            for bomb in player.bombs:
                bomb.draw()
            
            # 敵の描画
            for enemy in enemies:
                enemy.draw()
            
            # プレイヤーの描画
            player.draw()
            
            # スコアとステージ情報の表示
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {player.score}", True, WHITE)
            stage_text = font.render(f"Stage: {current_stage}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(stage_text, (SCREEN_WIDTH - 150, 10))
            
            # プレイヤーのステータス表示
            bomb_text = font.render(f"Bombs: {player.max_bombs}", True, WHITE)
            range_text = font.render(f"Range: {player.bomb_range}", True, WHITE)
            speed_text = font.render(f"Speed: {player.speed_level}", True, WHITE)
            screen.blit(bomb_text, (10, SCREEN_HEIGHT - 90))
            screen.blit(range_text, (10, SCREEN_HEIGHT - 60))
            screen.blit(speed_text, (10, SCREEN_HEIGHT - 30))
        
        # ゲームオーバー画面の描画
        elif game_state == GAME_OVER:
            draw_game_over(player.score)
        
        # ステージクリア画面の描画
        elif game_state == STAGE_CLEAR:
            draw_stage_clear(current_stage)
        
        # 画面更新
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def draw_menu(current_stage, max_cleared_stage):
    # タイトル
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    title = font_large.render("BOMBERMAN", True, WHITE)
    instruction = font_small.render("Press ENTER to Start", True, WHITE)
    
    # ロボットキャラクターの表示
    robot_player = Player(SCREEN_WIDTH // 2 - TILE_SIZE // 2, SCREEN_HEIGHT // 2)
    robot_player.draw()
    
    # テキスト表示
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    # ロボットの説明
    robot_desc = font_small.render("Place bombs with the Robot character!", True, BLUE)
    screen.blit(robot_desc, (SCREEN_WIDTH // 2 - robot_desc.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    
    # ステージ選択の表示
    stage_select = font_small.render(f"Stage: {current_stage}", True, WHITE)
    screen.blit(stage_select, (SCREEN_WIDTH // 2 - stage_select.get_width() // 2, SCREEN_HEIGHT // 2 + 150))
    
    # ステージ選択の説明（クリア済みステージのみ選択可能）
    if max_cleared_stage > 0:
        stage_help = font_small.render("Use LEFT/RIGHT arrows to select cleared stages", True, YELLOW)
        screen.blit(stage_help, (SCREEN_WIDTH // 2 - stage_help.get_width() // 2, SCREEN_HEIGHT // 2 + 180))

def draw_game_over(score):
    # ゲームオーバー表示
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    game_over = font_large.render("GAME OVER", True, RED)
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    instruction = font_small.render("Press ENTER to restart same stage", True, WHITE)
    menu_instruction = font_small.render("Press ESC to return to menu", True, WHITE)
    
    screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(menu_instruction, (SCREEN_WIDTH // 2 - menu_instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 90))

def draw_stage_clear(stage):
    # ステージクリア表示
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    clear_text = font_large.render(f"STAGE {stage} CLEAR!", True, YELLOW)
    instruction = font_small.render("Press ENTER for next stage", True, WHITE)
    menu_instruction = font_small.render("Press ESC to return to menu", True, WHITE)
    
    screen.blit(clear_text, (SCREEN_WIDTH // 2 - clear_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(menu_instruction, (SCREEN_WIDTH // 2 - menu_instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 90))

def spawn_enemy(enemies, game_map, player, enemy_type):
    # プレイヤーから離れた位置に敵を配置
    min_distance = 5  # プレイヤーからの最小距離
    
    for _ in range(20):  # 最大20回試行
        x = random.randint(1, GRID_WIDTH-2)
        y = random.randint(1, GRID_HEIGHT-2)
        
        # プレイヤーからの距離を計算
        distance = abs(x - player.grid_x) + abs(y - player.grid_y)
        
        if distance >= min_distance and game_map[y][x] == EMPTY:
            enemies.append(Enemy(x, y, enemy_type))
            return True
    
    # 適切な位置が見つからなかった場合、ランダムな空きマスに配置
    empty_cells = []
    for y in range(1, GRID_HEIGHT-1):
        for x in range(1, GRID_WIDTH-1):
            if game_map[y][x] == EMPTY:
                empty_cells.append((x, y))
    
    if empty_cells:
        x, y = random.choice(empty_cells)
        enemies.append(Enemy(x, y, enemy_type))
        return True
    
    return False

# メイン関数を呼び出す
if __name__ == "__main__":
    main() 