import zmq

# zmq initialization
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def write_to_csv(msg):
    csv = open("./maintenance_log.csv", "a")
    csv.write(str(msg).split("'")[1])
    csv.write("\n")
    csv.close()


while True:
    try:
        msg = socket.recv()

        # if the message says exit, this program will close
        if msg == b'exit':
            socket.send(b'closing')
            break

        # checks if the message can be split into 3
        # writes, sends 0 if true, else sends 1
        if len(str(msg).split(";")) == 3:
            write_to_csv(str(msg))
            socket.send_string("0")

        else:
            socket.send_string("1")

    # sends a -1 for any exceptions
    except:
        socket.send_string("-1")
