class ParserConfidence:

    def calculate(self, request: Request) -> float:

        score = 0.0

        if request.intent:
            score += 0.2

        if request.operator:
            score += 0.3

        if request.topic:
            score += 0.3

        if request.event:
            score += 0.2

        return min(score, 1.0)