import pytest

from app.database.factory import DatabaseFactory


class TestDatabaseFactory:
    def test_register_engine(self):
        class MockDB:
            pass

        DatabaseFactory.register("mock_test", MockDB)
        assert "mock_test" in DatabaseFactory.available_engines()

    def test_create_unknown_engine_raises(self):
        with pytest.raises(ValueError, match="no soportado"):
            DatabaseFactory.create("unknown_engine", {})

    def test_available_engines_returns_list(self):
        engines = DatabaseFactory.available_engines()
        assert isinstance(engines, list)
        assert len(engines) > 0

    def test_create_sqlite(self):
        engine = DatabaseFactory.create("sqlite", {"database": ":memory:"})
        assert engine is not None

    def test_factory_is_singleton_pattern(self):
        e1 = DatabaseFactory.create("sqlite", {"database": ":memory:"})
        e2 = DatabaseFactory.create("sqlite", {"database": ":memory:"})
        assert type(e1) == type(e2)
