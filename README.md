# Trace Context Parser

Inspect version-00 traceparent headers and derive synthetic child contexts.

All bundled examples use synthetic data.

## Run

Requires Python 3.9 or later; no third-party packages or network access are needed.

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

Run these commands from this repository's directory. The demo can also be launched from any directory by passing the absolute path to `main.py`.

## How it works

The parser checks the exact version-00 field shape, lowercase hexadecimal IDs, and nonzero trace/span identifiers. Sampling is read from the lowest flag bit. Header-name extraction is case insensitive and rejects duplicate case variants. A child context preserves the trace ID, requires a different parent/span ID, and clears reserved flag bits.

Parsing is bounded by the fixed 55-character format. The implementation follows the relevant version-00 field definitions in the [W3C Trace Context recommendation](https://www.w3.org/TR/2021/REC-trace-context-1-20211123/#traceparent-header).

## Reuse

```python
from main import parse_traceparent

incoming = "00-11111111111111111111111111111111-2222222222222222-01"
context = parse_traceparent(incoming)
assert context.sampled
child = context.child("3333333333333333", sampled=False)
assert child.trace_id == context.trace_id
assert child.to_header().endswith("-00")
```

## Demo behavior

Run `python3 main.py --header 00-11111111111111111111111111111111-2222222222222222-00` to inspect an unsampled context. Default IDs and the derived child are synthetic fixed values, chosen only to keep output reproducible.

## Boundaries

This focused lab supports only version `00`; it deliberately rejects future versions and does not implement `tracestate`, the complete propagation processing model, or ID generation. `to_header()` preserves parsed flags for pass-through use; `child()` emits only the sampled flag. Incoming context is untrusted metadata, not caller identity. A real tracer must generate suitable fresh span IDs and decide its own recording policy.

## Verification

`test_main.py` exercises boundary conditions, invalid inputs, and meaningful behavior specific to this implementation. The default demo is deterministic and completes without external services. See the collection's verification report for the recorded run; run the commands above to verify this repository independently.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
