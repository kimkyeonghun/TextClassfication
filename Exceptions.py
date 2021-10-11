

class InvalidCategory(Exception):
    def __init__(self):
        self.message = "유효하지 않은 카테고리입니다."

    def __str__(self):
        return str(self.message)


class OverFlowYear(Exception):
    def __init__(self):
        self.message = "시작연도는 종료연도를 넘을 수 없습니다."

    def __str__(self):
        return str(self.message)


class InvalidMonth(Exception):
    def __init__(self):
        self.message = "달은 1과 12사이의 수이어야 합니다."

    def __str__(self):
        return str(self.message)


class OverFlowMonth(Exception):
    def __init__(self):
        self.message = "같은 해에서 시작달은 종료달을 넘을 수 없습니다."

    def __str__(self):
        return str(self.message)


class ResponseTimeout(Exception):
    def __init__(self):
        self.message = "URL을 받아올 수 없습니다."

    def __str__(self):
        return str(self.message)


class UndefineTokenizer(Exception):
    def __init__(self):
        self.message = "정의되어 있지 않은 토크나이저 입니다."

    def __str__(self):
        return str(self.message)
