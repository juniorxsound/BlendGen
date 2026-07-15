"""BlendGen - Written by @juniorxsound <https://orfleisher.com>"""
import bpy
import bpy_extras
from mathutils import Matrix

from blendgen.utils.callables import is_function
from blendgen.utils.scene import bounding_box_to_world_positions, clamp, select

__all__ = [
    "bounding_box_to_world_positions",
    "camera_view_bounds_2d",
    "clamp",
    "get_camera_matrices",
    "get_intrinsic_matrix",
    "get_pose_bone_world_matrix",
    "get_rt_matrix",
    "get_screen_coords",
    "get_sensor_fit",
    "get_sensor_size",
    "is_function",
    "select",
]


def camera_view_bounds_2d(scene, cam_ob, me_ob):
    """
    Returns camera space bounding box of mesh object.

    Negative 'z' value means the point is behind the camera.

    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.

    Thanks to the wonderful
    https://blender.stackexchange.com/questions/7198/save-the-2d-bounding-box-of-an-object-in-rendered-image-to-a-text-file

    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg me: Untransformed Mesh.
    :type me: :class:`bpy.types.Mesh`
    :return: a Box object (call its to_tuple() method to get x, y, width and height)
    :rtype: :class:`Box`
    """

    mat = cam_ob.matrix_world.normalized().inverted()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh_eval = me_ob.evaluated_get(depsgraph)
    me = mesh_eval.to_mesh()
    me.transform(me_ob.matrix_world)
    me.transform(mat)

    camera = cam_ob.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    camera_persp = camera.type != 'ORTHO'

    lx = []
    ly = []

    for v in me.vertices:
        co_local = v.co
        z = -co_local.z

        if camera_persp:
            if z == 0.0:
                lx.append(0.5)
                ly.append(0.5)
            # Does it make any sense to drop these?
            # if z <= 0.0:
            #    continue
            else:
                frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    min_x = clamp(min(lx), 0.0, 1.0)
    max_x = clamp(max(lx), 0.0, 1.0)
    min_y = clamp(min(ly), 0.0, 1.0)
    max_y = clamp(max(ly), 0.0, 1.0)

    mesh_eval.to_mesh_clear()

    r = scene.render
    fac = r.resolution_percentage * 0.01
    dim_x = r.resolution_x * fac
    dim_y = r.resolution_y * fac

    # Sanity check
    if round((max_x - min_x) * dim_x) == 0 or round((max_y - min_y) * dim_y) == 0:
        return (0, 0, 0, 0)

    return (
        round(min_x * dim_x),            # X
        round(dim_y - max_y * dim_y),    # Y
        round((max_x - min_x) * dim_x),  # Width
        round((max_y - min_y) * dim_y)   # Height
    )


def get_pose_bone_world_matrix(armature_object, bone_name):
    """Get a pose bone's world matrix

    Arguments:
        armature_object {`bpy.types.Object`} -- The armature's object in the scene
        pose_bone {`str`} -- The pose bone name to transform

    Returns:
        {`mathutils.Matrix`} -- The world matrix for the pose bone
    """
    return armature_object.matrix_world @ armature_object.pose.bones[bone_name].matrix


def get_screen_coords(world_position, renderer):
    """Utility to get screen coordinates of a world vector

    Arguments:
        world_position {`mathutils.Vector`} -- The vector 3 to transform
        renderer {`blendgen.renderer.Renderer} -- The blendgen renderer instance

    Returns:
        [type] -- [description]
    """
    cam_space_coords = bpy_extras.object_utils.world_to_camera_view(renderer.scene,
                                                                    renderer.camera,
                                                                    world_position)
    _x = int(renderer.width * cam_space_coords[0])
    _y = int(renderer.height * (1 - cam_space_coords[1]))
    return _x, _y


