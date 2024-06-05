# Ryu package:

Change

    ```
    from eventlet.wsgi import ALREADY_HANDLED
    ```

to

    ```
    import eventlet.wsgi
    ALREADY_HANDLED = getattr(eventlet.wsgi, "ALREADY_HANDLED", None)
    ```

Or use two virtual env

# Pre-commit:

- If you install QoA4ML from source, install the dev version or all version (editable or not) by:

  ```bash
  # editable
  pip install -e ".[dev]"
  # non-editable
  pip install ".[dev]"
  ```

- Installing dev version will automatically have pre-commit, then, install pre-commit:

  ```bash
  pre-commit install
  ```

- Pre-commit failed: pre-commit can't automatically add new update to staging so you have to manually stage the file update from pre-commit
- Run pre-commit for all files, not just staging:

  ```bash
  pre-commit run --all-files
  ```
