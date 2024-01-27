import dearpygui.dearpygui as dpg
import ntpath
import json
from mutagen.wave import WAVE
from tkinter import Tk, filedialog
import threading
import pygame
import time
import random
import os
import atexit
from music import Music
from moises import Moises as moises

dpg.create_context()
dpg.create_viewport(title="Rhythm Player",
                    large_icon="icon.ico", small_icon="icon.ico")
pygame.mixer.init()
global state
state = None

global no
no = 0

global sound
sound = None

global audio
audio = None

_DEFAULT_MUSIC_VOLUME = 0.5
pygame.mixer.music.set_volume(0.5)


def update_volume(sender, app_data):  # altera o volume da musica
    pygame.mixer.music.set_volume(app_data / 100.0)

# Carrega os arquivos de som


def load_database():

    songs = json.load(open("data/paths.json", "r+"))
    print(songs)
    if len(songs) != 0:
        for musica, faixas in songs.items():

            user = Music(musica, faixas[0], faixas[1])

            dpg.add_button(label=f"{ntpath.basename(musica)}", callback=play, width=-1,
                           height=25, user_data=user, parent="list")

            dpg.add_spacer(height=2, parent="list")

# Toca a musica (instrumental)


def play_instr(file_path, volume):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

# Toca a parte vocal da música


def play_vocal(file_path, volume):

    global sound

    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    sound.play()
    return sound

# Atualiza a base de dados


def update_database(filename: str):
    data = json.load(open("data/paths.json", "r+"))
    if filename not in data.keys():
        data["songs"] += [filename]
    json.dump(data, open("data/songs.json", "r+"), indent=4)


def update_database_separados(dic, filename: str):
    # # # Acessar o primeiro endereço de arquivo
    # primeiro_endereco = dic[0]
    # # # Acessar o segundo endereço de arquivo
    # segundo_endereco = dic[1]

    # data = json.load(open("data/paths.json", "r+"))
    # if primeiro_endereco not in data["paths"]:
    #     data["paths"] += [primeiro_endereco]
    # if segundo_endereco not in data["paths"]:
    #     data["paths"] += [segundo_endereco]
    # json.dump(data, open("data/paths.json", "r+"), indent=4)

    # # Acessar o primeiro endereço de arquivo
    primeiro_endereco = dic[0]
    # # Acessar o segundo endereço de arquivo
    segundo_endereco = dic[1]

    data = json.load(open("data/paths.json", "r+"))

    # Cria um novo array
    novos_enderecos = []
    novos_enderecos.append(primeiro_endereco)
    novos_enderecos.append(segundo_endereco)

    # Adiciona o novo array ao JSON
    data[filename] = novos_enderecos

    json.dump(data, open("data/paths.json", "r+"), indent=4)


# Atualiza o controle deslizante de posição


def update_slider():
    global state, audio
    while pygame.mixer.music.get_busy() or state != 'paused':
        print(f'{pygame.mixer.music.get_pos()/1000} - {audio.info.length}')
        #print(type(pygame.mixer.music.get_pos()/1000))
        #print(type(audio.info.length))
        if (pygame.mixer.music.get_pos()/1000 >= (audio.info.length)-2.1):
            next_()
        dpg.configure_item(
            item="pos", default_value=pygame.mixer.music.get_pos()/1000)
        time.sleep(0.7)
    state = None
    dpg.configure_item("cstate", default_value=f"State: None")
    dpg.configure_item("csong", default_value="Now Playing : ")
    dpg.configure_item("play", label="Play")
    dpg.configure_item(item="pos", max_value=100)
    dpg.configure_item(item="pos", default_value=0)

# Reproduz a música

def play(sender, app_data, user_data):

    global state, no, sound, audio

    if user_data:
        if sound != None:
            sound.stop()
        # Tocando música - instrumental
        play_instr(user_data.instrumental, 1.0)

        # Tocando vocal
        vocal = play_vocal(user_data.vocal, 0.1)

        no = user_data

        audio = WAVE(user_data.instrumental)

        dpg.configure_item(item="pos", max_value=audio.info.length)

        thread = threading.Thread(target=update_slider, daemon=False).start()
        if pygame.mixer.music.get_busy():
            dpg.configure_item("play", label="Pause")
            state = "playing"
            dpg.configure_item("cstate", default_value=f"State: Playing")
            dpg.configure_item(
                "csong", default_value=f"Now Playing : {ntpath.basename(user_data.musica)}")

        return vocal

