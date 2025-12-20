.PHONY: build run clean test docker-build docker-run

build:
	go build -o protection-bot .

run:
	go run main.go

clean:
	rm -f protection-bot
	rm -f protection.db

test:
	go test -v ./...

docker-build:
	docker build -t protection-bot:latest .

docker-run:
	docker run -p 5000:5000 \
		-e LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET} \
		-e LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN} \
		protection-bot:latest

install:
	go mod download

dev:
	go run main.go

prod:
	CGO_ENABLED=1 go build -ldflags="-w -s" -o protection-bot .

logs:
	tail -f logs/bot.log
