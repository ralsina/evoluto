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
    def __init__(self):
        QtGui.QDialog.__init__(self)
        
        uifile = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'main.ui')
        uic.loadUi(uifile, self)

        # FIXME: load a sample image
        self.pic = QtGui.QPixmap(400,400)
        self.pic.fill(QtGui.QColor(255,255,255))
        self.img = self.pic.toImage()
        self.picture.setPixmap(self.pic)

        # Load default model
        mfname = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'models','triangles.py')
        self.on_load_clicked(mfname=mfname)

        # Create polygons
        self.model = None
        self.generation = 0
        self.generation_label.setText(str(self.generation))

    def on_load_target_clicked(self, checked = None):
        if checked is not None: return
        picname = QtGui.QFileDialog.getOpenFileName(self, "select a picture")
        self.pic = QtGui.QPixmap(picname)
        self.img = self.pic.toImage()
        self.picture.setPixmap(self.pic)
        self.picture.setFixedSize(self.pic.size())
        self.view.setFixedSize(self.pic.size())

    def on_load_clicked(self, checked = None, mfname=None):
        if checked is not None: return
        models = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'models')
        if not mfname:
            mfname = QtGui.QFileDialog.getOpenFileName(self, "select a model", models)
        if not mfname:
            return
        self.mfname = mfname
        mfname = "models.%s"%(mfname.split(os.sep)[-1][:-3])
        model=__import__(mfname, fromlist="Model")
        self.model = model.Model(self.pic)
        self.model_editor.setPlainText(open(self.mfname,'r').read())
        self.model_label.setText(mfname)

    def on_pause_play_clicked(self, checked = None):
        if checked is not None: return
        print "Play!"
        self.drawScene()
        
    def drawScene(self):
        self.generation +=1
        self.generation_label.setText(str(self.generation))
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

def main():
    import psyco
    psyco.full()
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
