import pygame
import sys
import random
import math

# 初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

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

class Bomb:
    def __init__(self, x, y, range=2):
        self.x = x
        self.y = y
        self.timer = 180  # 3秒 (60FPS × 3)
        self.range = range
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
            self.move_delay = 40  # ゆっくり移動
        elif enemy_type == ENEMY_CHASER:
            self.color = (220, 50, 50)  # 赤色の追跡者
            self.move_delay = 25  # 中程度の速さ
        elif enemy_type == ENEMY_SMART:
            self.color = (50, 180, 50)  # 緑色の賢い敵
            self.move_delay = 20  # やや速い
        
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

    def move(self, game_map, player=None, bombs=None):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        if self.enemy_type == ENEMY_SLIME:
            self.move_slime(game_map)
        elif self.enemy_type == ENEMY_CHASER:
            self.move_chaser(game_map, player)
        elif self.enemy_type == ENEMY_SMART:
            self.move_smart(game_map, player, bombs)

        self.move_cooldown = self.move_delay

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
        if player is None or bombs is None or len(bombs) == 0:
            self.move_chaser(game_map, player)
            return
            
        # 爆弾からの逃避行動
        for bomb in bombs:
            # 爆発範囲内にいるかチェック
            in_danger = False
            bomb_range = bomb.range
            
            # 水平方向の爆発範囲チェック
            if self.grid_y == bomb.y and abs(self.grid_x - bomb.x) <= bomb_range:
                in_danger = True
            # 垂直方向の爆発範囲チェック
            elif self.grid_x == bomb.x and abs(self.grid_y - bomb.y) <= bomb_range:
                in_danger = True
                
            if in_danger:
                # 安全な方向に逃げる
                safe_directions = []
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    new_x = self.grid_x + dx
                    new_y = self.grid_y + dy
                    if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                        game_map[new_y][new_x] == EMPTY and
                        not (new_y == bomb.y and abs(new_x - bomb.x) <= bomb_range) and
                        not (new_x == bomb.x and abs(new_y - bomb.y) <= bomb_range)):
                        safe_directions.append((dx, dy))
                
                if safe_directions:
                    dx, dy = random.choice(safe_directions)
                    if self.try_move(dx, dy, game_map):
                        return
        
        # 危険がなければプレイヤーを追いかける（ChaserEnemyと同様）
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

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.size, self.size))

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
        for r in range(1, bomb.range + 1):
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

# ゲーム状態
current_stage = 1
game_map = create_map(current_stage)
player = Player(TILE_SIZE, TILE_SIZE)
enemies = []

# 敵の生成（ステージに応じて種類と数を変更）
num_slimes = max(1, current_stage)
num_chasers = max(0, current_stage - 1)
num_smart = max(0, current_stage - 2)

# スライム型敵の配置
for _ in range(num_slimes):
    x = random.randint(GRID_WIDTH//2, GRID_WIDTH-2)
    y = random.randint(1, GRID_HEIGHT-2)
    enemies.append(Enemy(x, y, ENEMY_SLIME))

# 追跡型敵の配置（ステージ2以降）
for _ in range(num_chasers):
    x = random.randint(GRID_WIDTH//2, GRID_WIDTH-2)
    y = random.randint(GRID_HEIGHT//2, GRID_HEIGHT-2)
    enemies.append(Enemy(x, y, ENEMY_CHASER))

# 爆弾回避型敵の配置（ステージ3以降）
for _ in range(num_smart):
    x = random.randint(1, GRID_WIDTH-2)
    y = random.randint(GRID_HEIGHT//2, GRID_HEIGHT-2)
    enemies.append(Enemy(x, y, ENEMY_SMART))

game_state = "playing"  # "playing", "game_over", "stage_clear"

# メインゲームループ
clock = pygame.time.Clock()
running = True

while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "playing" and player.alive:
                    bomb = player.place_bomb(game_map)
                elif game_state == "game_over":
                    # ゲームリスタート
                    current_stage = 1
                    game_map = create_map(current_stage)
                    player = Player(TILE_SIZE, TILE_SIZE)
                    enemies = []
                    game_state = "playing"
                elif game_state == "stage_clear":
                    # 次のステージへ
                    current_stage += 1
                    game_map = create_map(current_stage)
                    player = Player(TILE_SIZE, TILE_SIZE)
                    
                    # 新しいステージの敵を生成
                    enemies = []
                    num_slimes = max(1, current_stage)
                    num_chasers = max(0, current_stage - 1)
                    num_smart = max(0, current_stage - 2)
                    
                    # スライム型敵の配置
                    for _ in range(num_slimes):
                        x = random.randint(GRID_WIDTH//2, GRID_WIDTH-2)
                        y = random.randint(1, GRID_HEIGHT-2)
                        enemies.append(Enemy(x, y, ENEMY_SLIME))
                    
                    # 追跡型敵の配置（ステージ2以降）
                    for _ in range(num_chasers):
                        x = random.randint(GRID_WIDTH//2, GRID_WIDTH-2)
                        y = random.randint(GRID_HEIGHT//2, GRID_HEIGHT-2)
                        enemies.append(Enemy(x, y, ENEMY_CHASER))
                    
                    # 爆弾回避型敵の配置（ステージ3以降）
                    for _ in range(num_smart):
                        x = random.randint(1, GRID_WIDTH-2)
                        y = random.randint(GRID_HEIGHT//2, GRID_HEIGHT-2)
                        enemies.append(Enemy(x, y, ENEMY_SMART))
                    
                    game_state = "playing"

    if game_state == "playing":
        # キー入力処理
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy, game_map)

        # 敵の移動
        for enemy in enemies:
            enemy.move(game_map, player, player.bombs)
            # プレイヤーとの衝突判定
            if player.alive and (enemy.grid_x, enemy.grid_y) == (player.grid_x, player.grid_y):
                player.alive = False

        # 爆弾の更新
        for bomb in player.bombs[:]:
            if not bomb.exploded:
                if bomb.update():
                    # 爆発の処理
                    explosions = check_explosion(bomb, game_map, player, enemies)
                    game_map[bomb.y][bomb.x] = EMPTY
            else:
                # 爆発後の更新
                bomb.update()
                # 爆発後のエフェクト表示期間が終了したら削除
                if bomb.explosion_frames >= bomb.explosion_duration:
                    player.bombs.remove(bomb)

        # ゲームオーバー判定
        if not player.alive:
            game_state = "game_over"

        # ステージクリア判定
        if len(enemies) == 0:
            game_state = "stage_clear"

    # 画面描画
    screen.fill(BLACK)
    draw_map(game_map)
    for bomb in player.bombs:
        bomb.draw()
    player.draw()
    for enemy in enemies:
        enemy.draw()
    draw_game_info(player, current_stage)

    if game_state == "game_over":
        game_over_screen()
    elif game_state == "stage_clear":
        stage_clear_screen(current_stage)
    
    # 画面更新
    pygame.display.flip()
    clock.tick(60)

# ゲーム終了
pygame.quit()
sys.exit() 