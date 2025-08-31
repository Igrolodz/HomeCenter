from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, A
import signal
import time
import logging
import os

log_file = 'static/logs/dns_server.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
open(log_file, 'w').close()
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configure dnslib logger
dns_logger = logging.getLogger('dnslib')
dns_logger.setLevel(logging.INFO)
# Remove any existing handlers to avoid duplicate logs
dns_logger.handlers = []
# Add file handler
dns_logger.addHandler(logging.FileHandler(log_file))


# Simple DNS resolver, responds to queries for "homecenter.panel" with a fixed IP which you can edit however you'd like.
# I recommend to use NSSM (Non-Sucking Service Manager) to run this script as a service on Windows.
class DNSResolver(BaseResolver):
    def __init__(self):
        super().__init__()
        self.upstream_dns = "192.168.0.1"  # Router's default DNS

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        
        if str(qname) == "homecenter.panel." and qtype == "A":
            logging.info(f"DNS Query: {qname} ({qtype}) -> 192.168.0.111")
            reply.add_answer(RR(rname=qname, rtype=QTYPE.A, rdata=A("192.168.0.111")))
        else:
            try:
                # Forward the query using DNSServer
                upstream_request = request.send(self.upstream_dns)
                if upstream_request:
                    logging.info(f"DNS Query: {qname} ({qtype}) -> Forwarded")
                    return upstream_request
            except Exception as e:
                logging.info(f"DNS Query: {qname} ({qtype}) -> Not Found: {str(e)}")
                reply.add_answer(RR(rname=qname, rtype=QTYPE.A, rdata=A("0.0.0.0")))
        return reply

def run_server():
    resolver = DNSResolver()
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    server.start_thread()
    
    # Handle graceful shutdown on CTRL+C
    def signal_handler(sig, frame):
        logging.info("\nStopping DNS server...")
        server.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    logging.info("DNS Server running. Press CTRL+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    run_server()