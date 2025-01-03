import pygame as pg

WIDTH, HEIGHT = 400, 600
BACKGROUND_COLOR = (240, 240, 240)


def main():
    # 初期化
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Turn Right Dogde Game")
    clock = pg.time.Clock()

    # ゲームループ
    running = True
    while running:
        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # 画面更新
        screen.fill(BACKGROUND_COLOR)
        pg.display.flip()
        clock.tick(60)

    # 終了処理
    pg.quit()


if __name__ == "__main__":
    main()