# Controla o play/pause
def play_pause():

    global state, no, sound

    if state == "playing":
        state = "paused"
        pygame.mixer.music.pause()
        sound.stop()
        dpg.configure_item("play", label="Play")
        dpg.configure_item("cstate", default_value=f"State: Paused")

    elif state == "paused":
        state = "playing"
        pygame.mixer.music.unpause()
        dpg.configure_item("play", label="Pause")
        dpg.configure_item("cstate", default_value=f"State: Playing")

    else:
        song = json.load(open("data/paths.json", "r"))

        key = list(song.keys())[0]

        if song:
            song = Music(key, song[key][0], song[key][1])
            print(song)
            no = song
            play(sender=any, app_data=any, user_data=song)

# Reproduz a música anterior
def pre():
    global state, no
    songs = json.load(open('data/paths.json', 'r'))
    try:
        n = songs.index(no)
        if n == 0:
            n = len(songs)
        print("1111111111111111111111111111111111111111")
        print(songs[n])
        print("11111111111111111111111111111111111111")
        play(sender=any, app_data=any, user_data=songs[n-1])
    except:
        pass

# Reproduz a próxima música


def next_():
    global state, no
    try:
        songs = json.load(open('data/paths.json', 'r'))
        chaves = list(songs.keys())
        n = chaves.index(no.musica)
        if n == len(chaves)-1:
            n = -1
        tocar = Music(chaves[n+1], songs[chaves[n+1]][0], songs[chaves[n+1]][1])
        play(sender=any, app_data=any, user_data=tocar)
    except:
        pass

# Pausa a reprodução


def stop():
    global state, sound
    pygame.mixer.music.stop()
    sound.stop()
    state = None

# Adiciona arquivos na reprodução
def add_files():
    data = json.load(open("data/paths.json", "r"))
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        filetypes=[("Music Files", ("*.mp3", "*.wav", "*.ogg"))])
    root.quit()
    if filename.endswith(".mp3" or ".wav" or ".ogg"):
        if ntpath.basename(filename) not in data.keys():
            ms = moises("29d82159-f9ac-4dc3-bcba-eef866e5a00e")
            dic_musica = ms.separa_vocal(filename)
            musica_adicionada = Music(ntpath.basename(filename), dic_musica[0], dic_musica[1])
            # update_database(filename)
            update_database_separados(dic_musica, ntpath.basename(filename))
            dpg.add_button(label=f"{ntpath.basename(filename)}", callback=play, width=-1,
                           height=25, user_data=musica_adicionada, parent="list")
            dpg.add_spacer(height=2, parent="list")
    # load_database()


def add_folder():
    data = json.load(open("data/paths.json", "r"))
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory()
    root.quit()
    for filename in os.listdir(folder):
        if filename.endswith(".mp3" or ".wav" or ".ogg"):
            if ntpath.basename(filename) not in data.keys():
                ms = moises("29d82159-f9ac-4dc3-bcba-eef866e5a00e")
                dic_musica = ms.separa_vocal(os.path.join(
                    folder, filename).replace("\\", "/"))
                musica_adicionada = Music(ntpath.basename(filename), dic_musica[0], dic_musica[1])
                # update_database(os.path.join(
                # folder, filename).replace("\\", "/"))
                update_database_separados(
                    dic_musica, ntpath.basename(filename))
                dpg.add_button(label=f"{ntpath.basename(filename)}", callback=play, width=-1, height=25,
                               user_data=musica_adicionada, parent="list")
                dpg.add_spacer(height=2, parent="list")
    # load_database()

# Procura por uma música específica


def search(sender, app_data, user_data):
    songs = json.load(open("data/paths.json", "r"))
    dpg.delete_item("list", children_only=True)
    for index, song in enumerate(songs):
        if app_data in song.lower():
            dpg.add_button(label=f"{ntpath.basename(song)}", callback=play,
                           width=-1, height=25, user_data=song, parent="list")
            dpg.add_spacer(height=2, parent="list")

