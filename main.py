# -*- coding: utf-8 -*-

"""The user interface for our app"""

import os,sys, random,popen2
import numpy
from PIL import Image

# Import Qt modules
from PyQt4 import QtCore, QtGui, uic, QtOpenGL
#from compimg import compare_images



# Create a class for our main window
class Main(QtGui.QDialog):
    def __init__(self, image):
        QtGui.QDialog.__init__(self)
        
        uifile = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'main.ui')
        uic.loadUi(uifile, self)

        self.pic = QtGui.QPixmap(sys.argv[1])
        self.img = self.pic.toImage()
        self.picture.setPixmap(self.pic)

        self.picture.setFixedSize(self.pic.size())
        self.view.setFixedSize(self.pic.size())

        # Create polygons
        self.model = None
        self.generation = 0

    def on_load_clicked(self, checked = None):
        if checked is not None: return
        models = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'models')
        mfname = QtGui.QFileDialog.getOpenFileName(self, "select a model", models)
        mfname = "models.%s"%(mfname.split(os.sep)[-1][:-3])
        model=__import__(mfname, fromlist="Model")
        print model, mfname
        self.model = model.Model(self.pic)

    def on_pause_play_clicked(self, checked = None):
        if checked is not None: return
        print "Play!"
        self.drawScene()
        
    def drawScene(self):
        self.generation +=1
        print 'GEN:', self.generation
        
        # Create scene, assign to view
        self.qgscene = QtGui.QGraphicsScene(QtCore.QRectF(0,0,
            self.pic.width(), self.pic.height()))
        self.qgscene.changed.connect(self.decide)
        self.view.setScene(self.qgscene)
        for p in self.model.step():
            self.qgscene.addItem(p.shape())
        self.qgscene.update(self.qgscene.sceneRect())
        self.qgscene.invalidate(self.qgscene.sceneRect())

    def decide(self):
        """Compare target and current output then call scene.decide()
        to prepare next step."""
        self.new = QtGui.QImage(self.pic.width(), self.pic.height(), QtGui.QImage.Format_RGB32)
        self.new.fill(QtGui.QColor(255,255,255).rgb())
        painter = QtGui.QPainter(self.new)
        self.qgscene.render(painter)
        painter.end()
        if self.generation % 100 == 10:
            self.new.save('%s.png'%self.generation)
        diff = compare_images(self.img, self.new)
        self.model.decide(diff)
        QtCore.QTimer.singleShot(100, self.drawScene)

import cStringIO

def compare_images_pil(img1, img2):

    # Convert images to PIL
    
    buffer1 = QtCore.QBuffer()
    buffer1.open(QtCore.QIODevice.ReadWrite)
    img1.save(buffer1, "PNG")
    strio1 = cStringIO.StringIO()
    strio1.write(buffer1.data())
    buffer1.close()
    strio1.seek(0)
    img1 = Image.open(strio1)
    
    buffer2 = QtCore.QBuffer()
    buffer2.open(QtCore.QIODevice.ReadWrite)
    img2.save(buffer2, "PNG")
    strio2 = cStringIO.StringIO()
    strio2.write(buffer2.data())
    buffer2.close()
    strio2.seek(0)
    img2 = Image.open(strio2)

    # Compare
    m1 = numpy.array([p[0] for p in img1.getdata()])#.reshape(*img1.size)
    m2 = numpy.array([p[0] for p in img2.getdata()])#.reshape(*img2.size)
    s = numpy.sum(numpy.abs(m1-m2))
    return s

compare_images = compare_images_pil

def compare_images_magick(img1, img2):
    img1.save('_1.png')
    img2.save('_2.png')
    v = os.popen3('compare _1.png _2.png -metric MAE -dissimilarity-threshold 1  diff.png', 'r')[2].read()
    return float(v.split(' ')[0])


def main():
    import psyco
    psyco.full()
    app = QtGui.QApplication(sys.argv)
    window=Main(sys.argv[1])
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
