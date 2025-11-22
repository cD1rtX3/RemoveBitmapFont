#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Usage: python %s path
   argv[1] ... path
eg. python removebitmap.py ~/Downloads/fonts
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
        print "Usage: python %s /path/dir" % argvs[0]
        print "   eg. python %s ~/Downloads/fonts" % argvs[0]
        quit()

    # TrueType 系統のファイルを探す。
    fontFiles = fontsSearch(argvs[1], '*.ttc', '*.ttf')

    # 見つかった TrueType 系統のファイルを順次変換する。
    for fontFile in fontFiles:
        # set variables.
        fontFSName = os.path.basename(fontFile)
        tmpPrefix = "breakttc"
        tempDir = tempfile.mkdtemp()

        print "Start breaking TTC."
        # Get packed family names
        familyNames = fontforge.fontsInFile(fontFile)
        i = 0

        # Break a TTC to some TTFs.
        for familyName in familyNames:
            # openName format: "msgothic.ttc(MS UI Gothic)"
            print "%s" % familyName
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
            font.os2_version = 1 # Windows で幅広問題を回避する。

            # ttf へ一時的に保存する。
            font.generate(tempDir + "/" + tmpTTF, flags=flags)
            font.close()
            i += 1
        print "Finish breaking TTC."


        print "Start generate TTC."
        # set variables.
        newTTCname = fontFSName
        newFontPath = tempDir + "/" + newTTCname
        saveFontPath = saveDir + "/" + newTTCname
        files = glob.glob(tempDir + "/" + tmpPrefix + '[0-9]a.ttf')

        f = fontforge.open(files[0])
        files.pop(0)

        # TTC の場合 pop しても一つ以上残るはず。
        if len(files) > 0:
            # 残りの ttf を最初の ttf に追加する。
            for file in files:
                # Raspberry Pi 3 は複数開くとメモリが足りなくて落ちるので注意。
                f2 = fontforge.open(file)
                f.generateTtc(newFontPath, f2, ttcflags=("merge",), layer=1)
                f2.close()
        # TTF の場合 pop して一つ減ってるから 0 になるはず。
        elif len(files) == 0:
            f.generate(newFontPath, flags=flags)

        # 新しく生成した分のフォントを閉じる。
        f.close()
        print "Finish generate TTC."

        # temporary 内の ttc ファイルを保存先へ移動する。
        if os.path.exists(newFontPath):
            shutil.move(newFontPath, saveFontPath)

        # temporary directory を掃除しておく。
        shutil.rmtree(tempDir)
        print "Cleanup temporary directory."

    # Finish
    print "Finish all in dir."

if __name__ == '__main__':
    main(sys.argv)
