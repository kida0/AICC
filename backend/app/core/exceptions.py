"""
Custom exceptions for the application
"""


class AICallCenterException(Exception):
    """Base exception for all custom exceptions"""
    pass


class TwilioException(AICallCenterException):
    """Twilio-related errors"""
    pass


class STTException(AICallCenterException):
    """Speech-to-Text errors"""
    pass


class LLMException(AICallCenterException):
    """LLM (Language Model) errors"""
    pass


class TTSException(AICallCenterException):
    """Text-to-Speech errors"""
    pass


class StorageException(AICallCenterException):
    """Storage (S3, Database) errors"""
    pass


class CallNotFoundException(AICallCenterException):
    """Call not found in database"""
    pass


class InvalidPhoneNumberException(AICallCenterException):
    """Invalid phone number format"""
    pass


class CallLimitExceededException(AICallCenterException):
    """Maximum concurrent calls limit exceeded"""
    pass
