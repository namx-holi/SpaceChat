
# TODO: A class that stores a message
# It has easy methods to convert to a packet to send.

# TODO: A class that stores a player message.
# These messages have a user associated with them.
# They are only sent to the terrain the player is on.

# TODO: A class that stores a server message.
# These messages are sent to all terrains.

# TODO: A helper method that converts a message to
# a packet. This is used to trade the token to login,
# as well as send the messages to the player.

"""
TODO: A class that manages all the connections.

It will have a socket that players can connect to.

The socket will require you to send your token to
log in.

This token can be sent multiple times to refresh the
session. Before sending messages, the token of the
player is checked and compared. If the login token is
invalid, the player will get an error message saying so.

When the token of the player is changed or the player
is logged out, the player will also recv a message
from this socket saying so.

As long as the token is valid, the player will recv
messages from their terrain, as well as the server.
"""