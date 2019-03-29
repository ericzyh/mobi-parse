# encoding: utf-8
from struct import *
from .utils import *

# Mobi parse
# refer : https://wiki.mobileread.com/wiki/MOBI
class Mobi:

    # constructor
    def __init__(self, filename):

        # 1. read cursor offset
        self.offset = 0

        # 2. mobi contents
        try:
            file = open(filename, "rb");
            self.contents = file.read();
        except IOError as e:
            sys.stderr.write("Could not open %s! " % filename);
            raise e;
        # 3. Like PalmDOC, the Mobipocket file format is that of a standard Palm Database Format file. The header of that format includes the name of the database (usually the book title and sometimes a portion of the authors name) which is up to 31 bytes of data.
        # refer : https://wiki.mobileread.com/wiki/PDB#Palm_Database_Format
        self.pdfHeader = self.parsePdfHeader()
        self.pdfRecord = self.parsePdfRecord()

        # 4. PalmDOC Header
        self.palmDocHeader = self.parsePalmDocHeader()

        # 5. MOBI Header
        self.mobiHeader = self.parseMobiHeader()

        # 6. EXTH Header
        self.exthHeader = self.parseExthHeader()

    def parse(self):
        htmldata = ''
        images = []
        for i in range(self.mobiHeader['firstRecord'], self.mobiHeader['nobookIndex']) :
            htmldata = htmldata + (self.contents[self.pdfRecord[i]['recordDataOffset']:self.pdfRecord[i+1]['recordDataOffset']])
        for i in range(self.mobiHeader['firstImageIndex'], self.mobiHeader['lastRecord']) :
            images.append(self.contents[self.pdfRecord[i]['recordDataOffset']:self.pdfRecord[i+1]['recordDataOffset']])
        return htmldata, images


    def parsePdfHeader(self):
        headerfmt = '>32shhIIIIII4s4sIIH'
        headerlen = calcsize(headerfmt)
        fields = [ "name", "attributes", "version", "created", "modified", "backup", "modnum", "appInfoId", "sortInfoID", "type", "creator", "uniqueIDseed", "nextRecordListID", "numberOfRecords" ]
        results = zip(fields, unpack(headerfmt, self.contents[self.offset:self.offset+headerlen]))
        self.offset += headerlen
        return toDict(results)

    def parsePdfRecord(self):
        records = {};
        index = 0;
        # read in all records in database
        for recordID in range(self.pdfHeader['numberOfRecords']):
            headerfmt = '>II'
            headerlen = calcsize(headerfmt)
            fields = [ "recordDataOffset", "uniqueID"]
            results = zip(fields, unpack(headerfmt, self.contents[self.offset:self.offset+headerlen]))
            # increment offset into file
            self.offset += headerlen
            # convert tuple to dictionary
            resultsDict = toDict(results);
            # futz around with the unique ID record, as the uniqueID's top 8 bytes are
            # really the "record attributes":
            resultsDict['recordAttributes'] = (resultsDict['uniqueID'] & 0xFF000000) >> 24;
            resultsDict['uniqueID'] = resultsDict['uniqueID'] & 0x00FFFFFF;
            # store into the records dict
            records[index] = resultsDict;
            index = index+1
        return records;

    def parsePalmDocHeader(self):
        headerfmt = '>HHIHHHH'
        headerlen = calcsize(headerfmt)
        fields = [ "compression", "unused", "textLength", "recordCount", "recordSize", "encryptionType", "unknown" ]
        # the first 16B in record[0] is palmdocheader
        offset = self.pdfRecord[0]['recordDataOffset'];
        # create tuple with info
        results = zip(fields, unpack(headerfmt, self.contents[offset:offset+headerlen]))
        # convert tuple array to dictionary
        resultsDict = toDict(results);
        self.offset = offset+headerlen;
        return resultsDict

    def parseMobiHeader(self):
        # the first 16B - 268B in record[0] is palmdocheader
        headerfmt = '>IIIIII40sIIIIIIIIIIIII36sIIII8sHHIIII28sII'
        headerlen = calcsize(headerfmt)
        fields = [ "identifier", "headerLength", "mobiType", "textEncoding", "uniqueID", "fileVersion", "index", "nobookIndex", "fullNameOffset", "fullNameLength", "language", "inputLanguage", "outputLanguage", "minVersion", "firstImageIndex", "firstHuffRecord", "huffRecordCount", "huffmanTableOffset", "huffmanTableOffset", "exthFlags", "unknown1", "drMOffset", "drmCount", "drmSize", "drmFlags", "unknown2", "firstRecord","lastRecord", "unknown3", "fcisRecord", "unknown4", "flisRecord",
                "unknown5", "extraRecordDataFlags", "indexRecordOffset", ]
        results = toDict(zip(fields, unpack(headerfmt, self.contents[self.offset:self.offset+headerlen])))
        self.offset += results['headerLength'];
        results['fullName'] = self.contents[self.pdfRecord[0]['recordDataOffset']+results['fullNameOffset']:self.pdfRecord[0]['recordDataOffset']+results['fullNameOffset']+results['fullNameLength']]
        return results;

    def parseExthHeader(self):
        if (self.mobiHeader['exthFlags']& 0x40) != 0 :
            return []
        return [];
