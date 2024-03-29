# import


class PipeParser:

    @staticmethod
    def parse(pipe_dict):
        return Pipeline(pipe_dict)


class BaseSection:

    html_class = ''

    @classmethod
    def _get_tag_attr(cls, tag, attr_name):
        attrs = tag.get('attributes', [])
        for attr in attrs:
            if attr['name'] == attr_name:
                return attr['value']
        return ''

    @classmethod
    def _get_tag_class(cls, tag):
        """以 set() 返回 html tag 中，所有 class 屬性的值"""
        class_str = cls._get_tag_attr(tag, 'class')
        return set(class_str.split(' ')) if class_str else set()

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

    @classmethod
    def _find_tag_dfs(cls, tag, tag_name):
        """深度優先(dfs)搜尋到第一個 <{tag}>，返回該 tag 的 dict"""
        # 自己是 <{tag_name}> 的時候
        if tag['name'] == tag_name:
            return tag
        # 嘗試找子孫有沒有 <{tag_name}>
        elif tag['children']:
            children = tag['children']
            for child in children:
                find_tag = cls._find_tag_dfs(child, tag_name)
                if find_tag:
                    return find_tag
        # 什麼都沒找到(自己跟後代都沒有)
        else:
            return {}

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


class LeafInputSection(BaseSection):
    """有 Input, 沒有子節點"""
    def __init__(self, remain_dict):
        super().__init__(remain_dict)
        first_input = self._find_tag_dfs(remain_dict, 'input')
        self.section_context = self._get_tag_attr(first_input, 'value')

    def __str__(self, tabwidth=4, level=0):
        indent = ' ' * tabwidth * level
        return f"{indent}{self.html_class} '{self.section_context}'\n"


class LeafTextSection(BaseSection):
    """有 Textarea, 沒有子節點"""
    def __init__(self, remain_dict):
        super().__init__(remain_dict)
        first_input = self._find_tag_dfs(remain_dict, 'textarea')
        self.section_context = self._get_tag_attr(first_input, 'value')

    def __str__(self, tabwidth=4, level=0):
        indent = ' ' * tabwidth * level
        context_indent = ' ' * tabwidth * (level + 1)
        context_list = self.section_context.split('\n')
        indented_context = ''
        # 縮排 context_indent 的每行文字
        for line in context_list:
            indented_context = indented_context + f"{context_indent}{line}\n"
        return f"{indent}{self.html_class} {{\n{indented_context}{indent}}}\n"


# inherit order is important, can't be changed arbitrarily.
class NonLeafInputSection(NonLeafSection, LeafInputSection):
    """有 Input, 有子節點"""
    def __init__(self, remain_dict):
        super().__init__(remain_dict)

    def __str__(self, tabwidth=4, level=0):
        # 先取得帶子節點的 str, 再用取代的方式填入 input 的資料
        sub_str = super().__str__(tabwidth, level)
        sub_str = sub_str.replace(' {', f"('{self.section_context}') {{", 1)
        return sub_str


class Pipeline(NonLeafSection):

    html_class = 'pipeline'
    allowed_subsections = ['agent', 'post', 'stages']


class Agent(LeafInputSection):
    html_class = 'agent'

    def __str__(self, tabwidth=4, level=0):
        original_context = super().__str__(tabwidth, level)
        return original_context.replace("'", '')


class Post(NonLeafSection):

    html_class = 'post'
    allowed_subsections = ['always']


class Stages(NonLeafSection):

    html_class = 'stages'
    allowed_subsections = ['stage']


class Stage(NonLeafInputSection):

    html_class = 'stage'
    allowed_subsections = ['when', 'environment', 'steps', 'parallel']


class When(LeafTextSection):

    html_class = 'when'


class Environment(LeafTextSection):

    html_class = 'environment'

    # def __str__(self, tabwidth=4, level=0):
    #     indent = ' ' * tabwidth * level
    #     context_indent = ' ' * tabwidth * (level + 1)
    #     context_list = self.section_context.split('\n')
    #     indented_context = ''
    #     # 縮排 context_indent 的每行文字
    #     for line in context_list:
    #         indented_context = indented_context + f"{context_indent}{line}\n"
    #     return f"{indent}environment {{\n{indented_context}{indent}}}\n"


class Steps(NonLeafSection):

    html_class = 'steps'
    allowed_subsections = ['sh', 'echo', 'jacoco']


class Always(NonLeafSection):

    html_class = 'always'
    allowed_subsections = ['always_sh', 'always_echo', 'junit']


class Parallel(NonLeafSection):

    html_class = 'parallel'
    allowed_subsections = ['stage']


class Sh(LeafTextSection):

    html_class = 'sh'

    def __str__(self, tabwidth=4, level=0):
        original_context = super().__str__(tabwidth, level)
        if '\n' in self.section_context:
            original_context = original_context.replace('{', "'''")
            original_context = original_context.replace('}', "'''")
            return original_context
        else:
            indent = ' ' * tabwidth * level
            return f"{indent}{self.html_class} '{self.section_context}'\n"


class AlwaysSh(Sh):

    html_class = 'always_sh'

    # FIXME: html_class 為 'always_sh', 但實際印出的值需要是 'sh' (目前: hard code)
    def __str__(self, tabwidth=4, level=0):
        original_context = super().__str__(tabwidth, level)
        if '\n' in self.section_context:
            original_context = original_context.replace('{', "'''")
            original_context = original_context.replace('}', "'''")
            original_context = original_context.replace('always_sh', 'sh')
            return original_context
        else:
            indent = ' ' * tabwidth * level
            return f"{indent}sh '{self.section_context}'\n"


class Echo(LeafInputSection):

    html_class = 'echo'


class AlwaysEcho(Echo):

    html_class = 'always_echo'

    # FIXME: html_class 為 'always_echo', 但實際印出的值需要是 'echo' (目前: hard code)
    def __str__(self, tabwidth=4, level=0):
        indent = ' ' * tabwidth * level
        return f"{indent}echo '{self.section_context}'\n"


class Junit(LeafInputSection):

    html_class = 'junit'


class Jacoco(LeafTextSection):

    html_class = 'jacoco'
    # allowed_subsections = ['classPattern:', 'inclusionPattern:', 'exclusionPattern:', 'execPattern:']

    def __str__(self, tabwidth=4, level=0):
        original_context = super().__str__(tabwidth, level)
        if '\n' in self.section_context:
            original_context = original_context.replace('{', "(")
            original_context = original_context.replace('}', ")")
            return original_context
        else:
            indent = ' ' * tabwidth * level
            return f"{indent}{self.html_class}({self.section_context})\n"


# {'html class name': python class name, ...}
_SECTION_DICT = {
    'pipeline': Pipeline,
    'agent': Agent,
    'post': Post,
    'stages': Stages,
    'stage': Stage,
    'when': When,
    'environment': Environment,
    'steps': Steps,
    'always': Always,
    'parallel': Parallel,
    'sh': Sh,
    'always_sh': AlwaysSh,
    'echo': Echo,
    'always_echo': AlwaysEcho,
    'junit': Junit,
    'jacoco': Jacoco,
}
