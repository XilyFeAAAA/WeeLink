# standard library
import abc
import re
from typing import TYPE_CHECKING

# local library
from weelink.core.message.component import Text
from weelink.core.message.event import MessageSource
if TYPE_CHECKING:
    from weelink.core.message.event import MessageEvent

class RuleChecker(abc.ABC):

    def __str__(self) -> None:
        return self.__class__.__name__
    
    
    @abc.abstractmethod
    def check(self, event: "MessageEvent") -> bool:
        raise NotImplementedError


class KeywordChecker(RuleChecker):
    
    def __init__(self, keywords: list[str]) -> None:
        self.keywords = keywords 


    def check(self, event: "MessageEvent") -> bool:
        if not isinstance(event, Text):
            raise Exception("KeywordChecker只支持Text类型的消息")
        return any(keyword in event.component.text for keyword in self.keywords)


class RegexChecker(RuleChecker):
    
    def __init__(self, pattern: str, flag: int) -> None:
        self.pattern = re.compile(pattern)
    
    def check(self, event: "MessageEvent") -> bool:
        if not isinstance(event, Text):
            raise Exception("RegexChecker只支持Text类型的消息")
        return re.search(self.pattern, event.component.text, self.flag)


class StartsWithChecker(RuleChecker):
    
    def __init__(self, prefix: str, ignore_case: bool = False) -> None:
        self.prefix = prefix
        self.ignore_case = ignore_case
    
    def check(self, event: "MessageEvent") -> bool:
        if not isinstance(event, Text):
            raise Exception("StartsWithChecker只支持Text类型的消息")
        
        text = event.component.text
        prefix = self.prefix
        
        if self.ignore_case:
            text = text.lower()
            prefix = prefix.lower()
            
        return text.startswith(prefix)


class EndsWithChecker(RuleChecker):
    
    def __init__(self, suffix: str, ignore_case: bool = False) -> None:
        self.suffix = suffix
        self.ignore_case = ignore_case
    
    def check(self, event: "MessageEvent") -> bool:
        if not isinstance(event, Text):
            raise Exception("EndsWithChecker只支持Text类型的消息")
        
        text = event.component.text
        suffix = self.suffix
        
        if self.ignore_case:
            text = text.lower()
            suffix = suffix.lower()
            
        return text.endswith(suffix)


class FullMatchChecker(RuleChecker):
    
    def __init__(self, text: str, ignore_case: bool = False) -> None:
        self.text = text
        self.ignore_case = ignore_case
    
    def check(self, event: "MessageEvent") -> bool:
        if not isinstance(event, Text):
            raise Exception("FullMatchChecker只支持Text类型的消息")
        
        text = event.component.text
        match_text = self.text
        
        if self.ignore_case:
            text = text.lower()
            match_text = match_text.lower()
            
        return text == match_text


class ToMeChecker(RuleChecker):
    
    def check(self, event: "MessageEvent") -> bool:
        return getattr(event, "is_at", False)


class FromChatroomChecker(RuleChecker):

    def check(self, event: "MessageEvent") -> bool:
        return event.source == MessageSource.CHATROOM


class FromFriendChecker(RuleChecker):
    
    def check(self, event: "MessageEvent") -> bool:
        return event.source == MessageSource.FRIEND


class Rule:
    
    def __init__(self, *checkers: list[RuleChecker]):
        self.checkers: list[RuleChecker] = checkers
        
    def add_checker(self, checker: RuleChecker) -> None:
        """添加额外的检查器"""
        if checker not in self.checkers:
            self.checkers.append(checker)
    
    def check(self, event: "MessageEvent") -> bool:
        """检查消息是否符合规则 """
        return True if not self.checkers \
            else all(checker.check(event) for checker in self.checkers)
    
    def __and__(self, other: "Rule") -> "Rule":
        if not isinstance(other, Rule):
            return self
        else:
            return Rule(*self.checkers, *other.checkers)
    
    
    def __rand__(self, other: "Rule") -> "Rule":
        if not isinstance(other, Rule):
            return self
        else:
            return Rule( *other.checkers, *self.checkers)


def keyword(keywords: list[str]) -> Rule:
    return Rule(
        KeywordChecker(keywords)
    )


def regex(pattern: str, flag: int) -> Rule:
    return Rule(
        RegexChecker(pattern, flag)
    )


def startswith(prefix: str, ignore_case: bool = False) -> Rule:
    return Rule(
        StartsWithChecker(prefix, ignore_case)
    )


def endswith(suffix: str, ignore_case: bool = False) -> Rule:
    return Rule(
        EndsWithChecker(suffix, ignore_case)
    )


def fullmatch(text: str, ignore_case: bool = False) -> Rule:
    return Rule(
        FullMatchChecker(text, ignore_case)
    )


def to_me() -> Rule:
    return Rule(
        ToMeChecker()
    )


def from_chatroom() -> Rule:
    return Rule(
        FromChatroomChecker()
    )


def from_friend() -> Rule:
    return Rule(
        FromFriendChecker()
    )

