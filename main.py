import os
from PIL import Image
import pygame
import sys
from pygame.locals import *
from tkinter import filedialog
import socket
import time
import threading
import random
import string

from Cryptodome.Cipher import DES3
from hashlib import md5
from compression import dct_compress

# game window
width = 1280
height = 720

pygame.init()

# Set app window
screen = pygame.display.set_mode((width, height), DOUBLEBUF)
pygame.display.set_caption("FlexShare")
icon = pygame.image.load("data/images/file.png").convert_alpha()
pygame.display.set_icon(icon)

# Define variables
black = (0, 0, 0)
white = (255, 255, 255)
blue = (117, 199, 251)
red = (255, 56, 71)
grey = (200, 200, 200)
grey_2 = (150, 150, 150)
grey_3 = (50, 50, 50)
font_1 = pygame.font.SysFont('Oswald', 50)
font_2 = pygame.font.SysFont('Oswald', 35)
font_3 = pygame.font.Font('data/fonts/Caprasimo-Regular.ttf', 35)
font_4 = pygame.font.Font('data/fonts/Kanit-Bold.ttf', 50)

# Set fps
clock = pygame.time.Clock()
fps = 240

# Connection progress
connection_progress = 'not connected'

key = ""

# Define socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

compressed_time_elapsed = 0
encryption_time_elapsed = 0


def homepage():
    home_image = pygame.image.load("data/images/home.png").convert_alpha()
    home_image = pygame.transform.smoothscale(home_image,
                                              (int(width / 2), int(height / 2)))

    flexshare_logo = pygame.image.load('Data/images/flexshare.png').convert_alpha()
    flexshare_logo = pygame.transform.scale(flexshare_logo, (int(width / 2.5), int(height / 6.5)))

    send_button_rect = pygame.Rect(int((3 * width) / 12), int(height - (height / 5.7)), int(width / 6),
                                   int(height / 8.64))
    send_button_rect_copy = pygame.Rect(int((3.03 * width) / 12), int(height - (height / 5.87)), int(width / 6),
                                        int(height / 8.64))

    receive_button_rect = pygame.Rect(int((6.8 * width) / 12), int(height - (height / 5.7)), int(width / 6),
                                      int(height / 8.64))
    receive_button_rect_copy = pygame.Rect(int((6.83 * width) / 12), int(height - (height / 5.87)), int(width / 6),
                                           int(height / 8.64))

    run = True
    while run:

        # get mouse pos
        mouse_pos = pygame.mouse.get_pos()

        screen.fill(white)
        screen.blit(flexshare_logo, (width / 2 - flexshare_logo.get_width() / 2, height / 9))
        screen.blit(home_image,
                    ((width / 2) - home_image.get_width() / 2, (height / 2) - home_image.get_height() / 2.3))

        if send_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, red, send_button_rect, border_radius=int(width / 45))
            text = font_1.render("SEND", True, white)
            text_rect = text.get_rect(center=send_button_rect.center)
            screen.blit(text, text_rect)

        else:
            pygame.draw.rect(screen, grey, send_button_rect_copy, border_radius=int(width / 45))
            pygame.draw.rect(screen, blue, send_button_rect, border_radius=int(width / 45))
            text = font_1.render("SEND", True, white)
            text_rect = text.get_rect(center=send_button_rect.center)
            screen.blit(text, text_rect)

        if receive_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, red, receive_button_rect, border_radius=int(width / 45))
            text = font_1.render("RECEIVE", True, white)
            text_rect = text.get_rect(center=receive_button_rect.center)
            screen.blit(text, text_rect)

        else:
            pygame.draw.rect(screen, grey, receive_button_rect_copy, border_radius=int(width / 45))
            pygame.draw.rect(screen, blue, receive_button_rect, border_radius=int(width / 45))
            text = font_1.render("RECEIVE", True, white)
            text_rect = text.get_rect(center=receive_button_rect.center)
            screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if pygame.mouse.get_pressed()[0]:
                if send_button_rect.collidepoint(mouse_pos):
                    sender()
                if receive_button_rect.collidepoint(mouse_pos):
                    receiver()

        pygame.display.update()
        clock.tick(fps)


