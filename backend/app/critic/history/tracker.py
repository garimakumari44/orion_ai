"""
Evaluation History Tracker.

Stores and manages past evaluation runs.

Responsibilities:
- Save evaluation records
- Retrieve historical evaluations
- Query failures and trends
- Track model/output versions
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid


@dataclass
class EvaluationRecord:
    """
    Single evaluation history entry.
    """

    id: str

    timestamp: str

    model: str

    input_text: str

    output_text: str

    scores: Dict[str, float]

    issues: List[str]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class HistoryTracker:
    """
    Evaluation history manager.

    Example:

    tracker = HistoryTracker()

    tracker.add(
        model="gpt-model",
        output="answer",
        scores={
            "accuracy":0.9
        }
    )

    """

    def __init__(self):

        self.records: List[
            EvaluationRecord
        ] = []



    def add(
        self,
        model: str,
        input_text: str,
        output_text: str,
        scores: Dict[str,float],
        issues: Optional[List[str]]=None,
        metadata: Optional[Dict[str,Any]]=None
    ) -> EvaluationRecord:
        """
        Add new evaluation record.
        """

        record = EvaluationRecord(

            id=str(uuid.uuid4()),

            timestamp=datetime.utcnow()
            .isoformat(),

            model=model,

            input_text=input_text,

            output_text=output_text,

            scores=scores,

            issues=issues or [],

            metadata=metadata or {}

        )


        self.records.append(record)

        return record



    def get_all(
        self
    ) -> List[EvaluationRecord]:
        """
        Return complete history.
        """

        return self.records



    def get_by_id(
        self,
        record_id:str
    ) -> Optional[EvaluationRecord]:
        """
        Find evaluation by ID.
        """

        for record in self.records:

            if record.id == record_id:

                return record


        return None



    def latest(
        self,
        limit:int = 10
    ) -> List[EvaluationRecord]:
        """
        Return latest evaluations.
        """

        return self.records[-limit:]



    def filter_by_model(
        self,
        model:str
    ) -> List[EvaluationRecord]:
        """
        Retrieve evaluations for a model.
        """

        return [

            record

            for record in self.records

            if record.model == model

        ]



    def failed_evaluations(
        self
    ) -> List[EvaluationRecord]:
        """
        Return evaluations containing failures.
        """

        return [

            record

            for record in self.records

            if len(record.issues) > 0

        ]



    def average_scores(
        self
    ) -> Dict[str,float]:
        """
        Compute average metric scores.

        Example:

        {
          accuracy:0.86,
          citation:0.75
        }

        """

        totals = {}

        counts = {}


        for record in self.records:

            for metric,value in record.scores.items():

                totals[metric] = (
                    totals.get(metric,0)
                    +
                    value
                )

                counts[metric] = (
                    counts.get(metric,0)
                    +
                    1
                )


        return {

            metric:
                round(
                    totals[metric] /
                    counts[metric],
                    4
                )

            for metric in totals

        }



    def issue_frequency(
        self
    ) -> Dict[str,int]:
        """
        Count recurring issues.
        """

        frequency={}


        for record in self.records:

            for issue in record.issues:

                frequency[issue] = (
                    frequency.get(issue,0)
                    +
                    1
                )


        return frequency



    def clear(
        self
    ):
        """
        Clear evaluation history.
        """

        self.records.clear()



    def export(
        self
    ) -> List[Dict[str,Any]]:
        """
        Convert history into JSON-compatible format.
        """

        return [

            {
                "id":record.id,
                "timestamp":record.timestamp,
                "model":record.model,
                "input":record.input_text,
                "output":record.output_text,
                "scores":record.scores,
                "issues":record.issues,
                "metadata":record.metadata
            }

            for record in self.records

        ]