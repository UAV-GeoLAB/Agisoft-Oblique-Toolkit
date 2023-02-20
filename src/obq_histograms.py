import Metashape as M
import numpy as np
import os


def calculate_histogram():
    document_path = M.app.document.path
    active_chunk = M.app.document.chunk

    histogram_path = os.path.join(os.path.dirname(document_path), active_chunk.label.replace(' ', '_') + '.csv')

    # Filter valid tie-points
    tie_points = active_chunk.point_cloud.points
    tie_points = filter(lambda x: x.valid, tie_points)
    tie_points = {t.track_id for t in tie_points}

    # Create counting dictionary
    projections_count = {t: [0] * 5 for t in tie_points}
    directions_codes = ['Nadir', 'Front', 'Right', "Back", "Left"]

    # Count each tie-point projections
    for camera in active_chunk.cameras:
        direction = camera.group.label
        direction = directions_codes.index(direction)

        camera_projections = active_chunk.point_cloud.projections[camera]
        for projection in camera_projections:
            track_id = projection.track_id
            if projections_count.get(track_id) is not None:
                projections_count[track_id][direction] += 1

    # Count histogram
    histogram = dict()

    for counts in projections_count.values():
        number_of_projections = sum(counts)

        if histogram.get(number_of_projections) is None:
            histogram[number_of_projections] = [0] * 5

        nadir_count = counts[0]
        obliques = counts[1:]
        oblique_count = sum(obliques)
        directions_count = np.count_nonzero(obliques)

        if oblique_count == 0:
            group_id = 0
        elif nadir_count == 0 and directions_count == 1:
            group_id = 1
        elif nadir_count > 0 and directions_count == 1:
            group_id = 2
        elif nadir_count == 0 and directions_count > 1:
            group_id = 3
        elif nadir_count > 0 and directions_count > 1:
            group_id = 4
        else:
            raise Exception(nadir_count, oblique_count, directions_count)

        histogram[number_of_projections][group_id] += 1

    # Return results
    with open(histogram_path, 'w') as file:
        file.write("N; G1; G2; G3; G4; G5\n")

        for n, counts in sorted(histogram.items(), key=lambda x: x[0]):
            file.write(f"{n}; {counts[0]}; {counts[1]}; {counts[2]}; {counts[3]}; {counts[4]}\n")
