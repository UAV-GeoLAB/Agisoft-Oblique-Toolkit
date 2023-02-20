import Metashape as M


def myround(x):
    """ Round angle to multiple of 90. """
    return 90 * round(x / 90)


def sort_by_direction():
    """ Split cameras to groups based on direction. """
    # Get active chunk
    active_chunk = M.app.document.chunk

    # Create groups for each direction
    direction_groups = []
    for g in ['Nadir', 'Front', 'Left', 'Back', 'Right']:
        group = active_chunk.addCameraGroup()
        group.label = g
        direction_groups.append(group)

    for camera in active_chunk.cameras:
        # Find assigned shape
        footprint = int(camera.meta['FootprintId'])
        footprint = active_chunk.shapes[footprint]

        tmp = M.Utils.opk2mat(camera.reference.rotation)
        tmp = M.Utils.mat2ypr(tmp)
        yaw, pitch, roll = tmp[0], tmp[1], tmp[2]

        if abs(pitch) < 20 and abs(roll) < 20:
            camera.group = direction_groups[0]
            footprint.attributes['Direction'] = direction_groups[0].label
            continue

        direction = None
        if pitch > 30:
            direction = 0
        if roll < -30:
            direction = 1
        if pitch < -30:
            direction = 2
        if roll > 30:
            direction = 3

        fly_direction = (myround(yaw) // 90) % 4
        direction = (direction + fly_direction) % 4
        camera.group = direction_groups[direction + 1]
        footprint.attributes['Direction'] = direction_groups[direction + 1].label

    print('Done.')
    M.app.update()
