# UART Sniffer

A script that allows to use two UART bridges to sniff UART fraffic between two MCUs.
This is useful as many smart devices from xiaomi and sonoff use separate Wi-Fi modules (ESP8266 or similar) to communicate with main MCU (STM32) over UART.

```
                                            -------
   ----------         ----------           | MCU 1 |
  |          |       |   UART   |  RX       -------
  |          | ----- | BRIDGE 1 | -----------|   |
  | Computer |        ----------             |   |
  |          |        ----------             |   |----
  |          | ----- |   UART   |  RX       -------   |
   ----------        | BRIDGE 2 | ------   | MCU 2 |  |
                      ----------       |    -------   |
                                        --------------
```

```
./sniff.py -h
usage: sniff.py [-h] -t TX -r RX [-s SEPARATOR] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -t TX, --tx TX        transfer uart bridge port to connect to
  -r RX, --rx RX        receive uart bridge port to connect to
  -s SEPARATOR, --separator SEPARATOR
                        line separator in form of \\r, \\n, \\x00 etc
  -o OUTPUT, --output OUTPUT
                        output style, one of: utf8, bytes, pybytes
```
