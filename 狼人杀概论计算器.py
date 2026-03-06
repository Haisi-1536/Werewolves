import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from collections import defaultdict
import math
import webbrowser
import json
import os


class WerewolfProbabilityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("狼人杀概论计算器 v1.0")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        self.root.resizable(True, True)
        # 存储发言记录的数据结构
        self.speech_records = {}  # 格式: {(player, round): "发言内容"}

        # 主题配置 - 默认浅色
        self.themes = {
            "浅色": {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'select': '#e0e0e0',
                'button': '#d9d9d9',
                'button_hover': '#c0c0c0',
                'frame_bg': '#ffffff',
                'tree_bg': '#ffffff',
                'tree_fg': '#000000',
                'tree_select': '#c0c0c0',
                'accent': '#ff4444',
                'wolf': '#cc0000',
                'god': '#9933cc',
                'human': '#008800',
                'gold': '#b8860b',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'player_bg': '#e6e6e6',
                'player_border': '#cccccc',
                'custom_tag': '#9933cc'  # 自定义标签颜色
            },
            "深色": {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'select': '#404040',
                'button': '#3c3c3c',
                'button_hover': '#4a4a4a',
                'frame_bg': '#333333',
                'tree_bg': '#2d2d2d',
                'tree_fg': '#ffffff',
                'tree_select': '#4a4a4a',
                'accent': '#ff6b6b',
                'wolf': '#ff4757',
                'god': '#1e90ff',
                'human': '#2ecc71',
                'gold': '#ffd700',
                'entry_bg': '#404040',
                'entry_fg': '#ffffff',
                'player_bg': '#3a3a3a',
                'player_border': '#555555',
                'custom_tag': '#b266ff'  # 自定义标签颜色
            }
        }

        self.current_theme = "浅色"  # 默认浅色
        self.colors = self.themes[self.current_theme]

        # 游戏配置 - 固定结构
        self.total_players = 12
        self.wolves = 4
        self.gods = 4
        self.villagers = 4
        self.players = list(range(1, 13))

        # 模拟次数
        self.simulation_count = 50000  # 默认模拟次数

        # 算法开关
        self.use_triangle_law = True  # 是否使用三角定律
        self.use_behavior_weight = True  # 是否使用行为权重

        # 身份分类（可扩展）
        self.role_categories = {
            "好人标记": {
                "金水": "good_mark",
                "银水": "good_mark",
                "铜水": "good_mark",
                "爆水": "good_mark",
                "花露水": "good_mark",
                "贴脸": "good_mark",
                "离线": "good_mark",
                "反金": "good_mark",
                "好人": "good_mark",
            },
            "狼人": {
                "狼人": "wolf",
                "狼王": "wolf",
                "白狼王": "wolf",
                "狼美人": "wolf",
                "石像鬼": "wolf",
                "赤月使徒": "wolf",
                "咒狐": "wolf",
                "噩梦之影": "wolf",
                "蚀时狼妃": "wolf",
                "狼巫": "wolf",
                "狼鸦之爪": "wolf",
                "蚀日侍女": "wolf",
                "寂夜导师": "wolf",
                "夜之贵族": "wolf",
                "寻香魅影": "wolf",
                "觉醒狼王": "wolf",
                "觉醒隐狼": "wolf",
                "隐狼": "wolf",
                "恶夜骑士": "wolf",
                "悍跳狼": "wolf",
            },
            "神职": {
                "预言家": "god",
                "女巫": "god",
                "猎人": "god",
                "愚者": "god",
                "守卫": "god",
                "摄梦人": "god",
                "魔术师": "god",
                "骑士": "god",
                "守墓人": "god",
                "猎魔人": "god",
                "乌鸦": "god",
                "奇迹商人": "god",
                "定序王子": "god",
                "纯白之女": "god",
                "炼金魔女": "god",
                "熊": "god",
                "子狐": "god",
                "河豚": "god",
                "白猫": "god",
                "白昼学者": "god",
                "流光伯爵": "god",
                "觉醒愚者": "god",
                "觉醒预言家": "god",
                "魔镜少女": "god",
            },
            "平民": {
                "平民": "human",
                "羊驼": "human",
                "孤独少女": "human",
                "千面人": "human",
                "丘比特": "human",
            }
        }

        # 所有身份列表（用于下拉框）
        self.all_roles = []
        for category, roles in self.role_categories.items():
            self.all_roles.extend(roles.keys())

        # 已知信息存储
        self.known_info = {}  # {player: {"role": role, "type": type}}
        self.behavior_weights = {}

        # 自定义标签存储 {tag_name: {"wolf": wolf_weight, "god": god_weight, "human": human_weight}}
        # 自定义标签存储 {tag_name: {"wolf": wolf_weight, "god": god_weight, "human": human_weight}}
        self.custom_tags = {
            # 狼面较大类
            "🔪 听杀": {"wolf": 2.1, "god": 0.4, "human": 0.5},
            "🔪 发言爆匪": {"wolf": 2.2, "god": 0.4, "human": 0.4},
            "👑 狼王逻辑": {"wolf": 2.5, "god": 0.3, "human": 0.2},
            "🔄 倒钩发言": {"wolf": 1.8, "god": 0.6, "human": 0.6},
            "💀 匪事干尽": {"wolf": 2.4, "god": 0.3, "human": 0.3},
            "👁️ 狼人视角": {"wolf": 2.2, "god": 0.4, "human": 0.4},
            "🔄 反复横跳": {"wolf": 1.8, "god": 0.8, "human": 1.4},
            "🔪 抗推位": {"wolf": 2.0, "god": 0.5, "human": 1.5},
            "🎣 倒钩": {"wolf": 2.0, "god": 0.8, "human": 0.7},
            "🎭 拱火": {"wolf": 1.8, "god": 0.6, "human": 1.6},

            # 神面较大类
            "💬 发言很正": {"wolf": 0.3, "god": 2.2, "human": 1.5},
            "✅ 逻辑正确": {"wolf": 0.4, "god": 2.3, "human": 1.3},
            "🛡️ 像个身份": {"wolf": 0.3, "god": 2.4, "human": 1.3},
            "👑 强势带队": {"wolf": 0.8, "god": 2.1, "human": 1.1},
            "💎 铁神": {"wolf": 0.2, "god": 2.5, "human": 0.3},

            # 平民面较大类
            "😐 平平无奇": {"wolf": 1.2, "god": 0.8, "human": 2.0},
            "🤔 闭眼玩家": {"wolf": 1.0, "god": 0.9, "human": 2.1},
            "😴 挂机玩家": {"wolf": 1.1, "god": 0.7, "human": 2.2},
            "📝 跟票玩家": {"wolf": 1.2, "god": 0.9, "human": 1.9},
            "👂 听劝玩家": {"wolf": 1.0, "god": 1.0, "human": 2.0},
            "🤐 沉默": {"wolf": 1.1, "god": 1.2, "human": 1.7},
            "🌾 铁民": {"wolf": 0.3, "god": 0.3, "human": 2.4},
            "😴 划水": {"wolf": 1.5, "god": 0.8, "human": 0.7},

            # 中性类
            "🌟 全场乱打": {"wolf": 0.5, "god": 1.8, "human": 1.7},
            "🎲 全场乱打": {"wolf": 1.5, "god": 1.2, "human": 1.3},
            "🔍 疑似好人": {"wolf": 0.5, "god": 1.8, "human": 1.7},
            "💎 逻辑全错": {"wolf": 1.3, "god": 1.2, "human": 1.5},
            "🔄 跟风": {"wolf": 1.3, "god": 1.2, "human": 1.5},
            "🗣️ 话痨": {"wolf": 1.2, "god": 1.5, "human": 1.3},
            "😤 贴脸": {"wolf": 1.3, "god": 1.2, "human": 1.5},
            "💢 暴躁": {"wolf": 1.4, "god": 1.1, "human": 1.5},
            "❓ 身份不明": {"wolf": 1.0, "god": 1.0, "human": 1.0},
        }

        # 定义三角形分组
        self.triangles = {
            "🔺159": {1, 5, 9},
            "🔺2610": {2, 6, 10},
            "🔺3711": {3, 7, 11},
            "🔺4812": {4, 8, 12}
        }

        # 三角形颜色
        self.triangle_colors = {
            "🔺159": '#ff6b6b',
            "🔺2610": '#4ecdc4',
            "🔺3711": '#ffe66d',
            "🔺4812": '#c77dff'
        }

        # 三角形之间的对角关系
        self.triangle_opposites = {
            "🔺159": "🔺3711",
            "🔺2610": "🔺4812",
            "🔺3711": "🔺159",
            "🔺4812": "🔺2610"
        }

        # 定义四角分组
        self.corner_groups = [
            {"name": "🔲四角1", "players": {1, 7, 4, 10}},
            {"name": "🔲四角2", "players": {2, 8, 5, 11}},
            {"name": "🔲四角3", "players": {3, 9, 6, 12}}
        ]

        # 定义三行分组
        self.rows = [
            {1, 7}, {2, 8}, {3, 9}, {4, 10}, {5, 11}, {6, 12}
        ]
        self.row_combinations = [
            {"name": "行1-3", "players": self.rows[0] | self.rows[1] | self.rows[2]},
            {"name": "行2-4", "players": self.rows[1] | self.rows[2] | self.rows[3]},
            {"name": "行3-5", "players": self.rows[2] | self.rows[3] | self.rows[4]},
            {"name": "行4-6", "players": self.rows[3] | self.rows[4] | self.rows[5]},
            {"name": "行5-6+1", "players": self.rows[4] | self.rows[5] | self.rows[0]},
            {"name": "行6+1-2", "players": self.rows[5] | self.rows[0] | self.rows[1]}
        ]

        # 存储玩家卡片的引用
        self.player_cards = {}
        self.player_labels = {}

        # 设置样式
        self.setup_styles()

        # 设置主界面
        self.setup_ui()

    def setup_styles(self):
        """设置自定义样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置颜色
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['button'], foreground=self.colors['fg'],
                        borderwidth=1, focusthickness=3, focuscolor='none')
        style.map('TButton',
                  background=[('active', self.colors['button_hover']),
                              ('pressed', self.colors['select'])])
        style.configure('TCombobox', fieldbackground=self.colors['entry_bg'],
                        foreground=self.colors['entry_fg'], background=self.colors['entry_bg'])
        style.configure('TSpinbox', fieldbackground=self.colors['entry_bg'],
                        foreground=self.colors['entry_fg'], background=self.colors['entry_bg'])

        # 自定义按钮样式
        style.configure('Accent.TButton', background=self.colors['accent'], foreground='white')
        style.map('Accent.TButton',
                  background=[('active', '#ff5252'), ('pressed', '#ff3838')])

        style.configure('Wolf.TButton', background=self.colors['wolf'], foreground='white')
        style.configure('God.TButton', background=self.colors['god'], foreground='white')
        style.configure('Human.TButton', background=self.colors['human'], foreground='white')
        style.configure('CustomTag.TButton', background=self.colors['custom_tag'], foreground='white')

        # 设置根窗口背景
        self.root.configure(bg=self.colors['bg'])

    def toggle_theme(self):
        """切换主题"""
        if self.current_theme == "浅色":
            self.current_theme = "深色"
        else:
            self.current_theme = "浅色"

        self.colors = self.themes[self.current_theme]
        self.setup_styles()

        # 刷新所有组件颜色
        self.refresh_ui_colors()

        # 更新玩家卡片颜色
        self.update_all_player_cards()

        self.log(f"切换主题为: {self.current_theme}模式")

    def refresh_ui_colors(self):
        """刷新UI颜色"""
        # 重新设置所有组件的颜色
        for widget in self.root.winfo_children():
            self.update_widget_colors(widget)

    def update_widget_colors(self, widget):
        """递归更新组件颜色"""
        try:
            if isinstance(widget, (ttk.Label, ttk.Frame, ttk.LabelFrame, ttk.Button, ttk.Combobox)):
                # ttk组件通过style管理，不需要直接设置
                pass
            elif isinstance(widget, tk.Text):
                widget.config(bg=self.colors['entry_bg'], fg=self.colors['fg'],
                              insertbackground=self.colors['fg'])
            elif isinstance(widget, tk.Listbox):
                widget.config(bg=self.colors['entry_bg'], fg=self.colors['fg'],
                              selectbackground=self.colors['tree_select'])
            elif isinstance(widget, tk.Canvas):
                widget.config(bg=self.colors['bg'])
            elif isinstance(widget, tk.Frame) and widget not in self.player_cards.values():
                widget.config(bg=self.colors['bg'])
        except:
            pass

        # 递归处理子组件
        for child in widget.winfo_children():
            self.update_widget_colors(child)

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架（使用paned window实现可调整布局）
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧面板（信息输入）- 修改 weight 为较小的值
        left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(left_frame, weight=1)  # 从 weight=2 改为 weight=1

        # 中间面板（结果显示 + 可视化号码牌）- 保持较大
        middle_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(middle_frame, weight=4)  # 从 weight=3 改为 weight=4

        # 右侧面板（实时日志 + 三角形分析）- 保持适中
        right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(right_frame, weight=2)  # 保持 weight=2

        # 创建顶部工具栏
        self.create_toolbar()

        # 设置各个面板的内容
        self.setup_left_panel(left_frame)
        self.setup_middle_panel(middle_frame)
        self.setup_right_panel(right_frame)

        # 底部状态栏
        self.create_status_bar()

        # 初始化日志
        self.log("系统初始化完成 - 狼人杀概论计算器 v1.0")
        self.log("三角定律核心：85%概率必有一组三角形有双狼")
        self.log("欢迎使用！请选择身份信息开始计算")

    def create_toolbar(self):
        """创建顶部工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        # 主题切换
        ttk.Button(toolbar, text="🎨 切换主题", command=self.toggle_theme).pack(side=tk.LEFT, padx=2)

        # 清空按钮
        ttk.Button(toolbar, text="🗑️ 清空所有信息", command=self.clear_all_info).pack(side=tk.RIGHT, padx=2)

        # 版本信息
        ttk.Label(toolbar, text="v1.0", font=("微软雅黑", 8)).pack(side=tk.RIGHT, padx=10)

    def setup_left_panel(self, parent):
        """设置左侧面板（信息输入）"""
        # 创建Notebook用于分页
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 页面1：身份输入
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="📝 身份输入")
        self.create_input_tab(input_frame)

        # 页面2：权重设置
        weight_frame = ttk.Frame(notebook)
        notebook.add(weight_frame, text="⚖️ 权重设置")
        self.create_weight_tab(weight_frame)

        # 页面3：分析设置
        setting_frame = ttk.Frame(notebook)
        notebook.add(setting_frame, text="⚙️ 分析设置")
        self.create_setting_tab(setting_frame)

    def create_input_tab(self, parent):
        """创建身份输入标签页"""
        # 使用Canvas+Scrollbar实现滚动
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 玩家选择
        player_frame = ttk.Frame(scrollable_frame)
        player_frame.pack(fill=tk.X, pady=5)

        ttk.Label(player_frame, text="👤 玩家编号:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        self.player_var = tk.StringVar()
        self.player_combo = ttk.Combobox(player_frame, textvariable=self.player_var,
                                         values=self.players, state="readonly", width=15)
        self.player_combo.pack(side=tk.LEFT, padx=10)
        self.player_combo.bind('<<ComboboxSelected>>', self.on_player_selected)

        # 身份分类选择（使用标签页）
        self.role_notebook = ttk.Notebook(scrollable_frame)  # 改为 self.role_notebook
        self.role_notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        self.role_vars = {}

        # 为每个身份分类创建标签页
        for category, roles in self.role_categories.items():
            category_frame = ttk.Frame(self.role_notebook)
            self.role_notebook.add(category_frame, text=category)

            # 创建单选按钮
            self.role_vars[category] = tk.StringVar()

            # 添加说明
            if category == "好人标记":
                ttk.Label(category_frame, text="⭐ 好人标记（可分配到神或民）",
                          foreground=self.colors['gold']).pack(anchor=tk.W, pady=5)
            elif category == "狼人":
                ttk.Label(category_frame, text="🐺 狼人阵营",
                          foreground=self.colors['wolf']).pack(anchor=tk.W, pady=5)
            elif category == "神职":
                ttk.Label(category_frame, text="👼 神职阵营",
                          foreground=self.colors['god']).pack(anchor=tk.W, pady=5)
            elif category == "平民":
                ttk.Label(category_frame, text="👤 平民阵营",
                          foreground=self.colors['human']).pack(anchor=tk.W, pady=5)

            # 创建按钮框架
            btn_frame = ttk.Frame(category_frame)
            btn_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            # 按行排列按钮
            roles_list = list(roles.keys())
            for i, role in enumerate(roles_list):
                row = i // 3
                col = i % 3

                # 根据类型设置按钮样式
                if category == "狼人":
                    btn_style = 'Wolf.TButton'
                elif category == "神职":
                    btn_style = 'God.TButton'
                elif category == "平民":
                    btn_style = 'Human.TButton'
                else:
                    btn_style = 'TButton'

                rb = ttk.Radiobutton(btn_frame, text=role,
                                     variable=self.role_vars[category],
                                     value=role, style=btn_style)
                rb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

        # 添加按钮
        add_btn = ttk.Button(scrollable_frame, text="➕ 添加已知信息",
                             command=self.add_known_info,
                             style='Accent.TButton')
        add_btn.pack(pady=15)

        # 提示信息
        ttk.Label(scrollable_frame, text="提示: 选择玩家编号后，点击对应身份添加",
                  font=("微软雅黑", 9), foreground=self.colors['gold']).pack(pady=5)

        # 已知信息列表（放在输入页面底部）
        info_frame = ttk.LabelFrame(scrollable_frame, text="📋 当前已知信息", padding="5")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 列表框架
        list_frame = ttk.Frame(info_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.info_listbox = tk.Listbox(list_frame, height=6,
                                       bg=self.colors['entry_bg'],
                                       fg=self.colors['fg'],
                                       selectbackground=self.colors['tree_select'],
                                       font=("微软雅黑", 9))
        self.info_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar2 = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                   command=self.info_listbox.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_listbox.configure(yscrollcommand=scrollbar2.set)

        # 绑定双击删除
        self.info_listbox.bind('<Double-Button-1>', lambda e: self.delete_selected_info())

        # 按钮框架
        btn_frame2 = ttk.Frame(info_frame)
        btn_frame2.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame2, text="🗑️ 删除选中",
                   command=self.delete_selected_info).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame2, text="🔄 清空所有",
                   command=self.clear_all_info).pack(side=tk.LEFT, padx=2)

        # 统计信息
        self.info_stats = ttk.Label(info_frame, text="已知: 0 | 狼: 0 | 神: 0 | 民: 0 | 标记: 0",
                                    font=("微软雅黑", 8))
        self.info_stats.pack(fill=tk.X, pady=2)

    def switch_to_category_tab(self, target_category):
        """切换到指定的分类标签页"""
        try:
            if not hasattr(self, 'role_notebook'):
                return

            tabs = self.role_notebook.tabs()
            for i, tab_id in enumerate(tabs):
                tab_text = self.role_notebook.tab(tab_id, "text")
                if tab_text == target_category:
                    self.role_notebook.select(i)
                    break
        except Exception as e:
            pass

    def create_weight_tab(self, parent):
        """创建权重设置标签页"""
        # 使用Canvas+Scrollbar
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 权重说明
        ttk.Label(scrollable_frame, text="⚖️ 行为权重设置",
                  font=("微软雅黑", 12, "bold")).pack(pady=10)

        ttk.Label(scrollable_frame,
                  text="权重值 >1 表示倾向该身份，<1 表示不倾向\n建议范围: 0.1 - 3.0",
                  foreground=self.colors['gold']).pack(pady=5)

        # 玩家选择 + 标签下拉
        select_frame = ttk.Frame(scrollable_frame)
        select_frame.pack(fill=tk.X, pady=5, padx=10)

        # 玩家选择
        ttk.Label(select_frame, text="选择玩家:").pack(side=tk.LEFT, padx=2)
        self.weight_player_var = tk.StringVar()
        self.weight_player_combo = ttk.Combobox(select_frame, textvariable=self.weight_player_var,
                                                values=self.players, state="readonly", width=8)
        self.weight_player_combo.pack(side=tk.LEFT, padx=2)

        # 标签选择
        ttk.Label(select_frame, text="标签:").pack(side=tk.LEFT, padx=(10, 2))
        self.tag_preset_var = tk.StringVar()

        # 创建标签列表，包含空白选项
        tag_list = [""] + list(self.custom_tags.keys())
        self.tag_preset_combo = ttk.Combobox(select_frame, textvariable=self.tag_preset_var,
                                             values=tag_list, state="readonly", width=15)
        self.tag_preset_combo.pack(side=tk.LEFT, padx=2)
        self.tag_preset_combo.bind('<<ComboboxSelected>>', self.on_tag_selected)

        # 权重值输入
        weight_frame = ttk.LabelFrame(scrollable_frame, text="权重值", padding="10")
        weight_frame.pack(fill=tk.X, pady=10, padx=10)

        # 狼权
        wolf_frame = ttk.Frame(weight_frame)
        wolf_frame.pack(fill=tk.X, pady=5)
        ttk.Label(wolf_frame, text="🐺 狼权:", foreground=self.colors['wolf'],
                  width=10).pack(side=tk.LEFT)
        self.wolf_weight = ttk.Entry(wolf_frame, width=20)
        self.wolf_weight.insert(0, "1.0")
        self.wolf_weight.pack(side=tk.LEFT, padx=5)

        # 神权
        god_frame = ttk.Frame(weight_frame)
        god_frame.pack(fill=tk.X, pady=5)
        ttk.Label(god_frame, text="👼 神权:", foreground=self.colors['god'],
                  width=10).pack(side=tk.LEFT)
        self.god_weight = ttk.Entry(god_frame, width=20)
        self.god_weight.insert(0, "1.0")
        self.god_weight.pack(side=tk.LEFT, padx=5)

        # 民权
        human_frame = ttk.Frame(weight_frame)
        human_frame.pack(fill=tk.X, pady=5)
        ttk.Label(human_frame, text="👤 民权:", foreground=self.colors['human'],
                  width=10).pack(side=tk.LEFT)
        self.human_weight = ttk.Entry(human_frame, width=20)
        self.human_weight.insert(0, "1.0")
        self.human_weight.pack(side=tk.LEFT, padx=5)

        # 标签提示信息（可选）
        self.tag_info_label = ttk.Label(scrollable_frame, text="", foreground=self.colors['gold'])
        self.tag_info_label.pack(fill=tk.X, pady=2, padx=10)

        # 操作按钮
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=10)

        # 应用权重按钮
        apply_btn = ttk.Button(btn_frame, text="✅应用权重",
                               command=self.add_behavior_weight,
                               style='Accent.TButton')
        apply_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # 添加/保存标签按钮
        save_tag_btn = ttk.Button(btn_frame, text="💾添加/保存标签",
                                  command=self.save_custom_tag,
                                  style='CustomTag.TButton')
        save_tag_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # 删除标签按钮（红色）
        delete_tag_btn = tk.Button(btn_frame, text="🗑️删除标签",
                                   command=self.delete_current_tag,
                                   bg='#ff4444', fg='white',
                                   font=("微软雅黑", 9),
                                   relief=tk.RAISED, borderwidth=1)
        delete_tag_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # 当前权重列表
        weight_list_frame = ttk.LabelFrame(scrollable_frame, text="已设置权重", padding="5")
        weight_list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # 列表框架
        list_container = ttk.Frame(weight_list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.weight_listbox = tk.Listbox(list_container, height=6,
                                         bg=self.colors['entry_bg'],
                                         fg=self.colors['fg'],
                                         selectbackground=self.colors['tree_select'],
                                         font=("微软雅黑", 9))
        self.weight_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        weight_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL,
                                         command=self.weight_listbox.yview)
        weight_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.weight_listbox.configure(yscrollcommand=weight_scrollbar.set)

        # 绑定选择事件
        self.weight_listbox.bind('<<ListboxSelect>>', self.on_weight_selected)

        # 列表下方按钮
        list_btn_frame = ttk.Frame(weight_list_frame)
        list_btn_frame.pack(fill=tk.X, pady=5)

        # 删除选中按钮（保留）
        delete_selected_btn = ttk.Button(list_btn_frame, text="🗑️ 删除选中",
                                         command=self.delete_selected_weight)
        delete_selected_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # 清除所有按钮
        clear_btn = ttk.Button(list_btn_frame, text="🔄 清除所有",
                               command=self.clear_all_weights)
        clear_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    def delete_current_tag(self):
        """删除当前选中的标签"""
        tag_name = self.tag_preset_var.get()
        if not tag_name:
            messagebox.showwarning("警告", "请先选择要删除的标签")
            return

        if tag_name not in self.custom_tags:
            messagebox.showerror("错误", f"标签 '{tag_name}' 不存在")
            return

        if messagebox.askyesno("确认删除", f"确定要删除标签 '{tag_name}' 吗？"):
            del self.custom_tags[tag_name]

            # 更新标签选择下拉框（包含空白选项）
            tag_list = [""] + list(self.custom_tags.keys())
            self.tag_preset_combo['values'] = tag_list

            # 清空当前选择
            self.tag_preset_var.set("")

            self.log(f"删除标签: {tag_name}")

    def on_tag_selected(self, event):
        """标签选择事件 - 自动填充三个权重值"""
        tag_name = self.tag_preset_var.get()
        if tag_name and tag_name in self.custom_tags:
            weights = self.custom_tags[tag_name]

            # 自动填充三个权重输入框
            self.wolf_weight.delete(0, tk.END)
            self.wolf_weight.insert(0, str(weights["wolf"]))

            self.god_weight.delete(0, tk.END)
            self.god_weight.insert(0, str(weights["god"]))

            self.human_weight.delete(0, tk.END)
            self.human_weight.insert(0, str(weights["human"]))

            # 更新提示信息
            self.tag_info_label.config(
                text=f"已加载标签: {tag_name} (狼{weights['wolf']} 神{weights['god']} 人{weights['human']})",
                foreground=self.colors['gold']
            )

            self.log(f"加载标签 '{tag_name}': 狼{weights['wolf']} 神{weights['god']} 人{weights['human']}")
        elif tag_name == "":
            # 选择了空白标签，不清空输入框，保持当前值
            self.tag_info_label.config(text="", foreground=self.colors['gold'])

    def on_weight_selected(self, event):
        """权重列表选择事件 - 加载选中的权重到输入框"""
        selection = self.weight_listbox.curselection()
        if selection:
            text = self.weight_listbox.get(selection[0])
            try:
                # 解析文本获取玩家编号和权重
                # 格式: "玩家X: 狼X.X 神X.X 人X.X"
                if '玩家' in text:
                    parts = text.split(':')
                    player_part = parts[0]
                    player = int(player_part.replace('玩家', ''))

                    # 解析权重
                    weight_part = parts[1].strip()
                    # 使用更安全的方式解析
                    import re
                    wolf_match = re.search(r'狼([\d.]+)', weight_part)
                    god_match = re.search(r'神([\d.]+)', weight_part)
                    human_match = re.search(r'人([\d.]+)', weight_part)

                    if wolf_match and god_match and human_match:
                        wolf_weight = wolf_match.group(1)
                        god_weight = god_match.group(1)
                        human_weight = human_match.group(1)

                        # 填充到输入框
                        self.weight_player_var.set(str(player))
                        self.wolf_weight.delete(0, tk.END)
                        self.wolf_weight.insert(0, wolf_weight)
                        self.god_weight.delete(0, tk.END)
                        self.god_weight.insert(0, god_weight)
                        self.human_weight.delete(0, tk.END)
                        self.human_weight.insert(0, human_weight)

                        self.log(f"加载玩家{player}的权重配置")
            except Exception as e:
                self.log(f"解析权重失败: {e}")

    def save_custom_tag(self):
        """保存当前三个权重值为自定义标签"""
        try:
            # 获取当前三个权重值
            wolf_weight = float(self.wolf_weight.get())
            god_weight = float(self.god_weight.get())
            human_weight = float(self.human_weight.get())

            # 检查是否选择了标签
            tag_name = self.tag_preset_var.get()

            # 如果没有选择标签或选择了空白，提示输入新标签名
            if not tag_name or tag_name == "":
                # 创建输入对话框
                dialog = tk.Toplevel(self.root)
                dialog.title("新建标签")
                dialog.geometry("300x150")
                dialog.transient(self.root)
                dialog.grab_set()

                # 居中显示
                dialog.update_idletasks()
                x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
                y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
                dialog.geometry(f"+{x}+{y}")

                ttk.Label(dialog, text="请输入标签名称:", font=("微软雅黑", 10)).pack(pady=10)

                tag_entry = ttk.Entry(dialog, width=25, font=("微软雅黑", 10))
                tag_entry.pack(pady=5)
                tag_entry.focus()

                def do_save():
                    new_tag = tag_entry.get().strip()
                    if new_tag:
                        # 保存三个权重值
                        self.custom_tags[new_tag] = {
                            "wolf": wolf_weight,
                            "god": god_weight,
                            "human": human_weight
                        }
                        # 更新下拉框（包含空白选项）
                        tag_list = [""] + list(self.custom_tags.keys())
                        self.tag_preset_combo['values'] = tag_list
                        self.tag_preset_var.set(new_tag)
                        self.log(f"新建标签: {new_tag} (狼{wolf_weight} 神{god_weight} 人{human_weight})")
                        dialog.destroy()
                    else:
                        messagebox.showwarning("警告", "标签名称不能为空")

                def do_cancel():
                    dialog.destroy()

                btn_frame = ttk.Frame(dialog)
                btn_frame.pack(pady=10)

                ttk.Button(btn_frame, text="保存", command=do_save).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="取消", command=do_cancel).pack(side=tk.LEFT, padx=5)

                # 绑定回车键
                tag_entry.bind('<Return>', lambda e: do_save())

            else:
                # 更新已有标签
                if messagebox.askyesno("确认",
                                       f"是否更新标签 '{tag_name}' 的权重为\n狼{wolf_weight} 神{god_weight} 人{human_weight}？"):
                    self.custom_tags[tag_name] = {
                        "wolf": wolf_weight,
                        "god": god_weight,
                        "human": human_weight
                    }
                    self.log(f"更新标签: {tag_name} (狼{wolf_weight} 神{god_weight} 人{human_weight})")

                    # 更新下拉框（包含空白选项）
                    tag_list = [""] + list(self.custom_tags.keys())
                    self.tag_preset_combo['values'] = tag_list

        except ValueError:
            messagebox.showerror("错误", "请输入有效的权重数值")

    def add_behavior_weight(self):
        """添加行为权重（应用权重）"""
        try:
            player = int(self.weight_player_var.get())
            wolf_weight = float(self.wolf_weight.get())
            god_weight = float(self.god_weight.get())
            human_weight = float(self.human_weight.get())

            # 检查是否已存在该玩家的权重
            old_weights = self.behavior_weights.get(player)
            if old_weights:
                self.log(f"更新玩家{player}的权重: 狼{old_weights['狼权']:.1f}->{wolf_weight:.1f}, "
                         f"神{old_weights['神权']:.1f}->{god_weight:.1f}, "
                         f"人{old_weights['民权']:.1f}->{human_weight:.1f}")
            else:
                self.log(f"添加行为权重: 玩家{player} 狼权={wolf_weight}, 神权={god_weight}, 民权={human_weight}")

            self.behavior_weights[player] = {
                '狼权': wolf_weight,
                '神权': god_weight,
                '民权': human_weight
            }

            self.update_weight_listbox()

            # 不清空玩家选择，方便继续操作同一个玩家

        except ValueError:
            messagebox.showerror("错误", "请输入有效的玩家编号和权重数值")

    def delete_selected_weight(self):
        """删除选中的权重"""
        selection = self.weight_listbox.curselection()
        if selection:
            text = self.weight_listbox.get(selection[0])
            try:
                # 解析文本获取玩家编号
                if '玩家' in text:
                    player = int(text.split('玩家')[1].split(':')[0])
                    if player in self.behavior_weights:
                        del self.behavior_weights[player]
                        self.log(f"删除玩家{player}的行为权重")
                        self.update_weight_listbox()

                        # 清空输入框
                        self.weight_player_var.set('')
                        self.wolf_weight.delete(0, tk.END)
                        self.wolf_weight.insert(0, "1.0")
                        self.god_weight.delete(0, tk.END)
                        self.god_weight.insert(0, "1.0")
                        self.human_weight.delete(0, tk.END)
                        self.human_weight.insert(0, "1.0")
            except:
                pass
        else:
            messagebox.showinfo("提示", "请在列表中选择要删除的权重项")

    def update_weight_listbox(self):
        """更新权重列表"""
        self.weight_listbox.delete(0, tk.END)

        for player, weights in sorted(self.behavior_weights.items()):
            display_text = f"玩家{player}: 狼{weights['狼权']:.1f} 神{weights['神权']:.1f} 人{weights['民权']:.1f}"
            self.weight_listbox.insert(tk.END, display_text)

    def clear_all_weights(self):
        """清除所有权重"""
        if self.behavior_weights:
            if messagebox.askyesno("确认", "确定要清除所有已设置的权重吗？"):
                self.behavior_weights.clear()
                self.update_weight_listbox()
                self.log("已清除所有行为权重")

                # 清空输入框
                self.weight_player_var.set('')
                self.wolf_weight.delete(0, tk.END)
                self.wolf_weight.insert(0, "1.0")
                self.god_weight.delete(0, tk.END)
                self.god_weight.insert(0, "1.0")
                self.human_weight.delete(0, tk.END)
                self.human_weight.insert(0, "1.0")



    def apply_selected_tag(self):
        """应用选中的标签"""
        try:
            player = int(self.weight_player_var.get())
            tag_name = self.tag_preset_var.get()

            if not tag_name:
                messagebox.showwarning("警告", "请先选择标签")
                return

            if tag_name not in self.custom_tags:
                messagebox.showerror("错误", f"标签 '{tag_name}' 不存在")
                return

            weight = self.custom_tags[tag_name]

            # 设置权重值（只修改狼权，神权和民权保持1.0）
            self.wolf_weight.delete(0, tk.END)
            self.wolf_weight.insert(0, str(weight))
            self.god_weight.delete(0, tk.END)
            self.god_weight.insert(0, "1.0")
            self.human_weight.delete(0, tk.END)
            self.human_weight.insert(0, "1.0")

            self.log(f"应用标签 '{tag_name}' (权重={weight}) 到玩家{player}")

            # 自动添加权重
            self.add_behavior_weight()

        except ValueError:
            messagebox.showwarning("警告", "请先选择玩家编号")

    def create_setting_tab(self, parent):
        """创建设置标签页"""
        # 使用Canvas+Scrollbar
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 标题
        ttk.Label(scrollable_frame, text="⚙️ 分析设置",
                  font=("微软雅黑", 12, "bold")).pack(pady=10)

        # 模拟次数设置
        sim_frame = ttk.LabelFrame(scrollable_frame, text="模拟次数", padding="10")
        sim_frame.pack(fill=tk.X, pady=10, padx=10)

        custom_frame = ttk.Frame(sim_frame)
        custom_frame.pack(fill=tk.X, pady=5)

        ttk.Label(custom_frame, text="模拟次数:").pack(side=tk.LEFT)
        self.sim_var = tk.StringVar(value="50000")
        sim_spinbox = ttk.Spinbox(custom_frame, from_=1000, to=500000,
                                  textvariable=self.sim_var, width=12)
        sim_spinbox.pack(side=tk.LEFT, padx=5)

        ttk.Button(custom_frame, text="应用",
                   command=self.apply_simulation_count).pack(side=tk.LEFT, padx=5)

        # 算法选择
        algo_frame = ttk.LabelFrame(scrollable_frame, text="算法选择", padding="10")
        algo_frame.pack(fill=tk.X, pady=10, padx=10)

        self.use_triangle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(algo_frame, text="📐 使用三角定律（85%双狼定理）",
                        variable=self.use_triangle_var,
                        command=self.update_algo_settings).pack(anchor=tk.W, pady=5)

        self.use_weight_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(algo_frame, text="⚖️ 使用行为权重（贝叶斯更新）",
                        variable=self.use_weight_var,
                        command=self.update_algo_settings).pack(anchor=tk.W, pady=5)

        # 分隔线
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # 计算按钮
        ttk.Label(scrollable_frame, text="开始分析",
                  font=("微软雅黑", 12, "bold")).pack(pady=10)

        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, pady=5, padx=10)

        buttons = [
            ("🎲 蒙特卡洛模拟", self.run_monte_carlo),
            ("📐 三角定律计算", self.run_triangle_law),
            ("📊 贝叶斯更新", self.run_bayesian_update),
            ("📈 综合分析", self.run_comprehensive_analysis)
        ]

        for text, cmd in buttons:
            btn = ttk.Button(btn_frame, text=text, command=cmd)
            btn.pack(fill=tk.X, pady=2)

        # 提示信息
        ttk.Label(scrollable_frame,
                  text="提示：综合分析会融合所有选中的算法",
                  font=("微软雅黑", 9), foreground=self.colors['gold']).pack(pady=10)

    def setup_middle_panel(self, parent):
        """设置中间面板（结果显示 + 可视化号码牌）"""
        # 创建Notebook
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 页面1：可视化号码牌
        visual_frame = ttk.Frame(notebook)
        notebook.add(visual_frame, text="🎴 号码牌视图")
        self.create_visual_tab(visual_frame)

        # 页面2：概率结果
        result_frame = ttk.Frame(notebook)
        notebook.add(result_frame, text="📊 概率结果")
        self.create_result_tab(result_frame)

        # 页面3：三角形分析
        triangle_frame = ttk.Frame(notebook)
        notebook.add(triangle_frame, text="📐 三角形分析")
        self.create_triangle_tab(triangle_frame)

    def create_visual_tab(self, parent):
        """创建可视化号码牌标签页（仿网易狼人杀）"""
        # 主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=10)

        ttk.Label(title_frame, text="玩家号码牌状态",
                  font=("微软雅黑", 14, "bold")).pack()

        ttk.Label(title_frame, text="点击号码牌可快速选择",
                  font=("微软雅黑", 9), foreground=self.colors['gold']).pack()

        # 创建两列布局
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        # 左列 (1-6)
        left_column = ttk.Frame(columns_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        ttk.Label(left_column, text="", font=("微软雅黑", 12, "bold")).pack(pady=5)

        # 创建左列6行
        for i in range(1, 7):
            self.create_player_card(left_column, i)

        # 右列 (7-12)
        right_column = ttk.Frame(columns_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        ttk.Label(right_column, text="", font=("微软雅黑", 12, "bold")).pack(pady=5)

        # 创建右列6行
        for i in range(7, 13):
            self.create_player_card(right_column, i)

        # 图例说明
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(fill=tk.X, pady=5)

        ttk.Label(legend_frame, text="图例: ",
                  font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # 狼人
        wolf_legend = tk.Frame(legend_frame, bg=self.colors['wolf'], width=20, height=20)
        wolf_legend.pack(side=tk.LEFT, padx=2)
        wolf_legend.pack_propagate(False)
        ttk.Label(legend_frame, text="狼人", foreground=self.colors['wolf']).pack(side=tk.LEFT, padx=5)

        # 神职
        god_legend = tk.Frame(legend_frame, bg=self.colors['god'], width=20, height=20)
        god_legend.pack(side=tk.LEFT, padx=2)
        god_legend.pack_propagate(False)
        ttk.Label(legend_frame, text="神职", foreground=self.colors['god']).pack(side=tk.LEFT, padx=5)

        # 平民
        human_legend = tk.Frame(legend_frame, bg=self.colors['human'], width=20, height=20)
        human_legend.pack(side=tk.LEFT, padx=2)
        human_legend.pack_propagate(False)
        ttk.Label(legend_frame, text="平民", foreground=self.colors['human']).pack(side=tk.LEFT, padx=5)

        # 好人标记
        mark_legend = tk.Frame(legend_frame, bg=self.colors['gold'], width=20, height=20)
        mark_legend.pack(side=tk.LEFT, padx=2)
        mark_legend.pack_propagate(False)
        ttk.Label(legend_frame, text="好人标记", foreground=self.colors['gold']).pack(side=tk.LEFT, padx=5)

        # 未知
        unknown_legend = tk.Frame(legend_frame, bg=self.colors['player_bg'], width=20, height=20)
        unknown_legend.pack(side=tk.LEFT, padx=2)
        unknown_legend.pack_propagate(False)
        ttk.Label(legend_frame, text="未知", foreground=self.colors['fg']).pack(side=tk.LEFT, padx=5)

    def create_player_card(self, parent, player_num):
        """创建单个玩家卡片"""
        # 卡片框架
        card_frame = tk.Frame(parent, bg=self.colors['player_bg'],
                              relief=tk.RAISED, borderwidth=2)
        card_frame.pack(fill=tk.X, pady=5, ipadx=10, ipady=5)

        # 存储卡片引用
        self.player_cards[player_num] = card_frame

        # 上部：号码和身份信息
        top_frame = tk.Frame(card_frame, bg=self.colors['player_bg'])
        top_frame.pack(fill=tk.X, padx=5, pady=2)

        # 左侧：号码和身份图标
        left_frame = tk.Frame(top_frame, bg=self.colors['player_bg'])
        left_frame.pack(side=tk.LEFT)

        # 圆形号码牌（用Label模拟）
        num_frame = tk.Frame(left_frame, bg=self.colors['player_border'],
                             width=40, height=40)
        num_frame.pack(side=tk.LEFT, padx=2)
        num_frame.pack_propagate(False)

        # 号码标签
        num_label = tk.Label(num_frame, text=str(player_num),
                             bg=self.colors['player_border'],
                             fg=self.colors['fg'],
                             font=("微软雅黑", 12, "bold"))
        num_label.pack(expand=True, fill=tk.BOTH)

        # 身份图标标签
        icon_label = ttk.Label(left_frame, text="❓", font=("微软雅黑", 14))
        icon_label.pack(side=tk.LEFT, padx=5)

        # 存储标签引用
        self.player_labels[player_num] = icon_label

        # 身份名称
        role_label = ttk.Label(top_frame, text="未知", font=("微软雅黑", 10))
        role_label.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # 存储角色名称标签
        self.player_labels[f"{player_num}_role"] = role_label

        # 底部：概率显示区域（新增）
        prob_frame = tk.Frame(card_frame, bg=self.colors['player_bg'])
        prob_frame.pack(fill=tk.X, padx=5, pady=2)

        # 狼人概率
        wolf_frame = tk.Frame(prob_frame, bg=self.colors['player_bg'])
        wolf_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        wolf_label = tk.Label(wolf_frame, text="🐺0%",
                              bg=self.colors['player_bg'],
                              fg=self.colors['wolf'],
                              font=("微软雅黑", 8))
        wolf_label.pack()

        # 神职概率
        god_frame = tk.Frame(prob_frame, bg=self.colors['player_bg'])
        god_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        god_label = tk.Label(god_frame, text="👼0%",
                             bg=self.colors['player_bg'],
                             fg=self.colors['god'],
                             font=("微软雅黑", 8))
        god_label.pack()

        # 平民概率
        human_frame = tk.Frame(prob_frame, bg=self.colors['player_bg'])
        human_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        human_label = tk.Label(human_frame, text="👤0%",
                               bg=self.colors['player_bg'],
                               fg=self.colors['human'],
                               font=("微软雅黑", 8))
        human_label.pack()

        # 存储概率标签引用
        self.player_labels[f"{player_num}_wolf_prob"] = wolf_label
        self.player_labels[f"{player_num}_god_prob"] = god_label
        self.player_labels[f"{player_num}_human_prob"] = human_label

        # 绑定点击事件 - 快速选择玩家
        for widget in [card_frame, num_label, icon_label, role_label, wolf_frame, god_frame, human_frame]:
            widget.bind('<Button-1>', lambda e, p=player_num: self.quick_select_player(p))
            # 添加鼠标样式变化，提示可点击
            widget.bind('<Enter>', lambda e, w=widget: w.config(cursor="hand2"))
            widget.bind('<Leave>', lambda e, w=widget: w.config(cursor=""))

        # 初始化卡片颜色
        self.update_player_card(player_num)

    def quick_select_player(self, player_num):
        """快速选择玩家 - 修复版：同时更新两个页面的玩家选择"""
        # 更新身份输入页面的玩家选择
        self.player_var.set(str(player_num))

        # 更新权重设置页面的玩家选择
        self.weight_player_var.set(str(player_num))

        self.log(f"快速选择玩家 {player_num}")

        # 先清空所有分类的选中状态
        for var in self.role_vars.values():
            var.set('')

        # 如果该玩家已有身份，自动选中对应的身份
        if player_num in self.known_info:
            role = self.known_info[player_num]["role"]
            category = self.known_info[player_num].get("category")

            # 直接使用保存的category来设置
            if category and category in self.role_vars:
                self.role_vars[category].set(role)

                # 自动切换到对应的标签页，方便用户查看和修改
                self.switch_to_category_tab(category)

                self.log(f"自动选中身份: {role} [分类: {category}]")
            else:
                # 兼容旧数据，如果没有保存category，则遍历查找
                for cat, roles in self.role_categories.items():
                    if role in roles:
                        self.role_vars[cat].set(role)

                        # 自动切换到对应的标签页
                        self.switch_to_category_tab(cat)

                        self.log(f"自动选中身份: {role} [分类: {cat}]")
                        break

    def apply_custom_tag(self, tag_name, default_weight):
        """应用自定义标签"""
        try:
            player = int(self.weight_player_var.get())

            # 设置权重值
            self.wolf_weight.delete(0, tk.END)
            self.wolf_weight.insert(0, str(default_weight))
            self.god_weight.delete(0, tk.END)
            self.god_weight.insert(0, "1.0")
            self.human_weight.delete(0, tk.END)
            self.human_weight.insert(0, "1.0")

            self.log(f"应用标签 '{tag_name}' 到玩家{player}，权重={default_weight}")

            # 自动添加权重
            self.add_behavior_weight()

        except ValueError:
            messagebox.showwarning("警告", "请先选择玩家编号")

    def add_custom_tag(self):
        """添加自定义标签"""
        tag_name = self.new_tag_name.get().strip()
        if not tag_name:
            messagebox.showwarning("警告", "请输入标签名称")
            return

        try:
            weight = float(self.new_tag_weight.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的权重值")
            return

        if tag_name in self.custom_tags:
            if not messagebox.askyesno("确认", f"标签 '{tag_name}' 已存在，是否覆盖？"):
                return

        self.custom_tags[tag_name] = weight

        # 更新标签按钮显示
        self.refresh_tag_buttons()

        # 更新删除下拉框
        self.tag_to_delete['values'] = list(self.custom_tags.keys())

        self.log(f"添加自定义标签: {tag_name} (权重={weight})")
        self.new_tag_name.delete(0, tk.END)

    def refresh_tag_buttons(self):
        """刷新标签按钮显示"""
        # 重新创建标签按钮（简化版本，实际应该重新布局）
        # 注意：由于按钮在scrollable_frame中，这里需要找到正确的父容器重新创建
        # 为了简化，我们可以重新加载整个权重标签页
        # 这里使用简单的方法：弹出提示让用户重启应用或重新加载
        messagebox.showinfo("提示", "标签已更新，建议重启应用以刷新界面")

    def update_player_card(self, player_num):
        """更新单个玩家卡片的显示"""
        if player_num not in self.player_cards:
            return

        card_frame = self.player_cards[player_num]
        icon_label = self.player_labels.get(player_num)
        role_label = self.player_labels.get(f"{player_num}_role")

        if player_num in self.known_info:
            info = self.known_info[player_num]
            role = info["role"]
            role_type = info["type"]

            # 设置颜色和图标
            if role_type == "wolf":
                color = self.colors['wolf']
                icon = "🐺"
            elif role_type == "god":
                color = self.colors['god']
                icon = "👼"
            elif role_type == "human":
                color = self.colors['human']
                icon = "👤"
            elif role_type == "good_mark":
                color = self.colors['gold']
                icon = "⭐"
            else:
                color = self.colors['player_bg']
                icon = "❓"

            card_frame.config(bg=color)
            # 同时更新内部所有框架的颜色
            for child in card_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=color)
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Frame):
                            subchild.config(bg=color)
                        elif isinstance(subchild, tk.Label):
                            if subchild not in [self.player_labels.get(f"{player_num}_wolf_prob"),
                                                self.player_labels.get(f"{player_num}_god_prob"),
                                                self.player_labels.get(f"{player_num}_human_prob")]:
                                subchild.config(bg=color)

            if icon_label:
                icon_label.config(text=icon)
            if role_label:
                role_label.config(text=role)
        else:
            # 未知玩家
            card_frame.config(bg=self.colors['player_bg'])
            # 更新内部框架颜色
            for child in card_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=self.colors['player_bg'])
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Frame):
                            subchild.config(bg=self.colors['player_bg'])
                        elif isinstance(subchild, tk.Label):
                            if subchild not in [self.player_labels.get(f"{player_num}_wolf_prob"),
                                                self.player_labels.get(f"{player_num}_god_prob"),
                                                self.player_labels.get(f"{player_num}_human_prob")]:
                                subchild.config(bg=self.colors['player_bg'])

            if icon_label:
                icon_label.config(text="❓")
            if role_label:
                role_label.config(text="未知")

    def update_card_probabilities(self, results, result_type="综合分析"):
        """更新每个卡片上的概率显示

        Args:
            results: 概率结果数据
            result_type: 结果类型（蒙特卡洛/三角定律/贝叶斯/综合分析）
        """
        try:
            # 先重置所有概率显示为0
            for player_num in range(1, 13):
                wolf_label = self.player_labels.get(f"{player_num}_wolf_prob")
                god_label = self.player_labels.get(f"{player_num}_god_prob")
                human_label = self.player_labels.get(f"{player_num}_human_prob")

                if wolf_label:
                    wolf_label.config(text="🐺0%")
                if god_label:
                    god_label.config(text="👼0%")
                if human_label:
                    human_label.config(text="👤0%")

            # 根据不同算法类型更新概率
            if result_type == "蒙特卡洛":
                # 从 tree 中获取数据并更新
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    if values and len(values) >= 4:
                        try:
                            player_text = values[0]
                            if '玩家' in player_text:
                                player_num = int(player_text.replace('玩家', ''))
                                wolf_prob = values[1].replace('%', '')
                                god_prob = values[2].replace('%', '')
                                human_prob = values[3].replace('%', '')

                                wolf_label = self.player_labels.get(f"{player_num}_wolf_prob")
                                god_label = self.player_labels.get(f"{player_num}_god_prob")
                                human_label = self.player_labels.get(f"{player_num}_human_prob")

                                if wolf_label:
                                    wolf_label.config(text=f"🐺{wolf_prob}")
                                if god_label:
                                    god_label.config(text=f"👼{god_prob}")
                                if human_label:
                                    human_label.config(text=f"👤{human_prob}")
                        except:
                            continue

            elif result_type == "三角定律":
                # 三角定律更新所有概率
                for player_num, probs in results.items():
                    wolf_label = self.player_labels.get(f"{player_num}_wolf_prob")
                    god_label = self.player_labels.get(f"{player_num}_god_prob")
                    human_label = self.player_labels.get(f"{player_num}_human_prob")

                    wolf_prob = probs.get('狼人', 0)
                    god_prob = probs.get('神职', 0)
                    human_prob = probs.get('平民', 0)

                    if wolf_label:
                        wolf_label.config(text=f"🐺{wolf_prob:.1%}")
                    if god_label:
                        god_label.config(text=f"👼{god_prob:.1%}")
                    if human_label:
                        human_label.config(text=f"👤{human_prob:.1%}")

            elif result_type == "贝叶斯":
                # 贝叶斯更新所有概率
                for player_num, probs in results.items():
                    wolf_label = self.player_labels.get(f"{player_num}_wolf_prob")
                    god_label = self.player_labels.get(f"{player_num}_god_prob")
                    human_label = self.player_labels.get(f"{player_num}_human_prob")

                    wolf_prob = probs.get('狼人', 0)
                    god_prob = probs.get('神职', 0)
                    human_prob = probs.get('平民', 0)

                    if wolf_label:
                        wolf_label.config(text=f"🐺{wolf_prob:.1%}")
                    if god_label:
                        god_label.config(text=f"👼{god_prob:.1%}")
                    if human_label:
                        human_label.config(text=f"👤{human_prob:.1%}")

            elif result_type == "综合分析":
                # 综合分析更新所有概率
                for player_num, probs in results.items():
                    wolf_label = self.player_labels.get(f"{player_num}_wolf_prob")
                    god_label = self.player_labels.get(f"{player_num}_god_prob")
                    human_label = self.player_labels.get(f"{player_num}_human_prob")

                    wolf_prob = probs.get('狼人', 0)
                    god_prob = probs.get('神民', 0)
                    human_prob = probs.get('平民', 0)

                    if wolf_label:
                        wolf_label.config(text=f"🐺{wolf_prob:.1%}")
                    if god_label:
                        god_label.config(text=f"👼{god_prob:.1%}")
                    if human_label:
                        human_label.config(text=f"👤{human_prob:.1%}")

            self.log(f"已更新卡片概率显示 ({result_type})")

        except Exception as e:
            self.log(f"更新卡片概率失败: {e}")

    def update_all_player_cards(self):
        """更新所有玩家卡片"""
        for player_num in range(1, 13):
            self.update_player_card(player_num)

    def create_result_tab(self, parent):
        """创建结果标签页"""
        # 创建Treeview
        columns = ('玩家', '狼人概率', '神民概率', '平民概率', '所在三角')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=20,
                                 selectmode='browse')

        # 设置列标题
        self.tree.heading('玩家', text='👤 玩家')
        self.tree.heading('狼人概率', text='🐺 狼人概率')
        self.tree.heading('神民概率', text='👼 神民概率')
        self.tree.heading('平民概率', text='👤 平民概率')
        self.tree.heading('所在三角', text='📐 所在三角')

        # 设置列宽
        self.tree.column('玩家', width=70, anchor='center')
        self.tree.column('狼人概率', width=100, anchor='center')
        self.tree.column('神民概率', width=100, anchor='center')
        self.tree.column('平民概率', width=100, anchor='center')
        self.tree.column('所在三角', width=100, anchor='center')

        # 添加滚动条
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_result_select)

        # 配置标签颜色
        self.tree.tag_configure('high', foreground=self.colors['wolf'])
        self.tree.tag_configure('medium', foreground=self.colors['gold'])
        self.tree.tag_configure('low', foreground=self.colors['god'])

    def create_triangle_tab(self, parent):
        """创建三角形分析标签页"""
        # 文本显示区域
        self.triangle_status_text = scrolledtext.ScrolledText(parent,
                                                              bg=self.colors['entry_bg'],
                                                              fg=self.colors['fg'],
                                                              font=("Consolas", 10),
                                                              height=20)
        self.triangle_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 配置标签
        self.triangle_status_text.tag_config("bold", font=("Consolas", 10, "bold"))
        self.triangle_status_text.tag_config("wolf", foreground=self.colors['wolf'])
        self.triangle_status_text.tag_config("god", foreground=self.colors['god'])
        self.triangle_status_text.tag_config("human", foreground=self.colors['human'])

        # 刷新按钮
        ttk.Button(parent, text="🔄 刷新分析",
                   command=self.update_triangle_analysis,
                   style='Accent.TButton').pack(pady=5)

        # 初始化分析
        self.update_triangle_analysis()

    def create_law_tab(self, parent):
        """创建基础定律标签页"""
        # 文本显示区域
        self.law_text = scrolledtext.ScrolledText(parent,
                                                  bg=self.colors['entry_bg'],
                                                  fg=self.colors['fg'],
                                                  font=("Consolas", 10),
                                                  height=20)
        self.law_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 配置标签
        self.law_text.tag_config("bold", font=("Consolas", 10, "bold"))

        # 刷新按钮
        ttk.Button(parent, text="🔄 刷新定律",
                   command=self.calculate_basic_probabilities,
                   style='Accent.TButton').pack(pady=5)

        # 计算基础概率
        self.calculate_basic_probabilities()

    def setup_right_panel(self, parent):
        """设置右侧面板（实时日志 + 基础定律 + 发言记录）"""
        # 创建Notebook
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 页面1：实时日志
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="📝 实时日志")
        self.create_log_tab(log_frame)

        # 页面2：基础定律（原学习资源位置）
        law_frame = ttk.Frame(notebook)
        notebook.add(law_frame, text="📏 基础定律")
        self.create_law_tab_right(law_frame)

        # 页面3：发言记录（新增）
        speech_frame = ttk.Frame(notebook)
        notebook.add(speech_frame, text="💬 发言记录")
        self.create_speech_tab(speech_frame)

        # 页面4：关于
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="ℹ️ 关于")
        self.create_about_tab(about_frame)

    def create_law_tab_right(self, parent):
        """创建右侧基础定律标签页"""
        # 创建主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 文本显示区域
        self.law_right_text = scrolledtext.ScrolledText(main_frame,
                                                        bg=self.colors['entry_bg'],
                                                        fg=self.colors['fg'],
                                                        font=("Consolas", 10),
                                                        height=20,
                                                        wrap=tk.WORD)
        self.law_right_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 配置标签
        self.law_right_text.tag_config("bold", font=("Consolas", 10, "bold"))
        self.law_right_text.tag_config("title", font=("Consolas", 11, "bold"), foreground=self.colors['gold'])
        self.law_right_text.tag_config("wolf", foreground=self.colors['wolf'])
        self.law_right_text.tag_config("god", foreground=self.colors['god'])
        self.law_right_text.tag_config("human", foreground=self.colors['human'])

        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="🔄 刷新定律",
                   command=self.calculate_basic_probabilities_right,
                   style='Accent.TButton').pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        ttk.Button(btn_frame, text="📋 复制内容",
                   command=lambda: self.copy_text_to_clipboard(self.law_right_text)).pack(side=tk.LEFT, padx=2,
                                                                                          expand=True, fill=tk.X)

        # 初始化基础定律显示
        self.calculate_basic_probabilities_right()

    def create_speech_tab(self, parent):
        """创建发言记录标签页"""
        # 创建主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 说明标签
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)

        ttk.Label(info_frame, text="📝 玩家发言记录",
                  font=("微软雅黑", 11, "bold")).pack(side=tk.LEFT)

        ttk.Label(info_frame, text="(可记录每轮发言，用于分析)",
                  font=("微软雅黑", 9), foreground=self.colors['gold']).pack(side=tk.LEFT, padx=10)

        # 玩家选择框架
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(select_frame, text="选择玩家:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=2)

        self.speech_player_var = tk.StringVar()
        self.speech_player_combo = ttk.Combobox(select_frame,
                                                textvariable=self.speech_player_var,
                                                values=self.players,
                                                state="readonly",
                                                width=10)
        self.speech_player_combo.pack(side=tk.LEFT, padx=5)
        self.speech_player_combo.bind('<<ComboboxSelected>>', self.on_speech_player_selected)

        ttk.Label(select_frame, text="轮次:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(20, 2))

        self.speech_round_var = tk.StringVar(value="第1轮")
        round_values = [f"第{i}轮" for i in range(1, 11)] + ["警上", "警下", "遗言", "总结"]
        self.speech_round_combo = ttk.Combobox(select_frame,
                                               textvariable=self.speech_round_var,
                                               values=round_values,
                                               state="readonly",
                                               width=8)
        self.speech_round_combo.pack(side=tk.LEFT, padx=5)

        # 发言记录文本框
        text_frame = ttk.LabelFrame(main_frame, text="发言内容", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.speech_text = scrolledtext.ScrolledText(text_frame,
                                                     bg=self.colors['entry_bg'],
                                                     fg=self.colors['fg'],
                                                     insertbackground=self.colors['fg'],
                                                     font=("微软雅黑", 10),
                                                     height=12,
                                                     wrap=tk.WORD,
                                                     undo=True)
        self.speech_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 按钮框架
        btn_frame1 = ttk.Frame(main_frame)
        btn_frame1.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame1, text="💾 保存发言",
                   command=self.save_speech,
                   style='Accent.TButton').pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        ttk.Button(btn_frame1, text="🔄 清空当前",
                   command=self.clear_current_speech).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # 发言记录列表
        list_frame = ttk.LabelFrame(main_frame, text="已保存的发言记录", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 创建左右布局
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        # 左侧：记录列表
        left_list = ttk.Frame(list_container)
        left_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.speech_listbox = tk.Listbox(left_list,
                                         height=6,
                                         bg=self.colors['entry_bg'],
                                         fg=self.colors['fg'],
                                         selectbackground=self.colors['tree_select'],
                                         font=("微软雅黑", 9))
        self.speech_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        list_scrollbar = ttk.Scrollbar(left_list, orient=tk.VERTICAL,
                                       command=self.speech_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.speech_listbox.configure(yscrollcommand=list_scrollbar.set)

        # 绑定选择事件
        self.speech_listbox.bind('<<ListboxSelect>>', self.on_speech_record_selected)

        # 右侧：操作按钮
        right_btn = ttk.Frame(list_container)
        right_btn.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        ttk.Button(right_btn, text="查看",
                   command=self.view_speech_record,
                   width=8).pack(pady=2)

        ttk.Button(right_btn, text="删除",
                   command=self.delete_speech_record,
                   width=8).pack(pady=2)

        # 底部按钮框架
        btn_frame2 = ttk.Frame(main_frame)
        btn_frame2.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame2, text="🗑️ 清空所有记录",
                   command=self.clear_all_speech_records).pack(side=tk.RIGHT, padx=2)

        # 存储发言记录的数据结构
        self.speech_records = {}  # 格式: {(player, round): "发言内容"}

    def on_speech_player_selected(self, event):
        """发言记录玩家选择事件"""
        player = self.speech_player_var.get()
        round_text = self.speech_round_var.get()

        if player and round_text:
            self.load_speech_record(int(player), round_text)

    def load_speech_record(self, player, round_text):
        """加载指定玩家和轮次的发言记录"""
        key = (player, round_text)
        if key in self.speech_records:
            self.speech_text.delete(1.0, tk.END)
            self.speech_text.insert(1.0, self.speech_records[key])
            self.log(f"加载发言记录: 玩家{player} {round_text}")
        else:
            self.speech_text.delete(1.0, tk.END)

    def save_speech(self):
        """保存发言记录"""
        try:
            player = int(self.speech_player_var.get())
            round_text = self.speech_round_var.get()
            content = self.speech_text.get(1.0, tk.END).strip()

            if not content:
                messagebox.showwarning("警告", "发言内容不能为空")
                return

            key = (player, round_text)
            old_content = self.speech_records.get(key)

            self.speech_records[key] = content
            self.update_speech_listbox()

            if old_content:
                self.log(f"更新发言记录: 玩家{player} {round_text}")
            else:
                self.log(f"保存发言记录: 玩家{player} {round_text}")

            # 自动在日志中显示发言内容摘要
            summary = content[:50] + "..." if len(content) > 50 else content
            self.log(f"  内容: {summary}")

        except ValueError:
            messagebox.showwarning("警告", "请选择玩家编号")

    def update_speech_listbox(self):
        """更新发言记录列表"""
        self.speech_listbox.delete(0, tk.END)

        # 按玩家和轮次排序显示
        sorted_keys = sorted(self.speech_records.keys(),
                             key=lambda x: (x[0], x[1]))

        for player, round_text in sorted_keys:
            display_text = f"玩家{player} - {round_text}"
            self.speech_listbox.insert(tk.END, display_text)

    def on_speech_record_selected(self, event):
        """发言记录选择事件"""
        selection = self.speech_listbox.curselection()
        if selection:
            text = self.speech_listbox.get(selection[0])
            try:
                # 解析文本获取玩家和轮次
                parts = text.split(" - ")
                player_part = parts[0]
                round_text = parts[1]

                player = int(player_part.replace("玩家", ""))

                self.speech_player_var.set(str(player))
                self.speech_round_var.set(round_text)
                self.load_speech_record(player, round_text)
            except:
                pass

    def view_speech_record(self):
        """查看选中的发言记录"""
        selection = self.speech_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先在列表中选择要查看的记录")
            return

        # 已经通过选择事件自动加载了，这里只需要弹出对话框显示完整内容
        text = self.speech_listbox.get(selection[0])
        try:
            parts = text.split(" - ")
            player_part = parts[0]
            round_text = parts[1]
            player = int(player_part.replace("玩家", ""))
            key = (player, round_text)

            if key in self.speech_records:
                content = self.speech_records[key]

                # 创建新窗口显示完整内容
                dialog = tk.Toplevel(self.root)
                dialog.title(f"玩家{player} {round_text} 发言记录")
                dialog.geometry("500x400")
                dialog.transient(self.root)

                text_widget = scrolledtext.ScrolledText(dialog,
                                                        bg=self.colors['entry_bg'],
                                                        fg=self.colors['fg'],
                                                        font=("微软雅黑", 10),
                                                        wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(1.0, content)
                text_widget.config(state=tk.DISABLED)

                ttk.Button(dialog, text="关闭",
                           command=dialog.destroy).pack(pady=5)
        except:
            pass

    def delete_speech_record(self):
        """删除选中的发言记录"""
        selection = self.speech_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先在列表中选择要删除的记录")
            return

        text = self.speech_listbox.get(selection[0])
        try:
            parts = text.split(" - ")
            player_part = parts[0]
            round_text = parts[1]
            player = int(player_part.replace("玩家", ""))
            key = (player, round_text)

            if messagebox.askyesno("确认删除", f"确定要删除玩家{player} {round_text}的发言记录吗？"):
                del self.speech_records[key]
                self.update_speech_listbox()

                # 如果当前显示的就是这条记录，清空显示
                current_player = self.speech_player_var.get()
                current_round = self.speech_round_var.get()
                if current_player and current_round:
                    if int(current_player) == player and current_round == round_text:
                        self.speech_text.delete(1.0, tk.END)

                self.log(f"删除发言记录: 玩家{player} {round_text}")
        except:
            pass

    def clear_current_speech(self):
        """清空当前发言输入框"""
        if self.speech_text.get(1.0, tk.END).strip():
            if messagebox.askyesno("确认", "确定要清空当前输入内容吗？"):
                self.speech_text.delete(1.0, tk.END)

    def clear_all_speech_records(self):
        """清空所有发言记录"""
        if self.speech_records:
            if messagebox.askyesno("确认", f"确定要清空所有{len(self.speech_records)}条发言记录吗？"):
                self.speech_records.clear()
                self.speech_listbox.delete(0, tk.END)
                self.speech_text.delete(1.0, tk.END)
                self.log("已清空所有发言记录")

    def copy_text_to_clipboard(self, text_widget):
        """复制文本内容到剪贴板"""
        try:
            content = text_widget.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.log("内容已复制到剪贴板")
            messagebox.showinfo("提示", "内容已复制到剪贴板")
        except Exception as e:
            self.log(f"复制失败: {e}")
            messagebox.showerror("错误", f"复制失败: {e}")

    def calculate_basic_probabilities_right(self):
        """计算基础概率（右侧显示版）"""
        self.law_right_text.delete(1.0, tk.END)

        # 标题
        self.law_right_text.insert(tk.END, "📐 三角定律分布\n", "title")
        self.law_right_text.insert(tk.END, "─" * 40 + "\n")

        # 三角定律
        tri_probs = self.calculate_triangle_probabilities()
        for case, prob in tri_probs.items():
            self.law_right_text.insert(tk.END, f"{case}: {prob:.1%}\n")

        prob_double = 1 - tri_probs.get("四个三角各1狼", 0)
        self.law_right_text.insert(tk.END, f"\n✅ 至少一组双狼: {prob_double:.1%}\n\n")

        # 三行定律
        self.law_right_text.insert(tk.END, "📏 三行定律\n", "title")
        self.law_right_text.insert(tk.END, "─" * 40 + "\n")

        row_prob = self.calculate_row_probability()
        self.law_right_text.insert(tk.END, f"连续三行有≥3狼: {row_prob:.1%}\n\n")

        # 四角定律
        self.law_right_text.insert(tk.END, "🔲 四角定律\n", "title")
        self.law_right_text.insert(tk.END, "─" * 40 + "\n")

        corner_probs = self.calculate_corner_probabilities()
        for k, v in corner_probs.items():
            self.law_right_text.insert(tk.END, f"单组{k}狼: {v:.1%}\n")

        # 添加组合数学说明
        self.law_right_text.insert(tk.END, "\n" + "─" * 40 + "\n")
        self.law_right_text.insert(tk.END, "📊 组合数学\n", "title")
        self.law_right_text.insert(tk.END, f"总组合数: C(12,4) = 495\n")
        self.law_right_text.insert(tk.END, f"每组各1狼: 81/495 = {81 / 495:.2%}\n")
        self.law_right_text.insert(tk.END, f"至少一组双狼: {1 - 81 / 495:.2%}\n")

    def create_log_tab(self, parent):
        """创建日志标签页"""
        self.log_text = scrolledtext.ScrolledText(parent,
                                                  bg=self.colors['entry_bg'],
                                                  fg=self.colors['fg'],
                                                  insertbackground=self.colors['fg'],
                                                  font=("Consolas", 9),
                                                  height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 清空日志按钮
        ttk.Button(parent, text="🗑️ 清空日志",
                   command=self.clear_log).pack(pady=5)

    def create_resource_tab(self, parent):
        """创建学习资源标签页"""
        # 使用Canvas实现滚动
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 资源内容
        resources = [
            ("📺 视频教学", [
                ("【三角定律】狼人杀位置学 - 申屠", "https://www.bilibili.com/video/BV1bE41157qh"),
                ("三行定律教学视频", "https://www.bilibili.com/video/BV1bE41157qh"),
            ]),
            ("📄 文章资料", [
                ("三行定律数理分析 - 申屠微博", "https://weibo.com/ttarticle/p/show?id=2309404485985248346432"),
                ("三角定律原理解析", "#"),
            ]),
            ("📊 数学原理", [
                ("组合数学在狼人杀中的应用", "#"),
                ("贝叶斯推理入门", "#"),
            ])
        ]

        for category, links in resources:
            ttk.Label(scrollable_frame, text=category,
                      font=("微软雅黑", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))

            for text, url in links:
                link = ttk.Label(scrollable_frame, text=f"  • {text}",
                                 foreground="#1e90ff", cursor="hand2")
                link.pack(anchor=tk.W, pady=2)
                link.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    def create_about_tab(self, parent):
        """创建关于标签页"""
        # 创建主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建文本框用于显示说明文字
        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=('微软雅黑', 10),
                              bg='#f0f0f0', relief=tk.FLAT, borderwidth=0)
        text_widget.pack(fill=tk.BOTH, expand=True)

        about_text = """
    ╔═══════════════════════════════════════╗
    ║            狼人杀概论计算器 v1.0                
    ║            Werewolf Probability Calculator   
    ╚═══════════════════════════════════════╝

    【主要特性】
    • 支持多种身份类型
      - 好人标记：金水/银水/铜水/爆水/花露水
      - 狼人：狼人/狼王/白狼王/狼美人/石像鬼等
      - 神职：预言家/女巫/猎人/愚者/守卫等
      - 平民：平民/混血儿/暗恋者/羊驼

    • 多种概率算法
      - 蒙特卡洛模拟
      - 三角定律（85%双狼定理）
      - 贝叶斯更新（狼权/神权/民权）
      - 综合分析

    • 可视化界面
      - 仿网易狼人杀号码牌布局
      - 点击卡片快速选择玩家
      - 实时身份状态显示

    • 自定义标签系统
      - 可添加任意行为标签
      - 每个标签有独立权重
      - 标签无阵营之分

    【数学原理】
    总组合数：C(12,4) = 495
    每组各1狼概率：81/495 = 16.36%
    至少一组双狼概率：83.64%

    【下载地址】
    GitHub: https://github.com/Haisi-1536/Werewolves

    【版本信息】
    版本：v1.0
    发布日期：2026年3月
        """

        # 插入文本
        text_widget.insert(tk.END, about_text)

        # 找到GitHub链接的位置并添加标签
        start_pos = about_text.find("https://github.com/Haisi-1536/Werewolves")
        if start_pos != -1:
            # 计算在文本框中的位置
            line_count = len(about_text[:start_pos].split('\n'))
            char_count = len(about_text[:start_pos].split('\n')[-1])

            start_index = f"{line_count}.{char_count}"
            end_index = f"{line_count}.{char_count + len('https://github.com/Haisi-1536/Werewolves')}"

            # 添加链接标签
            text_widget.tag_add("hyperlink", start_index, end_index)
            text_widget.tag_config("hyperlink", foreground="blue", underline=True)

            # 绑定点击事件
            def open_link(event):
                import webbrowser
                webbrowser.open("https://github.com/Haisi-1536/Werewolves")

            text_widget.tag_bind("hyperlink", "<Button-1>", open_link)
            text_widget.tag_bind("hyperlink", "<Enter>", lambda e: text_widget.config(cursor="hand2"))
            text_widget.tag_bind("hyperlink", "<Leave>", lambda e: text_widget.config(cursor=""))

        # 设置为只读
        text_widget.config(state=tk.DISABLED)

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=5, pady=2)

        # 状态信息
        self.status_label = ttk.Label(status_frame, text="就绪",
                                      font=("微软雅黑", 9))
        self.status_label.pack(side=tk.LEFT)

        # 模拟次数显示
        self.sim_label = ttk.Label(status_frame,
                                   text=f"模拟次数: {self.simulation_count}",
                                   font=("微软雅黑", 9))
        self.sim_label.pack(side=tk.RIGHT, padx=20)

        # 算法状态
        algo_status = []
        if self.use_triangle_law:
            algo_status.append("三角定律")
        if self.use_behavior_weight:
            algo_status.append("行为权重")
        algo_text = " | ".join(algo_status) if algo_status else "基础模式"

        self.algo_label = ttk.Label(status_frame,
                                    text=f"算法: {algo_text}",
                                    font=("微软雅黑", 9))
        self.algo_label.pack(side=tk.RIGHT, padx=20)

    def apply_simulation_count(self):
        """应用模拟次数"""
        try:
            count = int(self.sim_var.get())
            if count < 1000:
                count = 1000
                self.sim_var.set("1000")
            elif count > 500000:
                count = 500000
                self.sim_var.set("500000")

            self.simulation_count = count
            self.sim_label.config(text=f"模拟次数: {count}")
            self.log(f"设置模拟次数: {count}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def update_algo_settings(self):
        """更新算法设置"""
        self.use_triangle_law = self.use_triangle_var.get()
        self.use_behavior_weight = self.use_weight_var.get()

        # 更新状态栏
        algo_status = []
        if self.use_triangle_law:
            algo_status.append("三角定律")
        if self.use_behavior_weight:
            algo_status.append("行为权重")
        algo_text = " | ".join(algo_status) if algo_status else "基础模式"
        self.algo_label.config(text=f"算法: {algo_text}")

        self.log(f"算法设置: 三角定律{'开启' if self.use_triangle_law else '关闭'}, "
                 f"行为权重{'开启' if self.use_behavior_weight else '关闭'}")

    def set_weight_preset(self, wolf, god, human):
        """设置权重预设"""
        self.wolf_weight.delete(0, tk.END)
        self.wolf_weight.insert(0, wolf)
        self.god_weight.delete(0, tk.END)
        self.god_weight.insert(0, god)
        self.human_weight.delete(0, tk.END)
        self.human_weight.insert(0, human)
        self.log(f"应用权重预设: 狼{wolf} 神{god} 人{human}")

    def get_role_type(self, role):
        """获取身份类型"""
        for category, roles in self.role_categories.items():
            if role in roles:
                if category == "好人标记":
                    return "good_mark"
                elif category == "狼人":
                    return "wolf"
                elif category == "神职":
                    return "god"
                elif category == "平民":
                    return "human"
        return "unknown"

    def on_player_selected(self, event):
        """玩家选择事件（下拉框）"""
        player = self.player_var.get()
        if player and player.isdigit():
            player = int(player)

            # 先清空所有分类的选中状态
            for var in self.role_vars.values():
                var.set('')

            # 如果该玩家已有身份，自动选中对应的身份
            if player in self.known_info:
                role = self.known_info[player]["role"]
                # 找到对应的分类并选中
                for category, roles in self.role_categories.items():
                    if role in roles:
                        self.role_vars[category].set(role)
                        self.log(f"自动选中身份: {role}")
                        break

    def add_known_info(self):
        """添加已知信息"""
        try:
            player = int(self.player_var.get())

            # 获取当前显示的标签页
            current_tab_index = self.role_notebook.index(self.role_notebook.select())
            current_tab_text = self.role_notebook.tab(current_tab_index, "text")

            # 优先使用当前标签页的选中身份
            selected_role = None
            selected_category = None

            # 先检查当前标签页是否有选中身份
            if current_tab_text in self.role_vars:
                current_role = self.role_vars[current_tab_text].get()
                if current_role:
                    selected_role = current_role
                    selected_category = current_tab_text

            # 如果当前标签页没有选中，再遍历所有分类（兼容旧逻辑）
            if not selected_role:
                for category, var in self.role_vars.items():
                    role = var.get()
                    if role:
                        selected_role = role
                        selected_category = category
                        break

            if not selected_role:
                messagebox.showwarning("警告", "请选择身份")
                return

            # 检查是否要修改已有身份
            old_info = self.known_info.get(player)
            if old_info:
                old_role = old_info["role"]
                old_category = old_info.get("category")
                self.log(
                    f"修改玩家{player}的身份: {old_role} [{old_category}] -> {selected_role} [{selected_category}]")
            else:
                self.log(f"添加已知信息: 玩家{player} 是 {selected_role} [{selected_category}]")

            self.known_info[player] = {
                "role": selected_role,
                "type": self.get_role_type(selected_role),
                "category": selected_category
            }

            self.update_info_listbox()
            self.update_status()
            self.update_player_card(player)

            triangle = self.get_player_triangle(player)

            # 刷新三角形分析
            self.update_triangle_analysis()

            # 清空玩家编号选择，但保留当前标签页的选中状态
            self.player_var.set('')

            # 注意：不要清空 role_vars，让当前选中的身份保留

        except ValueError:
            messagebox.showerror("错误", "请选择有效的玩家编号")

    def add_behavior_weight(self):
        """添加行为权重"""
        try:
            player = int(self.weight_player_var.get())
            wolf_weight = float(self.wolf_weight.get())
            god_weight = float(self.god_weight.get())
            human_weight = float(self.human_weight.get())

            self.behavior_weights[player] = {
                '狼权': wolf_weight,
                '神权': god_weight,
                '民权': human_weight
            }

            self.update_weight_listbox()
            self.log(f"添加行为权重: 玩家{player} 狼权={wolf_weight}, 神权={god_weight}, 民权={human_weight}")

            # 清空选择
            self.weight_player_var.set('')

        except ValueError:
            messagebox.showerror("错误", "请输入有效的玩家编号和权重数值")

    def delete_selected_weight(self):
        """删除选中的权重"""
        selection = self.weight_listbox.curselection()
        if selection:
            text = self.weight_listbox.get(selection[0])
            try:
                # 解析文本获取玩家编号
                if '玩家' in text:
                    player = int(text.split('玩家')[1].split(':')[0])
                    if player in self.behavior_weights:
                        del self.behavior_weights[player]
                        self.log(f"删除玩家{player}的行为权重")
                        self.update_weight_listbox()
            except:
                pass

    def clear_all_weights(self):
        """清除所有权重"""
        self.behavior_weights.clear()
        self.update_weight_listbox()
        self.log("已清除所有行为权重")

    def update_info_listbox(self):
        """更新信息列表"""
        self.info_listbox.delete(0, tk.END)

        # 显示已知身份
        for player, info in sorted(self.known_info.items()):
            triangle = self.get_player_triangle(player)
            role = info["role"]
            role_type = info["type"]

            if role_type == "wolf":
                prefix = "🐺"
            elif role_type == "god":
                prefix = "👼"
            elif role_type == "human":
                prefix = "👤"
            else:
                prefix = "⭐"

            display_text = f"{prefix} 玩家{player}: {role} [{triangle}]"
            self.info_listbox.insert(tk.END, display_text)

    def update_weight_listbox(self):
        """更新权重列表"""
        self.weight_listbox.delete(0, tk.END)

        for player, weights in sorted(self.behavior_weights.items()):
            display_text = f"玩家{player}: 狼{weights['狼权']:.1f} 神{weights['神权']:.1f} 人{weights['民权']:.1f}"
            self.weight_listbox.insert(tk.END, display_text)
            self.clear_all_info

    def delete_selected_info(self):
        """删除选中的信息"""
        selection = self.info_listbox.curselection()
        if selection:
            text = self.info_listbox.get(selection[0])
            try:
                # 解析文本获取玩家编号
                if '玩家' in text:
                    player = int(text.split('玩家')[1].split(':')[0])
                    if player in self.known_info:
                        del self.known_info[player]
                        self.update_player_card(player)  # 更新对应卡片的显示
                        self.log(f"删除玩家{player}的已知信息")
                self.update_info_listbox()
                self.update_triangle_analysis()
                self.update_status()
            except:
                pass

    def clear_all_info(self):
        """清空所有信息"""
        self.known_info.clear()
        self.behavior_weights.clear()  # 确保清除权重
        self.update_info_listbox()
        self.update_weight_listbox()  # 更新权重列表显示
        self.update_all_player_cards()
        self.update_triangle_analysis()
        self.update_status()

        # 清空概率显示
        for player_num in range(1, 13):
            wolf_label = self.player_labels.get(f"{player_num}_wolf_prob")
            god_label = self.player_labels.get(f"{player_num}_god_prob")
            human_label = self.player_labels.get(f"{player_num}_human_prob")

            if wolf_label:
                wolf_label.config(text="🐺0%")
            if god_label:
                god_label.config(text="👼0%")
            if human_label:
                human_label.config(text="👤0%")

        self.log("已清空所有信息")

        # 清空结果显示
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("日志已清空")

    def update_status(self):
        """更新状态栏"""
        known_count = len(self.known_info)

        # 统计各类身份
        wolf_count = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
        god_count = sum(1 for info in self.known_info.values() if info.get("type") == "god")
        human_count = sum(1 for info in self.known_info.values() if info.get("type") == "human")
        mark_count = sum(1 for info in self.known_info.values() if info.get("type") == "good_mark")

        # 这里可以更新状态栏显示，如果有需要的话

        if known_count == 0:
            self.status_label.config(text="就绪 | 等待输入已知信息")
        else:
            self.status_label.config(text=f"运行中 | 已确认 {wolf_count} 狼, 剩余 {4 - wolf_count} 狼待找")

    def log(self, message):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def get_player_triangle(self, player):
        """获取玩家所在的三角形"""
        for tri_name, tri_players in self.triangles.items():
            if player in tri_players:
                return tri_name
        return "未知"

    def update_triangle_analysis(self):
        """更新三角形分析"""
        self.triangle_status_text.delete(1.0, tk.END)

        # 分析每个三角形的状态
        triangle_stats = {}

        for tri_name, tri_players in self.triangles.items():
            known_wolves = 0
            known_gods = 0
            known_humans = 0
            known_marks = 0
            unknown = []

            for player in tri_players:
                if player in self.known_info:
                    info = self.known_info[player]
                    role_type = info.get("type", "unknown")

                    if role_type == "wolf":
                        known_wolves += 1
                    elif role_type == "god":
                        known_gods += 1
                    elif role_type == "human":
                        known_humans += 1
                    elif role_type == "good_mark":
                        known_marks += 1
                else:
                    unknown.append(player)

            triangle_stats[tri_name] = {
                "known_wolves": known_wolves,
                "known_gods": known_gods,
                "known_humans": known_humans,
                "known_marks": known_marks,
                "unknown": unknown,
                "unknown_count": len(unknown)
            }

        # 显示三角形状态
        self.triangle_status_text.insert(tk.END, "🔺 三角形实时状态\n", "bold")
        self.triangle_status_text.insert(tk.END, "═" * 40 + "\n")

        for tri_name, stats in triangle_stats.items():
            self.triangle_status_text.insert(tk.END, f"\n{tri_name}: ", "bold")
            self.triangle_status_text.insert(tk.END, f"[🐺{stats['known_wolves']} ", "wolf")
            self.triangle_status_text.insert(tk.END, f"👼{stats['known_gods']} ", "god")
            self.triangle_status_text.insert(tk.END, f"👤{stats['known_humans']} ", "human")
            self.triangle_status_text.insert(tk.END, f"⭐{stats['known_marks']}] ", "gold")
            self.triangle_status_text.insert(tk.END, f"未知:{stats['unknown_count']}\n")

            if stats['unknown']:
                self.triangle_status_text.insert(tk.END, f"   未知玩家: {sorted(stats['unknown'])}\n")

        # 三角定律分析
        self.triangle_status_text.insert(tk.END, "\n" + "═" * 40 + "\n")
        self.triangle_status_text.insert(tk.END, "📐 三角定律分析:\n", "bold")

        # 检查是否已有双狼三角形
        has_double = False
        for tri_name, stats in triangle_stats.items():
            if stats['known_wolves'] >= 2:
                has_double = True
                self.triangle_status_text.insert(tk.END, f"✅ {tri_name} 已满足双狼！\n", "wolf")

                # 跳棋原则
                opposite = self.triangle_opposites[tri_name]
                self.triangle_status_text.insert(tk.END, f"   ↪ 关注对角 {opposite} 的格局\n", "god")

        if not has_double:
            self.triangle_status_text.insert(tk.END, "⚠️ 当前尚未出现双狼三角形\n", "human")
            self.triangle_status_text.insert(tk.END, f"📊 至少一组双狼概率: ≈{1 - 0.163:.1%}\n")

        # 最有可能出双狼的三角形
        self.triangle_status_text.insert(tk.END, "\n🎯 最可能出双狼的三角形:\n", "bold")

        candidates = []
        for tri_name, stats in triangle_stats.items():
            if stats['known_wolves'] == 1 and stats['unknown_count'] >= 1:
                prob = 1 / stats['unknown_count']
                candidates.append((tri_name, prob, stats['unknown']))
            elif stats['known_wolves'] == 0 and stats['unknown_count'] >= 2:
                prob = 2 / stats['unknown_count']
                candidates.append((tri_name, prob, stats['unknown']))

        candidates.sort(key=lambda x: x[1], reverse=True)

        for tri_name, prob, unknown in candidates[:2]:
            self.triangle_status_text.insert(tk.END, f"  {tri_name}: 概率{prob:.1%} 未知:{sorted(unknown)}\n")

        # 配置标签
        self.triangle_status_text.tag_config("bold", font=("Consolas", 10, "bold"))
        self.triangle_status_text.tag_config("wolf", foreground=self.colors['wolf'])
        self.triangle_status_text.tag_config("god", foreground=self.colors['god'])
        self.triangle_status_text.tag_config("human", foreground=self.colors['human'])
        self.triangle_status_text.tag_config("gold", foreground=self.colors['gold'])

    def calculate_basic_probabilities(self):
        """计算基础概率"""
        self.law_text.delete(1.0, tk.END)

        # 三角定律
        self.law_text.insert(tk.END, "📐 三角定律分布\n", "bold")
        self.law_text.insert(tk.END, "─" * 30 + "\n")

        tri_probs = self.calculate_triangle_probabilities()
        for case, prob in tri_probs.items():
            self.law_text.insert(tk.END, f"{case}: {prob:.1%}\n")

        prob_double = 1 - tri_probs.get("四个三角各1狼", 0)
        self.law_text.insert(tk.END, f"\n✅ 至少一组双狼: {prob_double:.1%}\n\n")

        # 三行定律
        self.law_text.insert(tk.END, "📏 三行定律\n", "bold")
        self.law_text.insert(tk.END, "─" * 30 + "\n")

        row_prob = self.calculate_row_probability()
        self.law_text.insert(tk.END, f"连续三行有≥3狼: {row_prob:.1%}\n\n")

        # 四角定律
        self.law_text.insert(tk.END, "🔲 四角定律\n", "bold")
        self.law_text.insert(tk.END, "─" * 30 + "\n")

        corner_probs = self.calculate_corner_probabilities()
        for k, v in corner_probs.items():
            self.law_text.insert(tk.END, f"单组{k}狼: {v:.1%}\n")

        self.law_text.tag_config("bold", font=("Consolas", 9, "bold"))

    def calculate_triangle_probabilities(self, num_simulations=100000):
        """计算三角形分布概率"""
        case1 = case2 = case3 = case4 = 0

        for _ in range(num_simulations):
            wolves = set(random.sample(self.players, self.wolves))
            counts = []
            for tri in self.triangles.values():
                counts.append(len(wolves.intersection(tri)))

            if counts.count(2) == 2 and counts.count(0) == 2:
                case1 += 1
            elif counts.count(2) == 1 and counts.count(1) == 2:
                case2 += 1
            elif all(c == 1 for c in counts):
                case3 += 1
            elif 3 in counts:
                case4 += 1

        return {
            "两个三角各2狼": case1 / num_simulations,
            "一三角2狼+两三角1狼": case2 / num_simulations,
            "四个三角各1狼": case3 / num_simulations,
            "一三角有3狼": case4 / num_simulations
        }

    def calculate_row_probability(self, num_simulations=100000):
        """计算三行定律概率"""
        case_count = 0

        for _ in range(num_simulations):
            wolves = set(random.sample(self.players, self.wolves))
            for combo in self.row_combinations:
                if len(wolves.intersection(combo["players"])) >= 3:
                    case_count += 1
                    break

        return case_count / num_simulations

    def calculate_corner_probabilities(self, num_simulations=100000):
        """计算四角定律概率"""
        counts = {4: 0, 3: 0, 2: 0, 1: 0}

        for _ in range(num_simulations):
            wolves = set(random.sample(self.players, self.wolves))
            for group in self.corner_groups:
                count = len(wolves.intersection(group["players"]))
                if count >= 1:
                    counts[count] += 1

        total = num_simulations * len(self.corner_groups)
        return {k: v / total for k, v in counts.items()}

    def run_monte_carlo(self):
        """运行蒙特卡洛模拟"""
        try:
            sim_count = self.simulation_count
            self.log(f"开始蒙特卡洛模拟，次数: {sim_count}")

            # 清空之前的结果
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 获取未知玩家
            unknown_players = [p for p in self.players if p not in self.known_info]

            if not unknown_players:
                messagebox.showinfo("提示", "没有未知玩家需要计算")
                return

            # 初始化计数器
            role_counts = {p: {'狼人': 0, '神民': 0, '平民': 0} for p in unknown_players}

            # 统计已知身份数量
            confirmed_wolves = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
            confirmed_gods = sum(1 for info in self.known_info.values() if info.get("type") == "god")
            confirmed_humans = sum(1 for info in self.known_info.values() if info.get("type") == "human")
            confirmed_marks = sum(1 for info in self.known_info.values() if info.get("type") == "good_mark")

            remaining_wolves = self.wolves - confirmed_wolves
            remaining_gods = self.gods - confirmed_gods
            remaining_humans = self.villagers - confirmed_humans

            # 蒙特卡洛模拟
            for i in range(sim_count):
                # 分配剩余身份
                remaining_roles = ['狼人'] * remaining_wolves

                # 分配神民和平民（包括从好人标记中分配的）
                gods_to_add = remaining_gods
                humans_to_add = remaining_humans

                # 如果有好人标记，随机分配到神民和平民
                if confirmed_marks > 0:
                    gods_from_marks = random.randint(0, confirmed_marks)
                    gods_to_add += gods_from_marks
                    humans_to_add += (confirmed_marks - gods_from_marks)

                remaining_roles.extend(['神民'] * gods_to_add)
                remaining_roles.extend(['平民'] * humans_to_add)

                random.shuffle(remaining_roles)

                # 分配给未知玩家
                for player, role in zip(unknown_players, remaining_roles):
                    role_counts[player][role] += 1

                # 显示进度
                if (i + 1) % 10000 == 0:
                    self.log(f"模拟进度: {i + 1}/{sim_count}")

            # 显示结果
            for player in unknown_players:
                wolf_prob = role_counts[player]['狼人'] / sim_count
                god_prob = role_counts[player]['神民'] / sim_count
                human_prob = role_counts[player]['平民'] / sim_count
                triangle = self.get_player_triangle(player)

                # 根据概率添加标签
                if wolf_prob > 0.4:
                    tag = 'high'
                elif wolf_prob > 0.25:
                    tag = 'medium'
                else:
                    tag = 'low'

                self.tree.insert('', tk.END, values=(
                    f"玩家{player}",
                    f"{wolf_prob:.1%}",
                    f"{god_prob:.1%}",
                    f"{human_prob:.1%}",
                    triangle
                ), tags=(tag,))

            # 收集结果用于概率显示
            mc_results = {}
            for player in unknown_players:
                wolf_prob = role_counts[player]['狼人'] / sim_count
                god_prob = role_counts[player]['神民'] / sim_count
                human_prob = role_counts[player]['平民'] / sim_count
                mc_results[player] = {
                    '狼人': wolf_prob,
                    '神民': god_prob,
                    '平民': human_prob
                }

            # 更新卡片概率显示
            self.update_card_probabilities(mc_results, "蒙特卡洛")

            self.log("蒙特卡洛模拟完成")

        except Exception as e:
            messagebox.showerror("错误", f"计算过程中出现错误: {str(e)}")
            self.log(f"错误: {str(e)}")

    def run_triangle_law(self):
        """运行三角定律计算 - 同时计算三类身份概率"""
        try:
            sim_count = self.simulation_count
            self.log(f"开始三角定律计算，次数: {sim_count}")

            # 清空结果
            for item in self.tree.get_children():
                self.tree.delete(item)

            unknown_players = [p for p in self.players if p not in self.known_info]

            if not unknown_players:
                messagebox.showinfo("提示", "没有未知玩家需要计算")
                return

            # 统计已知身份数量
            known_wolves = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
            known_gods = sum(1 for info in self.known_info.values() if info.get("type") == "god")
            known_humans = sum(1 for info in self.known_info.values() if info.get("type") == "human")
            known_marks = sum(1 for info in self.known_info.values() if info.get("type") == "good_mark")

            remaining_wolves = self.wolves - known_wolves
            remaining_gods = self.gods - known_gods
            remaining_humans = self.villagers - known_humans

            # 计数器
            role_counts = {p: {'狼人': 0, '神职': 0, '平民': 0} for p in unknown_players}

            # 计算三角形权重
            triangle_weights = self.calculate_triangle_weights()

            for i in range(sim_count):
                available_players = unknown_players.copy()

                # 计算剩余身份数量（包括好人标记的分配）
                gods_to_assign = remaining_gods
                humans_to_assign = remaining_humans

                # 随机分配好人标记
                if known_marks > 0:
                    gods_from_marks = random.randint(0, known_marks)
                    gods_to_assign += gods_from_marks
                    humans_to_assign += (known_marks - gods_from_marks)

                total_remaining = len(unknown_players)

                # 构建身份池
                identity_pool = []
                identity_pool.extend(['狼人'] * remaining_wolves)
                identity_pool.extend(['神职'] * gods_to_assign)
                identity_pool.extend(['平民'] * humans_to_assign)
                random.shuffle(identity_pool)

                # 根据权重分配身份
                assigned_roles = {}

                # 先分配狼人（带权重）
                wolves_assigned = 0
                temp_players = available_players.copy()

                while wolves_assigned < remaining_wolves:
                    if not temp_players:
                        break

                    weights = []
                    for player in temp_players:
                        tri = self.get_player_triangle(player)
                        weight = triangle_weights.get(tri, 1.0)
                        if self.use_behavior_weight and player in self.behavior_weights:
                            weight *= self.behavior_weights[player].get('狼权', 1.0)
                        weights.append(weight)

                    total = sum(weights)
                    if total > 0:
                        probs = [w / total for w in weights]
                        chosen = random.choices(temp_players, weights=probs)[0]
                    else:
                        chosen = random.choice(temp_players)

                    assigned_roles[chosen] = '狼人'
                    temp_players.remove(chosen)
                    wolves_assigned += 1

                # 分配神职和平民
                remaining_for_others = [p for p in available_players if p not in assigned_roles]
                other_roles = [r for r in identity_pool if r != '狼人']
                random.shuffle(other_roles)

                for player, role in zip(remaining_for_others, other_roles):
                    assigned_roles[player] = role

                # 统计
                for player, role in assigned_roles.items():
                    if role == '狼人':
                        role_counts[player]['狼人'] += 1
                    elif role == '神职':
                        role_counts[player]['神职'] += 1
                    else:  # 平民
                        role_counts[player]['平民'] += 1

                # 显示进度
                if (i + 1) % 10000 == 0:
                    self.log(f"三角定律模拟进度: {i + 1}/{sim_count}")

            # 显示结果
            for player in unknown_players:
                wolf_prob = role_counts[player]['狼人'] / sim_count
                god_prob = role_counts[player]['神职'] / sim_count
                human_prob = role_counts[player]['平民'] / sim_count
                triangle = self.get_player_triangle(player)

                # 根据狼人概率添加标签
                if wolf_prob > 0.4:
                    tag = 'high'
                elif wolf_prob > 0.25:
                    tag = 'medium'
                else:
                    tag = 'low'

                self.tree.insert('', tk.END, values=(
                    f"玩家{player}",
                    f"{wolf_prob:.1%}",
                    f"{god_prob:.1%}",
                    f"{human_prob:.1%}",
                    triangle
                ), tags=(tag,))

            # 收集结果用于概率显示
            tri_results = {}
            for player in unknown_players:
                tri_results[player] = {
                    '狼人': role_counts[player]['狼人'] / sim_count,
                    '神职': role_counts[player]['神职'] / sim_count,
                    '平民': role_counts[player]['平民'] / sim_count
                }

            # 更新卡片概率显示
            self.update_card_probabilities(tri_results, "三角定律")

            self.log("三角定律计算完成")

        except Exception as e:
            messagebox.showerror("错误", f"计算过程中出现错误: {str(e)}")
            self.log(f"错误: {str(e)}")

    def calculate_triangle_weights(self):
        """计算三角形权重"""
        triangle_weights = {}

        for tri_name, tri_players in self.triangles.items():
            known_wolves = 0
            known_good = 0
            unknown = []

            for player in tri_players:
                if player in self.known_info:
                    info = self.known_info[player]
                    role_type = info.get("type", "unknown")

                    if role_type == "wolf":
                        known_wolves += 1
                    else:
                        known_good += 1
                else:
                    unknown.append(player)

            if known_wolves == 2:
                triangle_weights[tri_name] = 0.1
            elif known_wolves == 1:
                if len(unknown) > 0:
                    triangle_weights[tri_name] = 2.0
                else:
                    triangle_weights[tri_name] = 0.5
            elif known_wolves == 0:
                if len(unknown) >= 2:
                    triangle_weights[tri_name] = 1.8
                else:
                    triangle_weights[tri_name] = 1.0
            else:
                triangle_weights[tri_name] = 1.0

            # 好人太多的地方狼少
            if known_good >= 2:
                triangle_weights[tri_name] *= 0.7

            # 跳棋原则
            opposite_tri = self.triangle_opposites.get(tri_name)
            if opposite_tri and known_wolves == 2:
                if opposite_tri in triangle_weights:
                    triangle_weights[opposite_tri] *= 1.3

        return triangle_weights

    def run_bayesian_update(self):
        """运行贝叶斯更新 - 同时计算三类身份概率"""
        try:
            self.log("开始贝叶斯更新计算")

            # 清空结果
            for item in self.tree.get_children():
                self.tree.delete(item)

            unknown_players = [p for p in self.players if p not in self.known_info]

            if not unknown_players:
                messagebox.showinfo("提示", "没有未知玩家需要计算")
                return

            # 统计已知身份数量
            known_wolves = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
            known_gods = sum(1 for info in self.known_info.values() if info.get("type") == "god")
            known_humans = sum(1 for info in self.known_info.values() if info.get("type") == "human")
            known_marks = sum(1 for info in self.known_info.values() if info.get("type") == "good_mark")

            remaining_wolves = self.wolves - known_wolves
            remaining_gods = self.gods - known_gods
            remaining_humans = self.villagers - known_humans

            # 好人标记的分配预估
            if known_marks > 0:
                # 假设好人标记平均分配到神职和平民
                gods_from_marks = known_marks // 2
                remaining_gods += gods_from_marks
                remaining_humans += (known_marks - gods_from_marks)

            total_unknown = len(unknown_players)

            # 基础先验概率
            base_wolf_prob = remaining_wolves / total_unknown if total_unknown > 0 else 0
            base_god_prob = remaining_gods / total_unknown if total_unknown > 0 else 0
            base_human_prob = remaining_humans / total_unknown if total_unknown > 0 else 0

            # 获取三角形权重
            triangle_weights = self.calculate_triangle_weights() if self.use_triangle_law else {}

            results = {}

            for player in unknown_players:
                wolf_prob = base_wolf_prob
                god_prob = base_god_prob
                human_prob = base_human_prob

                # 三角形定律调整
                if self.use_triangle_law:
                    tri = self.get_player_triangle(player)
                    tri_weight = triangle_weights.get(tri, 1.0)
                    # 三角形权重影响狼人概率
                    wolf_prob *= tri_weight

                    # 重新归一化
                    total = wolf_prob + god_prob + human_prob
                    if total > 0:
                        wolf_prob /= total
                        god_prob /= total
                        human_prob /= total

                # 行为权重贝叶斯更新
                if self.use_behavior_weight and player in self.behavior_weights:
                    weights = self.behavior_weights[player]
                    wolf_weight = weights.get('狼权', 1.0)
                    god_weight = weights.get('神权', 1.0)
                    human_weight = weights.get('民权', 1.0)

                    total_weight = wolf_weight + god_weight + human_weight
                    if total_weight > 0:
                        # 计算各个身份的似然因子
                        wolf_likelihood = wolf_weight / (total_weight / 3)
                        god_likelihood = god_weight / (total_weight / 3)
                        human_likelihood = human_weight / (total_weight / 3)

                        # 贝叶斯更新
                        new_wolf = wolf_prob * wolf_likelihood
                        new_god = god_prob * god_likelihood
                        new_human = human_prob * human_likelihood

                        # 归一化
                        total = new_wolf + new_god + new_human
                        if total > 0:
                            wolf_prob = new_wolf / total
                            god_prob = new_god / total
                            human_prob = new_human / total

                results[player] = {
                    '狼人': wolf_prob,
                    '神职': god_prob,
                    '平民': human_prob
                }

            # 显示结果
            for player, probs in sorted(results.items(), key=lambda x: x[1]['狼人'], reverse=True):
                triangle = self.get_player_triangle(player)
                wolf_prob = probs['狼人']

                if wolf_prob > 0.4:
                    tag = 'high'
                elif wolf_prob > 0.25:
                    tag = 'medium'
                else:
                    tag = 'low'

                self.tree.insert('', tk.END, values=(
                    f"玩家{player}",
                    f"{wolf_prob:.1%}",
                    f"{probs['神职']:.1%}",
                    f"{probs['平民']:.1%}",
                    triangle
                ), tags=(tag,))

            # 更新卡片概率显示
            self.update_card_probabilities(results, "贝叶斯")

            self.log("贝叶斯更新完成")

        except Exception as e:
            messagebox.showerror("错误", f"计算过程中出现错误: {str(e)}")
            self.log(f"错误: {str(e)}")

    def run_comprehensive_analysis(self):
        """运行综合分析"""
        try:
            sim_count = self.simulation_count
            self.log(f"开始综合分析，次数: {sim_count}")

            # 清空结果
            for item in self.tree.get_children():
                self.tree.delete(item)

            unknown_players = [p for p in self.players if p not in self.known_info]

            if not unknown_players:
                messagebox.showinfo("提示", "没有未知玩家需要计算")
                return

            # 计算各项得分
            self.log("计算蒙特卡洛得分...")
            mc_scores = self.get_monte_carlo_scores(unknown_players, sim_count // 3)

            triangle_scores = {}
            bayes_scores = {}

            if self.use_triangle_law:
                self.log("计算三角形定律得分...")
                triangle_scores = self.get_triangle_scores(unknown_players, sim_count // 3)
            else:
                triangle_scores = {p: 0.5 for p in unknown_players}

            if self.use_behavior_weight:
                self.log("计算行为权重得分...")
                bayes_scores = self.get_bayes_scores(unknown_players)
            else:
                bayes_scores = {p: 0.5 for p in unknown_players}

            # 综合评分
            comprehensive_scores = {}
            for player in unknown_players:
                comprehensive_scores[player] = (
                        mc_scores[player] * 0.4 +
                        triangle_scores.get(player, 0.5) * 0.3 +
                        bayes_scores.get(player, 0.5) * 0.3
                )

            # 显示结果
            for player, score in sorted(comprehensive_scores.items(), key=lambda x: x[1], reverse=True):
                triangle = self.get_player_triangle(player)

                if score > 0.4:
                    tag = 'high'
                elif score > 0.25:
                    tag = 'medium'
                else:
                    tag = 'low'

                self.tree.insert('', tk.END, values=(
                    f"玩家{player}",
                    f"{score:.1%}",
                    f"{mc_scores[player]:.1%}",
                    f"{bayes_scores.get(player, 0):.1%}",
                    triangle
                ), tags=(tag,))

            # 收集结果用于概率显示
            comp_results = {}
            for player in unknown_players:
                comp_results[player] = {
                    '狼人': comprehensive_scores[player],
                    '神民': mc_scores[player],
                    '平民': bayes_scores.get(player, 0)
                }

            # 更新卡片概率显示
            self.update_card_probabilities(comp_results, "综合分析")

            self.log("综合分析完成")

        except Exception as e:
            messagebox.showerror("错误", f"计算过程中出现错误: {str(e)}")

    def get_monte_carlo_scores(self, unknown_players, sim_count):
        """获取蒙特卡洛得分"""
        role_counts = {p: 0 for p in unknown_players}

        known_wolves = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
        remaining_wolves = self.wolves - known_wolves

        for _ in range(sim_count):
            wolves = set(random.sample(unknown_players, remaining_wolves))
            for wolf in wolves:
                role_counts[wolf] += 1

        max_count = max(role_counts.values()) if role_counts else 1
        return {p: role_counts[p] / max_count for p in unknown_players}

    def get_triangle_scores(self, unknown_players, sim_count):
        """获取三角形定律得分"""
        wolf_counts = defaultdict(int)

        known_wolves = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
        remaining_wolves = self.wolves - known_wolves

        triangle_weights = self.calculate_triangle_weights()

        for _ in range(sim_count):
            available = unknown_players.copy()
            wolves = set()

            while len(wolves) < remaining_wolves:
                weights = []
                for player in available:
                    tri = self.get_player_triangle(player)
                    weight = triangle_weights.get(tri, 1.0)
                    if self.use_behavior_weight and player in self.behavior_weights:
                        weight *= self.behavior_weights[player].get('狼权', 1.0)
                    weights.append(weight)

                total = sum(weights)
                if total > 0:
                    probs = [w / total for w in weights]
                    chosen = random.choices(available, weights=probs)[0]
                    wolves.add(chosen)
                    available.remove(chosen)
                else:
                    chosen = random.choice(available)
                    wolves.add(chosen)
                    available.remove(chosen)

            for wolf in wolves:
                wolf_counts[wolf] += 1

        max_count = max(wolf_counts.values()) if wolf_counts else 1
        return {p: wolf_counts.get(p, 0) / max_count for p in unknown_players}

    def get_bayes_scores(self, unknown_players):
        """获取贝叶斯得分"""
        known_wolves = sum(1 for info in self.known_info.values() if info.get("type") == "wolf")
        remaining_wolves = self.wolves - known_wolves
        base_prob = remaining_wolves / len(unknown_players) if unknown_players else 0

        scores = {}
        for player in unknown_players:
            prob = base_prob

            if player in self.behavior_weights:
                weights = self.behavior_weights[player]
                wolf_weight = weights.get('狼权', 1.0)
                god_weight = weights.get('神权', 1.0)
                human_weight = weights.get('民权', 1.0)

                total_weight = wolf_weight + god_weight + human_weight
                if total_weight > 0:
                    wolf_factor = wolf_weight / (total_weight / 3)
                    good_factor = (god_weight + human_weight) / (total_weight * 2 / 3)

                    numerator = base_prob * wolf_factor
                    denominator = numerator + (1 - base_prob) * good_factor
                    prob = numerator / denominator if denominator > 0 else base_prob

            scores[player] = prob

        return scores

    def on_result_select(self, event):
        """结果选择事件"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            if values:
                self.log(f"查看结果: {values[0]} - 狼人概率{values[1]}")


def main():
    root = tk.Tk()
    app = WerewolfProbabilityGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()