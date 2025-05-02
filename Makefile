.PHONY: run clean_db


run:
	poetry run uvicorn app.main:app


clean_db:
	poetry run scripts\clean_db.py