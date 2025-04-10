# 🥋 LabProjetos - Sistema de Detecção de Movimentos de Judô

Este projeto é um sistema de detecção e classificação de movimentos e eventos em lutas de judô utilizando sensores MPU (Motion Processing Unit) conectados a um ESP32, com processamento de dados em Python.

## 🌟 Funcionalidades

- Coleta de dados de movimento usando ESP32 e sensores MPU
- Transmissão de dados via serial para processamento
- Classificação de eventos de judô em tempo real, incluindo:
  - 🔴 Ippon (pontuação completa)
  - ⏸️ Matte (pausa)
  - 🟠 Wazari (meio ponto)
  - 🔢 ScoreChange (alteração na pontuação)
  - 🟨 Shido (penalidade)
  - 🔄 Toketa (continuar após imobilização)
- Treinamento de modelo de aprendizado de máquina com datasets personalizados
- Teste de modelos com conjuntos de dados separados

## 🛠️ Requisitos

### Hardware
- ESP32 (pode ser qualquer outro microcontrolador)
- Sensores MPU (MPU6050 ou similar)
- Cabos USB para comunicação serial
- Bateria ou fonte de alimentação para o ESP32 (para uso portátil)

### Software
- Python 3.6+
- Arduino IDE ou PlatformIO (para programar o ESP32)
- Bibliotecas Python
  - numpy
  - pandas
  - tensorflow/keras
  - pyserial
  - matplotlib (para visualizações)

## 📂 Estrutura do Projeto

- `/config` - Arquivos de configuração do projeto
- `/dataset` - Conjuntos de dados para treinamento e teste
- `/esp32` - Código para o microcontrolador ESP32
  - `/mpuSerialData` - Programa para leitura e envio de dados do MPU
- `/models` - Modelos treinados e scripts de treinamento
- `/src` - Código-fonte principal em Python

## ⚙️ Configuração

O sistema usa um arquivo de configuração localizado em `config/params.yaml` que define:

- `timesteps`: Número de elementos de dados para alimentar o modelo de uma vez (50 por padrão)
- `train_data`: Conjuntos de dados para treinar o modelo, separados por classe
- `test_data`: Conjuntos de dados para testar o modelo, separados por classe
- `classes`: Lista de classes para detecção (Ippon, Matte, Wazari, ScoreChange, Shido, Toketa)

Você pode modificar estes parâmetros de acordo com suas necessidades específicas.

## 🚀 Como Executar

Clone o repositório:

```bash
git clone https://github.com/AlanJs26/LabProjetos.git
cd LabProjetos
```

### Configurando o ESP32

1. Conecte os dois sensores MPU ao ESP32 usando as seguintes conexões:
   - VCC do MPU ao 3.3V do ESP32
   - GND do MPU ao GND do ESP32
   - SDA do MPU ao pino SDA do ESP32 (geralmente GPIO21)
   - SCL do MPU ao pino SCL do ESP32 (geralmente GPIO22)

> A ligação do segundo sensor é exatamente igual, porém com a diferença que o pino A0 em um dos sensores precisa estar no 3.3V e no outro GND

2. Instale a Arduino IDE e configure-a para o ESP32:
   - Adicione o URL do gerenciador de placas ESP32 nas preferências
   - Instale a placa ESP32 pelo gerenciador de placas
   - Selecione seu modelo de ESP32

3. Abra o código em `esp32/mpuSerialData` na Arduino IDE

4. Instale as bibliotecas necessárias:
   - `Wire.h` (padrão da Arduino IDE)
   - `MPU6050.h` ou biblioteca equivalente para seu sensor

5. Compile e faça upload do código para o ESP32

6. Verifique se o ESP32 está transmitindo dados via serial (use o Monitor Serial da Arduino IDE para testar)

### Executando o Código Python

Recomento fortemente utilizar o gerenciador de pacotes python [uv](https://github.com/astral-sh/uv). Ele gerencia automaticamente a versão do python e dos módulos necessários. 

1. Captura dos dados de treino

```bash
uv run main.py captura [nome_do_movimento] --com [porta_COM] --baudrate 115200
```

2. Treinando o modelo

```bash
uv run main.py train
```

3. Testando o modelo

```bash
uv run main.py metrics
```

4. Web App para detecção em tempo real

```bash
uv run main.py web
```

5. Outros comandos

```bash
uv run main.py --help
```

## 📝 Notas Adicionais

- Certifique-se de que o ESP32 está conectado corretamente antes de executar o código Python
- Você pode ajustar os parâmetros no arquivo config/params.yaml para melhorar a precisão da detecção
- Os dados brutos são armazenados na pasta dataset e podem ser utilizados para treinar modelos personalizados

## 📜 Licença

Este projeto está sob a licença MIT.

