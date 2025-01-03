import random

import pygame as pg

WIDTH, HEIGHT = 400, 600
BACKGROUND_COLOR = (240, 240, 240)

USEREVENT_SPAWNENEMY = pg.USEREVENT + 1


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

        self.rect.x = max(0, min(self.rect.x, WIDTH - self.SIZE))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.SIZE))


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


class Enemy(pg.sprite.Sprite):
    SIZE = 30
    COLOR = (150, 60, 120)
    SPEED = 3

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pg.Surface((self.SIZE, self.SIZE)).convert_alpha()
        self.image.fill((255, 255, 255, 0))
        pg.draw.circle(
            self.image, self.COLOR, (self.SIZE // 2, self.SIZE // 2), self.SIZE // 2
        )
        # 左右の画面外にスポーンし，反対側に向かって移動
        self.rect = self.image.get_rect()
        self.rect.y = random.randint(0, HEIGHT - self.SIZE)
        if random.choice([True, False]):
            self.rect.x = -self.SIZE
            self.target_x = WIDTH
            self.target_y = random.randint(0, HEIGHT - self.SIZE)
        else:
            self.rect.x = WIDTH
            self.target_x = -self.SIZE
            self.target_y = random.randint(0, HEIGHT - self.SIZE)

    def update(self):
        v = pg.Vector2(self.target_x - self.rect.x, self.target_y - self.rect.y)
        if v.length() < self.SPEED:
            self.kill()
        v = v.normalize() * self.SPEED
        self.rect.move_ip(v)


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

    # 敵のスポーンタイマーの設定
    pg.time.set_timer(USEREVENT_SPAWNENEMY, 1000)

    # ゲームループ
    running = True
    while running:
        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == USEREVENT_SPAWNENEMY:
                Enemy(all_sprites, enemies)

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
        pg.display.flip()
        clock.tick(60)

    # 終了処理
    pg.quit()


if __name__ == "__main__":
    main()
