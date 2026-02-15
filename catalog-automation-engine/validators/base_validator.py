"""
Base validator class that other validators should extend.
Each validator implements `validate(dataframe)` and returns a list of validation errors.
"""

from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """Abstract base validator for the catalog automation engine.
    
    Each validator inspects a dataframe and returns a list of error dictionaries.
    Error format: {"sku": str, "issue_type": str, "issue_description": str}
    """

    @abstractmethod
    def validate(self, dataframe):
        """Validate a dataframe and return a list of validation errors.
        
        Args:
            dataframe: pandas DataFrame with catalog records
            
        Returns:
            list: List of error dictionaries with keys sku, issue_type, issue_description
        """
        raise NotImplementedError("Subclasses must implement `validate`.")
