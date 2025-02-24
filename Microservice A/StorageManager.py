import zmq

# zmq initialization
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    try:
        msg = socket.recv()

        if msg == b'exit':
            socket.send(b'closing')
            break

        if len(str(msg).split(";")) == 3:
            csv = open("./maintenance_log.csv", "a")
            csv.write(str(msg).split("'")[1])
            csv.write("\n")
            socket.send_string("0")
            csv.close()
        else:
            socket.send_string("1")
    except:
        socket.send_string("-1")