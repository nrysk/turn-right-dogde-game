import math
import random

import pygame as pg

WIDTH, HEIGHT = 400, 600
BACKGROUND_COLOR = (240, 240, 240)

USEREVENT_SCOREUP = pg.USEREVENT + 1
USEREVENT_PHASEUP = pg.USEREVENT + 2
USEREVENT_SPAWNENEMY = pg.USEREVENT + 10


class Player(pg.sprite.Sprite):
    SIZE = 20
    COLOR = (150, 150, 150)
    COOLTIME = 30
    SPEED = 3
    MAX_HEALTH = 200

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pg.Surface((self.SIZE, self.SIZE))
        self.image.fill(self.COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.cooltime = 0
        self.direction = 0  # 0:上, 1:右, 2:下, 3:左
        self.health = Player.MAX_HEALTH

    def update(self):
        self.cooltime = max(0, self.cooltime - 1)
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.cooltime == 0:
            self.cooltime = self.COOLTIME
            self.direction = (self.direction + 1) % 4

        if self.direction == 0:
            self.rect.y -= self.SPEED
        elif self.direction == 1:
            self.rect.x += self.SPEED
        elif self.direction == 2:
            self.rect.y += self.SPEED
        elif self.direction == 3:
            self.rect.x -= self.SPEED

        if self.rect.x < 0:
            self.rect.x = 0
            self.health -= 0.5
        if self.rect.x > WIDTH - self.SIZE:
            self.rect.x = WIDTH - self.SIZE
            self.health -= 0.5
        if self.rect.y < 0:
            self.rect.y = 0
            self.health -= 0.5
        if self.rect.y > HEIGHT - self.SIZE:
            self.rect.y = HEIGHT - self.SIZE
            self.health -= 0.5


class HealthBar:
    def __init__(self, player, rect):
        self.player = player
        self.rect = pg.Rect(rect)
        self.max_width = self.rect.width

    def draw(self, screen):
        pg.draw.rect(screen, (255, 0, 0), self.rect)
        self.rect.width = self.player.health / Player.MAX_HEALTH * self.max_width
        pg.draw.rect(screen, (0, 255, 0), self.rect)


class CooltimeBar:
    def __init__(self, player, rect):
        self.player = player
        self.rect = pg.Rect(rect)
        self.max_width = self.rect.width

    def draw(self, screen):
        pg.draw.rect(screen, (120, 120, 120), self.rect)
        self.rect.width = (
            (Player.COOLTIME - self.player.cooltime) / Player.COOLTIME * self.max_width
        )
        pg.draw.rect(screen, (180, 180, 180), self.rect)


class ScoreBoard:
    def __init__(self, rect):
        self.score = 0
        self.rect = pg.Rect(rect)

    def draw(self, screen):
        font = pg.font.Font(None, self.rect.height)
        text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(text, self.rect.topleft)

    def raise_score(self, score):
        self.score += score


class PhaseBoard:
    def __init__(self, rect):
        self.phase = 1
        self.rect = pg.Rect(rect)

    def draw(self, screen):
        font = pg.font.Font(None, self.rect.height)
        text = font.render(f"Phase: {self.phase}", True, (0, 0, 0))
        screen.blit(text, self.rect.topleft)

    def raise_phase(self, phase):
        self.phase += phase


class Enemy(pg.sprite.Sprite):
    COLOR = (150, 60, 120)

    def __init__(self, size, speed, has_gun, shot_probability, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.size = size
        self.has_gun = has_gun
        self.shot_probability = shot_probability
        self.image = pg.Surface((self.size, self.size)).convert_alpha()
        self.image.fill((255, 255, 255, 0))
        pg.draw.circle(
            self.image, self.COLOR, (self.size // 2, self.size // 2), self.size // 2
        )
        # 左右の画面外にスポーンし，反対側に向かって移動
        self.rect = self.image.get_rect()
        self.rect.y = random.randint(0, HEIGHT - self.size)
        if random.choice([True, False]):
            self.rect.x = -self.size
            self.target_x = WIDTH
            self.target_y = random.randint(0, HEIGHT - self.size)
        else:
            self.rect.x = WIDTH
            self.target_x = -self.size
            self.target_y = random.randint(0, HEIGHT - self.size)

    def update(self):
        v = pg.Vector2(self.target_x - self.rect.x, self.target_y - self.rect.y)
        if v.length() < 10:
            self.kill()
        v = v.normalize() * self.speed
        self.rect.move_ip(v)

        # has_gun なら一定の確率で弾を発射
        if self.has_gun and random.random() < self.shot_probability:
            theta = random.uniform(-math.pi / 4, math.pi / 4)
            direction = v.rotate(theta)
            Bullet(self.rect.center, direction, self.groups())


class Bullet(pg.sprite.Sprite):
    COLOR = (40, 40, 70)
    SPEED = 5
    SIZE = 15

    def __init__(self, position, direction, *groups):
        super().__init__(*groups)
        self.image = pg.Surface((self.SIZE, self.SIZE)).convert_alpha()
        self.image.fill((255, 255, 255, 0))
        pg.draw.polygon(
            self.image,
            self.COLOR,
            [(0, 0), (0, self.SIZE), (self.SIZE, self.SIZE // 2)],
        )
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.velocity = pg.Vector2(direction).normalize() * self.SPEED

    def update(self):
        self.rect.move_ip(self.velocity)
        if not pg.Rect(0, 0, WIDTH, HEIGHT).colliderect(self.rect):
            self.kill()


def spawn_enemy(phase, *groups):
    # パラメータのデフォルト値
    speed = 3
    size = 25
    count = 1
    has_gun = False
    shot_probability = 0.01

    # フェーズに応じてパラメータを変更
    if phase >= 2:
        speed = random.randint(3, 5)
    if phase >= 3:
        size = random.randint(25, 45)
    if phase >= 4:
        speed = random.randint(2, 6)
    if phase >= 5:
        has_gun = True
    if phase >= 6:
        count = random.randint(1, 2)
    if phase >= 7:
        count = 2
        shot_probability = 0.03

    for _ in range(count):
        Enemy(size, speed, has_gun, shot_probability, *groups)


def main():
    # 初期化
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Turn Right Dogde Game")
    clock = pg.time.Clock()

    # スプライトグループ
    all_sprites = pg.sprite.Group()
    player = Player(all_sprites)
    all_sprites.add(player)
    enemies = pg.sprite.Group()
    all_sprites.add(enemies)

    # UI の初期化
    health_bar = HealthBar(player, (10, 10, 200, 15))
    cooltime_bar = CooltimeBar(player, (10, 30, 200, 8))
    score_board = ScoreBoard((10, 50, 200, 30))
    phase_board = PhaseBoard((10, 80, 200, 30))

    # タイマーの設定
    pg.time.set_timer(USEREVENT_SPAWNENEMY, 1000)
    pg.time.set_timer(USEREVENT_PHASEUP, 10000)
    pg.time.set_timer(USEREVENT_SCOREUP, 1000)

    # ゲームループ
    running = True
    while running:
        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == USEREVENT_SCOREUP:
                score_board.raise_score(1)
            elif event.type == USEREVENT_PHASEUP:
                if phase_board.phase < 8:
                    phase_board.raise_phase(1)
            elif event.type == USEREVENT_SPAWNENEMY:
                spawn_enemy(phase_board.phase, enemies, all_sprites)

        # 更新処理
        all_sprites.update()

        # 当たり判定
        for enemy in pg.sprite.spritecollide(player, enemies, False):
            player.health -= 1

        # 描画処理
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        health_bar.draw(screen)
        cooltime_bar.draw(screen)
        score_board.draw(screen)
        phase_board.draw(screen)
        pg.display.flip()
        clock.tick(60)

    # 終了処理
    pg.quit()


if __name__ == "__main__":
    main()
