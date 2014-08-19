#!/usr/bin/env python
# coding: utf-8
"""
Created On Nov 13, 2013

@Author : Jun Wang
"""

class ParameterError(Exception):
    """
    Base class for all parameter exceptions.
    """
    def __init__(self, message):
        super(ParameterError, self).__init__(message)
        self.message = message


class RequiredNoDefaultError(ParameterError):
    """
    This exception raised when required parameter has default value.
    """
    def __init__(self, message):
        super(RequiredNoDefaultError, self).__init__(message)
        self.message = message

    def __str__(self):
        return "Required parameter %s should't have default value" % self.message


class RequiredLackedError(ParameterError):
    """
    This exception raised when required parameter lacked.
    """
    def __init__(self, message):
        super(RequiredLackedError, self).__init__(message)
        self.message = message

    def __str__(self):
        return "Required parameter %s lacked" % self.message


class MethodError(ParameterError):
    """
    This exception raised when method is not supported.
    """
    def __init__(self, message):
        super(MethodError, self).__init__(message)
        self.message = message

    def __str__(self):
        return "Method %s is not supported" % self.message


class FormatterError(ParameterError):
    """
    This exception raised when formatter format failed.
    """
    def __init__(self, message):
        super(FormatterError, self).__init__(message)
        self.message = message

    def __str__(self):
        return "Formatter error: %s" % self.message
