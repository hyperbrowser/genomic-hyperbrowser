class Read:
    def __init__(lines):
        self.id = lines[0]
        self.sequence = lines[1]
        self.quality =  lines[3]
        self._extractBarcode()
        self._extractUmi()

    def _extractBarcode(self):
        self.sequence = self.sequence[someIndex:]
        self.quality =self.quality[someIndex:]
        self.barcode = '...'
        #in doing so, also remove this from sequence..

    def _extractUmi(self):
        self.umi = '...'
        #same as for barcodde


def parseFile(fn):
    reads = []
    collectedLines = []
    for line in open(fn):
        if line[0]=='@' and len(collectedLines)>0:
            read = Read(collectedLines)
            reads.append(read)
            collectedLines = []

        collectedLines.append(line)

    #readsPerBarcode = defaultdict(list)
    for read in reads:
        fn = '/'.join(['something', read.barcode, read.umi + '.fastq'])
        #here you can write directly to a file,
        #readsPerBarcode[read.barcode].append(read)

    # for barcode in readsPerBarcode:
    #     for read in readsPerBarcode[barcode]:
