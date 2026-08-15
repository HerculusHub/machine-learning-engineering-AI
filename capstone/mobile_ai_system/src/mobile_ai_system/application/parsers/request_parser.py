from __future__ import annotations

from mobile_ai_system.application.parsers.rule_parser import RuleParser
from mobile_ai_system.application.parsers.parse_result import ParseResult
from mobile_ai_system.application.parsers.parser_confidence import ParserConfidence
from mobile_ai_system.application.parsers.parser_validator import ParserValidator


class RequestParser:

    def __init__(self):

        self._rule_parser = RuleParser()

        self._confidence = ParserConfidence()

        self._validator = ParserValidator()

    def parse(self, text: str) -> ParseResult:

        request = self._rule_parser.parse(text)

        confidence = self._confidence.score(request)

        valid, warnings, errors = self._validator.validate(request)

        return ParseResult(
            request=request,
            parser_name="RuleParser",
            confidence=confidence,
            valid=valid,
            warnings=warnings,
            errors=errors,
        )