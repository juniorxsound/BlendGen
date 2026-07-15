# BlendGen Makefile docker commands 💻
# Written by @juniorxsound <https://orfleisher.com>

dockerfile := docker/Dockerfile.cpu
docker_image_tag ?= blendgen:latest
jupyter_image_tag ?= blendgen-jupyter:latest
# Blender 5.1.2 has no official Linux ARM64 release. Docker Desktop emulates
# this x64 image on Apple Silicon so it can open Blender 5 files.
docker_platform := linux/amd64
runtime := --platform $(docker_platform)
blend_project := examples/blend/character_4_cams.blend
blender_flags := --background --python-exit-code 1

# If NVIDIA SMI is intalled use the GPU docker file and change the runtime to include all gpus
ifneq (, $(shell which nvidia-smi))
	runtime += --gpus all
	dockerfile = docker/Dockerfile.gpu
endif

# BlendGen main Docker commands 🛠
build-clean:
	docker build --platform $(docker_platform) --no-cache -f $(dockerfile) -t $(docker_image_tag) .

build:
	docker build --platform $(docker_platform) -f $(dockerfile) -t $(docker_image_tag) .

build-arm64:
	@echo "Blender 5.1.2 has no official Linux ARM64 build; use 'make build'."
	@exit 1

build-amd64:
	docker build --platform linux/amd64 -f docker/Dockerfile.cpu -t $(docker_image_tag)-amd64 .

shell:
	docker run $(runtime) -w /data --rm -it -v $(PWD):/data -t $(docker_image_tag) /bin/bash

build-jupyter:
	docker build -f docker/Dockerfile.jupyter -t $(jupyter_image_tag) .

jupyter: build-jupyter
	docker run --init -p 127.0.0.1:8083:8083 -w /data --rm -v $(PWD):/data $(jupyter_image_tag) jupyter notebook --ip 0.0.0.0 --port 8083 --allow-root

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
