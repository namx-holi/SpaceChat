from test_client import make_request, display_tiles

print("Running move_test\n")

print("Register a new user")
resp = make_request("register", {"username":"Mover", "password":"123"})

print("Logging in as new user")
resp = make_request("login", {"username":"Mover", "password":"123"})
token = resp["token"]

print("Observe")
resp = make_request("observe", {"token":token})
tiles = resp["tiles"]
display_tiles(tiles)
print("")

print("Leaving a note")
resp = make_request("note", {"token":token, "msg":"Hello, World!"})

print("Moving North")
resp = make_request("move", {"token":token, "direction":"North"})

print("Observing after leaving note")
resp = make_request("observe", {"token":token})
tiles = resp["tiles"]
display_tiles(tiles)
print("")

print("Reading note left")
resp = make_request("inspect", {"token":token, "direction":"South"})

print("Logout")
resp = make_request("logout", {"token":token})