def get_sensor_size(sensor_fit, sensor_x, sensor_y):
    """ Get the size of the sensor based on it's X, Y sizes

    Returns:
        [float] - Width of sensor in float
    """
    if sensor_fit == 'VERTICAL':
        return sensor_y
    return sensor_x


def get_sensor_fit(sensor_fit, size_x, size_y):
    """Get the aspect ratio of the sensor based on it's X, Y sizes

    Returns:
        [str] - Type of sensor
    """
    if sensor_fit == 'AUTO':
        if size_x >= size_y:
            return 'HORIZONTAL'
        return 'VERTICAL'
    return sensor_fit


def get_intrinsic_matrix(renderer):
    """ uild intrinsic camera parameters from Blender camera data
    Arguments:
        camera {`blendgen.renderer.Renderer`} -- The Blender camera object

    Returns:
        [mathutils.Matrix] -- A 3x4 projection matrix
    """
    camera = bpy.data.cameras[renderer.camera.name]
    if camera.type != 'PERSP':
        raise ValueError('Non-perspective cameras not supported')
    scene = bpy.context.scene
    f_in_mm = camera.lens
    scale = scene.render.resolution_percentage / 100
    resolution_x_in_px = scale * scene.render.resolution_x
    resolution_y_in_px = scale * scene.render.resolution_y
    sensor_size_in_mm = get_sensor_size(
        camera.sensor_fit, camera.sensor_width, camera.sensor_height)
    sensor_fit = get_sensor_fit(
        camera.sensor_fit,
        scene.render.pixel_aspect_x * resolution_x_in_px,
        scene.render.pixel_aspect_y * resolution_y_in_px
    )
    pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
    if sensor_fit == 'HORIZONTAL':
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px
    pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px
    s_u = 1 / pixel_size_mm_per_px
    s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

    # Parameters of intrinsic calibration matrix K
    u_0 = resolution_x_in_px / 2 - camera.shift_x * view_fac_in_px
    v_0 = resolution_y_in_px / 2 + camera.shift_y * \
        view_fac_in_px / pixel_aspect_ratio
    skew = 0  # only use rectangular pixels

    intrinsic_matrix = Matrix(
        ((s_u, skew, u_0),
         (0, s_v, v_0),
         (0, 0, 1)))
    return intrinsic_matrix


def get_rt_matrix(renderer):
    """Returns camera rotation and translation matrices from Blender.

    Arguments:
        renderer {blendgen.renderer.Renderer} - The BlendGen renderer

    Returns:
        [mathutils.Matrix] - The RT matrix
    """

    r_bcam2cv = Matrix(
        ((1, 0, 0),
         (0, -1, 0),
         (0, 0, -1)))

    # Transpose since the rotation is object rotation,
    # and we want coordinate rotation
    # R_world2bcam = cam.rotation_euler.to_matrix().transposed()
    # T_world2bcam = -1*R_world2bcam * location
    #
    # Use matrix_world instead to account for all constraints
    location, rotation = renderer.camera.matrix_world.decompose()[0:2]
    r_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    # T_world2bcam = -1*R_world2bcam*cam.location
    # Use location from matrix_world to account for constraints:
    t_world2bcam = -1 * r_world2bcam @ location

    # Build the coordinate transform matrix from world to computer vision camera
    r_world2cv = r_bcam2cv @ r_world2bcam
    t_world2cv = r_bcam2cv @ t_world2bcam

    # put into 3x4 matrix
    rotation_translation = Matrix((
        r_world2cv[0][:] + (t_world2cv[0],),
        r_world2cv[1][:] + (t_world2cv[1],),
        r_world2cv[2][:] + (t_world2cv[2],)
    ))
    return rotation_translation


def get_camera_matrices(renderer):
    """Get projection, intrinsic and rotation and translation matrices from camera
    """
    intrinsic_matrix = get_intrinsic_matrix(renderer)
    rt_matrix = get_rt_matrix(renderer)

    return intrinsic_matrix @ rt_matrix, intrinsic_matrix, rt_matrix
