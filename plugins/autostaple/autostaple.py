import util
from model.strandset import StrandSet
from model.enum import StrandType
from model.parts.part import Part
def autoStaple(part):
    """Autostaple does the following:
    1. Clear existing staple strands by iterating over each strand
    and calling RemoveStrandCommand on each. The next strand to remove
    is always at index 0.
    2. Create temporary strands that span regions where scaffold is present.
    3. Determine where actual strands will go based on strand overlap with
    prexovers.
    4. Delete temporary strands and create new strands.
    """
    epDict = {}  # keyed on StrandSet
    cmds = []

    # clear existing staple strands
    for vh in part.getVirtualHelices():
        stapSS = vh.stapleStrandSet()
        for strand in stapSS:
            c = StrandSet.RemoveStrandCommand(stapSS, strand, 0)  # rm
            cmds.append(c)
    util.execCommandList(part, cmds, desc="Clear staples")
    cmds = []

    # create strands that span all bases where scaffold is present
    for vh in part.getVirtualHelices():
        segments = []
        scafSS = vh.scaffoldStrandSet()
        for strand in scafSS:
            lo, hi = strand.idxs()
            if len(segments) == 0:
                segments.append([lo, hi])  # insert 1st strand
            elif segments[-1][1] == lo - 1:
                segments[-1][1] = hi  # extend
            else:
                segments.append([lo, hi])  # insert another strand
        stapSS = vh.stapleStrandSet()
        epDict[stapSS] = []
        for i in range(len(segments)):
            lo, hi = segments[i]
            epDict[stapSS].extend(segments[i])
            c = StrandSet.CreateStrandCommand(stapSS, lo, hi, i)
            cmds.append(c)
    util.execCommandList(part, cmds, desc="Add tmp strands", useUndoStack=False)
    cmds = []

    # determine where xovers should be installed
    for vh in part.getVirtualHelices():
        stapSS = vh.stapleStrandSet()
        is5to3 = stapSS.isDrawn5to3()
        potentialXovers = part.potentialCrossoverList(vh)
        for neighborVh, idx, strandType, isLowIdx in potentialXovers:
            if strandType != StrandType.Staple:
                continue
            if isLowIdx and is5to3:
                strand = stapSS.getStrand(idx)
                neighborSS = neighborVh.stapleStrandSet()
                nStrand = neighborSS.getStrand(idx)
                if strand == None or nStrand == None:
                    continue
                # check for bases on both strands at [idx-1:idx+3]
                if strand.lowIdx() < idx and strand.highIdx() > idx + 1 and\
                   nStrand.lowIdx() < idx and nStrand.highIdx() > idx + 1:
                    epDict[stapSS].extend([idx, idx+1])
                    epDict[neighborSS].extend([idx, idx+1])

    # clear temporary staple strands
    for vh in part.getVirtualHelices():
        stapSS = vh.stapleStrandSet()
        for strand in stapSS:
            c = StrandSet.RemoveStrandCommand(stapSS, strand, 0)
            cmds.append(c)
    util.execCommandList(part, cmds, desc="Rm tmp strands", useUndoStack=False)
    cmds = []

    util.beginSuperMacro(part, desc="Auto-Staple")

    for stapSS, epList in epDict.iteritems():
        assert (len(epList) % 2 == 0)
        epList = sorted(epList)
        ssIdx = 0
        for i in range(0, len(epList),2):
            lo, hi = epList[i:i+2]
            c = StrandSet.CreateStrandCommand(stapSS, lo, hi, ssIdx)
            cmds.append(c)
            ssIdx += 1
    util.execCommandList(part, cmds, desc="Create strands")
    cmds = []

    # create crossovers wherever possible (from strand5p only)
    for vh in part.getVirtualHelices():
        stapSS = vh.stapleStrandSet()
        is5to3 = stapSS.isDrawn5to3()
        potentialXovers = part.potentialCrossoverList(vh)
        for neighborVh, idx, strandType, isLowIdx in potentialXovers:
            if strandType != StrandType.Staple:
                continue
            if (isLowIdx and is5to3) or (not isLowIdx and not is5to3):
                strand = stapSS.getStrand(idx)
                neighborSS = neighborVh.stapleStrandSet()
                nStrand = neighborSS.getStrand(idx)
                if strand == None or nStrand == None:
                    continue
                part.createXover(strand, idx, nStrand, idx, updateOligo=False)

    c = Part.RefreshOligosCommand(part)
    cmds.append(c)
    util.execCommandList(part, cmds, desc="Assign oligos")
    cmds = []
    util.endSuperMacro(part)
# end def