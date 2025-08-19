SIGNATURES = [
    b"evil_command_from_attacker",
    b"malware_beacon_packet"
]

def find_signature(payload: bytes) -> bool:
    for sig in SIGNATURES:
        if sig in payload:
            return True
    return False
