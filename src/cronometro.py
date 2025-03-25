import pygame
from datetime import datetime
import sys
import csv
import os


def cronometro():
    titulo = input("Nome do Movimento: ")
    os.makedirs("timestamps", exist_ok=True)
    arquivo = f"./timestamps/{titulo.casefold().replace(' ', '_')}.csv"

    while os.path.isfile(arquivo):
        arquivo = os.path.splitext(arquivo)[0] + "-novo.csv"

    print(f"Caminho do arquivo: {arquivo}")

    # Inicializa o pygame
    pygame.init()

    # Cria a tela do jogo
    WIDTH = HEIGHT = 300
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Indicador de Movimento")

    font = pygame.font.SysFont("Comic Sans MS", 60)

    # Abre o arquivo para escrita e adiciona cabeçalho se necessário
    with open(arquivo, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "Movimento"])

    counter = 0
    # Loop principal
    en_movimento = False
    start_time = 0
    while True:
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.unicode == "q"
            ):
                pygame.quit()
                sys.exit()
            if (
                event.type == pygame.KEYDOWN or event.type == pygame.KEYUP
            ) and event.unicode != " ":
                continue

            timestamp = datetime.now().timestamp()  # Obtém o timestamp em UTC

            if event.type == pygame.KEYDOWN and not en_movimento:
                display.fill((0, 255, 0))
                en_movimento = True

                start_time = timestamp
            elif event.type == pygame.KEYUP and en_movimento:
                display.fill((255, 0, 0))
                en_movimento = False
                counter += 1

                # Salva no arquivo CSV
                with open(arquivo, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([start_time, timestamp])

                    strtime_start = datetime.fromtimestamp(start_time).strftime(
                        "%H:%M:%S.%f"
                    )
                    strtime_end = datetime.fromtimestamp(timestamp).strftime(
                        "%H:%M:%S.%f"
                    )
                    print(f"{strtime_start} to {strtime_end} - N: {counter}")

                text_surface = font.render(str(counter), False, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
                display.blit(text_surface, text_rect)

        # Atualiza a tela
        pygame.display.flip()
