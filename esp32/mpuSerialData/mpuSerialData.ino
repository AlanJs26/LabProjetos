#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu1(0x68);  // Primeiro MPU6050 (AD0 em GND)
MPU6050 mpu2(0x69);  // Segundo MPU6050 (AD0 em VCC)

void setup() {
    Serial.begin(115200);
    Wire.begin(21, 22);  // Configura I2C no ESP32

    // Inicializa o primeiro MPU-6050
    mpu1.initialize();
    if (!mpu1.testConnection()) {
        Serial.println("Erro ao conectar no MPU6050 #1");
        while (1);
    }

    // Inicializa o segundo MPU-6050
    mpu2.initialize();
    if (!mpu2.testConnection()) {
        Serial.println("Erro ao conectar no MPU6050 #2");
        while (1);
    }

    // Serial.println("Dois MPU6050 conectados!");

    // Cabeçalho do CSV
    // Serial.println("timestamp,ax1,ay1,az1,gx1,gy1,gz1,ax2,ay2,az2,gx2,gy2,gz2");
}

void loop() {
    int16_t ax1, ay1, az1, gx1, gy1, gz1;
    int16_t ax2, ay2, az2, gx2, gy2, gz2;

    // Obtém dados do MPU6050 #1
    mpu1.getAcceleration(&ax1, &ay1, &az1);
    mpu1.getRotation(&gx1, &gy1, &gz1);

    // Obtém dados do MPU6050 #2
    mpu2.getAcceleration(&ax2, &ay2, &az2);
    mpu2.getRotation(&gx2, &gy2, &gz2);

    // Converte os valores para unidades físicas
    float acel_x1 = ax1 / 16384.0;
    float acel_y1 = ay1 / 16384.0;
    float acel_z1 = az1 / 16384.0;
    float giro_x1 = gx1 / 131.0;
    float giro_y1 = gy1 / 131.0;
    float giro_z1 = gz1 / 131.0;

    float acel_x2 = ax2 / 16384.0;
    float acel_y2 = ay2 / 16384.0;
    float acel_z2 = az2 / 16384.0;
    float giro_x2 = gx2 / 131.0;
    float giro_y2 = gy2 / 131.0;
    float giro_z2 = gz2 / 131.0;

    // Obtém o tempo atual (em milissegundos)
    unsigned long timestamp = millis();

    // Print no formato CSV
    Serial.print(acel_x1, 2); Serial.print(",");
    Serial.print(acel_y1, 2); Serial.print(",");
    Serial.print(acel_z1, 2); Serial.print(",");
    Serial.print(giro_x1, 2); Serial.print(",");
    Serial.print(giro_y1, 2); Serial.print(",");
    Serial.print(giro_z1, 2); Serial.print(",");
    Serial.print(acel_x2, 2); Serial.print(",");
    Serial.print(acel_y2, 2); Serial.print(",");
    Serial.print(acel_z2, 2); Serial.print(",");
    Serial.print(giro_x2, 2); Serial.print(",");
    Serial.print(giro_y2, 2); Serial.print(",");
    Serial.println(giro_z2, 2);

    delay(10);  // Coleta dados a cada 500ms
}
