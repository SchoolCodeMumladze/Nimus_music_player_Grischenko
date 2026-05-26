import pygame
from pygame import *
import os
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nimus Music Player")
clock = pygame.time.Clock()
try:
    icon = pygame.image.load("Nimus.jpg")
    pygame.display.set_icon(icon)
except:
    pass
WHITE = (255, 255, 255)
BLACK = (13, 17, 23)
GRAY = (66, 158, 255)
LIGHT_GRAY = (255, 198, 161)
ORANGE = (255, 107, 53)
GREEN = (0, 200, 0)
DARK_GRAY = (150, 150, 150)
RED = (255, 0, 0)

font = pygame.font.SysFont("Oswald", 24)
font_small = pygame.font.SysFont("Oswald", 18)

playlist = []
current_track_idx = -1
music_file = ""
song_length = 0
paused = False
running = True
time_offset = 0
is_looping = False

vol_w, vol_h = 20, 75
vol_x = WIDTH - vol_w - 20
vol_y = HEIGHT - vol_h - 20
volume = 0.5
pygame.mixer.music.set_volume(volume)
is_dragging_volume = False

bar_width, bar_height = 420, 16
bar_x, bar_y = 50, 270
is_dragging_progress = False

scroll_offset = 0


def open_folder():
    global playlist, current_track_idx, scroll_offset
    folder_path = filedialog.askdirectory(title="Выберите папку с музыкой")
    if folder_path:
        valid_extensions = ('.mp3', '.wav', '.ogg')
        playlist = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.lower().endswith(valid_extensions)
        ]
        scroll_offset = 0
        if playlist:
            current_track_idx = 0
            load_track(playlist[current_track_idx])
        else:
            playlist = []
            current_track_idx = -1


def load_track(filename):
    global song_length, music_file, time_offset, paused, is_dragging_progress
    if os.path.exists(filename):
        music_file = filename
        pygame.mixer.music.load(music_file)
        try:
            song_length = pygame.mixer.Sound(music_file).get_length() * 1000
        except:
            song_length = 0
        time_offset = 0
        paused = False
        is_dragging_progress = False
        pygame.mixer.music.play()
    else:
        music_file = f"Файл {os.path.basename(filename)} не найден"
        song_length = 0


def play_music():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    elif not pygame.mixer.music.get_busy() and song_length > 0:
        pygame.mixer.music.play()


def pause_music():
    global paused
    if pygame.mixer.music.get_busy() and not paused:
        pygame.mixer.music.pause()
        paused = True


def stop_music():
    global paused, time_offset, is_dragging_progress
    pygame.mixer.music.stop()
    paused = False
    time_offset = 0
    is_dragging_progress = False


def next_track():
    global current_track_idx
    if playlist:
        current_track_idx = (current_track_idx + 1) % len(playlist)
        load_track(playlist[current_track_idx])


def prev_track():
    global current_track_idx
    if playlist:
        current_track_idx = (current_track_idx - 1) % len(playlist)
        load_track(playlist[current_track_idx])


def toggle_loop():
    global is_looping
    is_looping = not is_looping


