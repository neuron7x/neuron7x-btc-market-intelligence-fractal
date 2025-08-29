# Adapters and Extension Points

The toolkit decouples IO from the signal engines via an adapter layer.
Implementations subclass `btcmi.adapters.Adapter` and provide three hooks:

- `load()`: retrieve the input payload
- `validate(data, schema)`: check data against a JSON schema
- `emit(data)`: persist or transmit the output

The CLI uses `FileAdapter` by default to read and write local JSON files.
`APIAdapter` shows how the same interface can interact with a remote HTTP
endpoint. Custom adapters can plug in databases, message queues or other
systems by extending the base class and wiring them into the engines/CLI.
