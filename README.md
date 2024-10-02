# qa-ai

## Requirements

- Python 3.7+
- pip

## Installation

Once the repository has been downloaded/cloned locally run:

1. `cd qa-ai`
2. `pip install .`

## Startup

`python qaai/app.py <listening_address> <listening_port>`

By default _listening_address_ = _0.0.0.0_ and _listening_port_ = _8088_.

## Testing

`curl -d '{"query":"something went wrong"}' -H "Content-Type: application/json" -X POST http://localhost:8088/prediction`

The endpoint is therefore _/predictions_.