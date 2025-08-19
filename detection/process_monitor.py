import psutil

_connection_cache = {}
_cache_time = 0

def get_process_name_from_port(port, protocol='tcp'):
    global _connection_cache, _cache_time
    import time
    
    current_time = time.time()
    if current_time - _cache_time > 2:
        try:
            connections = psutil.net_connections(kind=protocol)
            _connection_cache = {(c.laddr.port): psutil.Process(c.pid).name() for c in connections if c.pid}
            _cache_time = current_time
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            _connection_cache = {}
            
    return _connection_cache.get(port)
