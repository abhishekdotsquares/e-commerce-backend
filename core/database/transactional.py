from enum import Enum
from functools import wraps

from core.database import session


class Propagation(Enum):
    """Enumeration for transaction propagation types."""
    
    REQUIRED = "required"  # Use the current transaction if it exists
    REQUIRED_NEW = "required_new"  # Always create a new transaction


class Transactional:
    """Decorator to handle database transactions."""

    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        """
        Initialize the Transactional decorator.

        Args:
            propagation (Propagation): The propagation type for the transaction.
        """
        self.propagation = propagation

    def __call__(self, function):
        """Invoke the decorated function with transaction management."""
        
        @wraps(function)
        async def decorator(*args, **kwargs):
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                else:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
            except Exception as exception:
                await session.rollback()  # Rollback on exception
                raise exception  # Re-raise the exception

            return result

        return decorator

    async def _run_required(self, function, args, kwargs) -> None:
        """Run the function within the existing transaction."""
        
        result = await function(*args, **kwargs)
        await session.commit()  # Commit the transaction
        return result

    async def _run_required_new(self, function, args, kwargs) -> None:
        """Run the function in a new transaction."""
        
        session.begin()  # Start a new session
        result = await function(*args, **kwargs)
        await session.commit()  # Commit the new transaction
        return result
