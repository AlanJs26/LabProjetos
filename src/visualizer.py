import matplotlib.pyplot as plt
from collections import deque
import matplotlib.patches as patches
from matplotlib.widgets import SpanSelector
import numpy as np


def visualizar_dataframe(df, janela_tempo=None):
    """
    Visualiza dados de um DataFrame com histórico completo.

    Parâmetros:
    df - DataFrame com colunas: timestamp, ax1, ay1, az1, gx1, gy1, gz1,
                               ax2, ay2, az2, gx2, gy2, gz2, em_movimento
    janela_tempo - opcional: tempo total a ser mostrado no eixo X (segundos)
    """

    fig, (ax_accel, ax_gyro) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    fig.suptitle("Visualização Completa dos Dados", fontsize=18)

    # Configura tempo relativo
    tempo = df["timestamp"] - df["timestamp"].iloc[0]

    # Plota dados de aceleração
    ax_accel.plot(tempo, df["ax1"], label="AX1", color="blue", alpha=0.7)
    ax_accel.plot(tempo, df["ay1"], label="AY1", color="green", alpha=0.7)
    ax_accel.plot(tempo, df["az1"], label="AZ1", color="red", alpha=0.7)
    ax_accel.plot(
        tempo, df["ax2"], label="AX2", color="navy", linestyle="--", alpha=0.7
    )
    ax_accel.plot(
        tempo, df["ay2"], label="AY2", color="darkgreen", linestyle="--", alpha=0.7
    )
    ax_accel.plot(
        tempo, df["az2"], label="AZ2", color="darkred", linestyle="--", alpha=0.7
    )
    ax_accel.set_ylabel("Aceleração (g)")
    ax_accel.legend(loc="upper right", ncol=3)
    ax_accel.grid(True)

    # Plota dados giroscópio
    ax_gyro.plot(tempo, df["gx1"], label="GX1", color="purple", alpha=0.7)
    ax_gyro.plot(tempo, df["gy1"], label="GY1", color="orange", alpha=0.7)
    ax_gyro.plot(tempo, df["gz1"], label="GZ1", color="cyan", alpha=0.7)
    ax_gyro.plot(
        tempo, df["gx2"], label="GX2", color="indigo", linestyle="--", alpha=0.7
    )
    ax_gyro.plot(
        tempo, df["gy2"], label="GY2", color="darkorange", linestyle="--", alpha=0.7
    )
    ax_gyro.plot(tempo, df["gz2"], label="GZ2", color="teal", linestyle="--", alpha=0.7)
    ax_gyro.set_xlabel("Tempo (s)")
    ax_gyro.set_ylabel("Vel. Angular (°/s)")
    ax_gyro.legend(loc="upper right", ncol=3)
    ax_gyro.grid(True)

    # Adiciona regiões de movimento
    def add_movement_spans(axes):
        mov = df["em_movimento"].to_numpy()
        changes = np.where(np.diff(mov.astype(int)))[0] + 1
        segments = np.split(df.index, changes)

        for seg in segments:
            if len(seg) == 0:
                continue
            start = tempo.iloc[seg[0]]
            end = tempo.iloc[seg[-1]]
            if mov[seg[0]] == 1:
                axes.axvspan(start, end, color="red", alpha=0.15)

    add_movement_spans(ax_accel)
    add_movement_spans(ax_gyro)

    # Configura limites do eixo X
    if janela_tempo:
        ax_accel.set_xlim(0, janela_tempo)
    else:
        ax_accel.set_xlim(tempo.min(), tempo.max())

    # Adiciona zoom interativo
    def onselect(xmin, xmax):
        ax_accel.set_xlim(xmin, xmax)
        ax_accel.figure.canvas.draw_idle()

    span = SpanSelector(
        ax_accel,
        onselect,
        "horizontal",
        useblit=True,
        props=dict(alpha=0.5, facecolor="yellow"),
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # type: ignore
    plt.show()

    return fig, (ax_accel, ax_gyro)


def visualizar_realtime(janela_tempo=2, freq=50):
    fig, ax = plt.subplots(figsize=(16, 6))
    fig.suptitle("Visualização em Tempo Real - Dados do MPU6050", fontsize=18)
    plt.ion()
    plt.show()

    buffer_size = int(janela_tempo * freq)
    buffers = {
        "tempo": deque(maxlen=buffer_size),
        "ax1": deque(maxlen=buffer_size),
        "gx1": deque(maxlen=buffer_size),
        "ax2": deque(maxlen=buffer_size),
        "gx2": deque(maxlen=buffer_size),
        "em_movimento": deque(maxlen=buffer_size),
    }

    linhas = {}
    cores = {"ax1": "blue", "gx1": "green", "ax2": "orange", "gx2": "purple"}

    for chave in ["ax1", "gx1", "ax2", "gx2"]:
        (linha,) = ax.plot([], [], label=chave, color=cores[chave])
        linhas[chave] = linha

    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Valor")
    ax.legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # type: ignore

    tempo_inicial = [None]
    parada = {"sair": False}

    def on_key(event):
        if event.key in ["escape", "q"]:
            print("Encerrando visualização...")
            parada["sair"] = True
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", on_key)

    spans = []

    def atualizar(
        timestamp, ax1, ay1, az1, gx1, gy1, gz1, ax2, ay2, az2, gx2, gy2, gz2, em_mov
    ):
        if parada["sair"]:
            return

        if tempo_inicial[0] is None:
            tempo_inicial[0] = timestamp
        tempo_relativo = timestamp - tempo_inicial[0]

        buffers["tempo"].append(tempo_relativo)
        buffers["ax1"].append(ax1)
        buffers["gx1"].append(gx1)
        buffers["ax2"].append(ax2)
        buffers["gx2"].append(gx2)
        buffers["em_movimento"].append(em_mov)

        # Atualiza as linhas
        for chave in ["ax1", "gx1", "ax2", "gx2"]:
            linhas[chave].set_data(buffers["tempo"], buffers[chave])

        ax.relim()
        ax.autoscale_view()

        # Atualiza as faixas de movimento
        for span in spans:
            span.remove()
        spans.clear()

        tempo = list(buffers["tempo"])
        mov = list(buffers["em_movimento"])
        start = None
        for i in range(len(mov)):
            if mov[i] == 1 and start is None:
                start = tempo[i]
            elif mov[i] == 0 and start is not None:
                spans.append(ax.axvspan(start, tempo[i], color="red", alpha=0.15))
                start = None
        if start is not None:
            spans.append(ax.axvspan(start, tempo[-1], color="red", alpha=0.15))

        fig.canvas.draw_idle()
        fig.canvas.flush_events()

    return atualizar, parada


if __name__ == "__main__":
    import time
    import numpy as np
    import pandas as pd

    df = pd.read_csv("dataset/teste.csv")
    visualizar_dataframe(df)

    # atualizar, parada = visualizar_realtime()
    #
    # start_time = time.time()
    #
    # try:
    #     while not parada["sair"]:
    #         t = time.time() - start_time
    #         atualizar(
    #             timestamp=t,
    #             ax1=np.sin(t),
    #             ay1=0,
    #             az1=0,
    #             gx1=np.cos(t),
    #             gy1=0,
    #             gz1=0,
    #             ax2=np.sin(t + 1),
    #             ay2=0,
    #             az2=0,
    #             gx2=np.cos(t + 1),
    #             gy2=0,
    #             gz2=0,
    #             em_mov=1 if np.sin(t * 10) > 0.5 else 0,
    #         )
    #         time.sleep(0.005)
    # except KeyboardInterrupt:
    #     print("Encerrado via teclado.")