# Remove todas as músicas


def removeall():
    songs = json.load(open("data/paths.json", "r"))
    songs.clear()
    json.dump(songs, open("data/paths.json", "w"), indent=4)
    dpg.delete_item("list", children_only=True)
    load_database()


# Iniciando interface gráfica
with dpg.theme(tag="base"):
    with dpg.theme_component():
        dpg.add_theme_color(dpg.mvThemeCol_Button, (130, 142, 250))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (137, 142, 255, 95))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (137, 142, 255))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4, 4)
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.50, 0.50)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 14)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (25, 25, 25))
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (130, 142, 250))
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (221, 166, 185))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (172, 174, 197))

with dpg.theme(tag="slider_thin"):
    with dpg.theme_component():
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250, 99))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250, 99))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250, 99))
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.theme(tag="slider"):
    with dpg.theme_component():
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250, 99))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250, 99))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250, 99))
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.theme(tag="songs"):
    with dpg.theme_component():
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (89, 89, 144, 40))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))

with dpg.font_registry():
    monobold = dpg.add_font("fonts/MonoLisa-Bold.ttf", 12)
    head = dpg.add_font("fonts/MonoLisa-Bold.ttf", 15)

# Iniciando janela principal
with dpg.window(tag="main", label="window title"):
    with dpg.child_window(autosize_x=True, height=45, no_scrollbar=True):
        dpg.add_text(f"Now Playing : ", tag="csong")
    dpg.add_spacer(height=2)

    # Adicionando conteúdo na barra lateral
    with dpg.group(horizontal=True):
        with dpg.child_window(width=200, tag="sidebar"):
            dpg.add_text("Rainy Musicart", color=(137, 142, 255))
            dpg.add_text("Build by NotCookey")
            dpg.add_spacer(height=2)
            dpg.add_button(label="Support", width=-1, height=23,
                           callback=lambda: webbrowser.open(url="https://github.com/NotCookey/Rainy"))
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_button(label="Add File", width=-1,
                           height=28, callback=add_files)
            dpg.add_button(label="Add Folder", width=-1,
                           height=28, callback=add_folder)
            dpg.add_button(label="Remove All Songs", width=-
                           1, height=28, callback=removeall)
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text(f"State: {state}", tag="cstate")
            dpg.add_spacer(height=5)
            dpg.add_separator()

        # Adiciona controle de reprodução e sliders
        with dpg.child_window(autosize_x=True, border=False):
            with dpg.child_window(autosize_x=True, height=80, no_scrollbar=True):
                with dpg.group(horizontal=True):
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Play", width=65,
                                       height=30, tag="play", callback=play_pause)
                        dpg.add_button(label="Pre", width=65, height=30,
                                       show=True, tag="pre", callback=pre)
                        dpg.add_button(
                            label="Next", tag="next", show=True, callback=next_, width=65, height=30)
                        dpg.add_button(
                            label="Stop", callback=stop, width=65, height=30)
                    dpg.add_slider_float(tag="volume", width=120, height=15, pos=(
                        10, 59), format="%.0f%.0%", default_value=_DEFAULT_MUSIC_VOLUME * 100, callback=update_volume)
                    dpg.add_slider_float(
                        tag="pos", width=-1, pos=(140, 59), format="")

            # Adiciona janela para pesquisa e lista de músicas
            with dpg.child_window(autosize_x=True, delay_search=True):
                with dpg.group(horizontal=True, tag="query"):
                    dpg.add_input_text(
                        hint="Search for a song", width=-1, callback=search)
                dpg.add_spacer(height=5)
                with dpg.child_window(autosize_x=True, delay_search=True, tag="list"):
                    load_database()

    dpg.bind_item_theme("volume", "slider_thin")
    dpg.bind_item_theme("pos", "slider")
    dpg.bind_item_theme("list", "songs")

dpg.bind_theme("base")
dpg.bind_font(monobold)


def safe_exit():
    pygame.mixer.music.stop()
    pygame.quit()


atexit.register(safe_exit)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