def sender():
    # Flex Share Logo
    flexshare_logo = pygame.image.load('Data/images/flexshare.png').convert_alpha()
    flexshare_logo = pygame.transform.scale(flexshare_logo, (int(width / 2.5), int(height / 6.5)))

    # Define boxes to type connection code
    center = width / 2
    # code box
    code_box_2 = pygame.Rect(0, 0, int(width * 0.1), int(width * 0.1))
    code_box_2.topright = (center - width * 0.01, int(height * 0.53))

    code_box_3 = pygame.Rect(0, 0, int(width * 0.1), int(width * 0.1))
    code_box_3.topleft = (center + width * 0.01, code_box_2.y)

    code_box_1 = pygame.Rect(0, code_box_2.y, int(width * 0.1), int(width * 0.1))
    code_box_1.topright = (code_box_2.topleft[0] - width * 0.02, int(height * 0.53))

    code_box_4 = pygame.Rect(0, 0, int(width * 0.1), int(width * 0.1))
    code_box_4.topleft = (code_box_3.topright[0] + width * 0.02, int(height * 0.53))

    # Define rectangle for connect button
    rect_connect = pygame.Rect(int(width / 2) - int(width / 12), int(height - (height / 5.7)), int(width / 6),
                               int(height / 8.64))
    rect_connect_copy = pygame.Rect(int(width / 2) - int(width / 12), int(height - (height / 5.87)), int(width / 6),
                                    int(height / 8.64))

    # Define rectangle for proceed button
    rect_proceed = pygame.Rect(int(width / 2) - int(width / 24), int(height - (height / 5.7)), int(width / 12),
                               int(height / 8.64))
    rect_proceed_copy = pygame.Rect(int(width / 2) - int(width / 24), int(height - (height / 5.87)), int(width / 12),
                                    int(height / 8.64))

    # Define variables
    pressed = False
    code = ""
    color_list = [grey_3, grey_3, grey_3, grey_3]
    status = 0
    filename = "Browse for a image!"
    filename_copy = filename

    # Find the code of this pc
    hostname = socket.gethostname()
    my_ip = socket.gethostbyname(hostname)
    my_ip_list = my_ip.split(".")
    my_code = my_ip_list[-1]
    l = len(my_code)
    while len(my_code) < 3:
        my_code += "0"
    my_code = str(l) + my_code

    # Define some text and rectangles
    text1 = font_3.render("Enter Receiver Code", True, red)

    # Directory icon
    dir_icon = pygame.image.load('Data/images/directory.png').convert_alpha()
    dir_icon = pygame.transform.scale(dir_icon, (int(height * 0.09), int(height * 0.09)))

    # Location box
    loc = pygame.Rect(width * 0.11, int(height * 0.5), int(width * 0.7), int(height * 0.09))
    dir_rect = dir_icon.get_rect()
    dir_rect.x = loc.midright[0] + 20
    dir_rect.y = loc.midright[1] - dir_icon.get_height() / 2

    # Send button
    f_send_rect = pygame.Rect(int(width / 2) - int(width / 12), int(height - (height / 5.7)), int(width / 6),
                              int(height / 8.64))
    f_send_rect_copy = pygame.Rect(int(width / 2) - int(width / 12), int(height - (height / 5.87)),
                                   int(width / 6),
                                   int(height / 8.64))

    # Directory text
    file_dir = font_2.render(filename_copy, True, grey_2)
    file_dir_rect = file_dir.get_rect(midleft=(loc.midleft[0] + 15, loc.midleft[1]))

    # Create rectangle for the text
    text1_rect = text1.get_rect(
        midbottom=((code_box_2.midtop[0] + code_box_3.midtop[0]) // 2, code_box_2.midtop[1] - 60))

    waiting_text = font_3.render("Waiting for Connection...", True, red)
    established_text = font_3.render("Connection Established", True, red)
    compressing_text = font_3.render("Compressing...", True, blue)

    # Define function for encryption
    def encryption(image_data):
        characters = string.ascii_letters + string.digits
        key = ''.join(random.choice(characters) for _ in range(8))
        key = key.upper()

        key_hash = md5(key.encode('ascii')).digest()
        tdes_key = DES3.adjust_key_parity(key_hash)
        cipher = DES3.new(tdes_key, DES3.MODE_EAX, nonce=b'0')

        new_image_data = cipher.encrypt(image_data)

        return new_image_data, key

    # Define function of establishing connection between two pc's
    def connect2pc(code, my_ip):
        my_ip_list = my_ip.split(".")

        len_receiver = code[0]
        code = code[1:1 + int(len_receiver)]

        other_ip_list = my_ip_list
        other_ip_list[-1] = str(code)
        other_ip = ".".join([item for item in other_ip_list])

        port = 443
        receiver_ip = other_ip
        server_address = (receiver_ip, port)

        def establish_connection():
            global connection_progress
            while connection_progress != 'connected' and connection_progress != 'switchoff':
                try:
                    s.connect(server_address)
                    connection_progress = 'connected'

                except:
                    pass

        connection_thread = threading.Thread(target=establish_connection)
        connection_thread.start()

    def compression_algo():
        global filename_compressed
        global connection_progress
        global compressed_time_elapsed
        connection_progress = 'compressing'
        filename_compressed = filename.split("/")
        filename_compressed = filename_compressed[:-1]
        filename_compressed = "/".join([str(item) for item in filename_compressed])
        compression_time1 = time.time()
        dct_compress(filename, filename_compressed + "/compressed.jpg")
        compression_time2 = time.time()
        compressed_time_elapsed = compression_time2 - compression_time1
        connection_progress = 'compressed'

    # Define function for file transfer
    def send_image():
        def transfer_image():
            global connection_progress

            compression_algo()

            global key
            try:
                with open(filename_compressed + "/compressed.jpg", 'rb') as file:
                    image_data = file.read()
                encryption_time1 = time.time()
                image_data, key = encryption(image_data)
                encryption_time2 = time.time()
                global encryption_time_elapsed
                encryption_time_elapsed = encryption_time2 - encryption_time1
                filefound = 1
            except:
                filefound = 0

            if connection_progress == 'compressed':
                connection_progress = 'final send'
                s.sendall(image_data)
                s.close()
                connection_progress = 'sent'

                initial_file_size_b = os.path.getsize(filename)
                initial_file_size_kb = initial_file_size_b / 1024
                initial_file_size_mb = initial_file_size_kb / 1024
                initial_file_size_gb = initial_file_size_mb / 1024

                if initial_file_size_gb >= 1:
                    initial_file_size = str(initial_file_size_gb) + " GB"
                elif initial_file_size_mb >= 1:
                    initial_file_size = str(initial_file_size_mb) + " MB"
                elif initial_file_size_kb >= 1:
                    initial_file_size = str(initial_file_size_kb) + " KB"
                else:
                    initial_file_size = str(initial_file_size_b) + " Bytes"

                compressed_file_size_b = os.path.getsize(filename_compressed + "/compressed.jpg")
                compressed_file_size_kb = compressed_file_size_b / 1024
                compressed_file_size_mb = compressed_file_size_kb / 1024
                compressed_file_size_gb = compressed_file_size_mb / 1024

                if compressed_file_size_gb >= 1:
                    compressed_file_size = str(compressed_file_size_gb) + " GB"
                elif compressed_file_size_mb >= 1:
                    compressed_file_size = str(compressed_file_size_mb) + " MB"
                elif compressed_file_size_kb >= 1:
                    compressed_file_size = str(compressed_file_size_kb) + " KB"
                else:
                    compressed_file_size = str(compressed_file_size_b) + " Bytes"

                with Image.open(filename) as img:
                    width, height = img.size

                with open("data/log.txt", "a+") as file:
                    file.write("Filename: ")
                    file.write(str(filename.split("/")[-1]))
                    file.write("\n")
                    file.write("Initial file size: ")
                    file.write(str(initial_file_size))
                    file.write("\n")
                    file.write("Compressed file size: ")
                    file.write(str(compressed_file_size))
                    file.write("\n")
                    file.write("Dimension: ")
                    file.write(str(width)+", "+str(height))
                    file.write("\n")
                    file.write("Encryption time: ")
                    file.write(str(encryption_time_elapsed)+" s")
                    file.write("\n")
                    file.write("Compression time: ")
                    file.write(str(compressed_time_elapsed)+" s")
                    file.write("\n")
                    file.write("\n")

                os.remove(filename_compressed + "/compressed.jpg")


        connection_thread = threading.Thread(target=transfer_image)
        connection_thread.start()

    run = True
    while run:

        # Update screen and set fps
        pygame.display.update()
        clock.tick(fps)

        # Fill screen with white
        screen.fill(white)

        # Blit FlexShare logo
        screen.blit(flexshare_logo, (width / 2 - flexshare_logo.get_width() / 2, height / 9))

        # Disable typing after code length reached
        if len(code) > 3:
            pressed = False

        # get mouse pos
        mouse_pos = pygame.mouse.get_pos()

        global connection_progress
        if connection_progress == 'waiting for connection':
            connection_status_rect = waiting_text.get_rect(center=(width / 2, height / 1.3))
            screen.blit(waiting_text, connection_status_rect)
        elif connection_progress == 'connected':
            connection_status_rect = established_text.get_rect(center=(width / 2, height / 1.3))
            screen.blit(established_text, connection_status_rect)

        if connection_progress == 'not connected' or connection_progress == 'waiting for connection' or connection_progress == 'connected' or connection_progress == 'compressing' or connection_progress == 'compressed':

            # Blit my code and ask for other code
            screen.blit(text1, text1_rect)

            if connection_progress == 'not connected':
                if len(code) == 4:
                    if rect_connect.collidepoint(mouse_pos):
                        pygame.draw.rect(screen, red, rect_connect, border_radius=int(width / 45))
                        text = font_1.render("CONNECT", True, white)
                        text_rect = text.get_rect(center=rect_connect.center)
                        screen.blit(text, text_rect)
                    else:
                        pygame.draw.rect(screen, grey, rect_connect_copy, border_radius=int(width / 45))
                        pygame.draw.rect(screen, blue, rect_connect, border_radius=int(width / 45))
                        text = font_1.render("CONNECT", True, white)
                        text_rect = text.get_rect(center=rect_connect.center)
                        screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(screen, grey, rect_connect, border_radius=int(width / 45))
                    text = font_1.render("CONNECT", True, white)
                    text_rect = text.get_rect(center=rect_connect.center)
                    screen.blit(text, text_rect)
            elif connection_progress == 'waiting for connection':
                pygame.draw.rect(screen, grey, rect_connect, border_radius=int(width / 45))
                text = font_1.render("CONNECT", True, white)
                text_rect = text.get_rect(center=rect_connect.center)
                screen.blit(text, text_rect)
            elif connection_progress == 'connected':
                if rect_proceed.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, red, rect_proceed, border_radius=int(width / 45))
                    text = font_4.render("→", True, white)
                    text_rect = text.get_rect(center=(rect_proceed.centerx, rect_proceed.centery - 5))
                    screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(screen, grey, rect_proceed_copy, border_radius=int(width / 45))
                    pygame.draw.rect(screen, blue, rect_proceed, border_radius=int(width / 45))
                    text = font_4.render("→", True, white)
                    text_rect = text.get_rect(center=(rect_proceed.centerx, rect_proceed.centery - 5))
                    screen.blit(text, text_rect)
            elif connection_progress == 'compressing':
                compressing_text_rect = compressing_text.get_rect(center=(width / 2, height / 1.2))
                screen.blit(compressing_text, compressing_text_rect)
            elif connection_progress == 'compressed':
                compressed_text = font_3.render("Compressed", True, blue)
                compressed_text_rect = compressed_text.get_rect(center=(width / 2, height / 1.2))
                screen.blit(compressed_text, compressed_text_rect)

            # Draw the code boxes
            pygame.draw.rect(screen, color_list[0], code_box_1, 3, border_radius=int(width * 0.015))
            pygame.draw.rect(screen, color_list[1], code_box_2, 3, border_radius=int(width * 0.015))
            pygame.draw.rect(screen, color_list[2], code_box_3, 3, border_radius=int(width * 0.015))
            pygame.draw.rect(screen, color_list[3], code_box_4, 3, border_radius=int(width * 0.015))

            # Update code box color based on code length
            if pressed:
                if len(code) == 0:
                    color_list = [grey_2, grey_3, grey_3, grey_3]
                elif len(code) == 1:
                    color_list = [grey_3, grey_2, grey_3, grey_3]
                elif len(code) == 2:
                    color_list = [grey_3, grey_3, grey_2, grey_3]
                elif len(code) == 3:
                    color_list = [grey_3, grey_3, grey_3, grey_2]
            else:
                color_list = [grey_3, grey_3, grey_3, grey_3]

            # Display code on screen
            if len(code) == 1:
                code0 = font_1.render(str(code[0]), True, black)
                code0_rect = code0.get_rect(center=code_box_1.center)
                screen.blit(code0, code0_rect)
            elif len(code) == 2:
                code0 = font_1.render(str(code[0]), True, black)
                code0_rect = code0.get_rect(center=code_box_1.center)
                screen.blit(code0, code0_rect)

                code1 = font_1.render(str(code[1]), True, black)
                code1_rect = code1.get_rect(center=code_box_2.center)
                screen.blit(code1, code1_rect)
            elif len(code) == 3:
                code0 = font_1.render(str(code[0]), True, black)
                code0_rect = code0.get_rect(center=code_box_1.center)
                screen.blit(code0, code0_rect)

                code1 = font_1.render(str(code[1]), True, black)
                code1_rect = code1.get_rect(center=code_box_2.center)
                screen.blit(code1, code1_rect)

                code2 = font_1.render(str(code[2]), True, black)
                code2_rect = code2.get_rect(center=code_box_3.center)
                screen.blit(code2, code2_rect)

            elif len(code) == 4:
                code0 = font_1.render(str(code[0]), True, black)
                code0_rect = code0.get_rect(center=code_box_1.center)
                screen.blit(code0, code0_rect)

                code1 = font_1.render(str(code[1]), True, black)
                code1_rect = code1.get_rect(center=code_box_2.center)
                screen.blit(code1, code1_rect)

                code2 = font_1.render(str(code[2]), True, black)
                code2_rect = code2.get_rect(center=code_box_3.center)
                screen.blit(code2, code2_rect)

                code3 = font_1.render(str(code[3]), True, black)
                code3_rect = code3.get_rect(center=code_box_4.center)
                screen.blit(code3, code3_rect)

        elif connection_progress == 'proceeded' or connection_progress == 'final send' or connection_progress == 'sent':
            if filename == "":
                filename = "Browse for a image!"

            if len(key) >= 0 and connection_progress == 'sent':
                key_text = font_3.render("Encryption Key: " + key, True, red)
                key_text_rect = key_text.get_rect(center=(width / 2, height / 2.5))
                screen.blit(key_text, key_text_rect)

            if connection_progress == 'proceeded':
                if filename != "Browse for a image!":
                    if f_send_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(screen, red, f_send_rect, border_radius=int(width / 45))
                        text = font_1.render("SEND", True, white)
                        text_rect = text.get_rect(center=f_send_rect.center)
                        screen.blit(text, text_rect)

                    else:
                        pygame.draw.rect(screen, grey, f_send_rect_copy, border_radius=int(width / 45))
                        pygame.draw.rect(screen, blue, f_send_rect, border_radius=int(width / 45))
                        text = font_1.render("SEND", True, white)
                        text_rect = text.get_rect(center=f_send_rect.center)
                        screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(screen, grey, f_send_rect, border_radius=int(width / 45))
                    text = font_1.render("SEND", True, white)
                    text_rect = text.get_rect(center=f_send_rect.center)
                    screen.blit(text, text_rect)

            elif connection_progress == 'final send':
                pygame.draw.rect(screen, grey, f_send_rect, border_radius=int(width / 45))
                text = font_1.render("SEND", True, white)
                text_rect = text.get_rect(center=f_send_rect.center)
                screen.blit(text, text_rect)
                sending_text = font_3.render("Transferring file...", True, blue)
                sending_text_rect = sending_text.get_rect(center=(width / 2, height / 1.4))
                screen.blit(sending_text, sending_text_rect)

            elif connection_progress == 'sent':
                pygame.draw.rect(screen, grey, f_send_rect, border_radius=int(width / 45))
                text = font_1.render("SEND", True, white)
                text_rect = text.get_rect(center=f_send_rect.center)
                screen.blit(text, text_rect)

                sending_text = font_3.render("Image transferred successfully", True, blue)
                sending_text_rect = sending_text.get_rect(center=(width / 2, height / 1.4))
                screen.blit(sending_text, sending_text_rect)

            screen.blit(file_dir, file_dir_rect)

            pygame.draw.rect(screen, grey_3, loc, 3, border_radius=int(width * 0.015))
            screen.blit(dir_icon, dir_rect)

        global s
        # Event checker
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.close()
                connection_progress = 'switchoff'
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                if event.key == pygame.K_RETURN:
                    if len(code) == 4 and connection_progress == 'not connected':
                        connection_progress = 'waiting for connection'
                        connect2pc(code, my_ip)
                    if connection_progress == 'proceeded':
                        send_image()
                    if connection_progress == 'connected':
                        connection_progress = 'proceeded'

                if event.key == pygame.K_BACKSPACE:
                    if connection_progress == 'not connected':
                        code = code[:-1]
                        pressed = True

                # Update code based on typing
                if pressed or len(code) == 0:
                    if connection_progress == 'not connected':
                        if len(code) == 0:
                            pressed = True
                        if 0 <= event.key - 48 <= 9:
                            code += str(event.key - 48)

            if pygame.mouse.get_pressed()[0]:
                if connection_progress == 'not connected':
                    if code_box_1.collidepoint(mouse_pos) or code_box_2.collidepoint(mouse_pos) or code_box_3.collidepoint(
                            mouse_pos) or code_box_4.collidepoint(mouse_pos):
                        pressed = True
                    else:
                        pressed = False

                if rect_connect.collidepoint(mouse_pos) and len(code) == 4 and connection_progress == 'not connected':
                    connection_progress = 'waiting for connection'
                    connect2pc(code, my_ip)

                if f_send_rect.collidepoint(mouse_pos) and connection_progress == 'proceeded' and filename != "Browse for a image!":
                    send_image()

                if rect_proceed.collidepoint(mouse_pos) and connection_progress == 'connected':
                    connection_progress = 'proceeded'

                if dir_rect.collidepoint(mouse_pos) or loc.collidepoint(mouse_pos):
                    if connection_progress == 'proceeded':
                        filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                                              filetypes=(("JPG", "*.jpg"),))
                        filename_copy = filename
                        if len(filename) >= 68:
                            filename_copy = "..." + filename[len(filename) - 68:]
                        if filename == '':
                            filename = "Browse for a image!"
                        file_dir = font_2.render(filename_copy, True, grey_2)


