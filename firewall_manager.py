import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
RULE_PREFIX = "PyFire_"

def _run_netsh_command(command, check=True):
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=check, 
            creationflags=subprocess.CREATE_NO_WINDOW,
            encoding='utf-8',
            errors='ignore'
        )
        logging.info(f"Successfully executed: {' '.join(command)}")
        return result
    except FileNotFoundError:
        logging.error("`netsh` command not found. Ensure you are on Windows and it's in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {' '.join(command)}")
        logging.error(f"Return Code: {e.returncode}\nOutput:\n{e.stderr}")
        return None

def block_ip(ip_address: str):
    rule_name = f"{RULE_PREFIX}{ip_address}"
    command = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rule_name}", "dir=out", "action=block", f"remoteip={ip_address}"
    ]
    if not rule_exists(rule_name):
        return _run_netsh_command(command)

def unblock_ip(ip_address: str):
    rule_name = f"{RULE_PREFIX}{ip_address}"
    command = [
        "netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"
    ]
    return _run_netsh_command(command)

def rule_exists(rule_name):
    command = ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"]
    result = _run_netsh_command(command, check=False)
    return result and "No rules match the specified criteria." not in result.stdout

def sync_rules_with_state(app_state):
    command = ["netsh", "advfirewall", "firewall", "show", "rule", f"name={RULE_PREFIX}*", "verbose"]
    result = _run_netsh_command(command, check=False)
    if result and result.stdout:
        lines = result.stdout.splitlines()
        for line in lines:
            if line.strip().startswith("RemoteIP"):
                ip = line.split(":", 1)[-1].strip()
                if ip.lower() != 'any':
                    app_state.add_blocked_ip(ip)
    
    logging.info(f"Synced {len(app_state.get_blocked_ips())} rules from Windows Firewall.")
