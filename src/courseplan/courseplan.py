class CoursePlan:
    """

    """

    def __init__(self, meta: dict, content: dict, structure: dict):
        self.metaData = meta
        self.content = content
        self.structure = structure

    def getAll(self):
        return {"meta": self.metaData, "content": self.content, "structure": self.structure}

    def __iter__(self):
        return self.getAll().__iter__()

    def __len__(self):
        return 3
