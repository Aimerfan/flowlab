# import


class PipeParser:

    @staticmethod
    def parse(pipe_dict):
        return Pipeline(pipe_dict)


class BaseSection:

    html_class = ''

    @classmethod
    def _get_tag_class(cls, tag_dict):
        """以 set() 返回 html tag 中，所有 class 屬性的值"""
        for attr in tag_dict['attributes']:
            if attr['name'] == 'class':
                return set(attr['value'].split(' '))
        else:
            return set()

    @classmethod
    def _valid_html_class(cls, tag_dict):
        """驗證是否存在唯一可以對應成 Section 的 html class"""
        valid_classes = cls._get_tag_class(tag_dict) & set(_SECTION_DICT.keys())
        if len(valid_classes) == 1:
            return valid_classes.pop()
        elif len(valid_classes) == 0:
            return ''
        else:
            raise Exception('More than 1 valid section keyword in HTML classes.')

    def __init__(self, remain_dict):
        # 驗證 html class 正確對應 python class 型態
        if self.html_class not in self._get_tag_class(remain_dict):
            raise Exception(f'HTML Tag classes mismatch.')

    def __str__(self, tabwidth=4, level=0):
        raise Exception('BaseSection.__str__() must be override.')

    def str(self):
        return self.__str__()

    def debug_tree_print(self):
        next_level = getattr(self, 'subsections', [])
        print(self.html_class)
        while next_level:
            grand_level = []
            for section in next_level:
                print(section.html_class, end=' ')
                grands = getattr(section, 'subsections', [])
                if grands:
                    grand_level.extend(grands)
            else:
                print()
            next_level = grand_level


class NonLeafSection(BaseSection):
    """沒有 Input, 有子節點"""

    allowed_subsections = []

    def __init__(self, remain_dict):
        super().__init__(remain_dict)
        self.subsections = []
        self._build_children(remain_dict)

    def __str__(self, tabwidth=4, level=0):
        desc_str = ''
        for child in self.subsections:
            desc_str = desc_str + child.__str__(tabwidth, level+1)
        indent = ' ' * tabwidth * level
        return f"{indent}{self.html_class} {{\n{desc_str}{indent}}}\n"

    def _build_children(self, remain_dict):
        """解析並建立子區塊 (sub sections)"""
        for child in remain_dict['children']:
            valid_class = self._valid_html_class(child)
            if valid_class:
                # 如果 child 的 class 不在白名單(不是合法的 child)
                if valid_class not in self.allowed_subsections:
                    raise Exception(f'{self.html_class} not allowed child {valid_class}.')
                sub = _SECTION_DICT.get(valid_class)(child)
                self.subsections.append(sub)


class LeafTextSection(BaseSection):
    """有 Input, 沒有子節點"""

    def __init__(self, remain_dict):
        super().__init__(remain_dict)
        self.section_context = self._dfs_input_str(remain_dict)

    def __str__(self, tabwidth=4, level=0):
        indent = ' ' * tabwidth * level
        return f"{indent}{self.html_class} '{self.section_context}'\n"

    def _dfs_input_str(self, remain_dict):
        """深度優先(dfs)搜尋到第一個 <input>，返回其中的 input value"""
        # 自己是 <input> 的時候
        if remain_dict['name'] == 'input':
            tag_attrs = remain_dict['attributes']
            for attr in tag_attrs:
                if attr['name'] == 'value':
                    return attr['value']
        # 嘗試找子孫有沒有 <input>
        else:
            children = remain_dict['children']
            for child in children:
                search_child = self._dfs_input_str(child)
                if search_child:
                    return search_child
        # 什麼都沒找到(自己跟後代都沒有)，或是 <input> 沒有 value attr.
        return ''


# inherit order is important, can't be changed arbitrarily.
class NonLeafTextSection(NonLeafSection, LeafTextSection):
    """有 Input, 有子節點"""

    def __init__(self, remain_dict):
        super().__init__(remain_dict)

    def __str__(self, tabwidth=4, level=0):
        sub_str = super().__str__(tabwidth, level)
        sub_str = sub_str.replace(' {', f"('{self.section_context}') {{", 1)
        return sub_str


class Pipeline(NonLeafSection):

    html_class = 'pipeline'
    allowed_subsections = ['stages']


class Stages(NonLeafSection):

    html_class = 'stages'
    allowed_subsections = ['stage']


class Stage(NonLeafTextSection):

    html_class = 'stage'
    allowed_subsections = ['when', 'steps', 'parallel']


class When(LeafTextSection):

    html_class = 'when'


class Steps(NonLeafSection):

    html_class = 'steps'
    allowed_subsections = ['single_sh', 'multi_sh', 'echo']


class Parallel(NonLeafSection):

    html_class = 'parallel'
    allowed_subsections = ['stage']


class SingleSh(LeafTextSection):

    html_class = 'single_sh'


class MultiSh(LeafTextSection):

    html_class = 'multi_sh'

    def __str__(self, tabwidth=4, level=0):
        return f"{self.html_class} '''\n{self.section_context}\n'''\n"


class Echo(LeafTextSection):

    html_class = 'echo'


# {'html class name': python class name, ...}
_SECTION_DICT = {
    'pipeline': Pipeline,
    'stages': Stages,
    'stage': Stage,
    'when': When,
    'steps': Steps,
    'parallel': Parallel,
    'single_sh': SingleSh,
    'multi_sh': MultiSh,
    'echo': Echo,
}