def receiver():
    # Flex Share Logo
    flexshare_logo = pygame.image.load('Data/images/flexshare.png').convert_alpha()
    flexshare_logo = pygame.transform.scale(flexshare_logo, (int(width / 2.5), int(height / 6.5)))

    key = "Enter Decryption key..."

    # Define variables
    filepath = "Select Destination Folder..."
    filepath_copy = filepath

    global connection_progress

    # Find the code of this pc
    hostname = socket.gethostname()
    my_ip = socket.gethostbyname(hostname)
    my_ip_list = my_ip.split(".")
    my_code = my_ip_list[-1]
    l = len(my_code)
    while len(my_code) < 3:
        my_code += "0"
    my_code = str(l) + my_code

    # Define some text and rectangles
    text2 = font_3.render("Receiver Code: " + str(my_code), True, red)
    text2_rect = text2.get_rect(midbottom=(width // 2, height // 2.35))

    # Directory icon
    dir_icon = pygame.image.load('Data/images/directory.png').convert_alpha()
    dir_icon = pygame.transform.scale(dir_icon, (int(height * 0.09), int(height * 0.09)))

    # Location box
    loc = pygame.Rect(width * 0.11, int(height * 0.5), int(width * 0.7), int(height * 0.09))
    dir_rect = dir_icon.get_rect()
    dir_rect.x = loc.midright[0] + 20
    dir_rect.y = loc.midright[1] - dir_icon.get_height() / 2

    decrypt_rect = pygame.Rect(0, 0, loc.width / 2, loc.height)
    decrypt_rect.y = loc.y + (width * 0.09)
    decrypt_rect.x = width / 2 - decrypt_rect.width / 2

    # Send button
    rect_receive = pygame.Rect(int(width / 2) - int(width / 12), int(height - (height / 5.7)), int(width / 6),
                               int(height / 8.64))
    rect_receive_copy = pygame.Rect(int(width / 2) - int(width / 12), int(height - (height / 5.87)),
                                    int(width / 6),
                                    int(height / 8.64))

    # Directory text
    file_dir = font_2.render(filepath, True, grey_2)
    file_dir_rect = file_dir.get_rect(midleft=(loc.midleft[0] + 15, loc.midleft[1]))

    # Key text
    key_text = font_2.render(key, True, grey_2)
    key_text_rect = key_text.get_rect(center=decrypt_rect.center)

    # Waiting for connection text
    waiting_text = font_3.render("Waiting for Connection...", True, blue)
    connected_text = font_3.render("Connection Established", True, blue)
    success_text = font_3.render("Image received Successfully", True, blue)
    fail_text = font_3.render("Image not received", True, red)
    de_fail_text = font_3.render("Wrong Key", True, red)

    # Decryption
    def decryption(key, filepath):
        decryption_status = 0
        key_hash = md5(key.encode('ascii')).digest()
        tdes_key = DES3.adjust_key_parity(key_hash)
        cipher = DES3.new(tdes_key, DES3.MODE_EAX, nonce=b'0')

        with open(filepath, 'rb') as input_file:
            image_data = input_file.read()

        decrypted_data = cipher.decrypt(image_data)
        with open(filepath, 'wb+') as output_file:
            output_file.write(decrypted_data)

        try:
            with Image.open(filepath) as img:
                decryption_status = 1
        except IOError:
            os.remove(filepath)

        return decryption_status

    def receive_file(filepath):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        receiver_ip = socket.gethostbyname(hostname)
        port = 443
        s.bind((receiver_ip, port))
        nonlocal key

        def listen_to_message():
            global connection_progress
            s.listen(1)
            while True:
                conn, addr = s.accept()
                connection_progress = 'connected'
                with open(filepath + "/received_image.jpg", 'wb') as file:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        file.write(data)
                conn.close()
                s.close()
                break

            filename = filepath + "/received_image.jpg"
            connection_progress = 'can decrypt'
            while connection_progress == 'can decrypt':
                pass
            decryption_status = decryption(key, filename)

            if decryption_status:
                if os.path.exists(filepath + "/received_image.jpg"):
                    if os.path.getsize(filepath + "/received_image.jpg") > 0:
                        connection_progress = 'success'
                else:
                    connection_progress = 'failed'
            else:
                connection_progress = 'decryption failed'

        connection_thread = threading.Thread(target=listen_to_message)
        connection_thread.start()

    can_type = False
    run = True
    while run:

        if filepath == '':
            filepath = "Select Destination Folder..."

        # Update screen and set fps
        pygame.display.update()
        clock.tick(fps)

        # Fill screen with white
        screen.fill(white)

        # Blit FlexShare logo
        screen.blit(flexshare_logo, (width / 2 - flexshare_logo.get_width() / 2, height / 9))

        # Blit connection code
        screen.blit(text2, text2_rect)

        # get mouse pos
        mouse_pos = pygame.mouse.get_pos()

        # Directory rectangle
        screen.blit(file_dir, file_dir_rect)

        pygame.draw.rect(screen, grey_3, loc, 3, border_radius=int(width * 0.015))
        screen.blit(dir_icon, dir_rect)

        if connection_progress == 'not connected' or connection_progress == 'connected' or connection_progress == 'waiting for connection':
            pygame.draw.rect(screen, grey, rect_receive, border_radius=int(width / 45))
            text = font_1.render("RECEIVE", True, white)
            text_rect = text.get_rect(center=rect_receive.center)
            screen.blit(text, text_rect)

            if connection_progress == 'waiting for connection':
                connection_status_rect = waiting_text.get_rect(center=(width / 2, height / 1.4))
                screen.blit(waiting_text, connection_status_rect)
            elif connection_progress == 'connected':
                connection_status_rect = connected_text.get_rect(center=(width / 2, height / 1.4))
                screen.blit(connected_text, connection_status_rect)

        elif connection_progress == 'can connect':
            if rect_receive.collidepoint(mouse_pos):
                pygame.draw.rect(screen, red, rect_receive, border_radius=int(width / 45))
                text = font_1.render("RECEIVE", True, white)
                text_rect = text.get_rect(center=rect_receive.center)
                screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, grey, rect_receive_copy, border_radius=int(width / 45))
                pygame.draw.rect(screen, blue, rect_receive, border_radius=int(width / 45))
                text = font_1.render("RECEIVE", True, white)
                text_rect = text.get_rect(center=rect_receive.center)
                screen.blit(text, text_rect)
        elif connection_progress == 'success':
            connection_status_rect = success_text.get_rect(center=(width / 2, height / 1.4))
            screen.blit(success_text, connection_status_rect)
        elif connection_progress == 'failed':
            connection_status_rect = fail_text.get_rect(center=(width / 2, height / 1.4))
            screen.blit(fail_text, connection_status_rect)
        elif connection_progress == 'decryption failed':
            connection_status_rect = de_fail_text.get_rect(center=(width / 2, height / 1.4))
            screen.blit(de_fail_text, connection_status_rect)
        elif connection_progress == 'can decrypt':

            key_text = font_2.render(key, True, grey_2)
            key_text_rect = key_text.get_rect(center=decrypt_rect.center)
            screen.blit(key_text, key_text_rect)
            pygame.draw.rect(screen, grey_3, decrypt_rect, 3, border_radius=int(width * 0.015))

            if len(key) == 8:

                if rect_receive.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, red, rect_receive, border_radius=int(width / 45))
                    text = font_1.render("RECEIVE", True, white)
                    text_rect = text.get_rect(center=rect_receive.center)
                    screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(screen, grey, rect_receive_copy, border_radius=int(width / 45))
                    pygame.draw.rect(screen, blue, rect_receive, border_radius=int(width / 45))
                    text = font_1.render("RECEIVE", True, white)
                    text_rect = text.get_rect(center=rect_receive.center)
                    screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, grey, rect_receive, border_radius=int(width / 45))
                text = font_1.render("RECEIVE", True, white)
                text_rect = text.get_rect(center=rect_receive.center)
                screen.blit(text, text_rect)

        elif connection_progress == 'decrypt':
            pygame.draw.rect(screen, grey, rect_receive, border_radius=int(width / 45))
            text = font_1.render("RECEIVE", True, white)
            text_rect = text.get_rect(center=rect_receive.center)
            screen.blit(text, text_rect)

        # Event checker
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if 65 <= event.key <= 122 or 48 <= event.key <= 57:
                    if can_type and len(key) < 8:
                        key += chr(event.key).upper()

                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_RETURN:
                    if connection_progress == 'can connect':
                        connection_progress = 'waiting for connection'
                        receive_file(filepath)
                    elif connection_progress == 'can decrypt' and len(key) == 8:
                        connection_progress = 'decrypt'
                if event.key == pygame.K_BACKSPACE:
                    key = key[:-1]

            if pygame.mouse.get_pressed()[0]:
                if dir_rect.collidepoint(mouse_pos) or loc.collidepoint(mouse_pos):
                    if connection_progress == 'not connected' or connection_progress == 'can connect':
                        filepath = filedialog.askdirectory()
                        filepath_copy = filepath
                        if len(filepath_copy) >= 60:
                            filepath_copy = "..." + filepath_copy[len(filepath_copy) - 60:]
                        if filepath == "":
                            filepath = "Select Destination Folder..."
                        file_dir = font_2.render(filepath_copy, True, grey_2)

                    if os.path.exists(filepath):
                        connection_progress = 'can connect'
                if decrypt_rect.collidepoint(mouse_pos):
                    if connection_progress == 'can decrypt':
                        if key == 'Enter Decryption key...':
                            key = ""
                        can_type = True
                if rect_receive.collidepoint(mouse_pos):
                    if connection_progress == 'can connect':
                        connection_progress = 'waiting for connection'
                        receive_file(filepath)
                    elif connection_progress == 'can decrypt' and len(key) == 8:
                        connection_progress = 'decrypt'


if __name__ == "__main__":
    homepage()
