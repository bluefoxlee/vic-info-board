name: Airport Update Ferry

on:
  schedule:
    - cron: '*/5 * * * *'  # 每5分鐘跑一次
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4

      - name: Run airport ferry scraper
        run: |
          python airport-ferry-scraper.py

      - name: Commit and push changes
        run: |
          git config --global user.email "github-actions@github.com"
          git config --global user.name "github-actions"
          git add -f docs/data/airport-ferry.json
          git commit -m "Auto update airport ferry JSON [skip ci]" || echo "No changes to commit"
          git push
