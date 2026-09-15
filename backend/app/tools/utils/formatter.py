from datetime import datetime
from typing import Any



class ResponseFormatter:


    @staticmethod
    def success(
        data:Any,
        message:str="success"
    ):

        return {

            "status":"success",

            "message":message,

            "timestamp":
                datetime.utcnow().isoformat(),

            "data":data

        }



    @staticmethod
    def error(
        message:str,
        details=None
    ):

        return {

            "status":"error",

            "message":message,

            "timestamp":
                datetime.utcnow().isoformat(),

            "details":details

        }



    @staticmethod
    def tool_result(
        tool_name:str,
        result:Any
    ):

        return {

            "tool":tool_name,

            "executed_at":
                datetime.utcnow().isoformat(),

            "result":result

        }