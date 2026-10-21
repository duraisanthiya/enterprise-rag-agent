from unittest.mock import patch
from app.core.observability import get_langfuse_callback

def test_langfuse_callback_disabled_when_keys_missing():
    """Verify that observability returns None safely when keys are not configured."""
    with (
        patch("app.core.config.settings.LANGFUSE_PUBLIC_KEY", None),
        patch("app.core.config.settings.LANGFUSE_SECRET_KEY", None),
    ):
        handler = get_langfuse_callback()
        assert handler is None

def test_langfuse_callback_instantiated_when_keys_present():
    """Verify that CallbackHandler is created when keys are provided."""
    with (
        patch("app.core.config.settings.LANGFUSE_PUBLIC_KEY", "pk-lf-test"),
        patch("app.core.config.settings.LANGFUSE_SECRET_KEY", "sk-lf-test"),
    ):
        handler = get_langfuse_callback()
        assert handler is not None