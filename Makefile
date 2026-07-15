# BlendGen Makefile docker commands 💻
# Written by @juniorxsound <https://orfleisher.com>

dockerfile := "docker/Dockerfile.cpu"
docker_image_tag := "juniorxsound/blendgen:latest"
runtime :=
blend_project := "examples/blend/character_4_cams.blend"

# If NVIDIA SMI is intalled use the GPU docker file and change the runtime to include all gpus
ifneq (, $(shell which nvidia-smi))
	runtime = --gpus all
	dockerfile = "docker/Dockerfile.gpu"
endif

# BlendGen main Docker commands 🛠
build-clean:
	docker build --no-cache -f ./$(dockerfile) -t $(docker_image_tag) ./

build:
	docker build -f ./$(dockerfile) -t $(docker_image_tag) ./

shell:
	docker run $(runtime) -w /data --rm -it -v $(PWD):/data -t $(docker_image_tag) /bin/bash

jupyter:
	docker run $(runtime) -p 8083:8083 -w /data --rm -it -v $(PWD):/data -t $(docker_image_tag) jupyter notebook --ip 0.0.0.0 --port 8083 --allow-root

# BlendGen util Docker commands 🧹
lint:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) pylint ./blendgen/

test:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) python3.7m -m unittest tests/*_test.py

clean:
	rm ./data/toy_dataset/**/*.png & rm ./data/toy_dataset/**/*.exr & rm ./data/toy_dataset/*.json


# Examples Docker commands 🔤
simple:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/simple.py --background

callbacks:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/callbacks.py --background

render_passes:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/render_passes.py --background

advanced:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/advanced.py --background

bb_3D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/bounding_box_3D.py --background

bb_2D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/bounding_box_2D.py --background

pose_3D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/pose_3D.py --background

pose_2D:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/pose_2D.py --background

toy_dataset:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/toy_dataset.py --background

attributes_only:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/attributes_only.py --background

multicam:
	docker run $(runtime) -w /data --rm -v $(PWD):/data -t $(docker_image_tag) blender -b ${blend_project} --python examples/multicam.py --background
