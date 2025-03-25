import pygame
import sys
import time
import csv

# Inicializa o pygame
pygame.init()

# Cria a tela do jogo
display = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Indicador de Movimento")

titulo = input("Nome do Movimento: ")

# Nome do arquivo CSV
arquivo = f"{titulo}.csv"

# Abre o arquivo para escrita e adiciona cabeçalho se necessário
with open(arquivo, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "Movimento"])

counter = 0
# Loop principal
en_movimento = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN and event.unicode == ' ' and not en_movimento:
            timestamp = int(time.time())  # Obtém o timestamp em UTC
            movimento = "Start"
            en_movimento = True
            
            # Salva no arquivo CSV
            with open(arquivo, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, movimento])
            
            print(f"{timestamp}, {movimento}")
        
        if event.type == pygame.KEYUP and event.unicode == ' ' and en_movimento:
            timestamp = int(time.time())  # Obtém o timestamp em UTC
            movimento = "Stop"
            en_movimento = False
            
            # Salva no arquivo CSV
            with open(arquivo, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, movimento])
            
            counter += 1
            print(f"{timestamp}, {movimento} - N: {counter}")
    
    # Define a cor com base no estado do movimento
    cor = (0, 255, 0) if en_movimento else (255, 0, 0)  # Verde para Start, Vermelho para Stop
    
    # Preenche a tela com a cor correspondente
    display.fill(cor)
    
    # Atualiza a tela
    pygame.display.flip()
