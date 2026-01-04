import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agent import build_agent

agent = build_agent()
