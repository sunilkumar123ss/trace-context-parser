"""Parse the W3C version-00 traceparent field and derive an outbound child context."""
import argparse
from dataclasses import asdict, dataclass
import json
import re


TRACE_ID = re.compile(r"[0-9a-f]{32}")
PARENT_ID = re.compile(r"[0-9a-f]{16}")
HEADER = re.compile(r"00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})")


@dataclass(frozen=True)
class TraceParent:
    trace_id: str
    parent_id: str
    flags: int

    def __post_init__(self):
        if not isinstance(self.trace_id, str) or not TRACE_ID.fullmatch(self.trace_id) or int(self.trace_id, 16) == 0:
            raise ValueError("trace_id must be 32 lowercase hex digits and nonzero")
        if not isinstance(self.parent_id, str) or not PARENT_ID.fullmatch(self.parent_id) or int(self.parent_id, 16) == 0:
            raise ValueError("parent_id must be 16 lowercase hex digits and nonzero")
        if type(self.flags) is not int or not 0 <= self.flags <= 255:
            raise ValueError("flags must be an integer byte")

    @property
    def sampled(self):
        return bool(self.flags & 1)

    def to_header(self):
        return "00-{}-{}-{:02x}".format(self.trace_id, self.parent_id, self.flags)

    def child(self, new_parent_id, sampled=None):
        if new_parent_id == self.parent_id:
            raise ValueError("a child requires a different parent/span ID")
        if sampled is not None and type(sampled) is not bool:
            raise ValueError("sampled must be bool or None")
        sampled = self.sampled if sampled is None else sampled
        return TraceParent(self.trace_id, new_parent_id, 1 if sampled else 0)


def parse_traceparent(value):
    if not isinstance(value, str):
        raise ValueError("traceparent must be a string")
    match = HEADER.fullmatch(value)
    if match is None:
        raise ValueError("expected exactly a version-00 traceparent with lowercase hexadecimal fields")
    trace_id, parent_id, flags = match.groups()
    return TraceParent(trace_id, parent_id, int(flags, 16))


def extract_traceparent(headers):
    values = [value for key, value in headers.items() if isinstance(key, str) and key.lower() == "traceparent"]
    if not values:
        return None
    if len(values) != 1:
        raise ValueError("multiple traceparent header fields are ambiguous")
    return parse_traceparent(values[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--header", default="00-11111111111111111111111111111111-2222222222222222-01",
                        help="traceparent field value; default uses synthetic IDs")
    args = parser.parse_args()
    try:
        context = parse_traceparent(args.header)
    except ValueError as exc:
        parser.error(str(exc))
    child_id = "3333333333333333" if context.parent_id != "3333333333333333" else "4444444444444444"
    print(json.dumps({"parsed": asdict(context), "sampled": context.sampled,
                      "synthetic_child": context.child(child_id).to_header()}, indent=2))


if __name__ == "__main__":
    main()
