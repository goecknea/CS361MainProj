import pygame
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

def parseScramble(scramble):
    init_str = "wwwwwwwwwgggrrrbbbooogggrrrbbbooogggrrrbbboooyyyyyyyyy"

    strlen = len(scramble)
    moves = scramble.split(" ")

    for move in moves:
        rep = 0
        if len(move) == 1:
            rep = 1
        elif move[1] == "'":
            rep = 3
        elif move[1] == "2":
            rep = 2

        for i in range(rep):
            if move[0] == "U":
                new_str = (init_str[6] + init_str[3] + init_str[0] + init_str[7] + init_str[4] + init_str[1] +
                           init_str[8] + init_str[5] + init_str[2] + init_str[12:15] + init_str[15:18] +
                           init_str[18:21] + init_str[9:12] + init_str[21:])
            elif move[0] == "D":
                new_str = (init_str[:33] + init_str[42:45] + init_str[33:36] + init_str[36:39] + init_str[39:42] +
                           init_str[51] + init_str[48] + init_str[45] + init_str[52] + init_str[49] + init_str[46] +
                           init_str[53] + init_str[50] + init_str[47])
            elif move[0] == "R":
                new_str = (init_str[0:2] + init_str[11] + init_str[3:5] + init_str[23] + init_str[6:8] + init_str[35] +
                           init_str[9:11] + init_str[47] + init_str[36] + init_str[24] + init_str[12] + init_str[8] +
                           init_str[16:23] + init_str[50] + init_str[37] + init_str[25] + init_str[13] + init_str[5] +
                           init_str[28:35] + init_str[53] + init_str[38] + init_str[26] + init_str[14] + init_str[2] +
                           init_str[40:47] + init_str[39] + init_str[48:50] + init_str[27] + init_str[51:53] +
                           init_str[15])
            elif move[0] == "L":
                new_str = (init_str[41] + init_str[1:3] + init_str[29] + init_str[4:6] + init_str[17] + init_str[7:9] +
                           init_str[0] + init_str[10:17] + init_str[51] + init_str[42] + init_str[30] + init_str[18] +
                           init_str[3] + init_str[22:29] + init_str[48] + init_str[43] + init_str[31] + init_str[19] +
                           init_str[6] + init_str[34:41] + init_str[45] + init_str[44] + init_str[32] + init_str[20] +
                           init_str[9] + init_str[46:48] + init_str[21] + init_str[49:51] + init_str[33] +
                           init_str[52:])
            elif move[0] == 'F':
                new_str = (init_str[0:6] + init_str[44] + init_str[32] + init_str[20] + init_str[33] + init_str[21] +
                           init_str[9] + init_str[6] + init_str[13:20] + init_str[45] + init_str[34] + init_str[22] +
                           init_str[10] + init_str[7] + init_str[25:32] + init_str[46] + init_str[35] + init_str[23] +
                           init_str[11] + init_str[8] + init_str[37:44] + init_str[47] + init_str[36] + init_str[24] +
                           init_str[12] + init_str[48:])
            elif move[0] == 'B':
                new_str = (init_str[14] + init_str[26] + init_str[38] + init_str[3:14] + init_str[53] + init_str[39] +
                           init_str[27] + init_str[15] + init_str[2] + init_str[19:26] + init_str[52] + init_str[40] +
                           init_str[28] + init_str[16] + init_str[1] + init_str[31:38] + init_str[51] + init_str[41] +
                           init_str[29] + init_str[17] + init_str[0] + init_str[43:51] + init_str[18] + init_str[30] +
                           init_str[42])
            init_str = new_str

    new_str = (init_str[:9] + init_str[18:21] + init_str[9:18] + init_str[30:33] + init_str[21:30] + init_str[42:45] +
               init_str[33:42] + init_str[45:])
    init_str = new_str

    return init_str # bkg


# pygame.init()
# main_window = pygame.display.set_mode((1920, 1080))

while True:
    scramble = socket.recv().decode("utf-8")
    bkg = parseScramble(scramble)
    print(bkg)
    socket.send_string(bkg)
