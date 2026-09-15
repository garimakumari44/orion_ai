class AgentException(Exception):
    pass



class AgentExecutionError(AgentException):
    pass



class AgentValidationError(AgentException):
    pass