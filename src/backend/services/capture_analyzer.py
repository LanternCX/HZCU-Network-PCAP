import json
import shutil
import subprocess
from datetime import datetime, timezone


class CaptureAnalyzer:
    def __init__(self, repository, tshark_path="tshark"):
        self.repository = repository
        self.tshark_path = shutil.which(tshark_path) if tshark_path else None

    def analyze(self, capture_id):
        capture = self.repository.get_capture(capture_id)
        if not capture:
            return
        self.repository.update_status(capture_id, "Analyzing")
        if not self.tshark_path:
            self.repository.update_status(
                capture_id,
                "Failed",
                "tshark is required to analyze PCAP/PCAPNG files. Install Wireshark CLI tools and retry analysis.",
            )
            return
        try:
            output = subprocess.check_output(
                [
                    self.tshark_path,
                    "-r",
                    capture["stored_path"],
                    "-T",
                    "json",
                ],
                text=True,
                stderr=subprocess.STDOUT,
            )
            self.repository.save_analysis(capture_id, self._parse_tshark(output))
        except Exception as exc:
            self.repository.update_status(capture_id, "Failed", f"Analysis failed. {exc}")

    def _parse_tshark(self, output):
        packets = []
        for item in json.loads(output):
            layers = item.get("_source", {}).get("layers", {})
            frame = layers.get("frame", {})
            ip = layers.get("ip", {})
            ipv6 = layers.get("ipv6", {})
            tcp = layers.get("tcp", {})
            udp = layers.get("udp", {})
            number = self._field(frame, "frame.number") or len(packets) + 1
            protocol = self._field(layers.get("_ws.col", {}), "_ws.col.Protocol") or self._protocol(layers)
            length = int(self._field(frame, "frame.len") or 0)
            packets.append(
                {
                    "number": int(number),
                    "timestamp": self._timestamp(self._field(frame, "frame.time_epoch")),
                    "src_ip": self._field(ip, "ip.src") or self._field(ipv6, "ipv6.src") or "",
                    "src_port": self._field(tcp, "tcp.srcport") or self._field(udp, "udp.srcport") or "",
                    "dst_ip": self._field(ip, "ip.dst") or self._field(ipv6, "ipv6.dst") or "",
                    "dst_port": self._field(tcp, "tcp.dstport") or self._field(udp, "udp.dstport") or "",
                    "protocol": protocol,
                    "length": length,
                    "details": self._details(layers, protocol, number, length),
                }
            )
        return packets

    def _details(self, layers, protocol, number, length):
        details = {"Frame": {"Number": str(number), "Length": f"{length} bytes"}}
        sections = [
            ("Ethernet", layers.get("eth"), ["eth.src", "eth.dst", "eth.type"]),
            ("IPv4", layers.get("ip"), ["ip.src", "ip.dst", "ip.proto", "ip.ttl"]),
            ("IPv6", layers.get("ipv6"), ["ipv6.src", "ipv6.dst", "ipv6.nxt", "ipv6.hlim"]),
            ("TCP", layers.get("tcp"), ["tcp.srcport", "tcp.dstport", "tcp.flags", "tcp.seq", "tcp.ack"]),
            ("UDP", layers.get("udp"), ["udp.srcport", "udp.dstport", "udp.length"]),
            ("ICMP", layers.get("icmp"), ["icmp.type", "icmp.code"]),
            ("DNS", layers.get("dns"), ["dns.qry.name", "dns.a", "dns.flags.response"]),
            ("HTTP", layers.get("http"), ["http.request.method", "http.host", "http.request.uri", "http.response.code"]),
        ]
        for name, layer, keys in sections:
            values = {key: self._field(layer, key) for key in keys if self._field(layer, key)}
            if values:
                details[name] = values
        summary = self._field(layers.get("_ws.col", {}), "_ws.col.Info") or f"{protocol} packet"
        details["Raw summary"] = {"Summary": summary}
        return details

    @staticmethod
    def _field(layer, key):
        if not isinstance(layer, dict):
            return ""
        value = layer.get(key)
        if isinstance(value, list):
            return value[0] if value else ""
        if isinstance(value, dict):
            return value.get("show") or value.get("showname") or ""
        return value

    @staticmethod
    def _protocol(layers):
        for name in ("http", "dns", "tcp", "udp", "icmp", "ip", "ipv6"):
            if name in layers:
                return name.upper()
        return "Other"

    @staticmethod
    def _timestamp(value):
        if not value:
            return ""
        try:
            return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
        except ValueError:
            return str(value)
