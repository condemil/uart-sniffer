#!/usr/bin/env python3

import argparse
import ast
import sys
import threading
import termios
import time

import serial

GREEN = 32
YELLOW = 33

OUTPUT_STYLES = ("utf8", "bytes", "pybytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tx",
        metavar="TX",
        required=True,
        help="transfer uart bridge port to connect to",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--rx",
        metavar="RX",
        required=True,
        help="receive uart bridge port to connect to",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--separator",
        default="\\n",
        help="line separator in form of \\\\r, \\\\n, \\\\x00 etc",
        type=decode_separator,
    )
    parser.add_argument(
        "-o",
        "--output",
        default="pybytes",
        help="output style, one of: {}".format(", ".join(OUTPUT_STYLES)),
        type=str,
    )
    args = parser.parse_args()

    if args.output not in OUTPUT_STYLES:
        print("output style should be one of:", ", ".join(OUTPUT_STYLES))
        exit(1)

    sniff_tx = Sniff(args.tx, 115200, GREEN, "tx", args.separator, args.output)
    sniff_rx = Sniff(args.rx, 115200, YELLOW, "rx", args.separator, args.output)

    while threading.active_count() > 1:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            sniff_tx.alive = False
            sniff_rx.alive = False

    print()


def decode_separator(separator: str) -> bytes:
    return ast.literal_eval("b'" + separator + "'")


class Sniff(threading.Thread):
    def __init__(
        self,
        port: str,
        baudrate: int,
        color: int,
        prefix: str,
        separator: bytes,
        output_style: str,
    ):
        threading.Thread.__init__(self)

        self.port = port
        self.baudrate = baudrate
        self.color = color
        self.prefix = prefix
        self.separator = separator
        self.separator_len = len(separator)
        self.output_style = output_style

        self.serial = None
        self.alive = True
        self.connected = False
        self.setDaemon = True
        self.buffer = bytes()
        self.start()

    def connect(self):
        try:
            self.serial = serial.serial_for_url(
                self.port,
                self.baudrate,
                parity="N",
                rtscts=False,
                xonxoff=False,
                timeout=1,
            )
            self.connected = True
        except (serial.SerialException, termios.error) as e:
            print(e)
            time.sleep(1)

    def println(self):
        out = ""

        if self.output_style == "bytes":
            out = "".join("{:02x}{}".format(x, " ") for x in self.buffer).strip()

        if self.output_style == "pybytes":
            out = repr(self.buffer)[2:-1]

        if self.output_style == "utf8":
            out = self.buffer.decode()

        sys.stdout.write("\x1b[{}m{}: {}\x1b[0m\n".format(self.color, self.prefix, out))
        sys.stdout.flush()
        self.buffer = bytes()

    def read(self, cnt):
        out = b""
        while len(out) < cnt and self.alive:
            if not self.connected or not self.serial:
                self.connect()
                continue

            try:
                out += self.serial.read(1)
            except serial.SerialException as e:
                self.connected = False
                sys.stderr.write("serial exception: %s" % e)
                time.sleep(1)

        return out

    def run(self):
        while self.alive:
            self.buffer += self.read(1)

            if self.buffer[-self.separator_len :] == self.separator:
                self.println()
                continue


if __name__ == "__main__":
    main()
