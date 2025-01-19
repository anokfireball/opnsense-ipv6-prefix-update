import os

import requests

HOST = os.environ["OPNSENSE_HOST"]
PORT = os.environ["OPNSENSE_PORT"]
SSL = os.environ["OPNSENSE_SSL"] == "true"
BASE_URL = f"http{'s' if SSL else ''}://{HOST}:{PORT}"
SESSION = requests.Session()
SESSION.auth = (os.environ["OPNSENSE_KEY"], os.environ["OPNSENSE_SECRET"])
SESSION.verify = os.environ["OPENSENSE_VERIFY_SSL"] == "true"

IPV6_PREFIX_LENGTH = int(os.environ["IPV6_PREFIX_LENGTH"])
if IPV6_PREFIX_LENGTH < 1 or int(IPV6_PREFIX_LENGTH) > 128:
    raise ValueError("IPV6_PREFIX_LENGTH must be valid IPv6 prefix length [1-128]")

def get_prefix():
    r = SESSION.get(f"{BASE_URL}/api/diagnostics/interface/getRoutes")
    routes = r.json()
    for route in routes:
        if route["destination"].endswith(f"/{IPV6_PREFIX_LENGTH}"):
            return route["destination"]
    else:
        raise RuntimeError("No matching IPV6 prefix found!")


def find_selected(obj):
    for key, value in obj.items():
        if "selected" in value and value["selected"] == 1:
            return key
    else:
        return ""


def update_shaper():
    prefix = get_prefix()

    r = SESSION.get(f"{BASE_URL}/api/trafficshaper/settings/searchRules")
    rules = r.json()
    changed = False
    for rule in rules["rows"]:
        if rule["proto"] == "ipv6" and rule["interface"] == "WAN":
            uuid = rule["uuid"]
            r = SESSION.post(f"{BASE_URL}/api/trafficshaper/settings/getrule/{uuid}")
            rule = r.json()["rule"]

            old = None
            src = find_selected(rule["source"])
            if src != "any" and src != prefix:
                changed = True
                old = src
                src = prefix
            dst = find_selected(rule["destination"])
            if dst != "any" and dst != prefix:
                changed = True
                old = dst
                dst = prefix

            if changed:
                print(f"prefix changed from {old} to {prefix}")

            rule = {
                "rule": {
                    "description": rule["description"],
                    "destination_not": rule["destination_not"],
                    "destination": dst,
                    "direction": find_selected(rule["direction"]),
                    "dscp": find_selected(rule["dscp"]),
                    "dst_port": rule["dst_port"],
                    "enabled": rule["enabled"],
                    "interface": find_selected(rule["interface"]),
                    "interface2": find_selected(rule["interface2"]),
                    "iplen": rule["iplen"],
                    "proto": find_selected(rule["proto"]),
                    "sequence": rule["sequence"],
                    "source_not": rule["source_not"],
                    "source": src,
                    "src_port": rule["src_port"],
                    "target": find_selected(rule["target"]),
                }
            }
            r = SESSION.post(
                f"{BASE_URL}/api/trafficshaper/settings/setRule/{uuid}",
                json=rule,
            )
            if r.status_code != 200:
                raise RuntimeError(f"error {r.status_code} updating shaper rule {rule}")
    if changed:
        r = SESSION.post(f"{BASE_URL}/api/trafficshaper/service/reconfigure/")
        if r.status_code != 200:
            raise RuntimeError(f"error {r.status_code} applying shaper rules")

if __name__ == "__main__":
    update_shaper()
    print("done")
