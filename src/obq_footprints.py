import Metashape as M
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


def camera_footprint(cam, active_chunk, mean_terrain_height):
    """ Create footprint of given camera in specified chunk. """
    # Get camera name
    name = cam.label

    # Get camera EOP
    location = cam.reference.location
    location = [location.x, location.y, location.z]
    rotation = cam.reference.rotation
    rotation = [-rotation.x, -rotation.y, rotation.z]

    # Get camera focal length and corners in plate coordinates
    # Using pixel values
    if cam.sensor.calibration.f is not None:
        xaxis = cam.sensor.width / 2
        yaxis = cam.sensor.height / 2
        focal_length = cam.sensor.calibration.f
    # Using metric values if there is no exif data
    elif cam.sensor.focal_length is not None \
            and cam.sensor.pixel_width is not None \
            and cam.sensor.pixel_height is not None:
        xaxis = (cam.sensor.width * cam.sensor.pixel_width * 10 ** -3 / 2)
        yaxis = (cam.sensor.height * cam.sensor.pixel_height * 10 ** -3 / 2)
        focal_length = cam.sensor.focal_length * 10 ** -3
    else:
        raise Exception('You have to specify basic sensor parameters, either:\n'
                        '\t- Camera sensor initial f (in pixels)\n'
                        '\t- Camera focal length and pixel size (in mm)\n')

    # List of all corners
    plate_corners = [
        [-xaxis, -yaxis],
        [xaxis, -yaxis],
        [xaxis, yaxis],
        [-xaxis, yaxis]
    ]

    # Calculate XYZ of corners
    terrain_corners = []
    for x, y in plate_corners:
        X, Y, Z = collinearity_condition(location, rotation, focal_length, (x, y), mean_height=mean_terrain_height)
        terrain_corners.append(M.Vector((X, Y, Z)))

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
        poly = camera_footprint(camera, active_chunk, mean_height)
        poly.group = footprints_group

    print('Done.')
    M.app.update()
