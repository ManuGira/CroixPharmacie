import cv2
from rubikscross.graphic_painters import RollFuncMap
from rubikscross.graphics import Graphics
from rubikscross.mixer import SilentMixer
from rubikscross.rubikscross import RubiksCross
from rubikscross.tiles import TILES
import rubikscross
from rubikscross import controller_pro
import croix_pharmacie.pharmacontroller
import numpy.typing as npt
import pygame
from rubikscross.game_app import Action
import numpy as np


class GameApp_PharmaController:
    def __init__(self, board_size, rubikscross: RubiksCross):
        self.board_size = board_size
        self.rubikscross = rubikscross

        pygame.init()
        self.screen = croix_pharmacie.pharmacontroller.PharmaScreen(color_scale=False)

    def run(self):
        key_action_map = {
            pygame.K_LEFT: Action.LEFT,
            pygame.K_a: Action.LEFT,
            pygame.K_RIGHT: Action.RIGHT,
            pygame.K_d: Action.RIGHT,
            pygame.K_UP: Action.UP,
            pygame.K_w: Action.UP,
            pygame.K_DOWN: Action.DOWN,
            pygame.K_s: Action.DOWN,
            pygame.K_e: Action.ROT_RIGHT,
            pygame.K_q: Action.ROT_LEFT,
            pygame.K_SPACE: Action.SCRAMBLE,
            pygame.K_1: Action.SAVE1,
            pygame.K_2: Action.SAVE2,
            pygame.K_3: Action.SAVE3,
            pygame.K_F1: Action.LOAD1,
            pygame.K_F2: Action.LOAD2,
            pygame.K_F3: Action.LOAD3,
        }

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in [pygame.KEYDOWN]:
                    if event.key in key_action_map.keys():
                        self.rubikscross.on_action(key_action_map[event.key])

            hint_frame = self.rubikscross.rcgraphics.get_hint_frame()
            image, alpha = self.rubikscross.rcgraphics.get_next_frame()
            self.screen.set_image(image[:, :, 0].astype(float))

def recolorize_tiles(tiles_rgb):
    # recolorise les tuiles pour les rendre plus lisible sur la croix de pharmacie

    tiles_u3 = []

    # ce qui est noir (0) devient (1). Le reste (1-255) devient noir (0)
    lut = np.zeros((256,), dtype=np.uint8)
    lut[0] = 1

    for t_rgb in tiles_rgb:
        # converti en niveau de gris
        t_u3 = cv2.cvtColor(t_rgb, cv2.COLOR_RGB2GRAY)

        # applique les nouvelles couleurs
        t_u3 = cv2.LUT(t_u3, lut)

        # le jeu attend des tuiles en couleurs alors il faut reconvertire en rgb
        t_u3 = cv2.cvtColor(t_u3, cv2.COLOR_GRAY2BGR)

        tiles_u3.append(t_u3)

    tiles_u3[0] *= 0
    return tiles_u3


def main():
    difficulty = 2
    tiles = recolorize_tiles(rubikscross.tiles.TILES)
    tile_size = tiles[0].shape[0]
    board_size = difficulty * 3 * TILES[0].shape[0]
    assert board_size == croix_pharmacie.pharmacontroller.SCREEN_SIZE

    # construit le jeu. On peut réutiliser tout les composant du package rubikscross, a part le GameApp que l'on doit réimplémenter.
    # Le GameApp est la couche qui gère les inputs du joueur (clavier) et output (croix de pharmacie)
    GameApp_PharmaController(
        board_size,
        RubiksCross(
            Graphics(
                tiles=tiles,
                move_func_map=RollFuncMap(tile_size, board_size),
                animation_max_length=20),
            rcmixer=SilentMixer(),  # utilise le mixer silencieux (pas de son)
            difficulty=difficulty
        )).run()


if __name__ == '__main__':
    main()
