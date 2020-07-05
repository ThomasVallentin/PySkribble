from gui.utils import PainterContext
from PySide2 import QtGui, QtCore


def paint_point(pixmap, pos, width, color):
    # Create painter
    with PainterContext(pixmap) as painter:
        # Set painter settings
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        # Create and set pen
        pen = QtGui.QPen(color)
        pen.setWidth(width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Paint point
        painter.drawPoint(pos)

    return pixmap


def paint_line(pixmap, pos1, pos2, width, color):
    # Create painter
    with PainterContext(pixmap) as painter:
        # Set painter settings
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        # Create and set pen
        pen = QtGui.QPen(color)
        pen.setWidth(width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Paint line
        painter.drawLine(pos1, pos2)

    return pixmap


def erase_point(pixmap, pos, width):
    # Create painter
    with PainterContext(pixmap) as painter:
        # Set painter settings
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setCompositionMode(painter.CompositionMode_Clear)

        # Create and set pen
        pen = QtGui.QPen()
        pen.setWidth(width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Paint point
        painter.drawPoint(pos)

    return pixmap


def erase_line(pixmap, pos1, pos2, width):
    # Create painter
    with PainterContext(pixmap) as painter:
        # Set painter settings
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setCompositionMode(painter.CompositionMode_Clear)

        # Create and set pen
        pen = QtGui.QPen()
        pen.setWidth(width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Paint line
        painter.drawLine(pos1, pos2)

    return pixmap


def bucket_fill(pixmap, pos, fill_color):
    print("pixmap, pos, fill_color :", pixmap, pos, fill_color)
    start_pixel = pos.x(), pos.y()
    image = pixmap.toImage()

    image_width, image_height = image.width(), image.height()

    if (start_pixel[0] < 0 or
        start_pixel[0] > image_width or
        start_pixel[1] < 0 or
        start_pixel[1] > image_width):
        print ("return")
        return

    start_color = image.pixel(*start_pixel)
    # tolerance = self.tolerance / 100. / 4.

    to_sample = {start_pixel}
    already_added = {start_pixel}

    mask = image.createMaskFromColor(start_color)
    white = QtGui.qRgb(255, 255, 255)

    while to_sample:
        # Take one pixel from the set of pixel to sample
        x, y = to_sample.pop()

        # Get color at pixel
        mask_color = mask.pixel(x, y)

        # If color matches start_color
        if mask_color == white:
            # Fill pixel color with the view's color
            image.setPixelColor(x, y, fill_color)

            # Schedule adjacent pixels in to_sample and add them to already_added so that
            # they're not tested again

            # If pixel is not on the most left column, add the pixel at its left
            if x > 0:
                adj = (x - 1, y)
                if adj not in already_added:
                    to_sample.add(adj)
                    already_added.add(adj)

            # If pixel is not on the most right column, add the pixel at its right
            if x < image_width:
                adj = (x + 1, y)
                if adj not in already_added:
                    to_sample.add(adj)
                    already_added.add(adj)

            # If pixel is not on the highest row, add the pixel at above it
            if y > 0:
                adj = (x, y - 1)
                if adj not in already_added:
                    to_sample.add(adj)
                    already_added.add(adj)

            # If pixel is not on the lowest row, add the pixel at under it
            if y < image_height:
                adj = (x, y + 1)
                if adj not in already_added:
                    to_sample.add(adj)
                    already_added.add(adj)

    return QtGui.QPixmap.fromImage(image)
