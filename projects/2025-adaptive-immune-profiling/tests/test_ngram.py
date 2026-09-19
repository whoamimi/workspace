import sys
import types
from pathlib import Path
import unittest

_pandas = types.ModuleType("pandas")
_pandas.DataFrame = object
sys.modules.setdefault("pandas", _pandas)

_torch = types.ModuleType("torch")
_torch_nn = types.ModuleType("torch.nn")


class _Module:
    pass


_torch_nn.Module = _Module
_torch.nn = _torch_nn
sys.modules.setdefault("torch", _torch)
sys.modules.setdefault("torch.nn", _torch_nn)

for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.ngram import NGramKernelProcessor


class FakeSeries(list):
    def astype(self, _type):
        return FakeSeries(str(value) for value in self)

    def dropna(self):
        return FakeSeries(value for value in self if value is not None)

    def unique(self):
        return list(dict.fromkeys(self))


class FakeDataFrame:
    def __init__(self, values):
        self._values = values
        self.columns = list(values.keys())

    def __getitem__(self, key):
        return FakeSeries(self._values[key])


class NGramKernelProcessorTests(unittest.TestCase):
    def test_ngram_processor_returns_context_target_pairs(self):
        data = FakeDataFrame({"v_call": ["TRBV5-1", "TRBV7-2", "TRBV5-1"]})

        processor = NGramKernelProcessor(context_size=1)

        ngrams = processor(data)

        ids = [processor.tag2id[value] for value in data["v_call"]]
        self.assertEqual(ngrams, [([ids[0]], ids[1]), ([ids[1]], ids[2])])

    def test_ngram_processor_supports_custom_column(self):
        data = FakeDataFrame({"j_call": ["TRBJ1-1", "TRBJ2-1", "TRBJ1-1"]})

        processor = NGramKernelProcessor(context_size=1, column="j_call")

        ngrams = processor(data)
        ids = [processor.tag2id[value] for value in data["j_call"]]

        self.assertEqual(ngrams, [([ids[0]], ids[1]), ([ids[1]], ids[2])])

    def test_ngram_processor_raises_for_missing_column(self):
        processor = NGramKernelProcessor(context_size=1, column="j_call")

        with self.assertRaises(KeyError):
            processor(FakeDataFrame({"v_call": ["TRBV5-1"]}))

    def test_ngram_processor_skips_null_tokens(self):
        data = FakeDataFrame({"v_call": ["TRBV5-1", None, "TRBV7-2", "TRBV5-1"]})

        processor = NGramKernelProcessor(context_size=1)

        ngrams = processor(data)

        self.assertNotIn(None, processor.tag2id)
        ids = [processor.tag2id["TRBV5-1"], processor.tag2id["TRBV7-2"], processor.tag2id["TRBV5-1"]]
        self.assertEqual(ngrams, [([ids[0]], ids[1]), ([ids[1]], ids[2])])
