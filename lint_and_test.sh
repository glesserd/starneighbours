echo "----------------"
uv run ruff format .

echo "----------------"
uv run ruff check --fix .

echo "----------------"
uv run mypy .

echo "----------------"
uv run pytest .
