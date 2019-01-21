.PHONY: build fedmsg-start clean build-test-image test-in-container test

UCHO_IMAGE_NAME = docker.io/usercont/ucho
UCHO_TEST_IMAGE_NAME = user-cont/ucho-test

build:
	docker build --tag ${UCHO_IMAGE_NAME} .

fedmsg-start: build
	docker run -it --net=host \
	-e REDIS_BROKER='redis://localhost:6379/0' \
	-e REDIS_BACKEND='redis://localhost:6379/0' \
	${UCHO_IMAGE_NAME}


build-test-image: build
	docker build --tag ${UCHO_TEST_IMAGE_NAME} -f Dockerfile.test .

test-in-container: build-test-image
	docker run ${UCHO_TEST_IMAGE_NAME}

test:
	DEPLOYMENT='test' pytest --verbose --showlocals

clean:
	find . -name '*.pyc' -delete
