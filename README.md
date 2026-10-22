# Event Store

Append-only event stream with optimistic-version checks and SHA-256 hash chaining.

Python 3.11+; standard library only.

## Run tests

```sh
python -m unittest discover -s . -p 'test_core.py' -v
```

`core.py` implements in-memory append-only event streams with optimistic concurrency and hash chaining. `test_core.py` demonstrates version-conflict detection. GitHub Actions tests against Python 3.11–3.13.

**Scope:** Portfolio reference implementation; not a persistent or audited production event store. A deployed event-sourcing system requires durable storage, migration plans, authentication, observability and operational controls.



## Project Information

This project is developed using Python.
It includes an event store implementation and automated tests.
