import Metashape as M
import numpy as np
from scipy.spatial.transform import Rotation as R


def collinearity_condition(photo_location, photo_opk, focal_length, plate_xy, degrees=True, mean_height=200.0):
    """ Return XY coordinates of point measured in image plane. """
    x, y = plate_xy
    X0, Y0, Z0 = photo_location

    a = R.from_euler('xyz', photo_opk, degrees)
    a = a.as_matrix()

    X = X0 + (mean_height - Z0) \
        * (a[0, 0] * x + a[1, 0] * y - a[2, 0] * focal_length) \
        / (a[0, 2] * x + a[1, 2] * y - a[2, 2] * focal_length)
    Y = Y0 + (mean_height - Z0) \
        * (a[0, 1] * x + a[1, 1] * y - a[2, 1] * focal_length) \
        / (a[0, 2] * x + a[1, 2] * y - a[2, 2] * focal_length)

    return X, Y, mean_height


def camera_footprint(cam: M.Camera, active_chunk, mean_terrain_height, euler_angles):
    """ Create footprint of given camera in specified chunk. """
    # Get camera name
    name = cam.label

    # Get camera EOP
    extrinsic = np.identity(4)
    if euler_angles == M.EulerAngles.EulerAnglesOPK:
        extrinsic[:3, :3] = np.float64(M.Utils.opk2mat(cam.reference.rotation)).reshape((3,3))
    elif euler_angles == M.EulerAngles.EulerAnglesYPR:
        extrinsic[:3, :3] = np.float64(M.Utils.ypr2mat(cam.reference.rotation)).reshape((3,3))
    extrinsic[:3, 3] = np.float64(cam.reference.location)

    # Get camera IOP
    intrinsic = np.zeros((3, 4))
    intrinsic[0, 0] = cam.calibration.f
    intrinsic[1, 1] = cam.calibration.f
    intrinsic[2, 2] = 1.0
    intrinsic[0, 2] = cam.sensor.width / 2
    intrinsic[1, 2] = cam.sensor.height / 2

    # Cast corners onto Z plane
    terrain_corners = []
    image_corners = [
        [0, 0], [cam.sensor.width, 0], [cam.sensor.width, cam.sensor.height], [0, cam.sensor.height]
    ]
    for corner in image_corners:
        ray = np.hstack([corner, [1]])
        ray = np.linalg.inv(intrinsic[:, :3]) @ ray
        ray = ray / np.linalg.norm(ray)
        ray = extrinsic[:3, :3] @ ray
        ray = ray / np.linalg.norm(ray)

        ray_length = (mean_terrain_height - extrinsic[2, 3]) / ray[2]
        terrain_corner = extrinsic[:3, 3] + ray_length * ray
        terrain_corners.append(M.Vector(terrain_corner))

    # Add shape attributes and geometry
    shape = active_chunk.shapes.addShape()
    shape.label = name
    shape.attributes["Photo"] = name
    shape.attributes["Frame"] = str(cam.key)
    shape.geometry = M.Geometry.Polygon(terrain_corners)

    # Save footprint id to camera meta for later
    cam.meta['FootprintId'] = str(shape.key)
    return shape


def create_footprints():
    """ Create footprints for every camera in active chunk. """
    print('Drawing footprints...')
    # Get active chunk
    active_chunk = M.app.document.chunk

    # Initialize shapes
    if not active_chunk.shapes:
        active_chunk.shapes = M.Shapes()
        active_chunk.shapes.crs = active_chunk.crs

    # Create footprints shapes group
    print('Creating shapes group...')
    footprints_group = filter(lambda x: x.label == 'Footprints', active_chunk.shapes.groups)
    footprints_group = list(footprints_group)
    if len(footprints_group) > 0:
        for i in range(len(footprints_group)):
            footprints_group[i] = None

    footprints_group = active_chunk.shapes.addGroup()
    footprints_group.label = "Footprints"
    footprints_group.color = (30, 239, 30)

    # Get mean terrain height
    mean_height = M.app.getFloat("Set mean terrain height", 200)
    print(f"Mean terrain height was set to {mean_height}")

    # Process each photo
    print("Processing...")
    for camera in active_chunk.cameras:
        poly = camera_footprint(camera, active_chunk, mean_height, active_chunk.euler_angles)
        poly.group = footprints_group

    print('Done.')
    M.app.update()
