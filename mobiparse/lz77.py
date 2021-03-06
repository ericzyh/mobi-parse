import struct

def uncompress(data):
  length = len(data);
  offset = 0;   # Current offset into data
  text = '';   # Output (uncompressed) text

  while offset < length:
    char = data[offset];
    offset += 1;
    ord_ = ord(char);

    # The long if-elsif chain is the best logic for $ord handling
    ## no critic (Cascading if-elsif chain)
    if (ord_ == 0):
      # Nulls are literal
      text += char;
    elif (ord_ <= 8):
      # Next $ord bytes are literal
      text += data[offset:offset+ord_] # text .=substr($data,$offset,ord);
      offset += ord_;
    elif (ord_ <= 0x7f):
      # Values from 0x09 through 0x7f are literal
      text += char;
    elif (ord_ <= 0xbf):
      # Data is LZ77-compressed

      # From Wikipedia:
      # "A length-distance pair is always encoded by a two-byte
      # sequence. Of the 16 bits that make up these two bytes,
      # 11 bits go to encoding the distance, 3 go to encoding
      # the length, and the remaining two are used to make sure
      # the decoder can identify the first byte as the beginning
      # of such a two-byte sequence."

      offset += 1;
      if (offset > len(data)):
        return text;

      lz77, = struct.unpack('>H', data[offset-2:offset])

      # Leftmost two bits are ID bits and need to be dropped
      lz77 &= 0x3fff;

      # Length is rightmost 3 bits + 3
      lz77length = (lz77 & 0x0007) + 3;

      # Remaining 11 bits are offset
      lz77offset = lz77 >> 3;
      if (lz77offset < 1):
        return text;

      # Getting text from the offset is a little tricky, because
      # in theory you can be referring to characters you haven't
      # actually decompressed yet. You therefore have to check
      # the reference one character at a time.
      textlength = len(text);
      for lz77pos in range(lz77length): # for($lz77pos = 0; $lz77pos < $lz77length; $lz77pos++)
        textpos = textlength - lz77offset;
        if (textpos < 0):
          return;

        text += text[textpos:textpos+1]; #text .= substr($text,$textpos,1);
        textlength+=1;
    else:
      # 0xc0 - 0xff are single characters (XOR 0x80) preceded by
      # a space
      text += ' ' + chr(ord_ ^ 0x80);
  return text;
