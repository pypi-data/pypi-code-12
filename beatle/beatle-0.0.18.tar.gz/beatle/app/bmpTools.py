import wx


def JoinBitmap(leftBitmap, rightBitmap):
    """Create a new bitmap by joining"""
    width = leftBitmap.GetWidth() + rightBitmap.GetWidth()
    height = max(leftBitmap.GetHeight(), rightBitmap.GetHeight())
    leftOffset = (height - leftBitmap.GetHeight()) // 2
    rightOffset = (height - rightBitmap.GetHeight()) // 2
    image = wx.EmptyImage()
    image.Create(width, height, clear=True)
    image.Paste(leftBitmap.ConvertToImage(), 0, leftOffset)
    image.Paste(rightBitmap.ConvertToImage(),
        leftBitmap.GetWidth(), rightOffset)
    image.SetMaskColour(0, 0, 0)
    return image.ConvertToBitmap()

# Litte tool for debug
#
#counter=0
#def dumpBitmap(bmp):
#    global counter
#    name = '/home/mel/pythonProjects/proCxx/debug/bmp_{}.bmp'.format(counter)
#    bmp.SaveFile(name, wx.BITMAP_TYPE_BMP)
#    counter = counter + 1


def PrefixBitmapList(prefixBitmap, bitmapList, bitmapResult):
    """
    Prefixes a list of bitmaps with another bitmap
    and increases the original list.
    A map original_index:new_index is created and returned
    where original_index is the index in bitmapResult
    bitmapList must be a subset of bitmapResult
    """
    firstMap = {}
    newmap = {}
    i = 0
    j = len(bitmapResult)
    for bitmap in bitmapList:
        prefixed_bitmap = JoinBitmap(prefixBitmap, bitmap)
        bitmapResult.append(prefixed_bitmap)
        newmap[i] = j
        i = i + 1
        j = j + 1
    return newmap
    for bitmap in firstMap:
        newmap[bitmapList.index(bitmap)] = bitmapResult.index(
            firstMap[bitmap])
    return newmap

def SuffixBitmapList(suffixBitmap, bitmapList, bitmapResult):
    """
    Suffixes a list of bitmaps with another bitmap
    and increases the original list.
    A map original_index:new_index is created and returned
    where original_index is the index in bitmapResult
    bitmapList must be a subset of bitmapResult
    """
    firstMap = {}
    newmap = {}
    i = 0
    j = len(bitmapResult)
    for bitmap in bitmapList:
        suffixed_bitmap = JoinBitmap(bitmap, suffixBitmap)
        bitmapResult.append(suffixed_bitmap)
        newmap[i] = j
        i = i + 1
        j = j + 1
    return newmap
    for bitmap in firstMap:
        newmap[bitmapList.index(bitmap)] = bitmapResult.index(
            firstMap[bitmap])
    return newmap


def GetBitmapMaxSize(bitmapList):
    """
    Gets the maximum width and height for a bitmap list
    """
    width = 0
    height = 0
    for bmp in bitmapList:
        width = max(width, bmp.GetWidth())
        height = max(height, bmp.GetHeight())
    return (width, height)