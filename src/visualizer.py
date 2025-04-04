import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

def visualizar_realtime(caminho_csv):
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_csv):
        print("❌ Arquivo CSV não encontrado!")
        return

    # Cria a figura com 2x2 subplots
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    plt.suptitle("Visualização em Tempo Real - Dados do MPU6050", fontsize=18)

    # Janela de tempo para visualização (em segundos)
    MAX_TEMPO = 10

    def atualizar(frame):
        try:
            df = pd.read_csv(caminho_csv)
        except Exception as e:
            print("Erro ao ler CSV:", e)
            return

        # Verifica se o DataFrame contém os dados necessários
        if "timestamp" not in df.columns or "em_movimento" not in df.columns:
            return

        # Cria uma coluna de tempo relativo (em segundos)
        df["tempo"] = df["timestamp"] - df["timestamp"].iloc[0]

        # Filtra os dados para os últimos MAX_TEMPO segundos
        tempo_max = df["tempo"].max()
        df_filtrado = df[df["tempo"] >= tempo_max - MAX_TEMPO]

        # Limpa todos os subplots
        for ax in axs.flat:
            ax.cla()

        # Função para plotar um sensor e sobrepor as faixas de movimento
        def plot_sensor(ax, tempo, dados, titulo, ylabel):
            ax.plot(tempo, dados, label=titulo, color="blue")
            ax.set_title(titulo)
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel(ylabel)
            # Sobrepõe as faixas onde em_movimento==1
            movimento = df_filtrado["em_movimento"].values
            tempo_array = df_filtrado["tempo"].values
            start = None
            for i, val in enumerate(movimento):
                if val == 1 and start is None:
                    start = tempo_array[i]
                elif val == 0 and start is not None:
                    ax.axvspan(start, tempo_array[i], color="red", alpha=0.15)
                    start = None
            # Caso o último intervalo esteja aberto
            if start is not None:
                ax.axvspan(start, tempo_array[-1], color="red", alpha=0.15)
            ax.legend()

        # Exemplo de plots:
        # Aceleração MPU1 (ax1)
        plot_sensor(axs[0, 0], df_filtrado["tempo"], df_filtrado["ax1"],
                    "Aceleração MPU1 (ax1)", "Aceleração (g)")

        # Giroscópio MPU1 (gx1)
        plot_sensor(axs[0, 1], df_filtrado["tempo"], df_filtrado["gx1"],
                    "Giroscópio MPU1 (gx1)", "Vel. Angular (°/s)")

        # Aceleração MPU2 (ax2)
        plot_sensor(axs[1, 0], df_filtrado["tempo"], df_filtrado["ax2"],
                    "Aceleração MPU2 (ax2)", "Aceleração (g)")

        # Giroscópio MPU2 (gx2)
        plot_sensor(axs[1, 1], df_filtrado["tempo"], df_filtrado["gx2"],
                    "Giroscópio MPU2 (gx2)", "Vel. Angular (°/s)")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Atualiza a cada 500 ms
    ani = FuncAnimation(fig, atualizar, interval=200)
    plt.show()

import sys
if __name__ == "__main__":

    caminho = sys.argv[1].strip()
    
    # caminho = input("Caminho do arquivo CSV: ").strip()
    visualizar_realtime('dataset/'+caminho+'.csv')
