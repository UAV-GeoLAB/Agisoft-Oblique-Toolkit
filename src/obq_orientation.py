import Metashape as M
import itertools as itt
import numpy as np

from obq_block import poly_to_shapely


def generate_pairs(chunk):
    """ Generate matching pairs. """
    footprints = list(filter(lambda x: x.group.label == 'Footprints', chunk.shapes))
    footprints = [(x.attributes['Frame'], poly_to_shapely(x.geometry)) for x in footprints]
    all_pairs = itt.combinations(footprints, 2)
    all_pairs = filter(lambda x: x[0][1].intersects(x[1][1]), all_pairs)
    all_pairs = [(int(x[0][0]), int(x[1][0])) for x in all_pairs]
    return all_pairs


def pair_matching(chunk):
    """ Footprint pairs based matching """
    # Match photos
    pairs = generate_pairs(chunk)
    chunk.matchPhotos(
        downscale=1,
        generic_preselection=False,
        reference_preselection=False,
        keypoint_limit=30000,
        keypoint_limit_per_mpx=1000,
        tiepoint_limit=3000,
        reset_matches=True,
        filter_stationary_points=False,
        pairs=pairs,
        keep_keypoints=True
    )


def align_block_chunk(chunk):
    """ Multi-step image alignment for single block. """
    # Align nadir images
    nadir_images = filter(lambda x: x.group.label == 'Nadir', chunk.cameras)
    nadir_images = list(nadir_images)
    chunk.alignCameras(
        cameras=nadir_images,
        adaptive_fitting=False,
        reset_alignment=True,
    )

    # Align oblique images
    for direction in ['Front', 'Right', 'Back', 'Left']:
        direction_images = filter(lambda x: x.group.label == direction, chunk.cameras)
        direction_images = list(direction_images)

        chunk.alignCameras(
            cameras=direction_images,
            adaptive_fitting=False
        )


def filter_point_cloud(chunk):
    """ Tie points selection """
    cameras = chunk.cameras

    points = {}
    for point in chunk.point_cloud.points:
        points[point.track_id] = point

    projectionsforcameras = []
    for camera in cameras:
        tmpcameratab = [projection.track_id for projection in chunk.point_cloud.projections[camera]
                        if projection.track_id in points.keys()]
        projectionsforcameras.append(np.array(tmpcameratab))

    intersections = []
    camerachangecheck = projectionsforcameras[0]
    intforcamera = []
    tmpintersectionsrank = []

    for camera1, camera2 in itt.permutations(projectionsforcameras, 2):
        if camerachangecheck is not camera1:
            intersections.append(intforcamera)
            intforcamera = []
            camerachangecheck = camera1
        int1d = np.intersect1d(camera1, camera2, assume_unique=True)
        if int1d.size != 0:
            tmpintersectionsrank.append(int1d.tolist())
            intforcamera.append(int1d)

    tmpintersectionsrank = [x for sublist in tmpintersectionsrank for x in sublist]
    tmpintersectionsrank = np.array(tmpintersectionsrank)
    intrank = dict(zip(*np.unique(tmpintersectionsrank, return_counts=True)))

    selectedpoints = set()

    for cameraintersections in intersections:
        selectedpoint = -1
        for cameraintersection in cameraintersections:
            highestrank = 0
            for mergepoint in cameraintersection:
                if (highestrank < intrank[mergepoint]) and (mergepoint not in selectedpoints):
                    highestrank = intrank[mergepoint]
                    selectedpoint = mergepoint
            selectedpoints.add(selectedpoint)

    selectedpoints = np.array(list(selectedpoints))

    alltiepoints = np.unique(tmpintersectionsrank)
    mask = np.in1d(alltiepoints, selectedpoints, invert=True)
    pointstodelete = alltiepoints[mask]

    for point in pointstodelete:
        points[point].valid = False

    chunk.point_cloud.cleanup()
    M.app.update()


def match_active_chunk():
    chunk = M.app.document.chunk
    pair_matching(chunk)


def match_blocks():
    """ Align blocks in multi-step manner. """
    # Try to match blocks
    chunks = filter(lambda x: "BLOCK" in x.label, M.app.document.chunks)
    chunks = list(chunks)

    if len(chunks) != 0:
        for c in chunks:
            pair_matching(c)
        return

    # Try to match inside-outside
    inside_chunk = filter(lambda x: "INSIDE" in x.label, M.app.document.chunks)
    inside_chunk = list(inside_chunk)

    if len(inside_chunk) == 1:
        pair_matching(inside_chunk[0])
        return

    raise Exception('No blocks or inside-outside division detected. Try to use active chunk matching.')


def align_active_chunk():
    chunk = M.app.document.chunk
    align_block_chunk(chunk)


def align_blocks():
    """ Align blocks in multi-step manner. """
    # Try to orient blocks
    chunks = filter(lambda x: "BLOCK" in x.label, M.app.document.chunks)
    chunks = list(chunks)

    if len(chunks) != 0:
        for c in chunks:
            align_block_chunk(c)
        return

    # Try to orient inside-outside
    inside_chunk = filter(lambda x: "INSIDE" in x.label, M.app.document.chunks)
    inside_chunk = list(inside_chunk)

    if len(inside_chunk) == 1:
        align_block_chunk(inside_chunk[0])
        return

    raise Exception('No blocks or inside-outside division detected. Try to use active chunk alignment.')


def filter_active_chunk():
    chunk = M.app.document.chunk
    filter_point_cloud(chunk)


def filter_blocks():
    # Try to filter blocks
    chunks = filter(lambda x: "BLOCK" in x.label, M.app.document.chunks)
    chunks = list(chunks)

    if len(chunks) != 0:
        for c in chunks:
            filter_point_cloud(c)
        return

    # Try to filter inside-outside
    inside_chunk = filter(lambda x: "INSIDE" in x.label, M.app.document.chunks)
    inside_chunk = list(inside_chunk)

    if len(inside_chunk) == 1:
        filter_point_cloud(inside_chunk[0])
        return

    raise Exception('No blocks or inside-outside division detected. Try to use active chunk filtering.')
