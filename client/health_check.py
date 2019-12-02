#!/usr/bin/env python3
import requests

r = requests.get("http://localhost:8081/v1/birds")

print(r.text)
