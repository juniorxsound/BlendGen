"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""

# Dependencies
from os import getcwd
from tabulate import tabulate
import bpy

# Components
from blendgen.renderer import Renderer
from blendgen.renderers import CyclesBackend
from blendgen.dataset import Dataset, DatasetOutputType
from blendgen.utils.callables import is_function


class Session:
    """"A session wrapper class used to manage dataset creation"""

    def __init__(self,
                 renderer=None,
                 dataset=None,
                 output_dir=f"{getcwd()}/data/toy_dataset/",
                 frame_start=0,
                 frame_length=1,
                 passes=None,
                 on_before_new_frame=None,
                 on_after_new_frame=None,
                 on_start=None,
                 on_complete=None):
        """Creates a session wrapper class used for a rendering session

        Keyword Arguments:
            renderer {Renderer} -- BlendGen Renderer instace (default: {None})
            dataset {Dataset} -- BlendGen Dataset instace (default: {None})
            output_dir {str} -- Dataset base path \
                (default: {"data/toy_dataset/"})
            frame_length {int} -- Length of sequence to render (default: {1})
            passes {list} -- A list of render passes (default: {None})
            on_before_new_frame {function} -- Callback called before a \
                new frame is rendered (default: {None})
            on_after_new_frame {function} -- Callback called after a \
                new frame is rendered (default: {None})
            on_start {function} -- Callback called before a \
                dataset is rendered (default: {None})
            on_complete {function} -- Callback called after a \
                dataset is rendered (default: {None})
        """
        self.__output_dir = output_dir
        self.__frame_start = frame_start
        self.__frame_length = frame_length

        if not isinstance(frame_start, int):
            raise ValueError("frame_start must be an integer")
        if not isinstance(frame_length, int) or frame_length <= 0:
            raise ValueError("frame_length must be a positive integer")

        # Save the dependency graph which needs to be evaluated for matrix updates
        self.__depsgraph = bpy.context.evaluated_depsgraph_get()

        # Save the callbacks
        self.__on_before_new_frame = on_before_new_frame
        self.__on_after_new_frame = on_after_new_frame
        self.__on_start = on_start
        self.__on_complete = on_complete

        # Create the dataset or assign the passed dataset
        self.__dataset = dataset if isinstance(dataset, Dataset) \
            else Dataset(prefix="",
                         output_type=DatasetOutputType.JSON,
                         output_dir=output_dir)

        if renderer is not None and not isinstance(renderer, Renderer):
            raise ValueError("renderer must be a Renderer instance")
        if renderer is not None and passes is not None:
            raise ValueError("passes cannot be supplied with an explicit renderer")

        # Create the renderer or assign the passed renderer.
        self.__blendgen_renderer = renderer or Renderer(
            backend=CyclesBackend(), passes=passes)

    def run(self):
        """Run the session and capture the dataset"""

        # If we have a callback registered, call it
        if is_function(self.__on_start):
            self.__on_start()

        # Iterate over all frames in sequence (request in Session constructor)
        for frame in range(self.__frame_start,
                           self.__frame_start + self.__frame_length):
            # Update the frame in the timeline
            bpy.context.scene.frame_set(frame)

            # Force update all data blocks
            self.update()

            # If we have a callback registered, call it
            if is_function(self.__on_before_new_frame):
                self.__on_before_new_frame(self)

            # Render a frame (with all passes and save the passes path)
            render_passes_paths = self.__blendgen_renderer.render(frame)

            # Save the passes to the dataset
            self.__dataset.add_frame(
                frame_num=frame,
                passes=render_passes_paths
            )

            # If we have a callback registered, call it
            if is_function(self.__on_after_new_frame):
                self.__on_after_new_frame(self)

        # Save the dataset index/attribute file
        self.__dataset.save()

        # If we have a callback registered, call it
        if is_function(self.__on_complete):
            self.__on_complete()

    def update(self):
        """Force-update data blocks, replacing Blender 2.7's ``scene.update``."""
        self.__depsgraph.update()

    @property
    def on_complete(self):
        """Getter for the on complete callback

        Returns:
            :function: -- The function assigned or None
        """
        return self.__on_complete

    @property
    def on_start(self):
        """Getter for the on start callback

        Returns:
            :function: -- The function assigned or None
        """
        return self.__on_start

    @property
    def on_before_new_frame(self):
        """Getter for the on before a new frame is rendered callback

        Returns:
            :function: -- The function assigned or None
        """
        return self.__on_before_new_frame

    @property
    def on_after_new_frame(self):
        """Getter for the on after a new frame is rendered callback

        Returns:
            :function: -- The function assigned or None
        """
        return self.__on_after_new_frame

    @on_complete.setter
    def on_complete(self, callback):
        """A setter for the on complete callback

        Arguments:
            callback {function} -- The callback to call when completed
        """
        self.__on_complete = callback

    @on_start.setter
    def on_start(self, callback):
        """A setter for the on start callback

        Arguments:
            callback {function} -- The callback to call when started
        """
        self.__on_start = callback

    @on_before_new_frame.setter
    def on_before_new_frame(self, callback):
        """A setter for the on new frame callback

        Arguments:
            callback {function} -- The callback to call before every new frame
        """
        self.__on_before_new_frame = callback

    @on_after_new_frame.setter
    def on_after_new_frame(self, callback):
        """A setter for the after new frame callback

        Arguments:
            callback {function} -- The callback to call after every new frame
        """
        self.__on_after_new_frame = callback

    @property
    def info(self):
        """Get a pretty printed ASCII table with the session info

        Returns:
            str -- The ASCII table string
        """
        blender_project = bpy.path.abspath("//")
        attrs = [[blender_project, self.__blendgen_renderer.backend.name,
                  self.__output_dir, self.__frame_length]]
        names = ["Blender Project", "Renderer Type",
                 "Output Directory", "Frames"]
        return tabulate(attrs, names, tablefmt="fancy_grid")
