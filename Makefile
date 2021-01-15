.PHONY: build fedmsg-start clean build-test-image test-in-container test

UCHO_IMAGE_NAME = docker.io/usercont/ucho
UCHO_TEST_IMAGE_NAME = user-cont/ucho-test

build:
	docker build --tag ${UCHO_IMAGE_NAME} .

fedmsg-start: build
	docker run -it --net=host \
	--env FEDORA_MESSAGING_CONF=/home/ucho/.config/fedora.toml \
	-e REDIS_SERVICE_HOST=localhost \
	-v $(CURDIR)/fedora.toml:/home/ucho/.config/fedora.toml \
	${UCHO_IMAGE_NAME}


build-test-image: build
	docker build --tag ${UCHO_TEST_IMAGE_NAME} -f Dockerfile.test .

test-in-container: build-test-image
	docker run ${UCHO_TEST_IMAGE_NAME}

test:
	DEPLOYMENT='test' pytest --verbose --showlocals

clean:
	find . -name '*.pyc' -delete
