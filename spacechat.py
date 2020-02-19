#!/usr/bin/env python3

from app import create_app#, cli

app = create_app()
# cli.register(app)

@app.shell_context_processor
def make_shell_context():
	return {}

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=7777, debug=False)
