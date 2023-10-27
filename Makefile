# Default target to run the application
.PHONY: all
all: run

# Build and run the application
.PHONY: run
run:
	docker-compose up --build

# Run end-to-end tests
.PHONY: test
test:
	docker-compose up --build tester
	# docker-compose down

# Stop and remove all Docker containers
.PHONY: clean
clean:
	docker-compose down

