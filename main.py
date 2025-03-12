import pygame
import random
import time
import zmq

# init ZMQ for microservice B
microb_context = zmq.Context()
microb_socket = microb_context.socket(zmq.REQ)
microb_socket.connect("tcp://localhost:5556")

class ScrambleStack:
    def __init__(self, max_len):
        self.max = max_len
        self.internal_list = ["", "", "", "", ""]

    # adds element to top of stack
    def push(self, element):
        self.internal_list.append(element)
        if len(self.internal_list) > self.max:
            self.internal_list.pop(0)

    # removes first element from stack
    def pop(self):
        popped_val = self.internal_list[self.max - 1]
        for i in range(self.max - 2, -1, -1):
            self.internal_list[i + 1] = self.internal_list[i]
        self.internal_list[0] = ""
        return popped_val

    # return False if not empty else True
    def is_empty(self):
        for i in range(self.max):
            if self.internal_list[i] != "":
                return False
        return True


def generate_scramble_display(scramble):
    microb_socket.send_string(scramble)
    init_str = microb_socket.recv().decode("utf-8")
    strlen = len(init_str)
    init_str = init_str

    # parse response
    border = 5
    color = 30

    red = pygame.Color(255, 0, 0)
    orange = pygame.Color(255, 140, 0)
    yellow = pygame.Color(255, 255, 0)
    green = pygame.Color(0, 255, 0)
    blue = pygame.Color(0, 0, 255)
    white = pygame.Color(255, 255, 255)

    bkg_border = pygame.Surface(((13 * border) + (12 * color) + border, (10 * border) + (9 * color) + border))
    bkg_border.fill(pygame.Color(10, 10, 10))

    bkg = pygame.Surface(((13 * border) + (12 * color), (10 * border) + (9 * color)))
    bkg.fill(pygame.Color(20, 20, 20))

    vert_surf = pygame.Surface(((4 * border) + (3 * color), (10 * border) + (9 * color)))
    vert_pos = ((3 * border) + (3 * color), 2)
    vert_surf.fill(pygame.Color(10, 10, 10))

    hor_surf = pygame.Surface(((13 * border) + (12 * color), (4 * border) + (3 * color)))
    hor_pos = (2, (3 * border) + (3 * color))
    hor_surf.fill(pygame.Color(10, 10, 10))

    bkg.blit(vert_surf, vert_pos)
    bkg.blit(hor_surf, hor_pos)

    y_pos = 4
    index = 0

    for i in range(9):
        if 2 < i < 6:
            x_pos = border
            loop = 12
        else:
            x_pos = (4 * border) + (3 * color)
            loop = 3

        for j in range(loop):
            surf = pygame.Surface((color, color))

            if init_str[index] == 'w': surf.fill(white)
            elif init_str[index] == 'r': surf.fill(red)
            elif init_str[index] == 'g': surf.fill(green)
            elif init_str[index] == 'b': surf.fill(blue)
            elif init_str[index] == 'y': surf.fill(yellow)
            elif init_str[index] == 'o': surf.fill(orange)

            bkg.blit(surf, (x_pos, y_pos))
            x_pos += border + color
            index += 1

        y_pos += color + border

    bkg_border.blit(bkg, (border, border))

    return bkg_border

def generate_scramble(scr_len):
    prev_prev_choice = ""
    prev_choice = ""
    moves = ["U", "F", "R", "D", "B", "L"]
    mods = ["'", "", "2"]
    scramble = ""

    for i in range(scr_len):
        choice = random.choice(moves)
        while choice == prev_choice or (choice == prev_prev_choice and
                                        moves.index(prev_choice) % 3 == moves.index(prev_prev_choice) % 3):
            choice = random.choice(moves)
        mod = random.choice(mods)

        scramble += choice + mod + " "
        prev_prev_choice = prev_choice
        prev_choice = choice

    return scramble.strip()


def get_help(help_font, font_color, max_scramble):
    return [help_font.render("Welcome to LBRCT!", True, font_color), help_font.render("LBRCT is an offline Rubik's "
            "Cube timer that is written in Python using pygame.", True, font_color), help_font.render("To begin using "
            "LBRCT, use the generated scramble to scramble your Rubik's Cube.", True, font_color),
            help_font.render("Then, hold Space until the timer turns green, and begin to solve.", True, font_color),
            help_font.render("When you are finished solving, press space to stop the timer.", True, font_color),
            help_font.render("This will automatically generate a new scramble, and you can repeat this as many times "
            "as you want!", True, font_color), help_font.render("You can use the Prev and Next buttons underneath the "
            "scramble to look at up to " + str(max_scramble) + " previous scrambles.", True, font_color)]


