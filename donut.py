import sys
import math
import time
import pygame
import serial
import serial.tools.list_ports

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arduino Donut")
clock = pygame.time.Clock()

FONT_SIZE = 14
font = pygame.font.SysFont("Courier New", FONT_SIZE, bold=True)

A, B = 0.0, 0.0

def draw_donut():
    global A, B
    chars = ".,-~:;=!*#$@"
    output = [[" " for _ in range(80)] for _ in range(22)]
    zbuffer = [[0.0 for _ in range(80)] for _ in range(22)]
    
    j = 0.0
    while j < 6.28:
        j += 0.07
        i = 0.0
        while i < 6.28:
            i += 0.02
            
            sin_i, cos_i = math.sin(i), math.cos(i)
            sin_j, cos_j = math.sin(j), math.cos(j)
            sin_A, cos_A = math.sin(A), math.cos(A)
            sin_B, cos_B = math.sin(B), math.cos(B)
            
            h = cos_j + 2
            D = 1 / (sin_i * h * sin_A + sin_j * cos_A + 5)
            t = sin_i * h * cos_A - sin_j * sin_A
            
            x = int(40 + 30 * D * (cos_i * h * cos_B - t * sin_B))
            y = int(11 + 15 * D * (cos_i * h * sin_B + t * cos_B))
            
            L = int(8 * ((sin_j * sin_A - sin_i * cos_j * cos_A) * cos_B - sin_i * cos_j * sin_A - sin_j * cos_A - cos_i * cos_j * sin_B))
            
            if 0 <= y < 22 and 0 <= x < 80:
                if D > zbuffer[y][x]:
                    zbuffer[y][x] = D
                    output[y][x] = chars[L if L > 0 else 0]
    
    screen.fill((0, 0, 0))
    for row_idx, row in enumerate(output):
        line_text = "".join(row)
        text_surface = font.render(line_text, True, (0, 255, 0))
        screen.blit(text_surface, (WIDTH // 2 - 280, HEIGHT // 2 - 150 + row_idx * (FONT_SIZE - 2)))
        
    A += 0.05
    B += 0.03

def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Bluetooth" in port.description or "Блютуз" in port.description:
            continue
        try:
            ser = serial.Serial(port.device, 9600, timeout=0.5)
            time.sleep(0.1)
            ser.reset_input_buffer()
            
            for _ in range(5):
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "ARDUINO_READY" in line:
                    ser.close()
                    return port.device
            ser.close()
        except (serial.SerialException, PermissionError):
            continue
    return None

def main():
    arduino_port = None
    ser = None
    running = True
    
    while running and not arduino_port:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        screen.fill((20, 20, 20))
        wait_text = font.render("ПОДКЛЮЧИТЕ ARDUINO UNO К USB ПОРТУ...", True, (255, 50, 50))
        screen.blit(wait_text, (WIDTH // 2 - 200, HEIGHT // 2))
        pygame.display.flip()
        
        arduino_port = find_arduino()
        time.sleep(0.5)
        
    ser = serial.Serial(arduino_port, 9600, timeout=1)
    
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        try:
            if ser.in_waiting >= 0:
                ser.reset_input_buffer()
                draw_donut()
        except Exception:
            running = False
            
        pygame.display.flip()
        
    if ser:
        ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()

