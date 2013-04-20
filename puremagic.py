#!/usr/bin/env python

"""
puremagic is a pure python module that will identify a file based off it's
magic numbers. It is designed to be minimalistic and inherently cross platform
compatible, with no imports when used as a module. 
        
Usage:
    import puremagic
    ext = puremagic.from_file(filename)

Script:
    puremagic.py [options] filename <filename2>...
    
Compatibility:
    Python 2.6+ (including 3.x)
    Python 2.4-2.7 if you removing the byte notation before each hex string   

Copyright (c) 2013, Christopher D. Griffith
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice,
    this list of conditions, the following disclaimer and the acknowledgements.

    Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions, the following disclaimer and the acknowledgements
    in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Acknowledgements
Gary C. Kessler
    For use of his File Signature Tables, available at:
    http://www.garykessler.net/library/file_sigs.html
"""
__author__ = "Christopher D. Griffith"
__copyright__ = "Copyright (c) 2013, Christopher Griffith"
__credits__ = ["Christopher Griffith", "Gary C. Kessler"]
__license__ = "Simplified BSD License"
__version__ = "0.1.0"
__maintainer__ = "Christopher Griffith"
__email__ = "chris@christophergriffith.net"
__status__ = "Prototype"


def _identify(data):
    '''Attempt to identify 'data' by it's magic numbers'''
    
    # Capture the length of the data
    # That way we do not try to identify bytes that don't exist
    length = len(data)
    
    # Iterate through the items first via the header
    for magic_row in MAGIC_HEADER_ARRAY:
        start = magic_row[1]
        end = magic_row[1] + len(magic_row[0])
        if end > length:
            continue            
        if data[start:end] == magic_row[0]:
            return magic_row
    
    # Continue onto searching for magic numbers in the footer
    for magic_row in MAGIC_STANDARD_FOOTER_ARRAY:
        end = len(data) - magic_row[1]
        start = start - len(magic_row[0])
        if  len(magic_row[0]) > length:
            continue            
        if data[start:end] == magic_row[0]:
            return magic_row
    
    raise LookupError("Could not identify file")

def _confidence(row):
    lcon = len(row[0])
    if lcon >= 3:
        lcon += 1
    if lcon > 10:
        con = 0.9
    else:
        con = float("0.%s" % lcon)
    return con
    
def _identify_all(data):
    '''Attempt to identify 'data' by it's magic numbers'''
    
    # Capture the length of the data
    # That way we do not try to identify bytes that don't exist
    length = len(data)
    matches = list()
    # Iterate through the items first via the header
    for magic_row in MAGIC_HEADER_ARRAY:
        start = magic_row[1]
        end = magic_row[1] + len(magic_row[0])
        if end > length:
            continue            
        if data[start:end] == magic_row[0]:
            matches.append([magic_row[2], magic_row[3], magic_row[4],
                            _confidence(magic_row) ])
    # Continue onto searching for magic numbers in the footer
    for magic_row in MAGIC_FOOTER_ARRAY:
        end = len(data) - magic_row[1]
        start = start - len(magic_row[0])
        if  len(magic_row[0]) > length:
            continue            
        if data[start:end] == magic_row[0]:
            matches.append([magic_row[2], magic_row[3], magic_row[4],
                            _confidence(magic_row) ])
    
    return matches

def _magic(data, mime):
    if len(data) == 0:
        raise ValueError("Input was empty") 
    info = _identify(data)  
    if mime:
        return info[3]
    return info[2]

def from_file(filename, mime=False):
    '''Opens file, attempts to identfiy content based
    off magic number and will return the file extension.
    If mime is True it will return the mime type instead.'''
    fin = open(filename, "rb")
    data = fin.read()
    fin.close()
    return _magic(data, mime)

def from_string(string, mime=False):
    '''Reads in string, attempts to identfiy content based
    off magic number and will return the file extension.
    If mime is True it will return the mime type instead.'''
    return _magic(string, mime)

def magic_file(filename, info="ext"):
    '''Returns tuple of (num_of_matches, array_of_matches)
    arragned highest confidence match first.'''
    fin = open(filename, "rb")
    data = fin.read()
    fin.close()
    if len(data) == 0:
        raise ValueError("Input was empty") 
    info = _identify_all(data)
    info.sort(key=lambda x: x[3], reverse=True)
    return (len(info), info)

def magic_string(string, info="ext"):
    '''Returns tuple of (num_of_matches, array_of_matches)
    arragned highest confidence match first'''
    if len(string) == 0:
        raise ValueError("Input was empty") 
    info = _identify_all(string)
    info.sort(key=lambda x: x[3], reverse=True)
    return (len(info), info)

# Magic numbers, offset from end, extension, mimetype, description
MAGIC_FOOTER_ARRAY = [
    ### Image ###
    [b'\x54\x52\x55\x45\x56\x49\x53\x49\x4F\x4E\x2D\x58\x46\x49\x4C\x45\x2E\x00', 0, '.tga', 'image/tga', 'Truevision Targa Graphic file'],
    ### Video ###
    [b'\x00\x00\x01\xB7', 0, '.mpeg', 'video/mpeg', 'MPEG video file'],
]

