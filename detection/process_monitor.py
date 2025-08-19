import psutil
import time

_connection_cache = {}
_cache_time = 0
CACHE_EXPIRY = 2

def get_process_name_from_port(port: int) -> str or None:
    global _connection_cache, _cache_time
    
    current_time = time.time()
    if current_time - _cache_time > CACHE_EXPIRY:
        try:
            connections = psutil.net_connections(kind='inet')
            new_cache = {}
            for conn in connections:
                if conn.pid and conn.laddr and conn.laddr.port:
                    try:
                        proc_name = psutil.Process(conn.pid).name()
                        new_cache[conn.laddr.port] = proc_name
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            _connection_cache = new_cache
            _cache_time = current_time
        except Exception as e:
            _connection_cache = {}
            print(f"Error refreshing process connection cache: {e}")
            
    return _connection_cache.get(port)
