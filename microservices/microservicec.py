import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import json
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


def parse_int(str_num):
    num_list = str_num.split(".")
    total = 0

    if ":" in num_list[0]:
        sec_list = num_list[0].split(":")
        total += (int(sec_list[0]) * 60000) + (int(sec_list[1]) * 1000) + int(num_list[1])
        return total
    else:
        total += (int(num_list[0]) * 1000) + int(num_list[1])
        return total


def process_time(timer_total):
    milli = timer_total % 1000
    secs = (timer_total // 1000) % 60
    mins = (timer_total // 60000) % 24
    if mins == 0:
        return "{secs:02d}.{milli:03d}".format(secs=secs, milli=milli)
    else:
        return "{mins}:{secs:02d}.{milli:03d}".format(mins=mins, secs=secs, milli=milli)


def cs_import():
    root = tk.Tk()
    win = tk.Toplevel(root)

    file_path = filedialog.askopenfilename(parent=win, filetypes=[("txt file", ".txt")])

    if file_path == '':
        return

    file = open(file_path, "r")
    json_data = file.readline()

    # parse
    data = json.loads(json_data)

    if "properties" in data:
        data.pop("properties")

    for key in data:
        for time in data[key]:
            solve_time = process_time(time[0][1])
            scramble = time[1]
            unix_time = time[3]

            socket.send_string("W;" + solve_time + ";" + scramble + ";" + str(unix_time) + "\n")
            socket.recv()

    messagebox.showwarning(parent=win, message="Successfully imported " + file_path)

    root.destroy()


def cs_export():
    socket.send_string("R")
    data = socket.recv().decode("utf-8")

    if data == "error: csv file is empty!":
        messagebox.showwarning(message="No data to export")
        return

    data_list = data.split("\n")
    data_list.pop(0)

    exp_list = []

    for item in data_list:
        temp_list = []
        item_list = item.split(",")
        temp_list.append([0, parse_int(item_list[0])])
        temp_list.append(item_list[1])
        temp_list.append(int(item_list[2]))
        exp_list.append(temp_list)

    session_name = "session1"
    file = open(session_name + ".csv", "w+")
    file.write(json.dumps({session_name: exp_list}))
    file.close()

    root = tk.Tk()
    win = tk.Toplevel(root)
    win.iconify()

    messagebox.showwarning(message="File saved at " + os.getcwd() + "\\" + session_name + ".csv")

    root.destroy()


def main():
    main_socket = context.socket(zmq.REP)
    main_socket.bind("tcp://*:5557")

    while True:
        msg = main_socket.recv().decode("utf-8")
        print("main program called " + msg)
        if msg == "import":
            cs_import()
            main_socket.send(b"1")
        elif msg == "export":
            cs_export()
            main_socket.send(b"1")
        else:
            main_socket.send(b"0")


if __name__ == "__main__":
    main()
