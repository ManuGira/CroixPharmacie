import enum
import sys

import numpy as np
import pygame

import pharmacontroller

SCREEN_SIZE = pharmacontroller.SCREEN_SIZE

TILE_SIZE = 8
TILES = [
    np.zeros((TILE_SIZE, TILE_SIZE), dtype=np.uint8),
    np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ], dtype=np.uint8) * 255,
    np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ], dtype=np.uint8) * 255,
    np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ], dtype=np.uint8) * 255,
    np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ], dtype=np.uint8) * 255,
    np.ones((TILE_SIZE, TILE_SIZE), dtype=np.uint8) * 255,
]


def insert_tile(image, tile, coord_ij):
    th, tw = tile.shape
    i, j = coord_ij
    image[i * th:(i + 1) * th, j * tw:(j + 1) * tw] = tile


def generate_image(board):
    h, w = board.shape
    res = np.zeros((SCREEN_SIZE, SCREEN_SIZE), dtype=np.uint8)
    for i in range(h):
        for j in range(w):
            ind = int(board[i, j])
            insert_tile(res, TILES[ind], (i, j))
    return res


def drop_frames(animation, target_length):
    current_length = len(animation)
    drop_count = current_length - target_length
    for i in range(drop_count)[::-1]:
        ind = (i * current_length) // drop_count
        animation.pop(ind)


def generate_animation(board, move_func, frame_count):
    res = []
    image0 = generate_image(board)
    for i in range(frame_count):
        shift = (TILE_SIZE * (i + 1)) // frame_count
        frame = move_func(image0, shift)
        res.append(frame)
    return res


class Action(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()
    SCRAMBLE = enum.auto()


def move_right(board, shift=1):
    assert len(board.shape) == 2
    h, w = board.shape
    assert h % 3 == 0
    assert h == w

    n = h // 3
    board = board.copy()
    board[:n, n:2 * n] = np.roll(board[:n, n:2 * n], shift=shift, axis=1)
    board[n:2 * n, :] = np.roll(board[n:2 * n, :], shift=shift, axis=1)
    board[2 * n:, n:2 * n] = np.roll(board[2 * n:, n:2 * n], shift=shift, axis=1)
    return board


def move_left(board, shift=1):
    return move_right(board[:, ::-1], shift)[:, ::-1]


def move_up(board, shift=1):
    return move_left(board.T, shift).T


def move_down(board, shift=1):
    return move_right(board.T, shift).T


def main():
    pygame.init()
    screen = pharmacontroller.PharmaScreen()

    controls = {
        pygame.K_LEFT: Action.LEFT,
        pygame.K_a: Action.LEFT,
        pygame.K_RIGHT: Action.RIGHT,
        pygame.K_d: Action.RIGHT,
        pygame.K_UP: Action.UP,
        pygame.K_w: Action.UP,
        pygame.K_DOWN: Action.DOWN,
        pygame.K_s: Action.DOWN,
        pygame.K_SPACE: Action.SCRAMBLE,
    }

    img = np.zeros((SCREEN_SIZE, SCREEN_SIZE), dtype=np.uint8)
    init_2x2x5 = np.array([
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [2, 2, 3, 3, 4, 4],
        [2, 2, 3, 3, 4, 4],
        [0, 0, 5, 5, 0, 0],
        [0, 0, 5, 5, 0, 0],
    ], dtype=np.uint8)
    board = init_2x2x5.copy()

    lut = np.arange(256, dtype=float) * 255 / 7
    lut = np.clip(lut, 0, 255).astype(np.uint8)

    animation_max_length = 16
    animation = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                action = controls[event.key]
                move_func = None
                if action == Action.UP:
                    move_func = move_up
                elif action == Action.DOWN:
                    move_func = move_down
                elif action == Action.LEFT:
                    move_func = move_left
                elif action == Action.RIGHT:
                    move_func = move_right

                if move_func is not None:
                    new_frames = generate_animation(board, move_func, animation_max_length // 2)
                    target_total_length = (len(animation) + animation_max_length) // 2
                    animation += new_frames
                    drop_frames(animation, target_total_length)
                    board = move_func(board)

        if len(animation) == 0:
            img = generate_image(board)
        else:
            img = animation.pop(0)
        screen.set_image_u8(img)


if __name__ == '__main__':
    main()
