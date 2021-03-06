#! /usr/bin/env python

from __future__ import print_function
from builtins import str
import sys
import os

from vmrunner import vmrunner
import socket
# Get an auto-created VM from the vmrunner
vm = vmrunner.vms[0]

def UDP_test(trigger_line):
  print("<Test.py> Performing UDP tests")
  HOST, PORT = "10.0.0.55", 4242
  sock = socket.socket
  # SOCK_DGRAM is the socket type to use for UDP sockets
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  # NOTE: This is necessary for the test to exit after the VM has
  # been shut down due to a VM timeout
  sock.settimeout(20)

  data = "Lucky"
  sock.sendto(data, (HOST, PORT))
  received = sock.recv(1024)

  print("<Test.py> Sent:     {}".format(data))
  print("<Test.py> Received: {}".format(received))
  if received != data: return False

  data = "Luke"
  sock.sendto(data, (HOST, PORT))
  received = sock.recv(1024)

  print("<Test.py> Sent:     {}".format(data))
  print("<Test.py> Received: {}".format(received))
  if received != data: return False

  data = "x" * 1472
  sock.sendto(data, (HOST, PORT))
  received = sock.recv(1500)
  if received != data:
      print("<Test.py> Did not receive long string: {}".format(received))
      return False

  data = "x" * 9216 # 9216 is apparently default max for MacOS
  sock.sendto(data, (HOST, PORT))
  received = bytearray()
  while (len(received) < len(data)):
        received.extend(sock.recv(len(data)))
        print("RECEIVED: ", len(received))
  if received != data:
      print("<Test.py> Did not receive mega string (64k)")
      return False

  vm.exit(0, "Test completed without errors")

# Add custom event-handler
vm.on_output("UDP test service", UDP_test)

if len(sys.argv) > 1:
    vm.boot(image_name=str(sys.argv[1]))
else:
    # Boot the VM, taking a timeout as parameter
    vm.cmake().boot(30,image_name="net_udp").clean()