def draw_button(text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, active_color, rect)
    else:
        pygame.draw.rect(screen, inactive_color, rect)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    if pygame.mixer.music.get_busy() and not paused and song_length > 0:
        if not is_dragging_progress:
            current_pos = time_offset + pygame.mixer.music.get_pos()
            if current_pos >= song_length - 500:
                if is_looping:
                    load_track(music_file)
                else:
                    next_track()
    else:
        if not is_dragging_progress:
            current_pos = time_offset

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if pygame.Rect(50, 15, 420, 40).collidepoint(event.pos):
                    open_folder()

                elif pygame.Rect(vol_x - 5, vol_y, vol_w + 10, vol_h).collidepoint(event.pos):
                    is_dragging_volume = True
                    relative_y = max(0, min(event.pos[1] - vol_y, vol_h))
                    volume = 1.0 - (relative_y / vol_h)
                    pygame.mixer.music.set_volume(volume)

                elif song_length > 0 and pygame.Rect(bar_x, bar_y - 5, bar_width, bar_height + 10).collidepoint(
                        event.pos):
                    is_dragging_progress = True
                    relative_x = max(0, min(event.pos[0] - bar_x, bar_width))
                    progress_pct = relative_x / bar_width
                    current_pos = progress_pct * song_length

                elif pygame.Rect(50, 330, 100, 40).collidepoint(event.pos):
                    play_music()
                elif pygame.Rect(160, 330, 100, 40).collidepoint(event.pos):
                    pause_music()
                elif pygame.Rect(270, 330, 100, 40).collidepoint(event.pos):
                    stop_music()
                elif pygame.Rect(50, 385, 100, 40).collidepoint(event.pos):
                    prev_track()
                elif pygame.Rect(160, 385, 100, 40).collidepoint(event.pos):
                    next_track()
                elif pygame.Rect(270, 385, 100, 40).collidepoint(event.pos):
                    toggle_loop()

                elif pygame.Rect(500, 15, 230, 290).collidepoint(event.pos):
                    for i in range(min(10, len(playlist) - scroll_offset)):
                        item_rect = pygame.Rect(500, 15 + i * 29, 230, 29)
                        if item_rect.collidepoint(event.pos):
                            current_track_idx = scroll_offset + i
                            load_track(playlist[current_track_idx])
                            break

            elif event.button == 4:
                if pygame.Rect(500, 15, 230, 290).collidepoint(mouse_pos):
                    scroll_offset = max(0, scroll_offset - 1)
            elif event.button == 5:
                if pygame.Rect(500, 15, 230, 290).collidepoint(mouse_pos):
                    if scroll_offset < len(playlist) - 10:
                        scroll_offset += 1

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if is_dragging_volume:
                    is_dragging_volume = False
                if is_dragging_progress:
                    is_dragging_progress = False
                    time_offset = current_pos
                    pygame.mixer.music.play(start=time_offset / 1000)
                    if paused:
                        pygame.mixer.music.pause()

        elif event.type == pygame.MOUSEMOTION:
            if is_dragging_volume:
                relative_y = max(0, min(event.pos[1] - vol_y, vol_h))
                volume = 1.0 - (relative_y / vol_h)
                pygame.mixer.music.set_volume(volume)

            if is_dragging_progress and song_length > 0:
                relative_x = max(0, min(event.pos[0] - bar_x, bar_width))
                progress_pct = relative_x / bar_width
                current_pos = progress_pct * song_length

    progress = current_pos / song_length if song_length > 0 else 0

    draw_button("Открыть папку с музыкой", 50, 15, 420, 40, LIGHT_GRAY, GRAY)

    if playlist:
        count_text = font_small.render(f"Трек {current_track_idx + 1} из {len(playlist)}", True, DARK_GRAY)
        screen.blit(count_text, (50, 70))

    if music_file:
        clean_name = os.path.basename(music_file)
        if len(clean_name) > 40:
            clean_name = clean_name[:37] + "..."
        track_title = font.render(f"Играет: {clean_name}", True, BLACK)
        screen.blit(track_title, (50, 100))

    pygame.draw.rect(screen, LIGHT_GRAY, (500, 15, 230, 290))
    pygame.draw.rect(screen, GRAY, (500, 15, 230, 290), 1)

    for i in range(min(10, len(playlist) - scroll_offset)):
        idx = scroll_offset + i
        item_rect = pygame.Rect(500, 15 + i * 29, 230, 29)

        if idx == current_track_idx:
            pygame.draw.rect(screen, ORANGE, item_rect)
            text_color = WHITE
        else:
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, GRAY, item_rect)
            text_color = BLACK

        short_name = os.path.basename(playlist[idx])
        if len(short_name) > 24:
            short_name = short_name[:21] + "..."
        list_text = font_small.render(f"{idx + 1}. {short_name}", True, text_color)
        screen.blit(list_text, (505, 20 + i * 29))

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, ORANGE, (bar_x, bar_y, bar_width * min(progress, 1), bar_height))

    handle_x = bar_x + int(bar_width * min(progress, 1))
    pygame.draw.circle(screen, BLACK, (handle_x, bar_y + bar_height // 2), bar_height // 2 + 2)

    time_text = font.render(
        f"{int(current_pos / 1000)}s / {int(song_length / 1000)}s",
        True,
        BLACK
    )
    screen.blit(time_text, (bar_x, bar_y + 25))

    draw_button("Play", 50, 330, 100, 40, GRAY, GREEN)
    draw_button("Pause", 160, 330, 100, 40, GRAY, ORANGE)
    draw_button("Stop", 270, 330, 100, 40, GRAY, RED)

    draw_button("Prev", 50, 385, 100, 40, GRAY, LIGHT_GRAY)
    draw_button("Next", 160, 385, 100, 40, GRAY, LIGHT_GRAY)

    loop_color = ORANGE if is_looping else GRAY
    draw_button("Loop", 270, 385, 100, 40, loop_color, LIGHT_GRAY)
    pygame.draw.rect(screen, DARK_GRAY, (vol_x, vol_y, vol_w, vol_h))
    current_vol_h = int(vol_h * volume)
    current_vol_y = vol_y + (vol_h - current_vol_h)
    pygame.draw.rect(screen, ORANGE, (vol_x, current_vol_y, vol_w, current_vol_h))
    pygame.draw.rect(screen, BLACK, (vol_x, vol_y, vol_w, vol_h), 1)
    pygame.display.flip()

    clock.tick(30)

pygame.quit()

