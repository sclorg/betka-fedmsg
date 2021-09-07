.PHONY: build fedmsg-start clean build-test-image test-in-container test

UCHO_IMAGE_NAME = quay.io/rhscl/betka-fedmsg
UCHO_TEST_IMAGE_NAME = user-cont/ucho-test
UNAME=$(shell uname)
ifeq ($(UNAME),Darwin)
	PODMAN := /usr/local/bin/docker
else
	PODMAN := /usr/bin/podman
endif

build:
	$(PODMAN) build --tag ${UCHO_IMAGE_NAME} .

fedmsg-start: build
	$(PODMAN) run -it --net=host \
		--env FEDORA_MESSAGING_CONF=/home/ucho/.config/fedora.toml \
		-e REDIS_SERVICE_HOST=localhost \
		-v $(CURDIR)/fedora.toml:/home/ucho/.config/fedora.toml \
		${UCHO_IMAGE_NAME}


build-test-image: build
	$(PODMAN) build --tag ${UCHO_TEST_IMAGE_NAME} -f Dockerfile.test .

test-in-container: build-test-image
	$(PODMAN) run ${UCHO_TEST_IMAGE_NAME}

test:
	DEPLOYMENT='test' pytest --verbose --showlocals

clean:
	find . -name '*.pyc' -delete
