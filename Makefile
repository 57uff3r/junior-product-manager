ingest:
	poetry run python ./ingest.py

run:
	poetry run streamlit run app.py

build:
	docker build -t jpm . --progress=plain --no-cache
