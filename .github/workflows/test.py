name: Python Bot

on:
  [push, pull]

jobs:
  run-python:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Run Python Code
        run: |
          echo 'print("It works!")' > script.py
          python script.py
