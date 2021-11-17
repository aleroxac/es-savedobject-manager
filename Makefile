build:
	@mkdir .build
	@cp docker/{Dockerfile,.dockerignore} src/{app.py,requirements.txt} .build/
	@cd .build && DOCKER_BUILDKIT=1 docker build -t aleroxac/es-savedobject-manager:1.0.0 .
	@rm -rf .build