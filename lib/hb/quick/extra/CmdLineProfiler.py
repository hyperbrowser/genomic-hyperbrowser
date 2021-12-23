from __future__ import print_function

def print_profile(cmd, globs=globals(), locs=locals(), dump_path=None):
    import cProfile
    import pstats

    prof = cProfile.Profile()
    prof.runctx(cmd, globs, locs)
    stats = pstats.Stats(prof)

    PROFILE_HEADER = '--- Profile ({})---'
    PROFILE_FOOTER = '--- End Profile ({})---'

    sort_type = 'sorted by cumulative time'
    print(PROFILE_HEADER.format(sort_type))
    stats.sort_stats('cumulative')
    stats.print_stats()
    print(PROFILE_FOOTER.format(sort_type))

    sort_type = 'sorted by internal time'
    print(PROFILE_HEADER.format(sort_type))
    stats.sort_stats('time')
    stats.print_stats()
    print(PROFILE_FOOTER.format(sort_type))

    if dump_path:
        print('Raw profile stats path:', dump_path)
        stats.dump_stats(dump_path)
    else:
        from tempfile import NamedTemporaryFile
        from base64 import b64encode

        tmpfile = NamedTemporaryFile()
        stats.dump_stats(tmpfile.name)
        with tmpfile:
            print_content = 'internal pstat file'
            print(PROFILE_HEADER.format(print_content))
            print(b64encode(tmpfile.read()))
            print(PROFILE_FOOTER.format(print_content))


def create_call_graph_from_pstats_dump_file(pstats_dump_path, output_dir):
    import os
    from quick.util.PstatsUtil import OverheadStats

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    dot_graph_path = os.path.join(output_dir, 'call_graph.dot')
    png_file_path = os.path.join(output_dir, 'call_graph.png')

    overhead_stats = OverheadStats(pstats_dump_path)
    overhead_stats.writeDotGraph(dot_graph_path, prune=True)
    overhead_stats.renderGraph(dot_graph_path, png_file_path)

    print('Call graph dot file:', dot_graph_path)
    print('Call graph png file:', png_file_path)


def create_call_graph_from_pstats_dump_str(pstats_dump_str, output_dir):
    from tempfile import NamedTemporaryFile
    from base64 import b64decode

    tmpfile = NamedTemporaryFile()
    with tmpfile:
        tmpfile.write(b64decode(pstats_dump_str))
        tmpfile.flush()

        create_call_graph_from_pstats_dump_file(tmpfile.name, output_dir)


