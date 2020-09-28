build:
	docker build . -t barrymoo/ai4e-example:latest

serve:
	docker run -p 8081:80 bmooreii/ai4e-example:latest
