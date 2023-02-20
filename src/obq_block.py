import Metashape as M
import shapely.geometry as sh
import shapely.ops as so


def poly_to_shapely(polygon):
    """ Convert Metashape Polygon to shapely polygon. """
    exterior = polygon.coordinates[0]
    shape = sh.Polygon([[c.x, c.y] for c in exterior])
    return shape


def line_to_shapely(line):
    """ Convert Metashape LineString to shapely polyline. """
    shape = sh.LineString([(c.x, c.y) for c in line.coordinates])
    return shape


def split_polygon_by_lines(polygon, lines):
    """ Split polygon to smaller polygons based on break lines. """
    parts = polygon
    for l in lines:
        parts = so.split(parts, l)
        parts = sh.MultiPolygon(parts)
    return list(parts.geoms)


def create_blocks():
    """ Split chunk to smaller parts based on AOI shapes. """
    print('Splitting chunk into blocks...')
    # Get active chunk
    active_chunk = M.app.document.chunk

    # Create set of all cameras
    all_cameras = {x.key for x in active_chunk.cameras}

    # Get AOI shapes group
    shapes_groups = active_chunk.shapes.groups
    shapes_groups = filter(lambda x: x.label != 'Footprints', shapes_groups)
    shapes_groups = list(shapes_groups)

    if len(shapes_groups) > 1:
        raise Exception("Chunk must contains only one other shapes group other than `Footprints`!")

    aoi_group = shapes_groups[0]

    # Create AOI boundary and split lines
    aoi_polygon = filter(
        lambda x: x.group == aoi_group and x.geometry.type == M.Geometry.Type.PolygonType,
        active_chunk.shapes
    )
    aoi_splits = filter(
        lambda x: x.group == aoi_group and x.geometry.type == M.Geometry.Type.LineStringType,
        active_chunk.shapes
    )
    aoi_polygon = list(aoi_polygon)
    aoi_splits = list(aoi_splits)

    if len(aoi_polygon) > 1:
        raise Exception('AOI shapes group should contain only one Polygon!')

    aoi_polygon = aoi_polygon[0]
    aoi_polygon = poly_to_shapely(aoi_polygon.geometry)

    # Filter outside cameras
    outside_cameras = set()
    inside_cameras = list()
    footprints = list(filter(lambda x: x.group.label == 'Footprints', active_chunk.shapes))

    for f in footprints:
        footprint_poly = poly_to_shapely(f.geometry)
        camera_key = int(f.attributes['Frame'])

        if not aoi_polygon.intersects(footprint_poly):
            outside_cameras.add(camera_key)
        else:
            inside_cameras.append(f)

    # Create chunk for outside cameras
    diff = all_cameras.difference(outside_cameras)
    outside_chunk = active_chunk.copy()
    outside_chunk.label = active_chunk.label + f'_OUTSIDE'
    diff_cameras = [outside_chunk.findCamera(x) for x in diff]
    diff_footprints = list(filter(
        lambda x: x.group.label == 'Footprints' and int(x.attributes['Frame']) in diff,
        outside_chunk.shapes
    ))
    outside_chunk.remove(diff_cameras)
    outside_chunk.shapes.remove(diff_footprints)

    # Menage cameras inside AOI
    if len(aoi_splits) == 0:
        # Create chunk for inside cameras
        inside_chunk = active_chunk.copy()
        inside_chunk.label = active_chunk.label + f'_INSIDE'
        diff_cameras = [inside_chunk.findCamera(x) for x in outside_cameras]
        diff_footprints = list(filter(
            lambda x: x.group.label == 'Footprints' and int(x.attributes['Frame']) in outside_cameras,
            inside_chunk.shapes
        ))
        inside_chunk.remove(diff_cameras)
        inside_chunk.shapes.remove(diff_footprints)

    else:
        # Create blocks
        aoi_splits = [line_to_shapely(l.geometry) for l in aoi_splits]
        blocks_polygons = split_polygon_by_lines(aoi_polygon, aoi_splits)

        # Split cameras between chunks
        cameras_for_chunk = []
        for _ in range(len(blocks_polygons)):
            cameras_for_chunk.append([])

        for f in inside_cameras:
            footprint_poly = poly_to_shapely(f.geometry)

            for i, block_poly in enumerate(blocks_polygons):
                if block_poly.intersects(footprint_poly):
                    cameras_for_chunk[i].append(int(f.attributes['Frame']))

        for i in range(len(blocks_polygons)):
            cameras_set = set(cameras_for_chunk[i])
            diff = all_cameras.difference(cameras_set)
            chunk = active_chunk.copy()
            chunk.label = active_chunk.label + f'_BLOCK{i}'
            diff_cameras = [chunk.findCamera(x) for x in diff]
            diff_footprints = list(filter(
                lambda x: x.group.label == 'Footprints' and int(x.attributes['Frame']) in diff,
                chunk.shapes
            ))
            chunk.remove(diff_cameras)
            chunk.shapes.remove(diff_footprints)
    print("Done.")
