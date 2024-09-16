import json
import signal
import sys
import threading
from photon_packet_parser import PhotonPacketParser
from scapy.all import UDP, sniff

class Photon:
    def __init__(self) -> None:
        self.parser = PhotonPacketParser(
            self.on_event, self.on_request, self.on_response
        )
        self.stop_sniffing = threading.Event()
        self.sniffing_thread = threading.Thread(target=self.start_sniffing)
        self.sniffing_thread.daemon = True
        self.sniffing_thread.start()

        self.function_map = {}

        signal.signal(signal.SIGINT, self.handle_exit)

    def start_sniffing(self):
        sniff(
            prn=self.packet_callback, filter="udp and (port 5056 or port 5055)", store=0
        )

    def packet_callback(self, packet):
        if UDP in packet:
            udp_payload = bytes(packet[UDP].payload)

            try:
                self.parser.HandlePayload(udp_payload)
            except:
                pass

    def map(self, id, func):
        self.function_map[id] = func

    def handle_exit(self, signum, frame):
        self.stop_sniffing.set()
        sys.exit(0)

    def stop(self):
        self.stop_sniffing.set()
        self.sniffing_thread.join()

    def on_event(self, data):
        pass

    def on_request(self, data):
        if data.parameters[253] in self.function_map:
            self.function_map[data.parameters[253]](data.parameters)
        pass

    def on_response(self, data):
        pass