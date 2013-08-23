# -*- coding: utf-8 -*-

"""The user interface for our app"""

import os,sys, random,popen2
import numpy
from PIL import Image
import cStringIO

# Import Qt modules
from PyQt4 import QtCore, QtGui, uic, QtOpenGL
#from compimg import compare_images



# Create a class for our main window
class Main(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.pil_img1 = None
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
        self.model_mod=__import__(mfname, fromlist="Model")
        reload(self.model_mod)
        self.model = self.model_mod.Model(self.pic)
        print 'NUM_T',self.model.NUM_T
        self.model_editor.setPlainText(open(self.mfname,'r').read())
        self.model_label.setText(mfname)

    def on_applyModel_clicked(self, checked = None):
        if checked is not None: return
        print "Save and apply"
        mcode = unicode(self.model_editor.toPlainText())
        print 'Saving to',self.mfname
        f=open(self.mfname,'w')
        f.seek(0)
        f.write(mcode)
        f.close()
        self.on_load_clicked(mfname=self.mfname)

    def on_pause_play_clicked(self, checked = None):
        if checked is not None: return
        print "Play!"
        print 'MM', self.model
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
        diff = self.compare_images(self.img, self.new)
        self.model.decide(diff)
        QtCore.QTimer.singleShot(100, self.drawScene)

    def compare_images(self, img1, img2):
        # Convert images to PIL

        if not self.pil_img1:
            buffer1 = QtCore.QBuffer()
            buffer1.open(QtCore.QIODevice.ReadWrite)
            img1.save(buffer1, "PNG")
            strio1 = cStringIO.StringIO()
            strio1.write(buffer1.data())
            buffer1.close()
            strio1.seek(0)
            self.pil_img1 = Image.open(strio1)
            img = self.pil_img1
            self.m1 = numpy.asarray(img)

        buffer2 = QtCore.QBuffer()
        buffer2.open(QtCore.QIODevice.ReadWrite)
        img2.save(buffer2, "PNG")
        self.strio2 = cStringIO.StringIO()
        self.strio2.write(buffer2.data())
        buffer2.close()
        self.strio2.seek(0)
        img2 = Image.open(self.strio2)

        m2 = numpy.asarray(img2)
        #s = numpy.sum(numpy.abs(m1-m2))
        s = numpy.linalg.norm(self.m1-m2)
        return s




def main():
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

