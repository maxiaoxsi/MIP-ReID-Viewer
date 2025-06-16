import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileSystemModel, QTreeView, QLabel, QPushButton, 
                             QScrollArea, QSplitter, QToolBar, QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QPalette, QTransform
from PyQt5.QtCore import Qt, QDir, QSize


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('图片浏览器')
        self.setGeometry(100, 100, 1200, 800)
        
        self.initUI()
        self.current_folder = None
        self.current_image_path = None
        self.rotation_angle = 0  # 添加旋转角度跟踪
    
    def initUI(self):
        # ... [保持之前的initUI代码不变] ...
    
    def on_tree_view_clicked(self, index):
        # ... [保持之前的on_tree_view_clicked代码不变] ...
    
    def get_image_files(self, folder):
        # ... [保持之前的get_image_files代码不变] ...
    
    def load_image(self, path):
        """加载并显示图片"""
        self.original_pixmap = QPixmap(path)  # 保存原始图片
        if self.original_pixmap.isNull():
            self.image_label.setText("无法加载图片")
            return
        
        self.display_pixmap = self.original_pixmap  # 显示用的图片
        self.image_label.setPixmap(self.display_pixmap)
        self.scale_factor = 1.0
        self.rotation_angle = 0
        self.image_label.adjustSize()
        
        # 更新状态栏
        self.status_bar.showMessage(f"{os.path.basename(path)} ({self.current_image_index + 1}/{len(self.image_files)})")
    
    def show_previous_image(self):
        """显示上一张图片"""
        if not self.image_files or self.current_image_index <= 0:
            return
        
        self.current_image_index -= 1
        self.current_image_path = self.image_files[self.current_image_index]
        self.load_image(self.current_image_path)
    
    def show_next_image(self):
        """显示下一张图片"""
        if not self.image_files or self.current_image_index >= len(self.image_files) - 1:
            return
        
        self.current_image_index += 1
        self.current_image_path = self.image_files[self.current_image_index]
        self.load_image(self.current_image_path)
    
    def zoom_in(self):
        """放大图片"""
        self.scale_image(1.25)
    
    def zoom_out(self):
        """缩小图片"""
        self.scale_image(0.8)
    
    def scale_image(self, factor):
        """缩放图片"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
            
        self.scale_factor *= factor
        self.update_display_image()
    
    def update_display_image(self):
        """更新显示的图片（应用缩放和旋转）"""
        transform = QTransform()
        transform.scale(self.scale_factor, self.scale_factor)
        transform.rotate(self.rotation_angle)
        
        self.display_pixmap = self.original_pixmap.transformed(
            transform, Qt.SmoothTransformation)
        
        self.image_label.setPixmap(self.display_pixmap)
        self.image_label.adjustSize()
        
        # 调整滚动条位置
        self.adjust_scroll_bar(self.scroll_area.horizontalScrollBar(), 1.0)
        self.adjust_scroll_bar(self.scroll_area.verticalScrollBar(), 1.0)
    
    def adjust_scroll_bar(self, scroll_bar, factor):
        """调整滚动条位置"""
        scroll_bar.setValue(int(factor * scroll_bar.value() + ((factor - 1) * scroll_bar.pageStep() / 2)))
    
    def rotate_image(self):
        """旋转图片90度"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
        
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.update_display_image()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
        
        # 计算缩放比例
        viewport_size = self.scroll_area.viewport().size()
        pixmap_size = self.original_pixmap.size()
        
        # 考虑旋转后的尺寸
        if self.rotation_angle % 180 == 90:
            pixmap_size = pixmap_size.transposed()
        
        scale_factor = min(viewport_size.width() / pixmap_size.width(),
                          viewport_size.height() / pixmap_size.height())
        
        self.scale_factor = scale_factor
        self.update_display_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())