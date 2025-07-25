import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileSystemModel, QTreeView, QLabel, QPushButton, 
                             QScrollArea, QSplitter, QToolBar, QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QPalette
from PyQt5.QtCore import Qt, QDir, QSize


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('图片浏览器')
        self.setGeometry(100, 100, 1200, 800)
        
        self.initUI()
        self.current_folder = None
        self.current_image_path = None
    
    def initUI(self):
        # 主窗口部件和布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # 使用QSplitter实现可调整大小的左右分割
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧文件夹树形视图
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
        self.file_model.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"])
        self.file_model.setNameFilterDisables(False)
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree_view.setHeaderHidden(True)
        self.tree_view.hideColumn(1)  # 隐藏大小列
        self.tree_view.hideColumn(2)  # 隐藏类型列
        self.tree_view.hideColumn(3)  # 隐藏修改日期列
        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        
        # 连接点击事件
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        
        # 右侧图片显示区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(24, 24))
        
        # 添加工具栏按钮
        self.btn_prev = QPushButton("上一张")
        self.btn_next = QPushButton("下一张")
        self.btn_zoom_in = QPushButton("放大")
        self.btn_zoom_out = QPushButton("缩小")
        self.btn_rotate = QPushButton("旋转")
        self.btn_fit = QPushButton("适应窗口")
        
        self.toolbar.addWidget(self.btn_prev)
        self.toolbar.addWidget(self.btn_next)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.btn_zoom_in)
        self.toolbar.addWidget(self.btn_zoom_out)
        self.toolbar.addWidget(self.btn_rotate)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.btn_fit)
        
        # 连接按钮信号（暂时为空，可以后续添加功能）
        self.btn_prev.clicked.connect(self.show_previous_image)
        self.btn_next.clicked.connect(self.show_next_image)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_rotate.clicked.connect(self.rotate_image)
        self.btn_fit.clicked.connect(self.fit_to_window)
        
        # 图片显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.Dark)
        self.scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(False)
        
        self.scroll_area.setWidget(self.image_label)
        
        # 状态栏
        self.status_bar = self.statusBar()
        
        # 添加到右侧布局
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.scroll_area)
        
        # 添加左右部件到分割器
        splitter.addWidget(self.tree_view)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)  # 设置右侧可拉伸
        
        # 设置初始分割比例
        splitter.setSizes([200, 800])
        
        # 主布局
        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)
        
        # 初始化变量
        self.image_files = []
        self.current_image_index = -1
        self.scale_factor = 1.0
    
    def on_tree_view_clicked(self, index):
        path = self.file_model.filePath(index)
        
        if os.path.isfile(path):
            # 如果是文件，显示图片
            self.current_image_path = path
            self.load_image(path)
            # 获取当前文件夹中的所有图片文件
            folder = os.path.dirname(path)
            if folder != self.current_folder:
                self.current_folder = folder
                self.image_files = self.get_image_files(folder)
                self.current_image_index = self.image_files.index(path)
        elif os.path.isdir(path):
            # 如果是文件夹，更新当前文件夹
            self.current_folder = path
            self.image_files = self.get_image_files(path)
            if self.image_files:
                self.current_image_index = 0
                self.current_image_path = self.image_files[0]
                self.load_image(self.current_image_path)
    
    def get_image_files(self, folder):
        """获取文件夹中的所有图片文件"""
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(extensions):
                    image_files.append(os.path.join(root, file))
        return sorted(image_files)
    
    def load_image(self, path):
        """加载并显示图片"""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.image_label.setText("无法加载图片")
            return
        
        self.image_label.setPixmap(pixmap)
        self.scale_factor = 1.0
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
        self.scale_factor *= factor
        self.image_label.resize(self.scale_factor * self.image_label.pixmap().size())
        
        self.adjust_scroll_bar(self.scroll_area.horizontalScrollBar(), factor)
        self.adjust_scroll_bar(self.scroll_area.verticalScrollBar(), factor)
    
    def adjust_scroll_bar(self, scroll_bar, factor):
        """调整滚动条位置"""
        scroll_bar.setValue(int(factor * scroll_bar.value() + ((factor - 1) * scroll_bar.pageStep() / 2)))
    
    def rotate_image(self):
        """旋转图片"""
        if not self.current_image_path:
            return
        
        pixmap = QPixmap(self.current_image_path)
        if pixmap.isNull():
            return
        
        # 顺时针旋转90度
        rotated = pixmap.transformed(pixmap.transformationMode()).scaled(
            pixmap.height(), pixmap.width(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.image_label.setPixmap(rotated)
        self.image_label.adjustSize()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self.current_image_path:
            return
        
        pixmap = self.image_label.pixmap()
        if pixmap.isNull():
            return
        
        # 计算缩放比例
        viewport_size = self.scroll_area.viewport().size()
        pixmap_size = pixmap.size()
        
        scale_factor = min(viewport_size.width() / pixmap_size.width(),
                          viewport_size.height() / pixmap_size.height())
        
        self.image_label.resize(scale_factor * pixmap_size)
        self.scale_factor = scale_factor


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())