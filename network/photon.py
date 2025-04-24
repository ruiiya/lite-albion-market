import signal
import sys
import threading
import logging
from photon_packet_parser import PhotonPacketParser
from scapy.all import UDP, sniff

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Photon:
    def __init__(self) -> None:
        logger.info("Initializing Photon packet handler")
        self.parser = PhotonPacketParser(
            self.on_event, self.on_request, self.on_response
        )
        self.stop_sniffing = threading.Event()
        self.sniffing_thread = threading.Thread(target=self.start_sniffing)
        self.sniffing_thread.daemon = True
        self.sniffing_thread.start()
        logger.info("Photon sniffing thread started")

        self.function_request_map = {}
        self.function_event_map = {}

        signal.signal(signal.SIGINT, self.handle_exit)

    def start_sniffing(self):
        logger.info("Starting UDP packet capture on ports 5056 and 5055")
        try:
            sniff(
                prn=self.packet_callback, filter="udp and (port 5056 or port 5055)", store=0
            )
        except Exception as e:
            logger.error(f"Error in packet sniffing: {str(e)}", exc_info=True)

    def packet_callback(self, packet):
        if UDP in packet:
            udp_payload = bytes(packet[UDP].payload)

            try:
                self.parser.HandlePayload(udp_payload)
            except Exception as e:
                logger.debug(f"Error handling payload: {str(e)}")

    def map_request(self, id, func):
        logger.debug(f"Mapping request handler for ID: {id}")
        self.function_request_map[id] = func

    def map_event(self, id, func):
        logger.debug(f"Mapping event handler for ID: {id}")
        self.function_event_map[id] = func

    def handle_exit(self, signum, frame):
        logger.info("Received exit signal, shutting down")
        self.stop_sniffing.set()
        sys.exit(0)

    def stop(self):
        logger.info("Stopping packet sniffing")
        self.stop_sniffing.set()
        self.sniffing_thread.join()
        logger.info("Packet sniffing stopped")

    def on_event(self, data):
        event_id = data.parameters.get(252)
        if event_id in self.function_event_map:
            self.function_event_map[event_id](data.parameters)

    def on_request(self, data):
        request_id = data.parameters.get(253)
        if request_id in self.function_request_map:
            self.function_request_map[request_id](data.parameters)

    def on_response(self, data):
        pass