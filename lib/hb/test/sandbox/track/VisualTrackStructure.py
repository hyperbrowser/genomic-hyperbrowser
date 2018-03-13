from gold.track.TrackStructure import TrackStructureV2, SingleTrackTS
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV


def printTS(ts):
    for key, val in ts.iteritems():
        print key, '\t'
        if isinstance(val, dict):
            printTS(val)
        if isinstance(val, SingleTrackTS):
            print val.metadata

# def tsToAnytree(ts):
#     from anytree import Node, RenderTree

def printJson(ts):
    import json
    print json.dumps(ts, indent=4)


if __name__ == '__main__':
    t1 = SampleTrack(SampleTV( segments = [[10,20],[30,40],[50,55]], vals = [1,2,3], anchor = [0,100], valDType='int32'))
    t2 = SampleTrack(SampleTV( segments = [[11,21],[31,41],[51,56]], vals = [4,5,6], anchor = [0,100], valDType='int32'))
    t3 = SampleTrack(SampleTV( segments = [[12,22],[32,42],[52,57]], vals = [7,8,9], anchor = [0,100], valDType='int32'))
    t4 = SampleTrack(SampleTV( segments = [[13,23],[33,43],[53,58]], vals = [10,20,30], anchor = [0,100], valDType='int32'))
    t5 = SampleTrack(SampleTV( segments = [[14,24],[34,44],[54,59]], vals = [11,21,31], anchor = [0,100], valDType='int32'))
    ts = TrackStructureV2()
    ts['cat1'] = TrackStructureV2()
    ts['cat2'] = TrackStructureV2()
    ts['cat3'] = TrackStructureV2()
    ts['cat1']['query'] = SingleTrackTS(track=t1, metadata=dict(title='t1'))
    ts['cat1']['reference'] = TrackStructureV2(dict(t4=SingleTrackTS(track=t4, metadata=dict(title='t4')),
                                                    t5=SingleTrackTS(track=t5, metadata=dict(title='t5'))))
    ts['cat2']['query'] = TrackStructureV2(dict(t2=SingleTrackTS(track=t2, metadata=dict(title='t2'))))
    ts['cat3']['query'] = TrackStructureV2(dict(t3=SingleTrackTS(track=t3, metadata=dict(title='t3'))))

    printTS(ts)
    printJson(ts)