def process_time(timer_total):
    milli = timer_total % 1000
    secs = (timer_total // 1000) % 60
    mins = (timer_total // 60000) % 24
    if mins == 0:
        return "{secs:02d}.{milli:03d}".format(secs=secs, milli=milli)
    else:
        return "{mins}:{secs:02d}.{milli:03d}".format(mins=mins, secs=secs, milli=milli)


def main():
    # initialize pygame
    pygame.init()
    main_window = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Rubik's Cube Timer")

    # initialize zmq
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    micro_c_socket = context.socket(zmq.REQ)
    micro_c_socket.connect("tcp://localhost:5557")

    ACTIVE_BUTTON_COLOR = pygame.Color(40, 40, 40)
    BKG_COLOR = pygame.Color(20, 20, 20)
    BUTTON_BORDER_COLOR = pygame.Color(10, 10, 10)
    BUTTON_FONT = pygame.font.Font(None, 36)
    EXIT_BUTTON_ACTIVE = False
    EXPORT_BUTTON_ACTIVE = False
    FONT_COLOR = pygame.Color(200, 200, 200)
    G_TIMER = "00.000"
    HELP_BUTTON_ACTIVE = False
    HELP_EXIT_BUTTON_ACTIVE = False
    HELP_FONT = pygame.font.Font(None, 54)
    HELP_MENU = False
    IMPORT_BUTTON_ACTIVE = False
    INFO_FONT = pygame.font.Font(None, 24)
    MAX_SCRAMBLES_SAVED = 5
    MENU_FONT = pygame.font.Font(None, 72)
    MENU_OPEN = False
    NEXT_BUTTON_ACTIVE = False
    NEXT_SCRAMBLES = ScrambleStack(MAX_SCRAMBLES_SAVED)
    PREV_BUTTON_ACTIVE = False
    PREVIOUS_SCRAMBLE = ScrambleStack(MAX_SCRAMBLES_SAVED)
    SCRAMBLE_LENGTH = 20
    SCRAMBLE = generate_scramble(SCRAMBLE_LENGTH)
    SCRAMBLE_DISPLAY = generate_scramble_display(SCRAMBLE)
    SCRAMBLE_DISPLAY_ACTIVE = True
    SCRAMBLE_DISP_BUTTON_ACTIVE = False
    SPACE_HELD = False
    TIMER_ACTIVE = False
    TIMER_DELAY = 500
    TIMER_FONT = pygame.font.Font(None, 144)
    WINDOW_CENTER = (pygame.display.get_surface().get_rect().w // 2, pygame.display.get_surface().get_rect().h // 2)

    # display loop
    displayLoop = True
    while displayLoop:
        for event in pygame.event.get():
            # quit display loop
            if event.type == pygame.QUIT:
                displayLoop = False

            # handle mouse clicks
            if event.type == pygame.MOUSEBUTTONUP:
                mx, my = pygame.mouse.get_pos()

                # Prev scramble
                if PREV_BUTTON_ACTIVE:
                    if not PREVIOUS_SCRAMBLE.is_empty():
                        NEXT_SCRAMBLES.push(SCRAMBLE)
                        SCRAMBLE = PREVIOUS_SCRAMBLE.pop()
                        SCRAMBLE_DISPLAY = generate_scramble_display(SCRAMBLE)

                # next scramble
                elif NEXT_BUTTON_ACTIVE:
                    PREVIOUS_SCRAMBLE.push(SCRAMBLE)
                    if not NEXT_SCRAMBLES.is_empty():
                        SCRAMBLE = NEXT_SCRAMBLES.pop()
                        SCRAMBLE_DISPLAY = generate_scramble_display(SCRAMBLE)
                    else:
                        SCRAMBLE = generate_scramble(SCRAMBLE_LENGTH)
                        SCRAMBLE_DISPLAY = generate_scramble_display(SCRAMBLE)

                # show/hide scramble display
                elif SCRAMBLE_DISP_BUTTON_ACTIVE:
                    SCRAMBLE_DISPLAY_ACTIVE = False if SCRAMBLE_DISPLAY_ACTIVE else True

                # import
                elif IMPORT_BUTTON_ACTIVE:
                    micro_c_socket.send_string("import")
                    micro_c_socket.recv()

                # export
                elif EXPORT_BUTTON_ACTIVE:
                    micro_c_socket.send_string("export")
                    micro_c_socket.recv()

                # help
                elif HELP_BUTTON_ACTIVE:
                    HELP_MENU = True
                    while HELP_MENU:
                        main_window.fill(BKG_COLOR)

                        title = MENU_FONT.render("HELP", True, FONT_COLOR)
                        main_window.blit(title, ((WINDOW_CENTER[0] - title.get_rect().w // 2), 25))

                        help_texts = get_help(HELP_FONT, FONT_COLOR, MAX_SCRAMBLES_SAVED)

                        # render help texts
                        help_text_x = WINDOW_CENTER[0]
                        help_text_y = 40 + title.get_rect().h
                        for thing in help_texts:
                            main_window.blit(thing, ((help_text_x - thing.get_rect().w // 2), help_text_y))
                            help_text_y += thing.get_rect().h + 5

                        # help exit button
                        help_exit_text = MENU_FONT.render("EXIT", True, FONT_COLOR)
                        help_exit_surf = pygame.Surface(
                            (help_exit_text.get_rect().w + 10, help_exit_text.get_rect().h + 10))
                        help_exit_bkg = pygame.Surface(
                            (help_exit_text.get_rect().w + 14, help_exit_text.get_rect().h + 14))
                        help_exit_bkg.fill(BUTTON_BORDER_COLOR)

                        help_mouse_x, help_mouse_y = pygame.mouse.get_pos()
                        help_exit_x = WINDOW_CENTER[0] - (help_exit_bkg.get_rect().w // 2)
                        help_exit_y = main_window.get_rect().h - 25 - help_exit_bkg.get_rect().h
                        if (help_exit_x <= help_mouse_x <= help_exit_x + help_exit_bkg.get_rect().w) and (
                                help_exit_y <= help_mouse_y <= (main_window.get_rect().h - 25)):
                            help_exit_surf.fill(ACTIVE_BUTTON_COLOR)
                            HELP_EXIT_BUTTON_ACTIVE = True
                        else:
                            help_exit_surf.fill(BKG_COLOR)
                            HELP_EXIT_BUTTON_ACTIVE = False

                        help_exit_surf.blit(help_exit_text, (5, 5))
                        help_exit_bkg.blit(help_exit_surf, (2, 2))
                        main_window.blit(help_exit_bkg, (help_exit_x, help_exit_y))

                        pygame.display.flip()

                        # event handler to exit from help menu / program
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONUP:
                                if HELP_EXIT_BUTTON_ACTIVE:
                                    HELP_MENU = False

                            # quit display loop
                            if event.type == pygame.QUIT:
                                displayLoop = False
                                HELP_MENU = False

                # exit
                elif EXIT_BUTTON_ACTIVE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            # on space down, stop timer if it is running, else start hold timer
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not TIMER_ACTIVE:
                    SPACE_HELD = True
                    start_time = pygame.time.get_ticks()

                # timer stop
                if event.key == pygame.K_SPACE and TIMER_ACTIVE:
                    TIMER_ACTIVE = False
                    timer_end = pygame.time.get_ticks()
                    timer_total = timer_end - timer_start
                    G_TIMER = process_time(timer_total)

                    # send info to microservice a
                    req_str = "W;" + G_TIMER + ";" + SCRAMBLE + ";" + str(int(time.time())) + "\n"
                    for request in range(1):
                        socket.send_string(req_str)
                        resp = socket.recv()
                        if resp[:5] == "error":
                            print("unable to save scramble")

                    # get next scramble
                    PREVIOUS_SCRAMBLE.push(SCRAMBLE)
                    if not NEXT_SCRAMBLES.is_empty():
                        SCRAMBLE = NEXT_SCRAMBLES.pop()
                    else:
                        SCRAMBLE = generate_scramble(SCRAMBLE_LENGTH)
                        SCRAMBLE_DISPLAY = generate_scramble_display(SCRAMBLE)

            # if space released and the time held < TIMER_DELAY, timer does not start
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and SPACE_HELD:
                    end_time = pygame.time.get_ticks()
                    SPACE_HELD = False
                    if (end_time - start_time) > TIMER_DELAY:
                        TIMER_ACTIVE = True
                        timer_start = pygame.time.get_ticks()

        main_window.fill(BKG_COLOR)

        # timer text
        if not SPACE_HELD and not TIMER_ACTIVE:
            text_surface = TIMER_FONT.render(G_TIMER, True, FONT_COLOR)
        elif not SPACE_HELD and TIMER_ACTIVE:
            mid = pygame.time.get_ticks()
            mid_time = mid - timer_start
            G_TIMER = process_time(mid_time)
            text_surface = TIMER_FONT.render(G_TIMER, True, FONT_COLOR)
        elif SPACE_HELD:
            mid_time = pygame.time.get_ticks()
            if (mid_time - start_time) > TIMER_DELAY:
                G_TIMER = "00.000"
                color = pygame.Color(0, 255, 0)
            else:
                color = pygame.Color(255, 0, 0)

            text_surface = TIMER_FONT.render(G_TIMER, True, color)

        main_window.blit(text_surface, (
            WINDOW_CENTER[0] - (text_surface.get_rect().w // 2), WINDOW_CENTER[1] - (text_surface.get_rect().h // 2)))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # menu button
        menu_text_surface = MENU_FONT.render("MENU", True, FONT_COLOR)

        menu_surface = pygame.Surface((menu_text_surface.get_rect().w + 75, menu_text_surface.get_rect().h + 20))
        if (15 <= mouse_x <= 15 + menu_surface.get_rect().w) and (15 <= mouse_y <= 15 + menu_surface.get_rect().h):
            menu_surface.fill(ACTIVE_BUTTON_COLOR)
            MENU_OPEN = True
        else:
            menu_surface.fill(BKG_COLOR)
        menu_bkg_surface = pygame.Surface((menu_surface.get_rect().w + 4, menu_surface.get_rect().h + 4))
        menu_bkg_surface.fill(BUTTON_BORDER_COLOR)

        menu_surface.blit(menu_text_surface, (37.5, 10))
        menu_bkg_surface.blit(menu_surface, (2, 2))
        main_window.blit(menu_bkg_surface, (15, 15))

        # menu button size as var for all menu buttons
        menu_surf_size = (menu_surface.get_rect().w, menu_surface.get_rect().h)
        menu_bkg_size = (menu_bkg_surface.get_rect().w, menu_bkg_surface.get_rect().h)

        # import button
        imp_txt_surf = MENU_FONT.render("IMPORT", True, FONT_COLOR)
        imp_surf = pygame.Surface(menu_surf_size)
        imp_border = pygame.Surface(menu_bkg_size)
        imp_border.fill(BUTTON_BORDER_COLOR)

        imp_x = 15
        imp_y = 15 + menu_bkg_size[1] - 2  # (bkg.h - 2) * x for x button below menu

        if (imp_x <= mouse_x <= imp_x + menu_surf_size[0]) and (imp_y <= mouse_y <= imp_y + menu_surf_size[1]):
            imp_surf.fill(ACTIVE_BUTTON_COLOR)
            IMPORT_BUTTON_ACTIVE = True
        else:
            imp_surf.fill(BKG_COLOR)
            IMPORT_BUTTON_ACTIVE = False

        imp_surf.blit(imp_txt_surf, ((menu_surf_size[0] // 2) - (imp_txt_surf.get_rect().w // 2), (
                menu_surf_size[1] // 2) - (imp_txt_surf.get_rect().h // 2)))
        imp_border.blit(imp_surf, (2, 2))

        # export button
        exp_txt_surf = MENU_FONT.render("EXPORT", True, FONT_COLOR)
        exp_surf = pygame.Surface(menu_surf_size)
        exp_border = pygame.Surface(menu_bkg_size)
        exp_border.fill(BUTTON_BORDER_COLOR)

        exp_x = 15
        exp_y = 15 + (2 * (menu_bkg_size[1] - 2))  # (bkg.h - 2) * x for x button below menu

        if (exp_x <= mouse_x <= exp_x + menu_surf_size[0]) and (exp_y <= mouse_y <= exp_y + menu_surf_size[1]):
            exp_surf.fill(ACTIVE_BUTTON_COLOR)
            EXPORT_BUTTON_ACTIVE = True
        else:
            exp_surf.fill(BKG_COLOR)
            EXPORT_BUTTON_ACTIVE = False

        exp_surf.blit(exp_txt_surf, ((menu_surf_size[0] // 2) - (exp_txt_surf.get_rect().w // 2), (
                menu_surf_size[1] // 2) - (exp_txt_surf.get_rect().h // 2)))
        exp_border.blit(exp_surf, (2, 2))

        # help button
        help_txt_surf = MENU_FONT.render("HELP", True, FONT_COLOR)
        help_surf = pygame.Surface(menu_surf_size)
        help_border = pygame.Surface(menu_bkg_size)
        help_border.fill(BUTTON_BORDER_COLOR)

        help_x = 15
        help_y = 15 + (3 * (menu_bkg_size[1] - 2))   # (bkg.h - 2) * x for x button below menu

        if (help_x <= mouse_x <= help_x + menu_surf_size[0]) and (help_y <= mouse_y <= help_y + menu_surf_size[1]):
            help_surf.fill(ACTIVE_BUTTON_COLOR)
            HELP_BUTTON_ACTIVE = True
        else:
            help_surf.fill(BKG_COLOR)
            HELP_BUTTON_ACTIVE = False

        help_surf.blit(help_txt_surf, ((menu_surf_size[0] // 2) - (help_txt_surf.get_rect().w // 2), (
                menu_surf_size[1] // 2) - (help_txt_surf.get_rect().h // 2)))
        help_border.blit(help_surf, (2, 2))

        # exit button
        exit_txt_surf = MENU_FONT.render("EXIT", True, FONT_COLOR)
        exit_surf = pygame.Surface(menu_surf_size)
        exit_border = pygame.Surface(menu_bkg_size)
        exit_border.fill(BUTTON_BORDER_COLOR)

        exit_x = 15
        exit_y = 15 + (4 * (menu_bkg_size[1] - 2))  # (bkg.h - 2) * x for x button below menu

        if (exit_x <= mouse_x <= exit_x + menu_surf_size[0]) and (exit_y <= mouse_y <= exit_y + menu_surf_size[1]):
            exit_surf.fill(ACTIVE_BUTTON_COLOR)
            EXIT_BUTTON_ACTIVE = True
        else:
            exit_surf.fill(BKG_COLOR)
            EXIT_BUTTON_ACTIVE = False

        exit_surf.blit(exit_txt_surf, ((menu_surf_size[0] // 2) - (exit_txt_surf.get_rect().w // 2), (
                menu_surf_size[1] // 2) - (exit_txt_surf.get_rect().h // 2)))
        exit_border.blit(exit_surf, (2, 2))

        # display menu
        if MENU_OPEN:
            main_window.blit(imp_border, (imp_x, imp_y))
            main_window.blit(exp_border, (exp_x, exp_y))
            main_window.blit(help_border, (help_x, help_y))
            main_window.blit(exit_border, (exit_x, exit_y))

            # take last box and add size to get outer edge
            if (15 <= mouse_x <= 15 + menu_surf_size[0]) and (15 <= mouse_y <= exit_y + menu_surf_size[1]):
                MENU_OPEN = True
            else:
                MENU_OPEN = False

        # scramble display
        scramble_surface = MENU_FONT.render(SCRAMBLE, True, FONT_COLOR)
        main_window.blit(scramble_surface, (
            WINDOW_CENTER[0] + (menu_surf_size[0] // 2) - (scramble_surface.get_rect().w // 2), 25))

        # prev/next scramble buttons and bkgs
        button_x = WINDOW_CENTER[0] + (menu_surf_size[0] // 2)
        button_y = 35 + scramble_surface.get_rect().h

        prev_text_surf = BUTTON_FONT.render("PREV", True, FONT_COLOR)
        prev_surf = pygame.Surface((prev_text_surf.get_rect().w + 10, prev_text_surf.get_rect().h + 10))
        prev_bkg = pygame.Surface((prev_surf.get_rect().w + 4, prev_surf.get_rect().h + 4))
        prev_bkg.fill(BUTTON_BORDER_COLOR)

        prev_rect_x = button_x - (prev_bkg.get_rect().w - 2)

        # checks if mouse in prev button
        if (prev_rect_x <= mouse_x <= prev_rect_x + prev_bkg.get_rect().w - 2) and (
                button_y <= mouse_y <= button_y + prev_bkg.get_rect().h):
            prev_surf.fill(ACTIVE_BUTTON_COLOR)
            PREV_BUTTON_ACTIVE = True
        else:
            prev_surf.fill(BKG_COLOR)
            PREV_BUTTON_ACTIVE = False

        next_text_surf = BUTTON_FONT.render("NEXT", True, FONT_COLOR)
        next_surf = pygame.Surface((next_text_surf.get_rect().w + 10, next_text_surf.get_rect().h + 10))
        next_bkg = pygame.Surface((next_surf.get_rect().w + 4, next_surf.get_rect().h + 4))
        next_bkg.fill(BUTTON_BORDER_COLOR)

        # checks if mouse in next button
        if (button_x <= mouse_x <= button_x - 2 + next_bkg.get_rect().w) and (
                button_y <= mouse_y <= button_y + next_bkg.get_rect().h):
            next_surf.fill(ACTIVE_BUTTON_COLOR)
            NEXT_BUTTON_ACTIVE = True
        else:
            next_surf.fill(BKG_COLOR)
            NEXT_BUTTON_ACTIVE = False

        # draw prev and next buttons
        prev_surf.blit(prev_text_surf, (5, 5))
        prev_bkg.blit(prev_surf, (2, 2))
        main_window.blit(prev_bkg, (prev_rect_x, button_y))

        next_surf.blit(next_text_surf, (5, 5))
        next_bkg.blit(next_surf, (2, 2))
        main_window.blit(next_bkg, (button_x - 2, button_y))

        # help icon next to prev/next
        info_str = "?"
        i_font = BUTTON_FONT.render(info_str, True, FONT_COLOR)
        i_icon = pygame.Surface((next_bkg.get_rect().h, next_bkg.get_rect().h))
        i_icon.fill(BKG_COLOR)

        i_f = i_font.get_rect()
        i_s = i_icon.get_rect()
        i_icon.blit(i_font, ((i_s.w // 2) - (i_f.w // 2), (i_s.h // 2) - (i_f.h // 2)))
        main_window.blit(i_icon, ((button_x - 2 + next_bkg.get_rect().w), button_y))

        # check if mouse over ?
        if (button_x - 2 + next_bkg.get_rect().w) <= mouse_x <= ((button_x - 2 + next_bkg.get_rect().w) + i_s.h) and (
                button_y <= mouse_y <= button_y + i_s.w):
            info_text = INFO_FONT.render("Stores up to 5 scrambles to navigate through", True, FONT_COLOR,
                                         pygame.Color(75, 75, 75))
            main_window.blit(info_text, (mouse_x, mouse_y - info_text.get_rect().h))

        # show/hide button
        if SCRAMBLE_DISPLAY_ACTIVE:
            b_font = BUTTON_FONT.render("hide", True, FONT_COLOR)
        else:
            b_font = BUTTON_FONT.render("show", True, FONT_COLOR)
        b_button = pygame.Surface((b_font.get_rect().w + 2, b_font.get_rect().h + 2))
        b_bkg = pygame.Surface((b_button.get_rect().w + 10, b_font.get_rect().h + 10))
        b_bkg.fill(BUTTON_BORDER_COLOR)

        # blit scramble display
        scr_disp = (1920 - SCRAMBLE_DISPLAY.get_rect().w, 1080 - SCRAMBLE_DISPLAY.get_rect().h)

        if SCRAMBLE_DISPLAY_ACTIVE:
            b_pos = (scr_disp[0], scr_disp[1] - b_bkg.get_rect().h + 5)

            # scramble
            main_window.blit(SCRAMBLE_DISPLAY, scr_disp)
        else:
            b_pos = (scr_disp[0], 1080 - b_bkg.get_rect().h)

        # check button active
        if (b_pos[0] <= mouse_x <= b_pos[0] + b_bkg.get_rect().w) and (
                b_pos[1] <= mouse_y <= b_pos[1] + b_bkg.get_rect().h):
            SCRAMBLE_DISP_BUTTON_ACTIVE = True
            b_button.fill(ACTIVE_BUTTON_COLOR)
        else:
            SCRAMBLE_DISP_BUTTON_ACTIVE = False
            b_button.fill(BKG_COLOR)

        # blit show/hide button
        b_button.blit(b_font, (1, 1))
        b_bkg.blit(b_button, (5, 5))
        main_window.blit(b_bkg, b_pos)

        # update display
        pygame.display.flip()


if __name__ == "__main__":
    main()
