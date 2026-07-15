# BlendGen Makefile docker commands 💻
# Written by @juniorxsound <https://orfleisher.com>

dockerfile := docker/Dockerfile.cpu
docker_image_tag ?= blendgen:latest
runtime :=
blend_project := examples/blend/character_4_cams.blend
blender_flags := --background --python-exit-code 1

host_arch := $(shell uname -m)
ifeq ($(host_arch),x86_64)
	docker_arch := amd64
else ifeq ($(host_arch),aarch64)
	docker_arch := arm64
else
	docker_arch := $(host_arch)
endif
docker_platform ?= linux/$(docker_arch)

# If NVIDIA SMI is intalled use the GPU docker file and change the runtime to include all gpus
ifneq (, $(shell which nvidia-smi))
	runtime = --gpus all
	dockerfile = docker/Dockerfile.gpu
endif

# BlendGen main Docker commands 🛠
build-clean:
	docker build --platform $(docker_platform) --no-cache -f $(dockerfile) -t $(docker_image_tag) .

build:
	docker build --platform $(docker_platform) -f $(dockerfile) -t $(docker_image_tag) .

build-arm64:
	docker build --platform linux/arm64 -f docker/Dockerfile.cpu -t $(docker_image_tag)-arm64 .

build-amd64:
	docker build --platform linux/amd64 -f docker/Dockerfile.cpu -t $(docker_image_tag)-amd64 .

shell:
	docker run $(runtime) -w /data --rm -it -v $(PWD):/data -t $(docker_image_tag) /bin/bash

jupyter:
	docker run $(runtime) -p 8083:8083 -w /data --rm -it -v $(PWD):/data -t $(docker_image_tag) jupyter notebook --ip 0.0.0.0 --port 8083 --allow-root

# BlendGen util Docker commands 🧹
lint:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) pylint ./blendgen/

test:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) python3 -m unittest discover -s tests -p '*_test.py'

clean:
	rm ./data/toy_dataset/**/*.png & rm ./data/toy_dataset/**/*.exr & rm ./data/toy_dataset/*.json


# Examples Docker commands 🔤
simple:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/simple.py

callbacks:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/callbacks.py

render_passes:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/render_passes.py

advanced:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/advanced.py

bb_3D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/bounding_box_3D.py

bb_2D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/bounding_box_2D.py

pose_3D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/pose_3D.py

pose_2D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/pose_2D.py

toy_dataset:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/toy_dataset.py

attributes_only:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/attributes_only.py

multicam:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender $(blender_flags) $(blend_project) --python examples/multicam.py
