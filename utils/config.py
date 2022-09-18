import json
from enum import Enum
import tkinter as tk
import tkinter.messagebox
from locale import getdefaultlocale


# 项目属性
class Umi:
    name = None
    ver = None
    website = None
    about = None
    test = None  # 开发使用


class RunModeFlag(Enum):
    '''进程管理模式标志'''
    short = 0  # 按需关闭（减少空闲时内存占用）
    long = 1  # 后台常驻（大幅加快任务启动速度）


# 配置文件路径
ConfigJsonFile = 'Umi-OCR_config.json'

# 配置项
_ConfigDict = {
    # 计划任务设置
    'isOpenExplorer': {   # T时任务完成后打开资源管理器到输出目录。isOutputFile为T时才管用
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOpenOutputFile': {  # T时任务完成后打开输出文件。isOutputFile为T时才管用
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOkMission': {  # T时本次任务完成后执行指定计划任务。
        'default': False,
        'isSave': False,
        'isTK': True,
    },
    'okMissionName': {  # 当前选择的计划任务的name。
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'okMission': {  # 计划任务事件，code为cmd代码
        'default': {
            '关机':  # 取消：shutdown /a
            {'code': r'msg %username% /time:25 "Umi-OCR任务完成，将在30s后关机" & echo 关闭本窗口可取消关机 & choice /t 30 /d y /n >nul & shutdown /f /s /t 0'},
            '休眠':  # 用choice实现延时
            {'code': r'msg %username% /time:25 "Umi-OCR任务完成，将在30s后休眠" & echo 关闭本窗口可取消休眠 & choice /t 30 /d y /n >nul & shutdown /f /h'},
        },
        'isSave': True,
        'isTK': False,
    },
    # 读取剪贴板设置
    'isGlobalHotkey': {  # T时绑定全局快捷键
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isNeedCopy': {  # T时识别完成后自动复制文字
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'globalHotkey': {  # 全局快捷键
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    # 输入文件设置
    'isRecursiveSearch': {  # T时导入文件夹将递归查找子文件夹中所有图片
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    # 输出文件设置
    'isOutputTxt': {  # T时输出内容写入txt文件
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    'isOutputMD': {  # T时输出内容写入md文件
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isOutputJsonl': {  # T时输出内容写入jsonl文件
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'outputFilePath': {  # 输出文件目录
        'default': '',
        'isSave': False,
        'isTK': True,
    },
    'outputFileName': {  # 输出文件名称
        'default': '',
        'isSave': False,
        'isTK': True,
    },
    # 输出格式设置
    'isOutputDebug': {  # T时输出调试信息
        'default': False,
        'isSave': True,
        'isTK': True,
    },
    'isIgnoreNoText': {  # T时忽略(不输出)没有文字的图片信息
        'default': True,
        'isSave': True,
        'isTK': True,
    },
    # 引擎设置
    'ocrToolPath': {  # 引擎路径
        'default': 'PaddleOCR-json/PaddleOCR_json.exe',
        'isSave': True,
        'isTK': False,
    },
    'ocrRunModeName': {  # 当前选择的进程管理策略
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'ocrRunMode': {  # 进程管理策略
        'default': {
            '后台常驻（大幅加快任务启动速度）': RunModeFlag.long,
            '按需关闭（减少空闲时内存占用）': RunModeFlag.short,
        },
        'isSave': False,
        'isTK': False,
    },
    'ocrProcessStatus': {  # 进程运行状态字符串，由引擎单例传到tk窗口
        'default': '未启动',
        'isSave': False,
        'isTK': True,
    },
    'ocrConfigName': {  # 当前选择的配置文件的name
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'ocrConfig': {  # 配置文件信息
        'default': {  # 配置文件信息
            '简体中文': {
                'path': 'PaddleOCR_json_config_ch.txt'
            }
        },
        'isSave': True,
        'isTK': False,
    },
    'argsStr': {  # 启动参数字符串
        'default': '',
        'isSave': True,
        'isTK': True,
    },
    'imageSuffix': {  # 图片后缀
        'default': '.jpg .jpe .jpeg .jfif .png .webp .bmp .tif .tiff',
        'isSave': True,
        'isTK': True,
    },

    # 不同模块交流的接口
    'ignoreArea':  {  # 忽略区域
        'default': None,
        'isSave': False,
        'isTK': False,
    },
    'tipsTop1': {  # 主窗口顶部进度条上方的label，左侧
        'default': '',
        'isTK': True,
    },
    'tipsTop2': {  # 主窗口顶部进度条上方的label，右侧
        'default': '欢迎使用Umi-OCR ~',
        'isTK': True,
    },
    'panelOutput': {  # 主输出面板的接口
        'default': None,
    },
}


class ConfigModule:
    sysEncoding = 'cp936'  # 系统编码。初始化时获取
    # ↓ 在这些编码下能使用全部功能，其它编码不保证能使用如拖入含中文路径的图片等功能。
    # ↓ 但识图功能是可以正常使用的。
    sysEncodingSalf = ['cp936', 'cp65001']

    tkSaveTime = 200  # tk变量改变多长时间后写入本地。毫秒

    # ==================== 初始化 ====================

    def __init__(self):
        self.mainTK = None  # 主窗口tk，可用来刷新界面或创建计时器
        self.saveTimer = None  # 计时器，用来更新tk变量一段时间后写入本地
        self.optDict = {}  # 配置项的数据
        self.tkDict = {}  # tk绑定变量
        self.saveList = []  # 需要保存的项
        # 将配置项加载到self
        for key in _ConfigDict:
            value = _ConfigDict[key]
            self.optDict[key] = value['default']
            if value.get('isSave', False):
                self.saveList.append(key)
            if value.get('isTK', False):
                self.tkDict[key] = None

    def initTK(self, mainTK):
        '''初始化tk变量'''
        self.mainTK = mainTK  # 主窗口

        def toSaveConfig():  # 保存值的事件
            self.save()
            self.saveTimer = None

        def onTkVarChange(key):  # 值改变的事件
            self.update(key)  # 更新配置项
            if key in self.saveList:  # 需要保存
                if self.saveTimer:  # 计时器已存在，则停止已存在的
                    self.mainTK.after_cancel(self.saveTimer)  # 取消计时
                    self.saveTimer = None
                self.saveTimer = self.mainTK.after(  # 重新计时
                    self.tkSaveTime, toSaveConfig)

        for key in self.tkDict:
            if isinstance(self.optDict[key], bool):  # 布尔最优先，以免被int覆盖
                self.tkDict[key] = tk.BooleanVar()
            elif isinstance(self.optDict[key], str):
                self.tkDict[key] = tk.StringVar()
            elif isinstance(self.optDict[key], int):
                self.tkDict[key] = tk.IntVar()
            else:  # 给开发者提醒
                raise Exception(f'配置项{key}要生成tk变量，但类型不合法！')
            # 赋予初值
            self.tkDict[key].set(self.optDict[key])
            # 跟踪值改变事件
            self.tkDict[key].trace(
                "w", lambda *e, key=key: onTkVarChange(key))

    # ==================== 读写本地文件 ====================

    def load(self):
        '''从本地json文件读取配置。必须在initTK后执行'''
        try:
            with open(ConfigJsonFile, 'r', encoding='utf8')as fp:
                jsonData = json.load(fp)  # 读取json文件
                for key in jsonData:
                    if key in self.optDict:
                        self.set(key, jsonData[key])
        except json.JSONDecodeError:  # 反序列化json错误
            if tk.messagebox.askyesno(
                '遇到了一点小问题',
                    f'载入配置文件 {ConfigJsonFile} 时，反序列化json失败。\n\n选 “是” 重置该文件。\n选 “否” 将退出程序。'):
                self.save()
            else:
                exit(0)
        except FileNotFoundError:  # 无配置文件
            # 当成是首次启动软件，提示
            if self.sysEncoding not in self.sysEncodingSalf:  # 不安全的地区
                tk.messagebox.showwarning(
                    '警告',
                    f'您的系统地区编码为[{self.sysEncoding}]，可能导致拖入图片的功能异常，建议使用浏览按钮导入图片。其它功能应该能正常使用。')
            self.save()

        def setSysEncoding():  # 获取系统编码
            '''初始化编码'''
            # https://docs.python.org/zh-cn/3.8/library/locale.html#locale.getdefaultlocale
            # https://docs.python.org/zh-cn/3.8/library/codecs.html#standard-encodings
            self.sysEncoding = getdefaultlocale()[1]
            print(f'获取系统编码：{self.sysEncoding}')
        setSysEncoding()  # 初始化编码

    def save(self):
        '''保存配置到本地json文件'''
        saveDict = {}  # 提取需要保存的项
        for key in self.saveList:
            saveDict[key] = self.optDict[key]
        with open(ConfigJsonFile, 'w', encoding='utf8')as fp:
            fp.write(json.dumps(saveDict, indent=4, ensure_ascii=False))

    # ==================== 操作变量 ====================

    def update(self, key):
        '''更新某个值，从tk变量读取到配置项'''
        self.optDict[key] = self.tkDict[key].get()

    def get(self, key):
        '''获取一个配置项的值'''
        return self.optDict[key]

    def set(self, key, value, isUpdateTK=False):
        '''设置一个配置项的值'''
        if key in self.tkDict:  # 若是tk，则通过tk的update事件去更新optDict值
            self.tkDict[key].set(value)
            if isUpdateTK:  # 需要刷新界面
                self.mainTK.update()
        else:  # 不是tk，直接更新optDict
            self.optDict[key] = value

    def getTK(self, key):
        '''获取一个TK变量'''
        return self.tkDict[key]


Config = ConfigModule()  # 设置模块 单例