import pygame as pg

WIDTH, HEIGHT = 400, 600
BACKGROUND_COLOR = (240, 240, 240)


class Player(pg.sprite.Sprite):
    SIZE = 30
    COLOR = (150, 150, 150)
    COOLTIME = 60
    SPEED = 3

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pg.Surface((self.SIZE, self.SIZE))
        self.image.fill(self.COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.cooltime = 0
        self.direction = 0  # 0:上, 1:右, 2:下, 3:左

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


def main():
    # 初期化
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Turn Right Dogde Game")
    clock = pg.time.Clock()

    # スプライトグループ
    all_sprites = pg.sprite.Group()
    player = Player(all_sprites)

    # ゲームループ
    running = True
    while running:
        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # 更新処理
        all_sprites.update()

        # 描画処理
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        pg.display.flip()
        clock.tick(60)

    # 終了処理
    pg.quit()


if __name__ == "__main__":
    main()
