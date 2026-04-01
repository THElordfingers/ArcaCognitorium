#!/bin/bash


self.claude_generated.connect(self._on_claude_generated)
self.claude_generate_error.connect(self._on_claude_generate_error)
