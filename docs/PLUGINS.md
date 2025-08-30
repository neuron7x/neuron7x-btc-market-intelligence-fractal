# Runner plugins

The BTCMI tool discovers runner implementations via the `btcmi.runners`
entry point group.  Third-party packages can register new modes by
exposing a callable that matches the built-in runners' signature.

## Creating a plugin

1.  Define a function that accepts `(data, fixed_ts, out_path=None)` and
    returns a BTCMI result.
2.  Declare the entry point in your project's `pyproject.toml`:

    ```toml
    [project.entry-points."btcmi.runners"]
    "my-mode" = "my_package.module:my_runner"
    ```

3.  Install the package.  The CLI and API will automatically expose the
    new mode:

    ```bash
    btcmi run --mode my-mode --input payload.json
    ```
