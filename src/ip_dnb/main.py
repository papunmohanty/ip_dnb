from ipaddress import IPv4Address
import os
import re
from pathlib import Path

from dotenv import load_dotenv
import requests
from rich import print
from tinydb import Query, TinyDB
from typer import Typer

load_dotenv()

API_KEY = os.getenv("IPLOCATE_API_KEY")
app = Typer()


class RateLimitError(Exception):
    """API call rate limit error"""
    pass


def filter_private_and_loopback_ip_address(ip_addresses: list):
    if not ip_addresses:
        return list()
    return list(
        filter(
            lambda ip_addr: not(IPv4Address(ip_addr).is_loopback) and not(IPv4Address(ip_addr).is_private)
            , ip_addresses)
    )


def validate_ip(public_ip_address: str):
    ip_locator_url = f"https://iplocate.io/api/lookup/{public_ip_address}?apikey={API_KEY}"
    res = requests.get(ip_locator_url)
    if res.status_code == 429:
        raise RateLimitError("Rate limit error...")
    return res.json()


@app.command()
def main(files: list[Path]):
    for file in files:
        if Path(file).is_file():
            with open(file, 'r') as file_obj:
                log_data = file_obj.read()

            ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', log_data)
            public_ip_addresses = filter_private_and_loopback_ip_address(ip_addresses)
            for pub_ip in public_ip_addresses:
                # Query the DB for the Blocked IP
                with TinyDB("blocked_ips.json") as blocked_ips_table:
                    query = Query()
                    table_response = blocked_ips_table.table("blocked_ips").search(query.ip == pub_ip)
                    if table_response:
                        # print(f"[BLOCKED] IP {pub_ip} has been blocked due to suspicious activity.")
                        continue
                res = validate_ip(pub_ip)

                with TinyDB("blocked_ips.json") as blocked_ips_table:
                    query = Query()
                    table_response = blocked_ips_table.table("blocked_ips").search(query.ip == pub_ip)
                    if (res["country"] in ["China", "Russia", "North Korea"]) or (res['privacy']['is_tor']):
                        blocked_ips_table.table("blocked_ips").insert(
                            {
                                "ip": pub_ip,
                                "country": res["country"],
                                "is_tor": res['privacy']['is_tor'],
                            }
                        )
                        print(f"[BLOCKED] IP {pub_ip} has been blocked due to suspicious activity.")
        else:
            print(f"Error reading file {file}!! Check if this file exists or not?")


if __name__ == "__main__":
    app()