# Magic numbers, offset from beginning, extension, mimetype, description
MAGIC_HEADER_ARRAY = [
    ### Video ###
    [b'\x00\x00\x00\x14\x66\x74\x79\x70\x33\x67\x70', 0, '.3gp', 'video/3gpp', '3GPP 3rd Generation Partnership Project video file'],
    [b'\x00\x00\x00\x20\x66\x74\x79\x70\x33\x67\x70', 0, '.3g2', 'video/3gpp2', '3GPP2 3rd Generation Partnership Project video file'],
    [b'\x00\x00\x00\x14\x66\x74\x79\x70\x69\x73\x6F\x6D', 0, '.mp4', 'video/mp4', 'MPEG-4 video file'],
    [b'\x00\x00\x00\x1C\x66\x74\x79\x70\x4D\x53\x4E\x56\x01\x29\x00\x46\x4D\x53\x4E\x56\x6D\x70\x34\x32', 0, '.mp4', 'video/mp4', 'MPEG-4 video file'],
    [b'\x00\x00\x00\x14\x66\x74\x79\x70\x71\x74\x20\x20', 0, '.mov', 'video/quicktime', 'QuickTime movie file'],
    [b'\x00\x00\x00\x18\x66\x74\x79\x70\x33\x67\x70\x35', 0, '.mp4', 'video/mp4', 'MPEG-4 video files'],
    [b'\x00\x00\x00\x18\x66\x74\x79\x70\x6D\x70\x34\x32', 0, '.m4v', 'video/x-m4v', 'MPEG-4 video file'],
    [b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C', 0, '.wmv', 'video/x-ms-wmv', 'Microsoft Windows Media Video File'],
    [b'\x46\x4C\x56\x01', 0, '.flv', 'video/x-flv', 'Adobe flash video file'],
    [b'\x41\x56\x49\x20\x4C\x49\x53\x54', 8, '.avi', 'video/x-msvideo', 'Windows Audio Video Interleave file'],
    [b'\x00\x00\x01\xBA', 0, '.vob', 'video/dvd', 'DVD Video Movie File'],
    [b'\x2E\x52\x45\x43', 0, '.ivr', 'i-world/i-vrml', 'RealPlayer video file'],
    [b'\x2E\x52\x4D\x46', 0, '.rm', 'application/vnd.rn-realmedia', 'RealMedia media file'],
    [b'\x6D\x6F\x6F\x76', 4, '.mov', 'video/quicktime', 'QuickTime movie file'],
    ### Audio ###
    [b'\x2E\x52\x4D\x46\x00\x00\x00\x12\x00', 0, '.ra', 'audio/x-pn-realaudio', 'RealAudio file'],
    [b'\x2E\x72\x61\xFD\x00', 0, '.ra', 'audio/x-pn-realaudio', 'RealAudio media file'],
    [b'\x4D\x54\x68\x64', 0, '.midi', 'audio/x-midi', 'Musical Instrument Digital Interface sound file'],
    [b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C', 0, '.wma', 'audio/x-ms-wma', 'Microsoft Windows Media Audio file'],
    [b'\x49\x44\x33', 0, '.mp3', 'audio/mpeg', 'MPEG-1 Audio Layer 3 (MP3) audio file'],
    [b'\x4F\x67\x67\x53\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00', 0, '.ogg', 'application/ogg', 'Ogg Vorbis audio file'],
    [b'\x57\x41\x56\x45\x66\x6D\x74\x20', 8, '.wav', 'audio/x-wav', 'Windows audio file '],
    [b'\x46\x4F\x52\x4D\x00', 0, '.aiff', 'audio/x-aiff', 'Audio Interchange File'],
    [b'\xFF\xF9\x4C\x80', 0, '.aac', 'audio/aac', 'AAC audio file'],
    [b'\x66\x4C\x61\x43\x00\x00\x00\x22', 0, '.flac', 'audio/flac', 'Free Lossless Audio Codec file'],
    ### Image ###
    [b'\x47\x49\x46\x38\x37\x61', 0, '.gif', 'image/gif', 'Graphics interchange format file (GIF87a)'],
    [b'\x47\x49\x46\x38\x39\x61', 0, '.gif', 'image/gif', 'Graphics interchange format file (GIF87a)'],
    [b'\x00\x00\x01\x00', 0, '.ico', 'image/x-icon', 'Icon Image file'],
    [b'\x01\x00\x00\x00\x01', 0, '.pic', 'image/x-pict', 'PICT Image file'],
    [b'\x42\x4D', 0, '.bmp', 'image/x-ms-bmp', 'Bitmap image'],
    [b'\x38\x42\x50\x53', 0, '.psd', ' 	image/vnd.adobe.photoshop', 'Photoshop Image file'],
    [b'\x49\x20\x49', 0, '.tiff', 'image/tiff', 'Tagged Image File Format file'],
    [b'\x49\x49\x2A\x00', 0, '.tiff', 'image/tiff', 'Tagged Image File Format file (Intel)'],
    [b'\x4D\x4D\x00\x2A', 0, '.tiff', 'image/tiff', 'Tagged Image File Format file (Motorola)'],
    [b'\x4D\x4D\x00\x2B', 0, '.tiff', 'image/tiff', 'BigTIFF files, Tagged Image File Format file larger than 4 GB'],
    [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', 0, '.png', 'image/png', 'Portable Network Graphics file'],
    [b'\xFF\xD8\xFF', 0, '.jpg', 'image/jpeg', 'JPEG/JFIF graphics file'],
    [b'\x67\x69\x6d\x70\x20\x78\x63\x66\x20', 0, '.xcf', 'image/x-xcf', 'XCF Gimp Image file'],
    ### office ###
    [b'\x50\x4B\x03\x04\x14\x00\x06\x00', 0, '.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Office 2007+ Open XML Format Document file'],
    [b'\xEC\xA5\xC1\x00', 512, '.doc', 'application/msword', 'Microsoft Office Word Document file'],
    [b'\x00\x6E\x1E\xF0', 512, '.ppt', 'application/vnd.ms-powerpoint', 'Microsoft Office PowerPoint Presentation file'],
    [b'\x0F\x00\xE8\x03', 512, '.ppt', 'application/vnd.ms-powerpoint', 'Microsoft Office PowerPoint Presentation file'],
    [b'\x00\x00\xFF\xFF\xFF\xFF', 6, '.hlp', 'application/winhlp', 'Windows Help file'],
    [b'\x00\x01\x00\x00\x4D\x53\x49\x53\x41\x4D\x20\x44\x61\x74\x61\x62\x61\x73\x65', 0, '.mny', 'application/x-msmoney', 'Microsoft Money file'],
    [b'\x00\x01\x00\x00\x53\x74\x61\x6E\x64\x61\x72\x64\x20\x41\x43\x45\x20\x44\x42', 0, '.accdb', 'application/msaccess', 'Microsoft Access 2007 file'],
    [b'\x00\x01\x00\x00\x53\x74\x61\x6E\x64\x61\x72\x64\x20\x4A\x65\x74\x20\x44\x42', 0, '.mdb', 'application/x-msaccess', 'Microsoft Access file'],
    [b'\x25\x50\x44\x46', 0, '.pdf', 'application/pdf', 'Adobe Portable Document Format file'],
    [b'\xA0\x46\x1D\xF0', 512, '.ppt', 'application/vnd.ms-powerpoint', 'Microsoft Office PowerPoint Presentation file'],
    [b'\xCF\x11\xE0\xA1\xB1\x1A\xE1\x00', 0, '.doc', 'application/msword', 'Perfect Office Document file'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.doc', 'application/msword', 'Microsoft Office Document file'],
    [b'\xFD\xFF\xFF\xFF', 512, '.ppt', 'application/vnd.ms-powerpoint', 'Microsoft Office PowerPoint presentation subheader'],
    [b'\x1A\x00\x00\x04\x00\x00', 0, '.nsf', 'application/vnd.lotus-notes', 'Lotus Notes database'],
    [b'\x00\x00\x02\x00\x06\x04\x06\x00\x08\x00\x00\x00\x00\x00', 0, '.wk1', 'application/vnd.lotus-1-2-3', 'Lotus 1-2-3 spreadsheet (v1) file'],
    [b'\x00\x00\x1A\x00\x00\x10\x04\x00\x00\x00\x00\x00', 0, '.wk3', 'application/vnd.lotus-1-2-3', 'Lotus 1-2-3 spreadsheet (v3) file'],
    [b'\x00\x00\x1A\x00\x02\x10\x04\x00\x00\x00\x00\x00', 0, '.wk5', 'application/vnd.lotus-1-2-3', 'Lotus 1-2-3 spreadsheet (v4 or v5) file'],
    [b'\x00\x00\x1A\x00\x05\x10\x04', 0, '.123', 'application/vnd.lotus-1-2-3', 'Lotus 1-2-3 spreadsheet (v9) file'],
    ### Media ###
    [b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x02\x00\x01', 0, '.mdf', 'application/octet-stream', 'Alcohol 120% Virtual CD image'],
    [b'\x43\x44\x30\x30\x31', 32769, '.iso', 'application/octet-stream', 'ISO-9660 CD Disc Image file'],
    [b'\x43\x44\x30\x30\x31', 34817, '.iso', 'application/octet-stream', 'ISO-9660 CD Disc Image file'],
    [b'\x43\x44\x30\x30\x31', 36865, '.iso', 'application/octet-stream', 'ISO-9660 CD Disc Image file'],
    [b'\x43\x57\x53', 0, '.swf', 'application/x-shockwave-flash', 'Admobe Shockwave Flash file'],
    [b'\x46\x57\x53', 0, '.swf', 'application/x-shockwave-flash', 'Macromedia Shockwave Flash file'],
    [b'\x43\x4F\x57\x44', 0, '.vmdk', 'application/octet-stream', 'VMware 3 Virtual Split Disk file'],
    [b'\x23\x20\x44\x69\x73\x6B\x20\x44\x65\x73\x63\x72\x69\x70\x74\x6F', 0, '.vmdk', 'application/octet-stream', 'VMware 4 Virtual Split Disk file'],
    [b'\x4B\x44\x4D', 0, '.vmdk', 'application/octet-stream', 'VMware 4 Virtual Split Disk file'],
    [b'\x4B\x44\x4D\x56', 0, '.vmdk', 'application/octet-stream', 'VMware 4 Virtual Single Disk file'],
    ### Archives ###
    [b'\x1A\x0B', 0, '.pak', 'application/pak', 'Compressed archive file (often associated with Quake Engine games)'],
    [b'\x1F\x9D', 0, '.tar.gz', 'application/x-tgz', 'Compressed tape archive file using standard compression'],
    [b'\x1F\xA0', 0, '.tar.gz', 'application/x-tgz', 'Compressed tape archive file using LZH compression'],
    [b'\x1F\x8B\x08', 0, '.gz', 'application/x-gzip', 'GZIP Archive file'],
    [b'\x75\x73\x74\x61\x72', 257, '.tar', 'application/x-tar', 'Tape Archive file'],
    [b'\x2D\x6C\x68', 2, '.lzh', 'application/octet-stream', 'Compressed archive file'],
    [b'\xFD\x37\x7A\x58\x5A\x00', 0, '.xz', 'application/x-xz', 'LMZA XZ Archive file'],
    [b'\x37\x7A\xBC\xAF\x27\x1C', 0, '.7z', 'application/x-7z-compressed', '7-Zip Compressed file'],
    [b'\x42\x5A\x68', 0, '.bz2', 'application/x-bzip2', 'BZIP2 Compressed Archive file'],
    [b'\x50\x4B\x03\x04', 0, '.zip', 'application/zip', 'PKZIP Archive file'],
    [b'\x50\x4B\x03\x04\x14\x00\x01\x00\x63\x00\x00\x00\x00\x00', 0, '.zip', 'application/zip', 'ZLock Pro Encrypted ZIP file'],
    [b'\x50\x4B\x4C\x49\x54\x45', 30, '.zip', 'application/zip', 'PKLITE Compressed ZIP Archive file'],
    [b'\x50\x4B\x53\x70\x58', 526, '.zip', 'application/zip', 'Self-Extracting Executable PKSFX Compressed file'],
    [b'\x52\x61\x72\x21\x1A\x07\x00', 0, '.rar', 'application/x-rar-compressed', 'WinRAR Compressed Archive file'],
    ### System ###
    [b'\x4D\x53\x43\x46', 0, '.cab', 'application/vnd.ms-cab-compressed', 'Microsoft cabinet file'],
    [b'\x49\x53\x63\x28', 0, '.cab', ' 	application/vnd.ms-cab-compressed', 'Install Shield v5.x or 6.x compressed file'],
    [b'\x4D\x5A', 0, '.exe', 'application/octet-stream', 'Windows Executable file'],
    [b'\x50\x4B\x03\x04\x14\x00\x08\x00\x08\x00', 0, '.jar', 'application/java-archive', 'Java Archive file'],
    [b'\x5F\x27\xA8\x89', 0, '.jar', 'application/java-archive', 'Jar Archive file'],
    [b'\x62\x70\x6C\x69\x73\x74', 0, '.plist', 'application/x-plist', 'Binary Property list'],
    [b'\xED\xAB\xEE\xDB', 0, '.rpm', 'application/x-rpm', 'RedHat Package Manager file'],
    [b'\x04\x00\x00\x00', 524, '.db', 'application/octet-stream', 'Windows Thumbs.db file'],
    [b'\xFF\xFE', 0, '.reg', 'text/plain', 'Windows Registry file '],
    [b'\xFF\xFE\x23\x00\x6C\x00\x69\x00\x6E\x00\x65\x00\x20\x00\x31\x00', 0, '.mof', 'text/plain', 'Windows MSinfo file'],
    [b'\xFF\xFF\xFF\xFF', 0, '.sys', 'text/plain', 'DOS system driver'],
    ### Other ###
    [b'\x23\x21\x2f\x75\x73\x72\x2f\x62\x69\x6e\x2f\x65\x6e\x76\x20\x70\x79\x74\x68\x6f\x6e', 0, '.py', 'text/plain', 'Python file'],
    [b'\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x31\x2E\x30\x22\x3F\x3E\x0D\x0A\x3C\x4D\x4D\x43\x5F\x43\x6F\x6E\x73\x6F\x6C\x65\x46\x69\x6C\x65\x20\x43\x6F\x6E\x73\x6F\x6C\x65\x56\x65\x72\x73\x69\x6F\x6E\x3D\x22', 0, '.msc', '', 'MMC Snap-in Control file'],
    [b'\x4D\x69\x63\x72\x6F\x73\x6F\x66\x74\x20\x57\x69\x6E\x64\x6F\x77\x73\x20\x4D\x65\x64\x69\x61\x20\x50\x6C\x61\x79\x65\x72\x20\x2D\x2D\x20', 84, '.wpl', '', 'Windows Media Player playlist'],
    [b'\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x31\x2E\x30\x22\x3F\x3E', 0, '.xml', '', 'User Interface Language'],
    [b'\x00\x01\x00\x00\x53\x74\x61\x6E\x64\x61\x72\x64\x20\x4A\x65\x74\x20\x44\x42', 0, '.mdb', '', 'Microsoft Access'],
    [b'\x00\x01\x00\x00\x4D\x53\x49\x53\x41\x4D\x20\x44\x61\x74\x61\x62\x61\x73\x65', 0, '.mny', '', 'Microsoft Money file'],
    [b'\x00\x01\x00\x00\x53\x74\x61\x6E\x64\x61\x72\x64\x20\x41\x43\x45\x20\x44\x42', 0, '.accdb', '', 'Microsoft Access 2007'],
    [b'\x4D\x69\x63\x72\x6F\x73\x6F\x66\x74\x20\x56\x69\x73\x75\x61\x6C', 0, '.sln', '', 'Visual Studio .NET file'],
    [b'\x4D\x69\x63\x72\x6F\x73\x6F\x66\x74\x20\x43\x2F\x43\x2B\x2B\x20', 0, '.pdb', '', 'MS C++ debugging symbols file'],
    [b'\x00\x06\x15\x61\x00\x00\x00\x02\x00\x00\x04\xD2\x00\x00\x10\x00', 0, '.db', '', 'Netscape Navigator (v4) database'],
    [b'\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00', 0, '.db', '', 'SQLite database file'],
    [b'\x4D\x5A\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xFF\xFF', 0, '.zap', '', 'ZoneAlam data file'],
    [b'\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D', 0, '.manifest', '', 'Windows Visual Stylesheet'],
    [b'\x00\x00\x00\x20\x66\x74\x79\x70\x4D\x34\x41', 0, '.m4a', '', 'Apple audio and video files'],
    [b'\x40\x40\x40\x20\x00\x00\x40\x40\x40\x40', 32, '.enl', '', 'EndNote Library File'],
    [b'\x3E\x00\x03\x00\xFE\xFF\x09\x00\x06', 24, '.wb3', '', 'Quatro Pro for Windows 7.0'],
    [b'\x2A\x2A\x2A\x20\x20\x49\x6E\x73', 0, '.log', '', 'Symantec Wise Installer log'],
    [b'\x0E\x4E\x65\x72\x6F\x49\x53\x4F', 0, '.nri', '', 'Nero CD compilation'],
    [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', 0, '.png', '', 'PNG image'],
    [b'\x50\x47\x50\x64\x4D\x41\x49\x4E', 0, '.pgd', '', 'PGP disk image'],
    [b'\x03\x00\x00\x00\x41\x50\x50\x52', 0, '.adx', '', 'Approach index file'],
    [b'\x41\x4F\x4C\x56\x4D\x31\x30\x30', 0, '.org', '', 'AOL personal file cabinet'],
    [b'\x41\x4F\x4C\x56\x4D\x31\x30\x30', 0, '.pfc', '', 'AOL personal file cabinet'],
    [b'\x30\x00\x00\x00\x4C\x66\x4C\x65', 0, '.evt', '', 'Windows Event Viewer file'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.spo', '', 'SPSS output file'],
    [b'\x00\x1E\x84\x90\x00\x00\x00\x00', 0, '.snm', '', 'Netscape Communicator (v4) mail folder'],
    [b'\xFF\x00\x02\x00\x04\x04\x05\x54', 0, '.wks', '', 'Works for Windows spreadsheet'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.opt', '', 'Developer Studio File Options file'],
    [b'\x30\x26\xB2\x75\x8E\x66\xCF\x11', 0, '.wmv', '', 'Windows Media Audio|Video File'],
    [b'\x30\x26\xB2\x75\x8E\x66\xCF\x11', 0, '.asf', '', 'Windows Media Audio|Video File'],
    [b'\x30\x26\xB2\x75\x8E\x66\xCF\x11', 0, '.wma', '', 'Windows Media Audio|Video File'],
    [b'\x4C\x00\x00\x00\x01\x14\x02\x00', 0, '.lnk', '', 'Windows shortcut file'],
    [b'\xFD\xFF\xFF\xFF\x43\x00\x00\x00', 512, '.ppt', '', 'PowerPoint presentation subheader_6'],
    [b'\x5B\x47\x65\x6E\x65\x72\x61\x6C', 0, '.ecf', '', 'MS Exchange configuration file'],
    [b'\x4D\x2D\x57\x20\x50\x6F\x63\x6B', 0, '.pdb', '', 'Merriam-Webster Pocket Dictionary'],
    [b'\x4D\x53\x5F\x56\x4F\x49\x43\x45', 0, '.cdr', '', 'Sony Compressed Voice File'],
    [b'\x4D\x53\x5F\x56\x4F\x49\x43\x45', 0, '.dvf', '', 'Sony Compressed Voice File'],
    [b'\x4D\x53\x5F\x56\x4F\x49\x43\x45', 0, '.msv', '', 'Sony Compressed Voice File'],
    [b'\x41\x4F\x4C\x20\x46\x65\x65\x64', 0, '.bag', '', 'AOL and AIM buddy list'],
    [b'\x53\x49\x45\x54\x52\x4F\x4E\x49', 0, '.cpi', '', 'Sietronics CPI XRD document'],
    [b'\xE3\x10\x00\x01\x00\x00\x00\x00', 0, '.info', '', 'Amiga icon'],
    [b'\x51\x57\x20\x56\x65\x72\x2E\x20', 0, '.abd', '', 'Quicken data file'],
    [b'\x51\x57\x20\x56\x65\x72\x2E\x20', 0, '.qsd', '', 'Quicken data file'],
    [b'\x00\x00\x00\x0C\x6A\x50\x20\x20', 0, '.jp2', '', 'JPEG2000 image files'],
    [b'\x49\x6E\x6E\x6F\x20\x53\x65\x74', 0, '.dat', '', 'Inno Setup Uninstall Log'],
    [b'\xCF\x11\xE0\xA1\xB1\x1A\xE1\x00', 0, '.doc', '', 'Perfect Office document'],
    [b'\x49\x54\x4F\x4C\x49\x54\x4C\x53', 0, '.lit', '', 'MS Reader eBook'],
    [b'\x42\x45\x47\x49\x4E\x3A\x56\x43', 0, '.vcf', '', 'vCard'],
    [b'\x09\x08\x10\x00\x00\x06\x05\x00', 512, '.xls', '', 'Excel spreadsheet subheader_1'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.db', '', 'MSWorks database file'],
    [b'\x46\x41\x58\x43\x4F\x56\x45\x52', 0, '.cpe', '', 'MS Fax Cover Sheet'],
    [b'\x4D\x53\x46\x54\x02\x00\x01\x00', 0, '.tlb', '', 'OLE|SPSS|Visual C++ library file'],
    [b'\x45\x4E\x54\x52\x59\x56\x43\x44', 0, '.vcd', '', 'VideoVCD|VCDImager file'],
    [b'\xFD\xFF\xFF\xFF\x1C\x00\x00\x00', 512, '.ppt', '', 'PowerPoint presentation subheader_5'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.rvt', '', 'Revit Project file'],
    [b'\x74\x42\x4D\x50\x4B\x6E\x57\x72', 60, '.prc', '', 'PathWay Map file'],
    [b'\x56\x45\x52\x53\x49\x4F\x4E\x20', 0, '.ctl', '', 'Visual Basic User-defined Control file'],
    [b'\x53\x74\x75\x66\x66\x49\x74\x20', 0, '.sit', '', 'StuffIt compressed archive'],
    [b'\xFD\xFF\xFF\xFF\x0E\x00\x00\x00', 512, '.ppt', '', 'PowerPoint presentation subheader_4'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.vsd', '', 'Visio file'],
    [b'\x00\x00\x00\x18\x66\x74\x79\x70', 0, '.3gp5', '', 'MPEG-4 video files'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.msi', '', 'Microsoft Installer package'],
    [b'\x23\x3F\x52\x41\x44\x49\x41\x4E', 0, '.hdr', '', 'Radiance High Dynamic Range image file'],
    [b'\x63\x6F\x6E\x65\x63\x74\x69\x78', 0, '.vhd', '', 'Virtual PC HD image'],
    [b'\x45\x56\x46\x09\x0D\x0A\xFF\x00', 0, '.e01', '', 'Expert Witness Compression Format'],
    [b'\x49\x49\x1A\x00\x00\x00\x48\x45', 0, '.crw', '', 'Canon RAW file'],
    [b'\x1A\x45\xDF\xA3\x93\x42\x82\x88', 0, '.mkv', '', 'Matroska stream file'],
    [b'\xCD\x20\xAA\xAA\x02\x00\x00\x00', 0, '', '', 'NAV quarantined virus file'],
    [b'\xAC\xED\x00\x05\x73\x72\x00\x12', 0, '.pdb', '', 'BGBlitz position database file'],
    [b'\x53\x5A\x20\x88\xF0\x27\x33\xD1', 0, '', '', 'QBASIC SZDD file'],
    [b'\x4C\x56\x46\x09\x0D\x0A\xFF\x00', 0, '.e01', '', 'Logical File Evidence Format'],
    [b'\x63\x75\x73\x68\x00\x00\x00\x02', 0, '.csh', '', 'Photoshop Custom Shape'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.pub', '', 'MS Publisher file'],
    [b'\x50\x4B\x03\x04\x14\x00\x08\x00', 0, '.jar', '', 'Java archive_2'],
    [b'\xFF\x4B\x45\x59\x42\x20\x20\x20', 0, '.sys', '', 'Keyboard driver file'],
    [b'\x54\x68\x69\x73\x20\x69\x73\x20', 0, '.info', '', 'GNU Info Reader file'],
    [b'\x52\x45\x56\x4E\x55\x4D\x3A\x2C', 0, '.ad', '', 'Antenna data file'],
    [b'\x4B\x57\x41\x4A\x88\xF0\x27\xD1', 0, '', '', 'KWAJ (compressed) file'],
    [b'\x50\x4B\x03\x04\x14\x00\x01\x00', 0, '.zip', '', 'ZLock Pro encrypted ZIP'],
    [b'\x43\x50\x54\x37\x46\x49\x4C\x45', 0, '.cpt', '', 'Corel Photopaint file_1'],
    [b'\x00\x00\x02\x00\x06\x04\x06\x00', 0, '.wk1', '', 'Lotus 1-2-3 (v1)'],
    [b'\x52\x65\x74\x75\x72\x6E\x2D\x50', 0, '.eml', '', 'Generic e-mail_1'],
    [b'\xFF\xFE\x23\x00\x6C\x00\x69\x00', 0, '.mof', '', 'MSinfo file'],
    [b'\x3C\x21\x64\x6F\x63\x74\x79\x70', 0, '.dci', '', 'AOL HTML mail'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.mtw', '', 'Minitab data file'],
    [b'\x73\x72\x63\x64\x6F\x63\x69\x64', 0, '.cal', '', 'CALS raster bitmap'],
    [b'\x28\x54\x68\x69\x73\x20\x66\x69', 0, '.hqx', '', 'BinHex 4 Compressed Archive'],
    [b'\x43\x6C\x69\x65\x6E\x74\x20\x55', 0, '.dat', '', 'IE History file'],
    [b'\x43\x23\x2B\x44\xA4\x43\x4D\xA5', 0, '.rtd', '', 'RagTime document'],
    [b'\x4D\x5A\x90\x00\x03\x00\x00\x00', 0, '.flt', '', 'Audition graphic filter'],
    [b'\x2E\x52\x4D\x46\x00\x00\x00\x12', 0, '.ra', '', 'RealAudio file'],
    [b'\x53\x51\x4C\x4F\x43\x4F\x4E\x56', 0, '.cnv', '', 'DB2 conversion file'],
    [b'\x4B\x47\x42\x5F\x61\x72\x63\x68', 0, '.kgb', '', 'KGB archive'],
    [b'\x3A\x56\x45\x52\x53\x49\x4F\x4E', 0, '.sle', '', 'Surfplan kite project file'],
    [b'\x8A\x01\x09\x00\x00\x00\xE1\x08', 0, '.aw', '', 'MS Answer Wizard'],
    [b'\x00\x00\x1A\x00\x00\x10\x04\x00', 0, '.wk3', '', 'Lotus 1-2-3 (v3)'],
    [b'\x55\x46\x4F\x4F\x72\x62\x69\x74', 0, '.dat', '', 'UFO Capture map file'],
    [b'\x9C\xCB\xCB\x8D\x13\x75\xD2\x11', 0, '.wab', '', 'Outlook address file'],
    [b'\x24\x46\x4C\x32\x40\x28\x23\x29', 0, '.sav', '', 'SPSS Data file'],
    [b'\x64\x65\x78\x0A\x30\x30\x39\x00', 0, '.dex', '', 'Dalvik (Android) executable file'],
    [b'\x4D\x5A\x90\x00\x03\x00\x00\x00', 0, '.api', '', 'Acrobat plug-in'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.ac_', '', 'CaseWare Working Papers'],
    [b'\x43\x61\x74\x61\x6C\x6F\x67\x20', 0, '.ctf', '', 'WhereIsIt Catalog'],
    [b'\x41\x56\x47\x36\x5F\x49\x6E\x74', 0, '.dat', '', 'AVG6 Integrity database'],
    [b'\x30\x31\x4F\x52\x44\x4E\x41\x4E', 0, '.ntf', '', 'National Transfer Format Map'],
    [b'\xE4\x52\x5C\x7B\x8C\xD8\xA7\x4D', 0, '.one', '', 'MS OneNote note'],
    [b'\x4F\x67\x67\x53\x00\x02\x00\x00', 0, '.oga', '', 'Ogg Vorbis Codec compressed file'],
    [b'\x4F\x67\x67\x53\x00\x02\x00\x00', 0, '.ogg', '', 'Ogg Vorbis Codec compressed file'],
    [b'\x4F\x67\x67\x53\x00\x02\x00\x00', 0, '.ogv', '', 'Ogg Vorbis Codec compressed file'],
    [b'\x4F\x67\x67\x53\x00\x02\x00\x00', 0, '.ogx', '', 'Ogg Vorbis Codec compressed file'],
    [b'\x1A\x52\x54\x53\x20\x43\x4F\x4D', 0, '.dat', '', 'Runtime Software disk image'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.doc', '', 'Microsoft Office document'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.dot', '', 'Microsoft Office document'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.pps', '', 'Microsoft Office document'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.ppt', '', 'Microsoft Office document'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.xla', '', 'Microsoft Office document'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.xls', '', 'Microsoft Office document'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.wiz', '', 'Microsoft Office document'],
    [b'\x45\x6C\x66\x46\x69\x6C\x65\x00', 0, '.evtx', '', 'Windows Vista event log'],
    [b'\x07\x64\x74\x32\x64\x64\x74\x64', 0, '.dtd', '', 'DesignTools 2D Design file'],
    [b'\x58\x50\x43\x4F\x4D\x0A\x54\x79', 0, '.xpt', '', 'XPCOM libraries'],
    [b'\x4E\x41\x56\x54\x52\x41\x46\x46', 0, '.dat', '', 'TomTom traffic data'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.sou', '', 'Visual Studio Solution User Options file'],
    [b'\x56\x65\x72\x73\x69\x6F\x6E\x20', 0, '.mif', '', 'MapInfo Interchange Format file'],
    [b'\x45\x52\x46\x53\x53\x41\x56\x45', 0, '.dat', '', 'EasyRecovery Saved State file'],
    [b'\x5B\x66\x6C\x74\x73\x69\x6D\x2E', 0, '.cfg', '', 'Flight Simulator Aircraft Configuration'],
    [b'\x4D\x5A\x90\x00\x03\x00\x00\x00', 0, '.ax', '', 'DirectShow filter'],
    [b'\x21\x3C\x61\x72\x63\x68\x3E\x0A', 0, '.lib', '', 'Unix archiver (ar)|MS Program Library Common Object File Format (COFF)'],
    [b'\x25\x21\x50\x53\x2D\x41\x64\x6F', 0, '.eps', '', 'Encapsulated PostScript file'],
    [b'\x50\x4B\x03\x04\x14\x00\x06\x00', 0, '.docx', '', 'MS Office 2007 documents'],
    [b'\x50\x4B\x03\x04\x14\x00\x06\x00', 0, '.pptx', '', 'MS Office 2007 documents'],
    [b'\x50\x4B\x03\x04\x14\x00\x06\x00', 0, '.xlsx', '', 'MS Office 2007 documents'],
    [b'\x81\x32\x84\xC1\x85\x05\xD0\x11', 0, '.wab', '', 'Outlook Express address book (Win95)'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.wps', '', 'MSWorks text document'],
    [b'\xB5\xA2\xB0\xB3\xB3\xB0\xA5\xB5', 0, '.cal', '', 'Windows calendar'],
    [b'\x53\x75\x70\x65\x72\x43\x61\x6C', 0, '.cal', '', 'SuperCalc worksheet'],
    [b'\x50\x4E\x43\x49\x55\x4E\x44\x4F', 0, '.dat', '', 'Norton Disk Doctor undo file'],
    [b'\x00\x00\x00\x14\x66\x74\x79\x70', 0, '.3gp', '', '3GPP multimedia files'],
    [b'\x37\xE4\x53\x96\xC9\xDB\xD6\x07', 0, '', '', 'zisofs compressed file'],
    [b'\x5B\x57\x69\x6E\x64\x6F\x77\x73', 0, '.cpx', '', 'Microsoft Code Page Translation file'],
    [b'\xA9\x0D\x00\x00\x00\x00\x00\x00', 0, '.dat', '', 'Access Data FTK evidence'],
    [b'\x42\x4F\x4F\x4B\x4D\x4F\x42\x49', 0, '.prc', '', 'Palmpilot resource file'],
    [b'\x4F\x50\x4C\x44\x61\x74\x61\x62', 0, '.dbf', '', 'Psion Series 3 Database'],
    [b'\x11\x00\x00\x00\x53\x43\x43\x41', 0, '.pf', '', 'Windows prefetch file'],
    [b'\x52\x41\x5A\x41\x54\x44\x42\x31', 0, '.dat', '', 'Shareaza (P2P) thumbnail'],
    [b'\x53\x5A\x44\x44\x88\xF0\x27\x33', 0, '', '', 'SZDD file format'],
    [b'\x00\x00\x1A\x00\x02\x10\x04\x00', 0, '.wk4', '', 'Lotus 1-2-3 (v4|v5)'],
    [b'\x00\x00\x1A\x00\x02\x10\x04\x00', 0, '.wk5', '', 'Lotus 1-2-3 (v4|v5)'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.apr', '', 'Lotus|IBM Approach 97 file'],
    [b'\x00\x00\x00\x20\x66\x74\x79\x70', 0, '.3gp', '', '3GPP2 multimedia files'],
    [b'\x45\x4C\x49\x54\x45\x20\x43\x6F', 0, '.cdr', '', 'Elite Plus Commander game file'],
    [b'\x50\x00\x00\x00\x20\x00\x00\x00', 0, '.idx', '', 'Quicken QuickFinder Information File'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.msc', '', 'Microsoft Common Console Document'],
    [b'\x41\x4F\x4C\x49\x4E\x44\x45\x58', 0, '.abi', '', 'AOL address book index'],
    [b'\x23\x20\x4D\x69\x63\x72\x6F\x73', 0, '.dsp', '', 'MS Developer Studio project file'],
    [b'\x76\x32\x30\x30\x33\x2E\x31\x30', 0, '.flt', '', 'Qimage filter'],
    [b'\x3C\x4D\x61\x6B\x65\x72\x46\x69', 0, '.fm', '', 'Adobe FrameMaker'],
    [b'\x3C\x4D\x61\x6B\x65\x72\x46\x69', 0, '.mif', '', 'Adobe FrameMaker'],
    [b'\x53\x4D\x41\x52\x54\x44\x52\x57', 0, '.sdr', '', 'SmartDraw Drawing file'],
    [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, '.adp', '', 'Access project file'],
    [b'\x23\x20\x44\x69\x73\x6B\x20\x44', 0, '.vmdk', '', 'VMware 4 Virtual Disk description'],
    [b'\x80\x00\x00\x20\x03\x12\x04', 0, '.adx', '', 'Dreamcast audio'],
    [b'\x43\x52\x55\x53\x48\x20\x76', 0, '.cru', '', 'Crush compressed archive'],
    [b'\x00\x00\x1A\x00\x05\x10\x04', 0, '.123', '', 'Lotus 1-2-3 (v9)'],
    [b'\x49\x44\x33\x03\x00\x00\x00', 0, '.koz', '', 'Sprint Music Store audio'],
    [b'\x00\x00\x49\x49\x58\x50\x52', 0, '.qxd', '', 'Quark Express (Intel)'],
    [b'\x52\x45\x47\x45\x44\x49\x54', 0, '.reg', '', 'WinNT Registry|Registry Undo files'],
    [b'\x52\x45\x47\x45\x44\x49\x54', 0, '.sud', '', 'WinNT Registry|Registry Undo files'],
    [b'\x57\x6F\x72\x64\x50\x72\x6F', 0, '.lwp', '', 'Lotus WordPro file'],
    [b'\x72\x74\x73\x70\x3A\x2F\x2F', 0, '.ram', '', 'RealMedia metafile'],
    [b'\x64\x73\x77\x66\x69\x6C\x65', 0, '.dsw', '', 'MS Visual Studio workspace file'],
    [b'\x5B\x50\x68\x6F\x6E\x65\x5D', 0, '.dun', '', 'Dial-up networking file'],
    [b'\x00\x00\x4D\x4D\x58\x50\x52', 0, '.qxd', '', 'Quark Express (Motorola)'],
    [b'\x42\x4C\x49\x32\x32\x33\x51', 0, '.bin', '', 'Speedtouch router firmware'],
    [b'\x52\x61\x72\x21\x1A\x07\x00', 0, '.rar', '', 'WinRAR compressed archive'],
    [b'\x43\x50\x54\x46\x49\x4C\x45', 0, '.cpt', '', 'Corel Photopaint file_2'],
    [b'\x57\x53\x32\x30\x30\x30', 0, '.ws2', '', 'WordStar for Windows file'],
    [b'\x41\x4F\x4C\x49\x44\x58', 0, '.ind', '', 'AOL client preferences|settings file'],
    [b'\x56\x43\x50\x43\x48\x30', 0, '.pch', '', 'Visual C PreCompiled header'],
    [b'\x55\x46\x41\xC6\xD2\xC1', 0, '.ufa', '', 'UFA compressed archive'],
    [b'\xAC\x9E\xBD\x8F\x00\x00', 0, '.qdf', '', 'Quicken data'],
    [b'\x50\x4B\x4C\x49\x54\x45', 30, '.zip', '', 'PKLITE archive'],
    [b'\x57\x69\x6E\x5A\x69\x70', 29152, '.zip', '', 'WinZip compressed archive'],
    [b'\x50\x41\x47\x45\x44\x55', 0, '.dmp', '', 'Windows memory dump'],
    [b'\x37\x7A\xBC\xAF\x27\x1C', 0, '.7z', '', '7-Zip compressed file'],
    [b'\x4D\x44\x4D\x50\x93\xA7', 0, '.dmp', '', 'Windows dump file'],
    [b'\x4D\x44\x4D\x50\x93\xA7', 0, '.hdmp', '', 'Windows dump file'],
    [b'\x45\x86\x00\x00\x06\x00', 0, '.qbb', '', 'QuickBooks backup'],
    [b'\x7B\x5C\x72\x74\x66\x31', 0, '.rtf', '', 'RTF file'],
    [b'\x5F\x43\x41\x53\x45\x5F', 0, '.cas', '', 'EnCase case file'],
    [b'\x5F\x43\x41\x53\x45\x5F', 0, '.cbk', '', 'EnCase case file'],
    [b'\x4E\x45\x53\x4D\x1A\x01', 0, '.nsf', '', 'NES Sound file'],
    [b'\x01\xDA\x01\x01\x00\x03', 0, '.rgb', '', 'Silicon Graphics RGB Bitmap'],
    [b'\x1A\x00\x00\x04\x00\x00', 0, '.nsf', '', 'Lotus Notes database'],
    [b'\x00\x00\xFF\xFF\xFF\xFF', 7, '.hlp', '', 'Windows Help file_1'],
    [b'\x4D\x4D\x4D\x44\x00\x00', 0, '.mmf', '', 'Yamaha Synthetic music Mobile Application Format'],
    [b'\x50\x49\x43\x54\x00\x08', 0, '.img', '', 'ChromaGraph Graphics Card Bitmap'],
    [b'\x62\x70\x6C\x69\x73\x74', 0, '.plist', '', 'Binary property list (plist)'],
    [b'\x00\x14\x00\x00\x01\x02', 0, '', '', 'BIOS details in RAM'],
    [b'\x4E\x61\x6D\x65\x3A\x20', 0, '.cod', '', 'Agent newsreader character map'],
    [b'\x01\xFF\x02\x04\x03\x02', 0, '.drw', '', 'Micrografx vector graphic file'],
    [b'\x4A\x41\x52\x43\x53\x00', 0, '.jar', '', 'JARCS compressed archive'],
    [b'\x43\x42\x46\x49\x4C\x45', 0, '.cbd', '', 'WordPerfect dictionary'],
    [b'\x2E\x72\x61\xFD\x00', 0, '.ra', '', 'RealAudio streaming media'],
    [b'\x23\x21\x41\x4D\x52', 0, '.amr', '', 'Adaptive Multi-Rate ACELP Codec (GSM)'],
    [b'\x41\x4F\x4C\x44\x42', 0, '.aby', '', 'AOL address book'],
    [b'\x53\x49\x54\x21\x00', 0, '.sit', '', 'StuffIt archive'],
    [b'\x7B\x0D\x0A\x6F\x20', 0, '.lgc', '', 'Windows application log'],
    [b'\x7B\x0D\x0A\x6F\x20', 0, '.lgd', '', 'Windows application log'],
    [b'\x5B\x76\x65\x72\x5D', 0, '.sam', '', 'Lotus AMI Pro document_2'],
    [b'\x7B\x5C\x70\x77\x69', 0, '.pwi', '', 'MS WinMobile personal note'],
    [b'\x62\x65\x67\x69\x6E', 0, '', '', 'UUencoded file'],
    [b'\x4D\x56\x32\x31\x34', 0, '.mls', '', 'Milestones project management file_1'],
    [b'\x48\x48\x47\x42\x31', 0, '.sh3', '', 'Harvard Graphics presentation file'],
    [b'\xFD\xFF\xFF\xFF\x04', 512, '.suo', '', 'Visual Studio Solution subheader'],
    [b'\xFD\xFF\xFF\xFF\x1F', 512, '.xls', '', 'Excel spreadsheet subheader_3'],
    [b'\x50\x4B\x53\x70\x58', 526, '.zip', '', 'PKSFX self-extracting archive'],
    [b'\x4D\x41\x72\x30\x00', 0, '.mar', '', 'MAr compressed archive'],
    [b'\x43\x44\x30\x30\x31', 0, '.iso', '', 'ISO-9660 CD Disc Image'],
    [b'\xFD\xFF\xFF\xFF\x23', 512, '.xls', '', 'Excel spreadsheet subheader_5'],
    [b'\x30\x37\x30\x37\x30', 0, '', '', 'cpio archive'],
    [b'\x4D\x49\x4C\x45\x53', 0, '.mls', '', 'Milestones project management file'],
    [b'\x46\x4F\x52\x4D\x00', 0, '.aiff', '', 'Audio Interchange File'],
    [b'\xBE\x00\x00\x00\xAB', 0, '.wri', '', 'MS Write file_3'],
    [b'\x5B\x56\x45\x52\x5D', 0, '.sam', '', 'Lotus AMI Pro document_1'],
    [b'\x4D\x41\x52\x31\x00', 0, '.mar', '', 'Mozilla archive'],
    [b'\x75\x73\x74\x61\x72', 257, '.tar', '', 'Tape Archive'],
    [b'\xFD\xFF\xFF\xFF\x29', 512, '.xls', '', 'Excel spreadsheet subheader_7'],
    [b'\xFD\xFF\xFF\xFF\x22', 512, '.xls', '', 'Excel spreadsheet subheader_4'],
    [b'\xFF\x46\x4F\x4E\x54', 0, '.cpi', '', 'Windows international code page'],
    [b'\x5B\x4D\x53\x56\x43', 0, '.vcw', '', 'Visual C++ Workbench Info File'],
    [b'\x4E\x49\x54\x46\x30', 0, '.ntf', '', 'National Imagery Transmission Format file'],
    [b'\xFD\xFF\xFF\xFF\x10', 512, '.xls', '', 'Excel spreadsheet subheader_2'],
    [b'\x41\x4F\x4C\x44\x42', 0, '.idx', '', 'AOL user configuration'],
    [b'\xFD\xFF\xFF\xFF\x20', 512, '.opt', '', 'Developer Studio subheader'],
    [b'\xFD\xFF\xFF\xFF\x28', 512, '.xls', '', 'Excel spreadsheet subheader_6'],
    [b'\x50\x4B\x03\x04', 0, '.xpi', '', 'Mozilla Browser Archive'],
    [b'\x04\x00\x00\x00', 0, '', '', 'INFO2 Windows recycle bin_1'],
    [b'\x50\x4B\x03\x04', 0, '.wmz', '', 'Windows Media compressed skin file'],
    [b'\x00\x00\x01\xBA', 0, '.mpg', '', 'DVD video file'],
    [b'\x00\x00\x01\xBA', 0, '.vob', '', 'DVD video file'],
    [b'\x0A\x02\x01\x01', 0, '.pcx', '', 'ZSOFT Paintbrush file_1'],
    [b'\xEB\x3C\x90\x2A', 0, '.img', '', 'GEM Raster file'],
    [b'\x4D\x4D\x00\x2A', 0, '.tif', '', 'TIFF file_3'],
    [b'\x4D\x4D\x00\x2A', 0, '.tiff', '', 'TIFF file_3'],
    [b'\x72\x65\x67\x66', 0, '.dat', '', 'WinNT registry file'],
    [b'\x72\x69\x66\x66', 0, '.ac', '', 'Sonic Foundry Acid Music File'],
    [b'\x4D\x4C\x53\x57', 0, '.mls', '', 'Skype localization data file'],
    [b'\x0A\x03\x01\x01', 0, '.pcx', '', 'ZSOFT Paintbrush file_2'],
    [b'\x50\x4D\x43\x43', 0, '.grp', '', 'Windows Program Manager group file'],
    [b'\xFD\xFF\xFF\xFF', 512, '.db', '', 'Thumbs.db subheader'],
    [b'\x47\x50\x41\x54', 0, '.pat', '', 'GIMP pattern file'],
    [b'\xEC\xA5\xC1\x00', 512, '.doc', '', 'Word document subheader'],
    [b'\x70\x6E\x6F\x74', 4, '.mov', '', 'QuickTime movie_5'],
    [b'\x50\x41\x43\x4B', 0, '.pak', '', 'Quake archive file'],
    [b'\x41\x43\x53\x44', 0, '', '', 'AOL parameter|info files'],
    [b'\x4D\x53\x43\x46', 0, '.ppz', '', 'Powerpoint Packaged Presentation'],
    [b'\x50\x4B\x03\x04', 0, '.xpt', '', 'eXact Packager Models'],
    [b'\x4D\x53\x43\x46', 0, '.cab', '', 'Microsoft cabinet file'],
    [b'\x4D\x41\x52\x43', 0, '.mar', '', 'Microsoft|MSN MARC archive'],
    [b'\x0D\x44\x4F\x43', 0, '.doc', '', 'DeskMate Document'],
    [b'\x4D\x54\x68\x64', 0, '.mid', '', 'MIDI sound file'],
    [b'\x4D\x54\x68\x64', 0, '.midi', '', 'MIDI sound file'],
    [b'\x0F\x00\xE8\x03', 512, '.ppt', '', 'PowerPoint presentation subheader_2'],
    [b'\x38\x42\x50\x53', 0, '.psd', '', 'Photoshop image'],
    [b'\x4A\x47\x03\x0E', 0, '.jg', '', 'AOL ART file_1'],
    [b'\x50\x4B\x05\x06', 0, '.zip', '', 'PKZIP archive_2'],
    [b'\x52\x49\x46\x46', 0, '.4xm', '', '4X Movie video'],
    [b'\x4A\x47\x04\x0E', 0, '.jg', '', 'AOL ART file_2'],
    [b'\xA1\xB2\xC3\xD4', 0, '', '', 'tcpdump (libpcap) capture file'],
    [b'\x01\x0F\x00\x00', 0, '.mdf', '', 'SQL Data Base'],
    [b'\x2E\x52\x4D\x46', 0, '.rm', '', 'RealMedia streaming media'],
    [b'\x2E\x52\x4D\x46', 0, '.rmvb', '', 'RealMedia streaming media'],
    [b'\x58\x43\x50\x00', 0, '.cap', '', 'Packet sniffer files'],
    [b'\x50\x4B\x03\x04', 0, '.zip', '', 'MacOS X Dashboard Widget'],
    [b'\x02\x64\x73\x73', 0, '.dss', '', 'Digital Speech Standard file'],
    [b'\x47\x49\x46\x38', 0, '.gif', '', 'GIF file'],
    [b'\xB1\x68\xDE\x3A', 0, '.dcx', '', 'PCX bitmap'],
    [b'\x52\x49\x46\x46', 0, '.cdr', '', 'CorelDraw document'],
    [b'\x73\x6B\x69\x70', 4, '.mov', '', 'QuickTime movie_6'],
    [b'\x07\x53\x4B\x46', 0, '.skf', '', 'SkinCrafter skin'],
    [b'\x49\x54\x53\x46', 0, '.chi', '', 'MS Compiled HTML Help File'],
    [b'\x49\x54\x53\x46', 0, '.chm', '', 'MS Compiled HTML Help File'],
    [b'\x43\x52\x45\x47', 0, '.dat', '', 'Win9x registry hive'],
    [b'\x91\x33\x48\x46', 0, '.hap', '', 'Hamarsoft compressed archive'],
    [b'\x6D\x6F\x6F\x76', 4, '.mov', '', 'QuickTime movie_1'],
    [b'\x52\x49\x46\x46', 0, '.avi', '', 'Resource Interchange File Format'],
    [b'\x52\x49\x46\x46', 0, '.cda', '', 'Resource Interchange File Format'],
    [b'\x52\x49\x46\x46', 0, '.qcp', '', 'Resource Interchange File Format'],
    [b'\x52\x49\x46\x46', 0, '.rmi', '', 'Resource Interchange File Format'],
    [b'\x52\x49\x46\x46', 0, '.wav', '', 'Resource Interchange File Format'],
    [b'\x50\x4B\x03\x04', 0, '.kwd', '', 'KWord document'],
    [b'\x43\x4D\x58\x31', 0, '.clb', '', 'Corel Binary metafile'],
    [b'\x25\x50\x44\x46', 0, '.pdf', '', 'PDF file'],
    [b'\x25\x50\x44\x46', 0, '.fdf', '', 'PDF file'],
    [b'\x7F\x45\x4C\x46', 0, '', '', 'ELF executable'],
    [b'\x64\x00\x00\x00', 0, '.p10', '', 'Intel PROset|Wireless Profile'],
    [b'\xC3\xAB\xCD\xAB', 0, '.acs', '', 'MS Agent Character file'],
    [b'\x53\x43\x48\x6C', 0, '.ast', '', 'Underground Audio'],
    [b'\x49\x53\x63\x28', 0, '.cab', '', 'Install Shield compressed file'],
    [b'\x49\x53\x63\x28', 0, '.hdr', '', 'Install Shield compressed file'],
    [b'\x41\x43\x31\x30', 0, '.dwg', '', 'Generic AutoCAD drawing'],
    [b'\x4E\x42\x2A\x00', 0, '.jnt', '', 'MS Windows journal'],
    [b'\x4E\x42\x2A\x00', 0, '.jtp', '', 'MS Windows journal'],
    [b'\x52\x49\x46\x46', 0, '.ds4', '', 'Micrografx Designer graphic'],
    [b'\x50\x4B\x03\x04', 0, '.sxc', '', 'StarOffice spreadsheet'],
    [b'\x52\x49\x46\x46', 0, '.ani', '', 'Windows animated cursor'],
    [b'\x53\x48\x4F\x57', 0, '.shw', '', 'Harvard Graphics presentation'],
    [b'\xD4\xC3\xB2\xA1', 0, '', '', 'WinDump (winpcap) capture file'],
    [b'\xDB\xA5\x2D\x00', 0, '.doc', '', 'Word 2.0 file'],
    [b'\x50\x45\x53\x54', 0, '.dat', '', 'PestPatrol data|scan strings'],
    [b'\x73\x6C\x68\x2E', 0, '.dat', '', 'Allegro Generic Packfile (uncompressed)'],
    [b'\xCA\xFE\xBA\xBE', 0, '.class', '', 'Java bytecode'],
    [b'\x57\x4D\x4D\x50', 0, '.dat', '', 'Walkman MP3 file'],
    [b'\x00\x00\x01\xB3', 0, '.mpg', '', 'MPEG video file'],
    [b'\x00\x00\x02\x00', 0, '.wb2', '', 'QuattroPro spreadsheet'],
    [b'\x49\x49\x2A\x00', 0, '.tif', '', 'TIFF file_2'],
    [b'\x49\x49\x2A\x00', 0, '.tiff', '', 'TIFF file_2'],
    [b'\x6C\x33\x33\x6C', 0, '.dbb', '', 'Skype user data file'],
    [b'\x52\x49\x46\x46', 0, '.dat', '', 'Video CD MPEG movie'],
    [b'\x0E\x57\x4B\x53', 0, '.wks', '', 'DeskMate Worksheet'],
    [b'\x6D\x64\x61\x74', 4, '.mov', '', 'QuickTime movie_3'],
    [b'\x3F\x5F\x03\x00', 0, '.gid', '', 'Windows Help file_2'],
    [b'\x3F\x5F\x03\x00', 0, '.hlp', '', 'Windows Help file_2'],
    [b'\x68\x49\x00\x00', 0, '.shd', '', 'Win Server 2003 printer spool file'],
    [b'\x00\x00\x01\x00', 0, '.ico', '', 'Windows icon|printer spool file'],
    [b'\x00\x00\x01\x00', 0, '.spl', '', 'Windows icon|printer spool file'],
    [b'\x53\x43\x4D\x49', 0, '.img', '', 'Img Software Bitmap'],
    [b'\x51\x45\x4C\x20', 92, '.qel', '', 'Quicken data'],
    [b'\x73\x7A\x65\x7A', 0, '.pdb', '', 'PowerBASIC Debugger Symbols'],
    [b'\x00\x00\x02\x00', 0, '.cur', '', 'Windows cursor'],
    [b'\x5F\x27\xA8\x89', 0, '.jar', '', 'Jar archive'],
    [b'\x50\x4B\x03\x04', 0, '.docx', '', 'MS Office Open XML Format Document'],
    [b'\x50\x4B\x03\x04', 0, '.pptx', '', 'MS Office Open XML Format Document'],
    [b'\x50\x4B\x03\x04', 0, '.xlsx', '', 'MS Office Open XML Format Document'],
    [b'\x77\x69\x64\x65', 4, '.mov', '', 'QuickTime movie_4'],
    [b'\x43\x4F\x57\x44', 0, '.vmdk', '', 'VMware 3 Virtual Disk'],
    [b'\x44\x42\x46\x48', 0, '.db', '', 'Palm Zire photo database'],
    [b'\x4B\x49\x00\x00', 0, '.shd', '', 'Win9x printer spool file'],
    [b'\xFF\x57\x50\x43', 0, '.wp', '', 'WordPerfect text and graphics'],
    [b'\xFF\x57\x50\x43', 0, '.wpd', '', 'WordPerfect text and graphics'],
    [b'\xFF\x57\x50\x43', 0, '.wpg', '', 'WordPerfect text and graphics'],
    [b'\xFF\x57\x50\x43', 0, '.wpp', '', 'WordPerfect text and graphics'],
    [b'\xFF\x57\x50\x43', 0, '.wp5', '', 'WordPerfect text and graphics'],
    [b'\xFF\x57\x50\x43', 0, '.wp6', '', 'WordPerfect text and graphics'],
    [b'\x2E\x52\x45\x43', 0, '.ivr', '', 'RealPlayer video file (V11+)'],
    [b'\x1A\x35\x01\x00', 0, '.eth', '', 'WinPharoah capture file'],
    [b'\x66\x49\x00\x00', 0, '.shd', '', 'WinNT printer spool file'],
    [b'\x4D\x4D\x00\x2B', 0, '.tif', '', 'TIFF file_4'],
    [b'\x4D\x4D\x00\x2B', 0, '.tiff', '', 'TIFF file_4'],
    [b'\x44\x4D\x53\x21', 0, '.dms', '', 'Amiga DiskMasher compressed archive'],
    [b'\xD7\xCD\xC6\x9A', 0, '.wmf', '', 'Windows graphics metafile'],
    [b'\x52\x49\x46\x46', 0, '.cmx', '', 'Corel Presentation Exchange metadata'],
    [b'\xA1\xB2\xCD\x34', 0, '', '', 'Extended tcpdump (libpcap) capture file'],
    [b'\x4D\x56\x32\x43', 0, '.mls', '', 'Milestones project management file_2'],
    [b'\x05\x00\x00\x00', 0, '', '', 'INFO2 Windows recycle bin_2'],
    [b'\x64\x6E\x73\x2E', 0, '.au', '', 'Audacity audio file'],
    [b'\x50\x4B\x03\x04', 0, '.zip', '', 'PKZIP archive_1'],
    [b'\xB4\x6E\x68\x44', 0, '.tib', '', 'Acronis True Image'],
    [b'\x4D\x53\x43\x46', 0, '.snp', '', 'MS Access Snapshot Viewer file'],
    [b'\x43\x4F\x4D\x2B', 0, '.clb', '', 'COM+ Catalog'],
    [b'\x03\x00\x00\x00', 0, '.qph', '', 'Quicken price history'],
    [b'\x50\x4B\x03\x04', 0, '.xps', '', 'XML paper specification file'],
    [b'\x50\x4B\x03\x04', 0, '.jar', '', 'Java archive_1'],
    [b'\x67\x49\x00\x00', 0, '.shd', '', 'Win2000|XP printer spool file'],
    [b'\x34\xCD\xB2\xA1', 0, '', '', 'Tcpdump capture file'],
    [b'\x7E\x42\x4B\x00', 0, '.psp', '', 'Corel Paint Shop Pro image'],
    [b'\x41\x4D\x59\x4F', 0, '.syw', '', 'Harvard Graphics symbol graphic'],
    [b'\xD2\x0A\x00\x00', 0, '.ftr', '', 'WinPharoah filter file'],
    [b'\x50\x4B\x03\x04', 0, '.odt', '', 'OpenDocument template'],
    [b'\x50\x4B\x03\x04', 0, '.odp', '', 'OpenDocument template'],
    [b'\x50\x4B\x03\x04', 0, '.ott', '', 'OpenDocument template'],
    [b'\x7A\x62\x65\x78', 0, '.info', '', 'ZoomBrowser Image Index'],
    [b'\xC5\xD0\xD3\xC6', 0, '.eps', '', 'Adobe encapsulated PostScript'],
    [b'\xC8\x00\x79\x00', 0, '.lbk', '', 'Jeppesen FliteLog file'],
    [b'\x0A\x05\x01\x01', 0, '.pcx', '', 'ZSOFT Paintbrush file_3'],
    [b'\x4C\x4E\x02\x00', 0, '.gid', '', 'Windows help file_3'],
    [b'\x4C\x4E\x02\x00', 0, '.hlp', '', 'Windows help file_3'],
    [b'\x55\x43\x45\x58', 0, '.uce', '', 'Unicode extensions'],
    [b'\xED\xAB\xEE\xDB', 0, '.rpm', '', 'RedHat Package Manager'],
    [b'\x41\x72\x43\x01', 0, '.arc', '', 'FreeArc compressed file'],
    [b'\xB0\x4D\x46\x43', 0, '.pwl', '', 'Win95 password file'],
    [b'\x5A\x4F\x4F\x20', 0, '.zoo', '', 'ZOO compressed archive'],
    [b'\x2E\x73\x6E\x64', 0, '.au', '', 'NeXT|Sun Microsystems audio file'],
    [b'\x52\x54\x53\x53', 0, '.cap', '', 'WinNT Netmon capture file'],
    [b'\x46\x72\x6F\x6D', 0, '.eml', '', 'Generic e-mail_2'],
    [b'\x4D\x52\x56\x4E', 0, '.nvram', '', 'VMware BIOS state file'],
    [b'\x66\x72\x65\x65', 4, '.mov', '', 'QuickTime movie_2'],
    [b'\xA0\x46\x1D\xF0', 512, '.ppt', '', 'PowerPoint presentation subheader_3'],
    [b'\xFF\xFF\xFF\xFF', 0, '.sys', '', 'DOS system driver'],
    [b'\xE3\x82\x85\x96', 0, '.pwl', '', 'Win98 password file'],
    [b'\x73\x6C\x68\x21', 0, '.dat', '', 'Allegro Generic Packfile (compressed)'],
    [b'\x00\x01\x42\x44', 0, '.dba', '', 'Palm DateBook Archive'],
    [b'\xFF\xFE\x00\x00', 0, '', '', 'UTF-32|UCS-4 file'],
    [b'\xCF\xAD\x12\xFE', 0, '.dbx', '', 'Outlook Express e-mail folder'],
    [b'\x00\x01\x42\x41', 0, '.aba', '', 'Palm Address Book Archive'],
    [b'\x00\x6E\x1E\xF0', 512, '.ppt', '', 'PowerPoint presentation subheader_1'],
    [b'\x50\x4B\x07\x08', 0, '.zip', '', 'PKZIP archive_3'],
    [b'\x50\x4B\x03\x04', 0, '.sxc', '', 'OpenOffice documents'],
    [b'\x50\x4B\x03\x04', 0, '.sxd', '', 'OpenOffice documents'],
    [b'\x50\x4B\x03\x04', 0, '.sxi', '', 'OpenOffice documents'],
    [b'\x50\x4B\x03\x04', 0, '.sxw', '', 'OpenOffice documents'],
    [b'\x81\xCD\xAB', 0, '.wpf', '', 'WordPerfect text'],
    [b'\x50\x41\x58', 0, '.pax', '', 'PAX password protected bitmap'],
    [b'\x49\x44\x33', 0, '.mp3', '', 'MP3 audio file'],
    [b'\x44\x56\x44', 0, '.ifo', '', 'DVD info file'],
    [b'\x1F\x8B\x08', 0, '.gz', '', 'GZIP archive file'],
    [b'\xEF\xBB\xBF', 0, '', '', 'UTF8 file'],
    [b'\x49\x20\x49', 0, '.tif', '', 'TIFF file_1'],
    [b'\x49\x20\x49', 0, '.tiff', '', 'TIFF file_1'],
    [b'\x43\x57\x53', 0, '.swf', '', 'Shockwave Flash file'],
    [b'\x41\x43\x76', 0, '.sle', '', 'Steganos virtual secure drive'],
    [b'\x41\x4F\x4C', 0, '.abi', '', 'AOL config files'],
    [b'\x41\x4F\x4C', 0, '.aby', '', 'AOL config files'],
    [b'\x41\x4F\x4C', 0, '.bag', '', 'AOL config files'],
    [b'\x41\x4F\x4C', 0, '.idx', '', 'AOL config files'],
    [b'\x41\x4F\x4C', 0, '.ind', '', 'AOL config files'],
    [b'\x41\x4F\x4C', 0, '.pfc', '', 'AOL config files'],
    [b'\x4B\x44\x4D', 0, '.vmdk', '', 'VMware 4 Virtual Disk'],
    [b'\x42\x5A\x68', 0, '.bz2', '', 'bzip2 compressed archive'],
    [b'\x42\x5A\x68', 0, '.tar.bz2', '', 'bzip2 compressed archive'],
    [b'\x42\x5A\x68', 0, '.tbz2', '', 'bzip2 compressed archive'],
    [b'\x42\x5A\x68', 0, '.tb2', '', 'bzip2 compressed archive'],
    [b'\xFF\xD8\xFF', 0, '.jfif', '', 'JPEG|EXIF|SPIFF images'],
    [b'\xFF\xD8\xFF', 0, '.jpe', '', 'JPEG|EXIF|SPIFF images'],
    [b'\xFF\xD8\xFF', 0, '.jpeg', '', 'JPEG|EXIF|SPIFF images'],
    [b'\xFF\xD8\xFF', 0, '.jpg', '', 'JPEG|EXIF|SPIFF images'],
    [b'\x2D\x6C\x68', 2, '.lha', '', 'Compressed archive'],
    [b'\x2D\x6C\x68', 2, '.lzh', '', 'Compressed archive'],
    [b'\x44\x56\x44', 0, '.dvr', '', 'DVR-Studio stream file'],
    [b'\x1A\x00\x00', 0, '.ntf', '', 'Lotus Notes database template'],
    [b'\x50\x35\x0A', 0, '.pgm', '', 'Portable Graymap Graphic'],
    [b'\x46\x57\x53', 0, '.swf', '', 'Shockwave Flash player'],
    [b'\x46\x4C\x56', 0, '.flv', '', 'Flash video file'],
    [b'\x51\x46\x49', 0, '.qemu', '', 'Qcow Disk Image'],
    [b'\x73\x6D\x5F', 0, '.pdb', '', 'PalmOS SuperMemo'],
    [b'\x44\x4F\x53', 0, '.adf', '', 'Amiga disk file'],
    [b'\x1F\x9D\x90', 0, '.tar.z', '', 'Compressed tape archive_1'],
    [b'\x47\x58\x32', 0, '.gx2', '', 'Show Partner graphics file'],
    [b'\x01\x10', 0, '.tr1', '', 'Novell LANalyzer capture file'],
    [b'\x4C\x01', 0, '.obj', '', 'MS COFF relocatable object code'],
    [b'\x1A\x0B', 0, '.pak', '', 'Compressed archive file'],
    [b'\x4D\x5A', 0, '.ocx', '', 'ActiveX|OLE Custom Control'],
    [b'\x1D\x7D', 0, '.ws', '', 'WordStar Version 5.0|6.0 document'],
    [b'\x1A\x04', 0, '.arc', '', 'LH archive (old vers.|type 3)'],
    [b'\x4D\x56', 0, '.dsn', '', 'CD Stomper Pro label file'],
    [b'\x1A\x09', 0, '.arc', '', 'LH archive (old vers.|type 5)'],
    [b'\x58\x2D', 0, '.eml', '', 'Exchange e-mail'],
    [b'\x1A\x02', 0, '.arc', '', 'LH archive (old vers.|type 1)'],
    [b'\x1F\xA0', 0, '.tar.z', '', 'Compressed tape archive_2'],
    [b'\xFF\xFE', 0, '.reg', '', 'Windows Registry file'],
    [b'\x60\xEA', 0, '.arj', '', 'Compressed archive file'],
    [b'\x4D\x5A', 0, '.scr', '', 'Screen saver'],
    [b'\x4D\x5A', 0, '.ax', '', 'Library cache file'],
    [b'\x4D\x5A', 0, '.acm', '', 'MS audio compression manager driver'],
    [b'\xFE\xFF', 0, '', '', 'UTF-16|UCS-2 file'],
    [b'\x6F\x3C', 0, '', '', 'SMS text (SIM)'],
    [b'\x1A\x08', 0, '.arc', '', 'LH archive (old vers.|type 4)'],
    [b'\x4D\x5A', 0, '.olb', '', 'OLE object library'],
    [b'\x0C\xED', 0, '.mp', '', 'Monochrome Picture TIFF bitmap'],
    [b'\x99\x01', 0, '.pkr', '', 'PGP public keyring'],
    [b'\x45\x50', 0, '.mdi', '', 'MS Document Imaging file'],
    [b'\x95\x00', 0, '.skr', '', 'PGP secret keyring_1'],
    [b'\x4D\x5A', 0, '.fon', '', 'Font file'],
    [b'\x21\x12', 0, '.ain', '', 'AIN Compressed Archive'],
    [b'\x4D\x5A', 0, '.vxd', '', 'Windows virtual device drivers'],
    [b'\x4D\x5A', 0, '.386', '', 'Windows virtual device drivers'],
    [b'\x58\x54', 0, '.bdr', '', 'MS Publisher'],
    [b'\x4D\x5A', 0, '.cpl', '', 'Control panel application'],
    [b'\x32\xBE', 0, '.wri', '', 'MS Write file_2'],
    [b'\x00\x11', 0, '.fli', '', 'FLIC animation'],
    [b'\xD4\x2A', 0, '.arl', '', 'AOL history|typed URL files'],
    [b'\xD4\x2A', 0, '.aut', '', 'AOL history|typed URL files'],
    [b'\x95\x01', 0, '.skr', '', 'PGP secret keyring_2'],
    [b'\x42\x4D', 0, '.bmp', '', 'Bitmap image'],
    [b'\x42\x4D', 0, '.dib', '', 'Bitmap image'],
    [b'\x1A\x03', 0, '.arc', '', 'LH archive (old vers.|type 2)'],
    [b'\xDC\xFE', 0, '.efx', '', 'eFax file'],
    [b'\xDC\xDC', 0, '.cpl', '', 'Corel color palette'],
    [b'\x31\xBE', 0, '.wri', '', 'MS Write file_1'],
    [b'\x4D\x5A', 0, '.com', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.dll', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.drv', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.exe', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.pif', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.qts', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.qtx', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.sys', '', 'Windows|DOS executable file'],
    [b'\x4D\x5A', 0, '.vbx', '', 'VisualBASIC application'],
    [b'\xAC\xED', 0, '', '', 'Java serialization data'],
    [b'\xFE\xEF', 0, '.gho', '', 'Symantex Ghost image file'],
    [b'\xFE\xEF', 0, '.ghs', '', 'Symantex Ghost image file'],
    [b'\x23\x20', 0, '.msi', '', 'Cerius2 file'],
    [b'\x4F\x7B', 0, '.dw4', '', 'Visio|DisplayWrite 4 text file'],
    [b'\x80', 0, '.obj', '', 'Relocatable object code'],
    [b'\x3C', 0, '.asx', '', 'Advanced Stream Redirector'],
    [b'\xEB', 0, '.com', '', 'Windows executable file_3'],
    [b'\xEB', 0, '.sys', '', 'Windows executable file_3'],
    [b'\x04', 0, '.db4', '', 'dBASE IV file'],
    [b'\xFF', 0, '.sys', '', 'Windows executable'],
    [b'\x08', 0, '.db', '', 'dBASE IV or dBFast configuration file'],
    [b'\x03', 0, '.db3', '', 'dBASE III file'],
    [b'\x03', 0, '.dat', '', 'MapInfo Native Data Format'],
    [b'\x07', 0, '.drw', '', 'Generic drawing programs'],
    [b'\x99', 0, '.gpg', '', 'GPG public keyring'],
    [b'\x30', 0, '.cat', '', 'MS security catalog file'],
    [b'\xE8', 0, '.com', '', 'Windows executable file_1'],
    [b'\xE8', 0, '.sys', '', 'Windows executable file_1'],
    [b'\xE9', 0, '.com', '', 'Windows executable file_2'],
    [b'\xE9', 0, '.sys', '', 'Windows executable file_2'],
    [b'\x3C', 0, '.xdr', '', 'BizTalk XML-Data Reduced Schema'],
    [b'\x78', 0, '.dmg', '', 'MacOS X image file'],
]

if __name__ == '__main__':
    import sys
    import os
    from optparse import OptionParser
    usage = "usage: %prog [options] filename <filename2>..."
    description = "puremagic is a pure python file identification module. It looks for matching magic numbers in the file to locate the file type. "
    parser = OptionParser(usage=usage, version=__version__, description=description)
    parser.add_option("-m", "--mime",
                  action="store_true", dest="mime", help="Return the mime type instead of file type")
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("please specifiy a filename")
        sys.exit()
    if options.mime:
        mime = True
    else:
        mime = False

    for filename in args:
        if not os.path.exists(filename):    
            sys.stderr.write("File '%s' does not exist!\n Please check the location and filename and try again.\n" % filename)
            continue
        try:
            sys.stdout.write("'%s' : %s\n" % (filename, from_file(filename, mime)))
        except LookupError:
            sys.stdout.write("'%s' : could not be Identified \n" % filename)
      