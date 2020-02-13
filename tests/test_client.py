
import requests

BASE_URL = "http://localhost:7777/api"


def make_request(endpoint, json):
	url = f"{BASE_URL}/{endpoint}"
	r = requests.post(url=url, json=json)
	resp = r.json()
	print(resp)
	print("")
	return resp



def read_broadcast(json):
	url = f"{BASE_URL}/broadcast"
	r = requests.get(url=url, json=json, stream=True)

	for line in r.iter_lines(chunk_size=1, decode_unicode=True):
		if line:
			print(line)



def display_tiles(tiles):
	for row in tiles:
		for col in row:
			print(col, end=" ")
		print("")
