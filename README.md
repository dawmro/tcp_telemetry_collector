# tcp_telemetry_collector
Program in client - server tcp architecture that collects telemetry data from PC and sends them to server.
Client written in Python, server in C.

Libre Hardware Monitor is being used as data source for WMI: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor


## Usage
1. compile tcp_receiver.c  with ``` sh gcc tcp_receiver.c ```
2. run ./a.out 
3. run python script
