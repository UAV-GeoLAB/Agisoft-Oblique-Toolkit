import Metashape as M

from obq_block import create_blocks
from obq_direction import sort_by_direction
from obq_footprints import create_footprints, create_footprints_multithread
from obq_histograms import calculate_histogram
from obq_orientation import align_blocks, match_blocks, filter_blocks, \
    match_active_chunk, align_active_chunk, filter_active_chunk, reference_match_active_chunk

M.app.removeMenuItem('Oblique')
M.app.addMenuItem('Oblique/Create footprints', create_footprints)
M.app.addMenuItem('Oblique/Create footprints (TEST)', create_footprints_multithread)
M.app.addMenuItem('Oblique/Group by direction', sort_by_direction)
M.app.addMenuItem('Oblique/Create blocks', create_blocks)

M.app.addMenuItem('Oblique/Footprint-based image matching/Active chunk', match_active_chunk)
M.app.addMenuItem('Oblique/Footprint-based image matching/Blocks', match_blocks)
M.app.addMenuItem('Oblique/Reference preselection image matching (Active chunk)', reference_match_active_chunk)

M.app.addMenuItem('Oblique/Multi-stage image alignment/Active chunk', align_active_chunk)
M.app.addMenuItem('Oblique/Multi-stage image alignment/Blocks', align_blocks)

M.app.addMenuItem('Oblique/Tie points filtering/Active chunk', filter_active_chunk)
M.app.addMenuItem('Oblique/Tie points filtering/Blocks', filter_active_chunk)

M.app.addMenuItem('Oblique/Calculate histograms', calculate_histogram)
