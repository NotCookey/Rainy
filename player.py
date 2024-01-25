import pygame
import time

def play_music(file_path, volume):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

def play_sound(file_path, volume):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    return sound.play()

# Caminhos para as faixas de áudio
faixa1_path = "/home/luiz/Cod/RhythmPlayer-/out/song.mp3/vocal.wav"
faixa2_path = "/home/luiz/Cod/RhythmPlayer-/out/song.mp3/instr.wav"

# Volumes iniciais
volume_faixa1 = 0.8
volume_faixa2 = 0.8

# Reproduza as faixas de áudio independentes
play_music(faixa1_path, volume_faixa1)
sound = play_sound(faixa2_path, volume_faixa2)

try:
    while pygame.mixer.music.get_busy():
        # Altere o volume dinamicamente (exemplo: a cada 5 segundos)
        time.sleep(5)
        volume_faixa1 = float(input("Novo volume para a faixa 1 (0.0 a 1.0): "))
        volume_faixa2 = float(input("Novo volume para a faixa 2 (0.0 a 1.0): "))

        pygame.mixer.music.set_volume(volume_faixa1)
        sound.set_volume(volume_faixa2)

except KeyboardInterrupt:
    pygame.mixer.music.stop()
    pygame.quit()
