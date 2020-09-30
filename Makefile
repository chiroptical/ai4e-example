build:
	docker build . -t barrymoo/ai4e-example:latest

stop:
	./scripts/stop-container.sh

serve:
	docker run -p 8081:80 barrymoo/ai4e-example:latest

format:
	black .
