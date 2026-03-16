#
#   transaction.py
#
#   Class: _FLExTransaction
#          Context manager for safe rollback transactions within a FLEx project.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)


class _FLExTransaction:
    """
    Context manager providing safe rollback transactions on a FLEx project.

    Marks a point in the LCM undo stack (if supported) and rolls back to
    that mark if an exception occurs inside the block.

    This is Phase 1 (rollback-only) behavior. The transaction does NOT
    appear in the FLEx Ctrl+Z undo menu - it is a programmatic safety net.

    Usage::

        with project.Transaction("Import entries") as txn:
            project.LexEntry.Create("run", "stem")
            project.LexEntry.Create("walk", "stem")
        # If any line raises, all changes in the block are rolled back.

    Nesting Behavior:
        Nested transactions are allowed but share outer-level semantics:
        a rollback in an inner transaction rolls back to the outer mark.
        This is documented behavior, not an error.

    Note:
        This class is internal. Obtain instances via FLExProject.Transaction().
    """

    def __init__(self, project, label, mark_fn, rollback_fn):
        """
        Initialize transaction.

        Args:
            project:     The FLExProject instance
            label:       Human-readable description (for logging)
            mark_fn:     Callable() -> mark_token  (LCM mark API)
            rollback_fn: Callable(mark_token)      (LCM rollback API)
        """
        self._project = project
        self._label = label
        self._mark_fn = mark_fn
        self._rollback_fn = rollback_fn
        self._mark = None
        self._committed = False

    def __enter__(self):
        """
        Enter the transaction context.

        If the project is write-enabled, attempts to mark a rollback point.
        If the project is read-only or marking fails, logs a warning and continues.
        """
        if not self._project.writeEnabled:
            # Silently allow entering on read-only project;
            # any writes will fail anyway at BaseOperations validation.
            self._mark = None
            logger.debug(f"Transaction '{self._label}': read-only project, skipping mark")
            return self

        try:
            self._mark = self._mark_fn()
            logger.debug(f"Transaction '{self._label}': marked at {self._mark}")
        except Exception as e:
            logger.warning(f"Transaction '{self._label}': could not set mark: {e}")
            self._mark = None

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the transaction context.

        On success (no exception): commits changes (nothing explicit needed).
        On failure (exception raised): attempts rollback to the mark.
        Re-raises the original exception in all cases.
        """
        if exc_type is None:
            # Success path: commit (nothing explicit needed in non-undoable mode)
            self._committed = True
            logger.debug(f"Transaction '{self._label}': committed")
            return False  # Do not suppress exceptions (none occurred)

        # Failure path: rollback
        logger.warning(
            f"Transaction '{self._label}': exception {exc_type.__name__}, "
            f"rolling back to mark {self._mark}"
        )

        if self._mark is not None and self._rollback_fn is not None:
            try:
                self._rollback_fn(self._mark)
                logger.info(f"Transaction '{self._label}': rollback successful")
            except Exception as rollback_err:
                logger.error(
                    f"Transaction '{self._label}': ROLLBACK FAILED: {rollback_err}. "
                    f"Project may be in inconsistent state. Consider closing without saving."
                )
        else:
            logger.warning(
                f"Transaction '{self._label}': no mark available, "
                f"rollback not performed. Changes from this block are NOT reversed."
            )

        return False  # Re-raise the original exception
