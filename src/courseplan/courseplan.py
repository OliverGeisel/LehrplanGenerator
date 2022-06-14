from typing import Dict, List


class CoursePlan:
    """

    """

    def __init__(self, meta: Dict, content: Dict, structure: List):
        self.metaData = meta
        self.content = content
        self.structure = structure

    def getAll(self):
        return {"meta": self.metaData, "content": self.content, "structure": self.structure}

    def __iter__(self):
        return self.getAll().__iter__()

    def __len__(self):
        return 3
