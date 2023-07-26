"""Parse the W3C version-00 traceparent field and derive an outbound child context."""
import argparse
from dataclasses import asdict, dataclass
import json
import re


TRACE_ID = re.compile(r"[0-9a-f]{32}")
PARENT_ID = re.compile(r"[0-9a-f]{16}")
HEADER = re.compile(r"00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})")


