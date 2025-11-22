#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Usage: fontforge %s path
   argv[1] ... path
eg. fontforge removebitmap.py ~/Downloads/fonts
"""

import sys
import glob
import tempfile
import os
import shutil

# fontforge setting.
fontforge.setPrefs('CoverageFormatsAllowed', 1)
fontforge.setPrefs('UndoDepth', 0)


# TTF flags
flags = ('opentype', 'round')


"""
antialias: Hints are not applied, use grayscale smoothing.
gridfit: Use hinting in Windows.
gridfit+smoothing: ClearType GridFitting; (hinting with ClearType).
symmetric-smoothing: ClearType Antialiasing; (ClearType smoothing only).

gridfit is hinting on Windows. So gridfit is unnecessary for me.
"""
def gasp():
    return (
        (65535, ('antialias', 'symmetric-smoothing')),
    )


"""
@return: list
"""
def fontsSearch(dir, *exts):
    files = []
    dir = os.path.abspath(os.path.expanduser(dir))
    for ext in exts:
        files.extend(glob.glob(dir + '/' + ext))
    return files


"""
Main function
"""
def main(argvs):
    # Set work and save director. Please apply these to your environment.
    workDir = argvs[1]
    saveDir = workDir + "/new"

    if not os.path.exists(saveDir):
        os.makedirs(saveDir)


    """
    DO NOT CHANGE BELLOW.
    """
    argc = len(argvs)

    if argc != 2:
        print("Usage: fontforge %s /path/dir" % argvs[0])
        print("   eg. fontforge %s ~/Downloads/fonts" % argvs[0])
        quit()

    # Search for TrueType files
    fontFiles = fontsSearch(argvs[1], '*.ttc', '*.ttf')
    for fontFile in fontFiles:
        # set variables.
        fontFSName = os.path.basename(fontFile)
        tmpPrefix = "breakttc"
        tempDir = tempfile.mkdtemp()

        print("Starting to break TTC.")
        # Get packed family names
        familyNames = fontforge.fontsInFile(fontFile)
        i = 0

        # Break a TTC to some TTFs.
        for familyName in familyNames:
            # openName format: "msgothic.ttc(MS UI Gothic)"
            print("%s" % familyName)
            openName = "%s(%s)" % (fontFile, familyName)

            # tmp file name: breakttf0a.ttf and breakttf1a.ttf and so on.
            tmpTTF = "%s%da.ttf" % (tmpPrefix, i)

            # Open font
            font = fontforge.open(openName)

            # Edit font
            font.encoding = 'UnicodeFull'
            font.gasp = gasp()
            font.gasp_version = 1
            font.os2_vendor = "maud"
            font.os2_version = 1 # Avoid UTF-16 issues on Windows

            # Temporarily save to TTF
            font.generate(tempDir + "/" + tmpTTF, flags=flags)
            font.close()
            i += 1
        print("Finished breaking TTC.")


        print("Starting to generate TTC.")
        # set variables.
        newTTCname = fontFSName
        newFontPath = tempDir + "/" + newTTCname
        saveFontPath = saveDir + "/" + newTTCname
        files = glob.glob(tempDir + "/" + tmpPrefix + '[0-9]a.ttf')

        f = fontforge.open(files[0])
        
        # If we're to make a TTC, we should have at least two files. We're popping one,
        # so `len` should be at least 1.
        files.pop(0)
        if len(files) > 0:
            # Append further TTFs onto the first one.
            for file in files:
                # With multiple applications open on small embedded systems, this will crash due
                # to insufficient memory.
                f2 = fontforge.open(file)
                f.generateTtc(newFontPath, f2, ttcflags=("merge",), layer=1)
                f2.close()
        # If there was only one file (`len` is now 0 after popping), just make a TTF.
        elif len(files) == 0:
            f.generate(newFontPath, flags=flags)

        # Close our new TTC.
        f.close()
        print("Finished generating TTC.")

        # Move the TTC files from the temporary directory to their permanent location.
        if os.path.exists(newFontPath):
            shutil.move(newFontPath, saveFontPath)

        # Remove the temporary directory.
        shutil.rmtree(tempDir)
        print("Cleaned up temporary directory.")

    # Finish
    print("Finished all in dir.")

if __name__ == '__main__':
    main(sys.argv)
