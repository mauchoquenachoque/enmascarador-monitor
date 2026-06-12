from app.masking.aes_strategy import AESStrategy
from app.masking.factory import MaskingFactory
from app.masking.fpe_strategy import FPEStrategy, FPESimulationStrategy
from app.masking.redaction_strategy import RedactionStrategy
from app.masking.sha256_strategy import SHA256Strategy

class TestRedactionStrategy:
    def test_mask_replaces_with_x(self):
        s = RedactionStrategy()
        assert s.mask("Juan") == "XXXX"
        assert s.mask("Hola Mundo") == "XXXXXXXXXX"

    def test_mask_preserves_length(self):
        s = RedactionStrategy()
        value = "Test123"
        assert len(s.mask(value)) == len(value)

    def test_name(self):
        assert RedactionStrategy().name == "redaccion"

    def test_not_reversible(self):
        assert RedactionStrategy().reversible is False

    def test_mask_dict(self):
        s = RedactionStrategy()
        data = [{"name": "Juan", "city": "Bogota"}]
        result = s.mask_dict(data, {"name": "redaccion"})
        assert result[0]["name"] == "XXXX"
        assert result[0]["city"] == "Bogota"


class TestSHA256Strategy:
    def test_mask_produces_hash(self):
        s = SHA256Strategy()
        result = s.mask("test")
        assert result.endswith("...")
        assert len(result) == 19

    def test_mask_deterministic(self):
        s = SHA256Strategy()
        assert s.mask("hello") == s.mask("hello")

    def test_mask_different_inputs(self):
        s = SHA256Strategy()
        assert s.mask("hello") != s.mask("world")

    def test_name(self):
        assert SHA256Strategy().name == "hashing"

    def test_not_reversible(self):
        assert SHA256Strategy().reversible is False


class TestAESStrategy:
    def test_mask_produces_encrypted_prefix(self):
        s = AESStrategy()
        result = s.mask("sensitive data")
        assert result.startswith("enc::")

    def test_encrypt_decrypt_raw(self):
        original = "secret message"
        encrypted = AESStrategy.encrypt_raw(original)
        decrypted = AESStrategy.decrypt_raw(encrypted)
        assert decrypted == original

    def test_name(self):
        assert AESStrategy().name == "encriptacion"

    def test_reversible(self):
        assert AESStrategy().reversible is True


class TestFPEStrategy:
    def test_mask_preserves_length(self):
        s = FPEStrategy()
        value = "Hello123"
        assert len(s.mask(value)) == len(value)

    def test_mask_preserves_format(self):
        s = FPEStrategy()
        result = s.mask("12345")
        assert result.isdigit()

    def test_mask_preserves_case(self):
        s = FPEStrategy()
        result = s.mask("AbCd")
        assert result[0].isupper()
        assert result[1].islower()

    def test_name(self):
        assert FPEStrategy().name == "fpe"


class TestFPESimulationStrategy:
    def test_mask_preserves_length(self):
        s = FPESimulationStrategy()
        value = "TestValue"
        assert len(s.mask(value)) == len(value)

    def test_mask_is_deterministic(self):
        s = FPESimulationStrategy()
        assert s.mask("hello") == s.mask("hello")


class TestMaskingFactory:
    def test_register_and_get(self):
        strategy = MaskingFactory.get("redaccion")
        assert strategy.name == "redaccion"

    def test_available_algorithms(self):
        available = MaskingFactory.available()
        assert len(available) >= 4
        keys = [a["key"] for a in available]
        assert "redaccion" in keys
        assert "hashing" in keys

    def test_apply_masking(self):
        data = [{"name": "Juan", "email": "juan@test.com"}]
        rules = {"name": "redaccion", "email": "hashing"}
        masked, used = MaskingFactory.apply_masking(data, rules)
        assert masked[0]["name"] == "XXXX"
        assert masked[0]["email"].endswith("...")
        assert "redaccion" in used
        assert "hashing" in used

    def test_apply_masking_empty_rules(self):
        data = [{"name": "Juan"}]
        masked, used = MaskingFactory.apply_masking(data, {})
        assert masked == data
        assert used == []

    def test_invalid_algorithm_raises(self):
        import pytest

        with pytest.raises(ValueError):
            MaskingFactory.get("invalid_algorithm")
