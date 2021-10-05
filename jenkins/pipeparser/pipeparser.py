from bs4 import BeautifulSoup


class PipeParser:

    @staticmethod
    def parse(raw_div):
        soup = BeautifulSoup(raw_div, 'html.parser')
        pipe_root_tag = soup.find(attrs={'class': 'pipeline'})
        pipe_tree = Pipeline(pipe_root_tag)
        return pipe_tree


class BaseSection:

    html_class = ''
    allowed_subsections = []
    pipe_str = ''

    def __init__(self, remain_tags):
        self.section_content = ''
        self.subsections = []
        self._parse(remain_tags)
        # raise Exception('BaseSection.__init__() must be override.')

    def __str__(self):
        # raise Exception('BaseSection.__str__() must be override.')
        children_pipe_str = ''
        for child in self.subsections:
            children_pipe_str = children_pipe_str + child.str()
        return self.pipe_str.format(children_pipe_str=children_pipe_str)

    def str(self):
        return self.__str__()

    def _parse(self, remain_tags):
        # TODO: self.section_content
        section_keys_set = set(_SECTION_DICT.keys())
        for child in remain_tags.children:
            valid_classes = set(child['class']) & section_keys_set
            if len(valid_classes) == 1:
                valid_class = list(valid_classes)[0]
                sub = _SECTION_DICT.get(valid_class)(child)
                self.subsections.append(sub)
            else:
                raise Exception(f'bs4 Tag {child} has valid class is not equal to 1.')


class Pipeline(BaseSection):

    html_class = 'pipeline'
    allowed_subsections = ['stages']
    pipe_str = 'pipeline { {children_pipe_str} }'


class Stages(BaseSection):

    html_class = 'stages'
    allowed_subsections = ['stage']
    pipe_str = 'stages { {children_pipe_str} }'


class Stage(BaseSection):

    html_class = 'stage'
    allowed_subsections = ['when', 'steps', 'parallel']
    pipe_str = 'stage { {children_pipe_str} }'


class When(BaseSection):

    html_class = 'when'
    allowed_subsections = []
    pipe_str = 'when { {children_pipe_str} }'


class Steps(BaseSection):

    html_class = 'steps'
    allowed_subsections = ['single_sh', 'multi_sh', 'echo']
    pipe_str = 'steps { {children_pipe_str} }'


class Parallel(BaseSection):

    html_class = 'parallel'
    allowed_subsections = ['stage']
    pipe_str = 'parallel { {children_pipe_str} }'


class SingleSh(BaseSection):

    html_class = 'single_sh'
    allowed_subsections = []
    pipe_str = "sh ''"


class MultiSh(BaseSection):

    html_class = 'multi_sh'
    allowed_subsections = []
    pipe_str = "sh ''' '''"


class Echo(BaseSection):

    html_class = 'echo'
    allowed_subsections = []
    pipe_str = "echo ''"


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
